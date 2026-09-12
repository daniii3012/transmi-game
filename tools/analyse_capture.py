"""Turn captured GTFS-Realtime readings into what the published timetable cannot say.

The feed gives arrival equal to departure at every stop, so the published stretch time carries the
dwell inside it and there is no way to separate them from the package alone. Observing the system
does separate them, and it also answers the question the timetable cannot: not how long a stretch
*should* take, but how long it took.

Four measurements, in increasing order of how much data they need:

  cobertura   how many builds were captured, over what span, and where the gaps are
  flota       vehicles by hour and component, the curve the fixed dispatch rule stood in for
  tramos      observed stop-to-stop time against the published one, per route and stretch
  intervalos  spacing between consecutive buses of a route reaching the same stop

Why stretches and not speeds. Each vehicle refreshes its GPS on its own cadence while the feed keeps
repeating its last known position, so between two builds a bus may show no movement and then a jump
that is catching up rather than travelling: reading a speed off two consecutive builds invents
values above 150 km/h. The stop a bus is heading to does not suffer from that, and the moment it
changes is the moment the bus left the previous one. Everything here is built on those changes.

Standard library only, like the rest of the data tools.
"""
import argparse
import csv
import gzip
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAPTURE = ROOT / 'data/raw/rt_capture'
OUT = ROOT / 'data/processed/rt_capture_analysis.json'


