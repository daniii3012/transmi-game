"""Tie the local service catalogue to the published GTFS and emit the departures the engine runs.

The simulator dispatched on a binary rule —four minutes in peak, eight the rest— identical for the
137 services. The feed publishes the real departure of every trip, so the rule can go. What this
builds is the correspondence between both catalogues and, for every service that matches, the list
of departures per GTFS service_id.

Three decisions, all of them visible in the audit file:

  * Correspondence is exact on code and destination, normalised NFC because the two catalogues come
    from the same family of data and write accents decomposed. No fuzzy matching: a service that
    does not match stays pending and keeps the synthetic rule, flagged, instead of being guessed.
  * A local service can map to several GTFS route records. They are calendar or pattern splits of
    the same service —one record for weekdays, another for Saturday— and their departures add up.
  * A GTFS record whose name carries `||`, or whose code joins two codes, is a full round trip
    covering two local services. Those are never matched: one such trip is one bus, and attaching
    it to both codes would invent a second one. They are listed apart.

Calendars are not collapsed into the project's three day types. What travels to the browser is the
GTFS calendar as published —weekday flags plus added and removed dates— so that which services run
on a date is decided once, by GTFS rules, over the real date.
"""
import csv
import json
import statistics
from statistics import median
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / 'app/dist/services.json'
OUT_APP = ROOT / 'app/dist/schedule.json'
OUT_AUDIT = ROOT / 'data/processed/schedule_audit.json'
SCOPE = ('1', '6')
DAYS = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')


def norm(text):
    """NFC, upper, single spaces. Los dos catálogos escriben los acentos descompuestos."""
    return ' '.join(unicodedata.normalize('NFC', (text or '')).upper().split())


def combined(route):
    """True when the record is a round trip covering two services, not one direction of one."""
    return '||' in route['route_long_name'] or '-' in route['route_short_name'].strip()


def newest(folder):
    latest = folder / 'latest.json'
    if not latest.exists():
        raise SystemExit('Falta data/raw/gtfs/latest.json: ejecutar antes tools/fetch_gtfs.py')
    return folder / json.loads(latest.read_text(encoding='utf-8'))['folder']


def read(path):
    with path.open(encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))


def correspondence(routes, catalogue):
    """(matches, pending, combined records). Exact on code and destination, nothing else."""
    index = defaultdict(list)
    aside = []
    for route in routes:
        if route['agency_id'] not in SCOPE:
            continue
        if combined(route):
            aside.append(route)
            continue
        index[(norm(route['route_short_name']), norm(route['route_long_name']))].append(route)
    matches, pending = {}, []
    for service in catalogue:
        if not service.get('ready'):
            continue
        key = (norm(service['code']), norm(service['name']))
        found = index.get(key)
        if not found:
            candidates = sorted({r['route_long_name'] for r in routes
                                 if norm(r['route_short_name']) == key[0] and r['agency_id'] in SCOPE})
            pending.append({'id': service['id'], 'code': service['code'], 'name': service['name'],
                            'dual': bool(service.get('dual')), 'variant': service.get('variant'),
                            'reason': 'sin destino equivalente en el paquete' if candidates else 'el código no está en el paquete',
                            'gtfs_same_code': candidates})
            continue
        matches[service['id']] = found
    return matches, pending, aside


BUCKETS = ('peak', 'weekday', 'saturday', 'holiday')


def running_times(service, found, by_route, segments):
    """(list of [base, peak, weekday, saturday, holiday] seconds per stretch, or None and a reason).

    The published stretch time carries the dwell inside it, because the feed gives arrival equal to
    departure at every stop. It is handed over raw: what to subtract for dwell and for signals is
    the engine's business, which is where those two are actually modelled.

    Se exige que los dos catálogos cuenten las mismas paradas. Alinear por índice dos secuencias de
    distinto largo emparejaría tramos que no son el mismo trecho de vía, y el error no se vería.
    """
    wanted = len(service.get('stops') or []) - 1
    if wanted < 1:
        return None, 'el servicio local no tiene tramos'
    # Los registros publicados de un mismo servicio suelen repartirse el calendario: uno lleva los
    # días laborables y otro el sábado. Para cada tipo de día manda el que más viajes aportó a ese
    # tipo; quedarse solo con el registro mayor daría al sábado los tiempos de un martes.
    usable = [r for r in found if len(segments.get(r['route_id']) or []) == wanted]
    if not usable:
        counts = sorted({len(segments.get(r['route_id']) or []) for r in found})
        return None, f'el catálogo local cuenta {wanted} tramos y el paquete {counts}'
    rows = {r['route_id']: sorted(segments[r['route_id']], key=lambda x: int(x['index'])) for r in usable}
    out = []
    for index in range(wanted):
        here = [rows[r['route_id']][index] for r in usable]
        base = median([float(x['seconds']) for x in here])
        if base <= 0:
            return None, 'algún tramo publicado dura cero segundos'
        entry = [round(base, 1)]
        for bucket in BUCKETS:
            best = max(here, key=lambda x: int(x.get(f'trips_{bucket}') or 0))
            value = best.get(f'seconds_{bucket}')
            # Un tipo de día sin viajes en ningún registro cae al agregado: mejor eso que inventarlo.
            entry.append(round(float(value), 1) if value and int(best[f'trips_{bucket}']) else round(base, 1))
        out.append(entry)
    return out, None


