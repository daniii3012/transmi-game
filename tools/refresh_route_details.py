"""Re-download the published detail of specific routes without replacing the base snapshot.

Some records arrive in a snapshot without a shape and gain one later, and some
arrive with a truncated shape. Re-running the full catalogue download to pick those
up would change every other record at the same time. This writes only the named
routes into their own dated folder and leaves a pointer that build_services.py
prefers over the base snapshot for those identifiers alone.

Usage: python3 tools/refresh_route_details.py 12444 1213 629
"""
import argparse
import json
from datetime import datetime, timezone

from fetch_services import ROOT, API, request, save

POINTER = ROOT / 'data/raw/services/refresh_latest.json'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ids', nargs='+', help='route identifiers to refresh')
    parser.add_argument('--reason', default='', help='why these records are being refreshed')
    args = parser.parse_args()

    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder = ROOT / 'data/raw/services' / f'refresh_{stamp}'
    (folder / 'details').mkdir(parents=True, exist_ok=False)

    sources, kept = [], []
    for sid in args.ids:
        raw, evidence = request(API + f'/api/v1/rutas/{sid}/rutaDetalle')
        # Same whitelist as the supplement fetcher: transport fields only.
        data = {
            'color': raw.get('color'), 'nombre': raw.get('nombre'),
            'estaciones': [{k: s.get(k) for k in ['id', 'codigo', 'nombre', 'direccion', 'posicion', 'sistema', 'color']}
                           for s in raw.get('estaciones', [])],
            'horario': [{k: h.get(k) for k in ['tipoDia', 'inicio', 'fin']} for h in raw.get('horario', [])],
            'trazado': raw.get('trazado'),
        }
        evidence['saved_sha256'] = save(folder / 'details' / f'{sid}.json', data)
        sources.append(evidence)
        shape = data['trazado'] or {}
        kept.append({'id': sid, 'name': data['nombre'], 'stops': len(data['estaciones']),
                     'geometry_type': shape.get('type'), 'geometry_coordinates': len(shape.get('coordinates') or [])})

    save(folder / 'manifest.json', {
        'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'base_snapshot': json.loads((ROOT / 'data/raw/services/latest.json').read_text())['snapshot'],
        'reason': args.reason, 'records': kept, 'sources': sources,
        'note': 'Detail override for these ids only. Catalogue metadata still comes from the base snapshot.',
    })
    save(POINTER, {'snapshot': folder.name, 'ids': [r['id'] for r in kept], 'reason': args.reason})
    for r in kept:
        print(f"{r['id']:>6}  {r['name'][:34]:<34} paradas={r['stops']:>3}  trazado={r['geometry_type']} ({r['geometry_coordinates']} coords)")
    print(f'\nGuardado en {folder.relative_to(ROOT)} y apuntado desde {POINTER.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