def read_csv(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def newest_gtfs():
    latest = ROOT / 'data/raw/gtfs/latest.json'
    if not latest.exists():
        raise SystemExit('Falta data/raw/gtfs/latest.json: ejecutar antes tools/fetch_gtfs.py')
    return ROOT / 'data/raw/gtfs' / json.loads(latest.read_text(encoding='utf-8'))['folder']


def percentiles(values, scale=1.0, digits=1):
    if not values:
        return None
    ordered = sorted(values)
    take = lambda q: round(ordered[min(len(ordered) - 1, int(len(ordered) * q))] / scale, digits)
    return {'n': len(ordered), 'p10': take(.1), 'p50': take(.5), 'p90': take(.9)}


def cobertura(summary):
    """Builds captured, span and the gaps, because an average over a broken series lies."""
    builds = sorted({int(row['build']) for row in summary if 'build' in row})
    if not builds:
        return {'builds': 0}
    gaps = [(a, b - a) for a, b in zip(builds, builds[1:]) if b - a > 120]
    failures = sum(1 for row in summary if 'error' in row)
    return {
        'builds': len(builds), 'failures': failures,
        'from': datetime.fromtimestamp(builds[0]).isoformat(timespec='seconds'),
        'to': datetime.fromtimestamp(builds[-1]).isoformat(timespec='seconds'),
        'span_h': round((builds[-1] - builds[0]) / 3600, 2),
        'median_step_s': round(statistics.median(b - a for a, b in zip(builds, builds[1:]))) if len(builds) > 1 else None,
        'gaps_over_2min': [{'at': datetime.fromtimestamp(a).isoformat(timespec='seconds'),
                            'seconds': b} for a, b in gaps[:20]],
        'gaps_total': len(gaps),
    }


def flota(summary):
    """Vehicles by hour and component: the curve the 4/8 minute rule was standing in for."""
    by_hour = defaultdict(lambda: defaultdict(list))
    for row in summary:
        if 'by_agency' not in row:
            continue
        hour = int(float(row['hour']))
        for agency, count in row['by_agency'].items():
            by_hour[hour][agency].append(count)
        by_hour[hour]['Troncal+Dual'].append(row.get('trunk', 0))
    return {str(hour): {agency: round(statistics.median(v)) for agency, v in sorted(agencies.items())}
            for hour, agencies in sorted(by_hour.items())}


def transiciones(detail):
    """(bus, trip) -> ordered [(build, stop_id, sequence)] of the moments the target stop changed.

    Se toma el primer lote en que aparece la parada nueva. La transición ocurrió entre ese lote y el
    anterior, así que cada instante trae hasta un intervalo de muestreo de incertidumbre; sobre
    muchas observaciones se compensa, sobre una no.
    """
    trips = defaultdict(list)
    for row in detail:
        trips[(row['bus'], row['viaje'])].append(row)
    out = {}
    for key, rows in trips.items():
        rows.sort(key=lambda r: int(r['build']))
        marks, previous = [], None
        for row in rows:
            if row['parada'] != previous:
                marks.append((int(row['build']), row['parada'], row['secuencia'], row['ruta']))
                previous = row['parada']
        if len(marks) > 1:
            out[key] = marks
    return out


def tramos(detail, published, minimum=3):
    """Observed stop-to-stop time against the published one, joined by route and both stop ids.

    Lo observado va de dejar una parada a dejar la siguiente; lo publicado, de una parada a la otra.
    Difieren en a qué extremo se atribuye la atención, no en cuánto incluyen: ambos son un trecho
    más una atención. Se emparejan por identificadores de parada, no por posición en la lista, para
    no comparar trechos distintos cuando un patrón corto cambia la numeración.
    """
    observed = defaultdict(list)
    for marks in transiciones(detail).values():
        for (t1, stop1, _, route), (t2, stop2, _, _) in zip(marks, marks[1:]):
            if t2 > t1:
                observed[(route, stop1, stop2)].append(t2 - t1)
    rows, matched, unmatched = [], 0, 0
    for key, times in sorted(observed.items()):
        reference = published.get(key)
        if not reference:
            unmatched += len(times)
            continue
        matched += len(times)
        rows.append({'route_id': key[0], 'from_stop': key[1], 'to_stop': key[2],
                     'observed': percentiles(times), 'published_s': reference['seconds'],
                     'metres': reference['metres']})
    # La razón se reparte por duración publicada porque la medición no vale igual en todas. El
    # instante de cada transición se conoce con la resolución del muestreo, así que en un tramo de
    # minuto y medio el error es una fracción grande de lo medido y en uno de cinco minutos no.
    bands = (('<90 s', 0, 90), ('90-150 s', 90, 150), ('150-240 s', 150, 240), ('>240 s', 240, 1e9))
    usable = [r for r in rows if r['published_s'] > 0 and r['observed']['n'] >= minimum]
    by_band = {}
    for label, low, high in bands:
        got = [r['observed']['p50'] / r['published_s'] for r in usable if low <= r['published_s'] < high]
        if got:
            by_band[label] = percentiles(got, digits=2)
    ratios = [r['observed']['p50'] / r['published_s'] for r in usable]
    return {
        'stretches': len(rows), 'observations_matched': matched, 'observations_unmatched': unmatched,
        'minimum_observations_per_stretch': minimum,
        'ratio_observed_over_published': percentiles(ratios, digits=2) if ratios else None,
        'ratio_by_published_duration': by_band,
        'reliable_from_s': 150,
        'detail': sorted(rows, key=lambda r: -r['observed']['n'])[:200],
    }


def intervalos(detail, agency_of):
    """Spacing between consecutive buses of one route reaching the same stop.

    El horario publica cada cuánto sale un bus, no cada cuánto llega: si se agrupan por el camino,
    solo se ve observando. Aquí el intervalo es entre dos buses distintos que dejan la misma parada
    de la misma ruta, uno detrás de otro.
    """
    arrivals = defaultdict(list)
    for (bus, _), marks in transiciones(detail).items():
        for build, stop, _, route in marks:
            arrivals[(route, stop)].append((build, bus))
    gaps = defaultdict(list)
    for (route, stop), events in arrivals.items():
        events.sort()
        for (t1, bus1), (t2, bus2) in zip(events, events[1:]):
            if bus1 != bus2 and 0 < t2 - t1 < 3600:
                gaps[agency_of.get(route, '?')].append(t2 - t1)
    out = {}
    for agency, values in gaps.items():
        if len(values) < 20:
            continue
        ordered = sorted(values)
        out[agency] = {**percentiles(values, 60),
                       'bunched_under_60s_pct': round(100 * sum(1 for x in ordered if x < 60) / len(ordered))}
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--capture', default=str(DEFAULT_CAPTURE), help='Carpeta con rt.jsonl y los rt_detalle_*.csv.gz')
    parser.add_argument('--out', default=str(OUT), help='Informe de salida')
    parser.add_argument('--min-observations', type=int, default=3, help='Observaciones mínimas para que un tramo cuente en la razón')
    args = parser.parse_args()

    folder = Path(args.capture)
    summary_path = folder / 'rt.jsonl'
    if not summary_path.exists():
        raise SystemExit(f'No hay capturas en {folder}: ejecutar antes tools/capture_rt.py')
    summary = []
    for line in summary_path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            summary.append(json.loads(line))

    source = newest_gtfs()
    routes = read_csv(source / 'routes.txt')
    agencies = {'1': 'Troncal', '2': 'Alimentador', '3': 'Zonal urbano', '4': 'Zonal complementario',
                '5': 'Zonal especial', '6': 'Dual', '7': 'Cable'}
    agency_of = {r['route_id']: agencies.get(r['agency_id'], '?') for r in routes}
    published = {(r['route_id'], r['from_stop'], r['to_stop']):
                 {'seconds': float(r['seconds']), 'metres': float(r['metres'])}
                 for r in read_csv(source / 'trunk_segments.csv')}

    detail, days, provenance = [], [], []
    for path in sorted(folder.glob('rt_detalle_*.csv.gz')):
        detail.extend(read_csv(path))
        days.append(path.name)
        sidecar = path.with_suffix('').with_suffix('.json')
        if sidecar.exists():
            provenance.append({'file': path.name, **json.loads(sidecar.read_text(encoding='utf-8'))})

    print(f'{len(summary):,} lecturas de resumen, {len(detail):,} filas de detalle en {len(days)} día(s)')
    report = {
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'capture_folder': str(folder), 'detail_files': days,
        'gtfs_used': {'folder': source.name,
                      'sha256': json.loads((source / 'manifest.json').read_text(encoding='utf-8'))['sources'][0]['sha256']},
        'provenance': provenance,
        'cobertura': cobertura(summary),
        'flota_por_hora': flota(summary),
        'tramos': tramos(detail, published, args.min_observations) if detail else None,
        'intervalos_min': intervalos(detail, agency_of) if detail else None,
        'limitations': [
            'El instante de cada transición se conoce con la resolución del muestreo: una sola observación arrastra hasta un intervalo de error, un agregado no.',
            'Por eso la razón se reparte por duración publicada: por debajo de unos 150 s el error de medida es una fracción grande de lo medido y la cifra no es utilizable.',
            'Lo observado va de dejar una parada a dejar la siguiente; lo publicado, de una parada a la otra. Ambos incluyen una atención, atribuida a extremos distintos.',
            'No se derivan velocidades entre lotes: cada bus refresca su GPS a su ritmo y el feed repite la última posición conocida mientras tanto.',
            'Es programación frente a operación de los días capturados, no una medición de otros meses ni una predicción.',
        ],
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    c = report['cobertura']
    print(f"cobertura: {c['builds']} lotes, {c['span_h']} h, paso mediano {c['median_step_s']} s, "
          f"{c['gaps_total']} hueco(s) de más de 2 min, {c['failures']} fallo(s)")
    if report['tramos']:
        t = report['tramos']
        print(f"tramos: {t['stretches']} distintos, {t['observations_matched']:,} observaciones emparejadas, "
              f"{t['observations_unmatched']:,} sin equivalente publicado")
        if t['ratio_by_published_duration']:
            print('  razón observado/publicado, por duración publicada del tramo:')
            for label, r in t['ratio_by_published_duration'].items():
                aviso = '  (en el límite de la resolución del muestreo)' if label in ('<90 s', '90-150 s') else ''
                print(f"    {label:10s} n={r['n']:>3}  p10 {r['p10']:.2f}  mediana {r['p50']:.2f}  p90 {r['p90']:.2f}{aviso}")
    for agency, v in (report['intervalos_min'] or {}).items():
        print(f"intervalos {agency}: mediana {v['p50']} min, p10 {v['p10']}, p90 {v['p90']}, "
              f"{v['bunched_under_60s_pct']}% a menos de un minuto")
    print(f"informe -> {Path(args.out).relative_to(ROOT) if Path(args.out).is_relative_to(ROOT) else args.out}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
