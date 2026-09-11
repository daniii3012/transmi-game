"""Snapshot public trunk catalog, supplementary dual candidates and route details.

Whitelists transport fields. Network is only needed at data-import time.
"""
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
API='https://api.buscador-rutas.transmilenio.gov.co'
SEARCH='https://ms-transmiapp-rm2xahnybq-uk.a.run.app'
DUAL_CODES={'M80','L80','H81','M81','L82','M82','D83','L83','M83','C84','M84','M85','P85','L85','K86','M86','F63','Z63','D81','L81','H83'}
FIELDS=['id','codigo','nombre','tipo','color','fechaDesde','fechaHasta','troncal','horarios','activa']


def now():return datetime.now(timezone.utc).isoformat()

def request(url,body=None):
    req=urllib.request.Request(url,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json','User-Agent':'BogotaTransmi-local-research/0.2'})
    with urllib.request.urlopen(req,timeout=40) as response: raw=response.read()
    return json.loads(raw),{'url':url,'method':'GET' if body is None else 'POST','body':body,'retrieved_at_utc':now(),'response_sha256':hashlib.sha256(raw).hexdigest(),'response_bytes':len(raw)}


def save(path,data):
    b=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode();path.write_bytes(b)
    return hashlib.sha256(b).hexdigest()


def main():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder=ROOT/'data/raw/services'/stamp;folder.mkdir(parents=True,exist_ok=False)
    (folder/'details').mkdir();sources=[];failures=[]
    catalog,evidence=request(API+'/api/v1/rutas/troncales',{});sources.append(evidence)
    catalog=[{k:r.get(k) for k in ['id','codigo','nombre','color']} for r in catalog]
    save(folder/'map_catalog.json',catalog)
    metadata=[];page=0;total=None
    while True:
        result,evidence=request(SEARCH+f'/api/v1/rutas/buscar?page={page}&size=50&sort=idCodigo,asc',{'activa':True,'tipo':'TransMilenio'});sources.append(evidence)
        if total is not None and total!=result['totalElements']:raise ValueError('Catalog changed during paging')
        total=result['totalElements'];metadata.extend({k:r.get(k) for k in FIELDS} for r in result['content'])
        if result['last']:break
        page+=1
        if page>15:raise ValueError('Unexpected catalog growth')
    if len(metadata)!=total or len({r['id'] for r in metadata})!=total:raise ValueError('Incomplete candidate catalog')
    save(folder/'candidate_catalog.json',metadata)
    by_id={r['id']:r for r in metadata};selected={r['id']:dict(r,scope_source='digital_map') for r in catalog}
    for r in metadata:
        if r['codigo'] in DUAL_CODES and r['id'] not in selected:
            selected[r['id']]=dict(r,scope_source='supplementary_dual_candidate')
    records=[]
    for row in selected.values():
        meta=by_id.get(row['id'])
        if meta is None:
            try:
                raw,evidence=request(SEARCH+f'/api/v1/rutas/{row["id"]}/{urllib.parse.quote(row["codigo"])}/');sources.append(evidence)
                meta={k:raw.get(k) for k in FIELDS}
            except Exception as error:failures.append({'id':row['id'],'stage':'metadata','error':str(error)})
        records.append(dict(row,metadata=meta))
    save(folder/'selected_catalog.json',records)
    def detail(row):
        url=API+f'/api/v1/rutas/{row["id"]}/rutaDetalle'
        try:
            raw,evidence=request(url)
            data={'color':raw.get('color'),'nombre':raw.get('nombre'),
                'estaciones':[{k:s.get(k) for k in ['id','codigo','nombre','direccion','posicion','sistema','color']} for s in raw.get('estaciones',[])],
                'horario':[{k:s.get(k) for k in ['tipoDia','inicio','fin']} for s in raw.get('horario',[])],
                'trazado':raw.get('trazado')}
            digest=save(folder/'details'/f'{row["id"]}.json',data)
            return dict(evidence,record_id=row['id'],saved_sha256=digest)
        except Exception as error:return {'record_id':row['id'],'stage':'detail','url':url,'error':str(error)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for i,result in enumerate(pool.map(detail,records)):
            if 'error'in result:failures.append(result)
            else:sources.append(result)
            if (i+1)%25==0:print('DETAILS',i+1,'/',len(records),flush=True)
    for name,path in [('map_stations','/api/v1/arcgis/estaciones'),('map_corridors','/api/v1/arcgis/trazados_troncal')]:
        data,evidence=request(API+path);sources.append(evidence);save(folder/(name+'.geojson'),data)
    manifest={'schema_version':1,'created_at_utc':now(),'snapshot':stamp,'map_records':len(catalog),'candidate_records':total,
        'selected_records':len(records),'detail_files':len(list((folder/'details').glob('*.json'))),'sources':sources,'failures':failures,
        'license_status':'Not established for these endpoints; no inheritance from separate CC BY GIS catalog.',
        'limitations':['Source publication is not independent operational verification.','Supplementary candidates require variant/calendar review.','No frequencies, bus type or berth assignment published in sampled detail schema.'],
        'file_sha256':{str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}}
    save(folder/'manifest.json',manifest);save(ROOT/'data/raw/services/latest.json',{'snapshot':stamp})
    print('SERVICES_SNAPSHOT',folder,'details',manifest['detail_files'],'failures',len(failures),flush=True)

if __name__=='__main__':main()