def percentiles(values):
    if not values:
        return None
    ordered = sorted(values)
    take = lambda q: round(ordered[min(len(ordered) - 1, int(len(ordered) * q))] / 60, 1)
    return {'p10': take(.1), 'p50': take(.5), 'p90': take(.9), 'n': len(ordered)}


def main():
    source = newest(ROOT / 'data/raw/gtfs')
    manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
    routes = read(source / 'routes.txt')
    calendar = read(source / 'calendar.txt')
    exceptions = read(source / 'calendar_dates.txt') if (source / 'calendar_dates.txt').exists() else []
    trips = read(source / 'trunk_trips.csv')
    tramos_crudos = read(source / 'trunk_segments.csv') if (source / 'trunk_segments.csv').exists() else []
    catalogue = json.loads(CATALOGUE.read_text(encoding='utf-8'))['routes']

    matches, pending, aside = correspondence(routes, catalogue)
    print(f'{len(matches)} servicios emparejados, {len(pending)} pendientes, {len(aside)} registros de vuelta completa apartados')

    by_route = defaultdict(list)
    for trip in trips:
        by_route[trip['route_id']].append(trip)

    segments = defaultdict(list)
    for row in tramos_crudos:
        segments[row['route_id']].append(row)

    salidas, auditoria, sin_tramos = {}, [], []
    for local_id, found in sorted(matches.items()):
        service = next(s for s in catalogue if s['id'] == local_id)
        departures, durations, metres = defaultdict(list), defaultdict(list), []
        for route in found:
            for trip in by_route.get(route['route_id'], []):
                departure, arrival = int(trip['departure_s']), int(trip['arrival_s'])
                departures[trip['service_id']].append(departure)
                durations[trip['service_id']].append(arrival - departure)
                if float(trip['metres']) > 0:
                    metres.append(float(trip['metres']))
        if not any(departures.values()):
            pending.append({'id': local_id, 'code': service['code'], 'name': service['name'],
                            'dual': bool(service.get('dual')), 'variant': service.get('variant'),
                            'reason': 'emparejado pero sin viajes en el paquete',
                            'gtfs_same_code': [r['route_id'] for r in found]})
            continue
        salidas[local_id] = {
            'gtfs': [r['route_id'] for r in found],
            'departures': {k: sorted(v) for k, v in sorted(departures.items())},
        }
        tramos, motivo = running_times(service, found, by_route, segments)
        if tramos:
            salidas[local_id]['segments'] = tramos
        else:
            sin_tramos.append({'id': local_id, 'code': service['code'], 'name': service['name'],
                               'reason': motivo})
        auditoria.append({
            'id': local_id, 'code': service['code'], 'name': service['name'],
            'dual': bool(service.get('dual')),
            'gtfs': [{'route_id': r['route_id'], 'agency_id': r['agency_id'],
                      'short': r['route_short_name'], 'long': r['route_long_name']} for r in found],
            'trips': sum(len(v) for v in departures.values()),
            'by_service': {k: len(v) for k, v in sorted(departures.items())},
            'duration_min': {k: percentiles(v) for k, v in sorted(durations.items())},
            'metres_median': round(statistics.median(metres)) if metres else None,
            'local_length_m': service.get('length_m'),
            'segments': len(salidas[local_id].get('segments') or []),
            'segments_total_s': round(sum(s[0] for s in salidas[local_id].get('segments') or [])),
        })

    calendario = {row['service_id']: {'days': [int(row[d]) for d in DAYS],
                                      'start': row['start_date'], 'end': row['end_date']}
                  for row in calendar}
    excepciones = defaultdict(lambda: {'added': [], 'removed': []})
    for row in exceptions:
        excepciones[row['service_id']]['added' if row['exception_type'] == '1' else 'removed'].append(row['date'])

    app = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'source': {'folder': source.name, 'sha256': manifest['sources'][0]['sha256'],
                   'retrieved_at_utc': manifest['sources'][0]['retrieved_at_utc'],
                   'feed_info': manifest.get('feed_info'), 'url': manifest['sources'][0]['url']},
        'scope': 'Troncal y Dual. Alimentador, zonal y cable quedan fuera.',
        'calendar': calendario,
        'exceptions': {k: v for k, v in sorted(excepciones.items())},
        'routes': salidas,
        'pending': sorted(pending, key=lambda p: (p['code'], p['name'])),
        'without_segments': sorted(sin_tramos, key=lambda p: (p['code'], p['name'])),
    }
    OUT_APP.write_text(json.dumps(app, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')

    OUT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    OUT_AUDIT.write_text(json.dumps({
        'generated_at_utc': app['generated_at_utc'],
        'source': app['source'],
        'matched': len(salidas), 'pending': len(app['pending']),
        'combined_records': [{'route_id': r['route_id'], 'short': r['route_short_name'],
                              'long': r['route_long_name']} for r in aside],
        'routes': sorted(auditoria, key=lambda a: (a['code'], a['name'])),
        'still_pending': app['pending'],
        'without_segments': app['without_segments'],
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    con = sum(1 for r in salidas.values() if r.get('segments'))
    print(f'{con} servicios con tiempos por tramo, {len(sin_tramos)} sin ellos')
    total = sum(len(v) for r in salidas.values() for v in r['departures'].values())
    print(f'{total:,} salidas en {len(salidas)} servicios -> {OUT_APP.relative_to(ROOT)} '
          f'({OUT_APP.stat().st_size / 1e6:.2f} MB)')
    print(f'auditoría -> {OUT_AUDIT.relative_to(ROOT)}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
