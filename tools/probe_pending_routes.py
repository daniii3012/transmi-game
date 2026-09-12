"""Read-only probe of the pending route records against the published catalog.

Answers one question per record: does the official detail endpoint now publish a
usable shape and stop sequence? Nothing is written into the curated catalog; the
probe only archives evidence under data/research so a later curation decision can
cite it. A record stays pending until this probe shows the missing evidence.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.buscador-rutas.transmilenio.gov.co'
DETAIL = API + '/api/v1/rutas/{id}/rutaDetalle'
AGENT = 'BogotaTransmi-local-research/0.2'


def now():
    return datetime.now(timezone.utc).isoformat()


def request(url):
    req = urllib.request.Request(url, headers={'Content-Type': 'application/json', 'User-Agent': AGENT})
    with urllib.request.urlopen(req, timeout=40) as response:
        raw = response.read()
    return json.loads(raw), {'url': url, 'retrieved_at_utc': now(),
                             'response_sha256': hashlib.sha256(raw).hexdigest(), 'response_bytes': len(raw)}


def shape_of(detail):
    """Return (geometry kind, coordinate count) without copying the geometry itself."""
    for key in ('trazado', 'geometria', 'geometry', 'shape'):
        value = detail.get(key)
        if not value:
            continue
        if isinstance(value, dict):
            coords = value.get('coordinates')
            if isinstance(coords, list):
                flat = coords[0] if coords and isinstance(coords[0], list) and coords[0] and isinstance(coords[0][0], list) else coords
                return value.get('type', 'unknown'), len(flat)
        if isinstance(value, str):
            return 'encoded', len(value)
    return None, 0


def stops_of(detail):
    for key in ('estaciones', 'paraderos', 'stops'):
        value = detail.get(key)
        if isinstance(value, list):
            return value
    return []


def main():
    source = json.loads((ROOT / 'app/dist/services.json').read_text())
    pending = [r for r in source['routes'] if not r.get('ready')]
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder = ROOT / 'data/research' / f'pending_probe_{stamp}'
    folder.mkdir(parents=True, exist_ok=False)

    records, evidence, failures = [], [], []
    for route in sorted(pending, key=lambda r: r['code']):
        try:
            detail, proof = request(DETAIL.format(id=route['id']))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            failures.append({'id': route['id'], 'code': route['code'], 'error': repr(error)})
            continue
        evidence.append(proof)
        kind, count = shape_of(detail)
        stops = stops_of(detail)
        schedule = detail.get('horarios') or detail.get('horario') or []
        records.append({
            'id': route['id'], 'code': route['code'], 'name': route['name'],
            'local_issues': route.get('issues', []),
            'valid_from': route.get('valid_from'), 'valid_until': route.get('valid_until'),
            'published_geometry': kind is not None, 'geometry_type': kind, 'geometry_coordinates': count,
            'published_stop_count': len(stops),
            'published_schedule': [{k: v for k, v in h.items() if k in ('tipoDia', 'inicio', 'fin')}
                                   for h in schedule if isinstance(h, dict)],
            # rutaDetalle publishes colour, name, stops, shape and schedule only: no validity or active flag.
            'published_fields': sorted(detail.keys()),
            'detail_sha256': proof['response_sha256'],
            # A record only becomes curatable when both a shape and an ordered stop list exist.
            'resolves_pending': bool(kind is not None and count > 1 and len(stops) > 1),
        })
        time.sleep(.4)

    manifest = {
        'created_utc': now(), 'purpose': 'read_only_pending_route_probe',
        'source': API, 'detail_url_template': DETAIL,
        'catalog_source': 'app/dist/services.json', 'catalog_revision': source.get('revision'),
        'pending_records': len(pending), 'probed': len(records), 'failures': failures,
        'resolved': [r['code'] + '/' + r['id'] for r in records if r['resolves_pending']],
        'evidence': evidence,
        'note': 'Probe only. Curation still requires an explicit decision in data/curated/services.json.',
    }
    for name, payload in (('manifest.json', manifest), ('probe.json', {'records': records})):
        (folder / name).write_bytes((json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode())
    print(f'{len(records)} registros consultados en {folder.relative_to(ROOT)}')
    print(f'con trazado y paradas publicados: {len(manifest["resolved"])} -> {manifest["resolved"]}')
    if failures:
        print(f'fallos: {failures}')


if __name__ == '__main__':
    main()
