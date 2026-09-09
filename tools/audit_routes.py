"""Audit the public route finder. Does not enable routes in the game.
Uses the same public search endpoint and sort key observed in the official app.
Stores a whitelist of transport fields; excludes administrative account metadata.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
HOST = 'https://ms-transmiapp-rm2xahnybq-uk.a.run.app'
BODY = {'activa': True, 'tipo': 'TransMilenio'}
FIELDS = ['id', 'codigo', 'nombre', 'tipo', 'color', 'fechaDesde', 'fechaHasta', 'troncal', 'horarios']

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--from-cache',type=Path,help='Directory with routes_trunk_pageN.json, for reproducing the captured audit')
    args=parser.parse_args()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    rows=[]; sources=[]; page=0; total=None
    while True:
        url=HOST+'/api/v1/rutas/buscar?page=%d&size=50&sort=idCodigo,asc'%page
        if args.from_cache:
            raw=(args.from_cache/('routes_trunk_page%d.json'%page)).read_bytes()
        else:
            request=urllib.request.Request(url,data=json.dumps(BODY).encode(),headers={'Content-Type':'application/json'})
            raw=urllib.request.urlopen(request,timeout=30).read()
        data=json.loads(raw)
        if total is not None and total!=data['totalElements']: raise RuntimeError('Catalog changed during paging; repeat the audit')
        total=data['totalElements']
        rows.extend({key:r.get(key) for key in FIELDS} for r in data['content'])
        sources.append({'url':url,'body':BODY,'sha256_response':hashlib.sha256(raw).hexdigest()})
        if data['last']:break
        page+=1
        if page>100: raise RuntimeError('Unexpected catalog size')
    if len(rows)!=total or len({r['id'] for r in rows})!=total:raise RuntimeError('Incomplete or duplicated pages')
    out=ROOT/'data/research'/stamp
    out.mkdir(parents=True,exist_ok=False)
    payload=json.dumps(rows,ensure_ascii=False,indent=2).encode()
    (out/'route_candidates.json').write_bytes(payload)
    manifest={'created_utc':stamp,'source_application':'https://buscador-rutas.transmilenio.gov.co/rutas',
      'purpose':'research_only_not_playable_routes','records':len(rows),'requests':sources,
      'cached_response_input':args.from_cache is not None,
      'sha256_candidates':hashlib.sha256(payload).hexdigest(),
      'license':'Not established for this endpoint. Do not inherit the geographic layers license.',
      'limitations':['TransMilenio source bucket is not a validated BRT-only classification.',
        'Visible route code is not unique; keep record id, destination, direction and dates.',
        'Date fields are preserved verbatim; service-day boundaries need validation.',
        'No lane paths, station module assignments or door anchors imported.']}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print('ROUTE_AUDIT_READY',out,'records',len(rows))
if __name__=='__main__':main()
