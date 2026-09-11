"""Select street-stop points referenced by the chosen trunk/dual services only."""
import json
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from fetch_services import request, save, ROOT


def main():
    snapshot=json.loads((ROOT/'data/raw/services/latest.json').read_text())['snapshot']
    source=ROOT/'data/raw/services'/snapshot
    known={str(f['properties']['id']) for f in json.loads((source/'map_stations.geojson').read_text())['features']}
    codes=sorted({s['codigo'] for f in (source/'details').glob('*.json') for s in json.loads(f.read_text())['estaciones'] if str(s['id']) not in known and s.get('codigo')})
    catalog_url='https://datosabiertos.bogota.gov.co/api/3/action/package_show?id=paraderos-zonales-del-sitp'
    catalog,cat_source=request(catalog_url)
    endpoint=next(r['url'] for r in catalog['result']['resources'] if r['name']=='Servicio REST')
    metadata,meta_source=request(endpoint+'?f=pjson')
    sources=[cat_source,meta_source];features=[]
    # Short queries avoid the public gateway's URL length limit.
    for start in range(0,len(codes),20):
        where='cenefa IN ('+','.join("'"+code.replace("'","''")+"'" for code in codes[start:start+20])+')'
        params={'where':where,'outFields':'objectid,cenefa,nombre,via,direccion_bandera','outSR':4326,'returnGeometry':'true','f':'pjson'}
        result,evidence=request(endpoint+'/query?'+urllib.parse.urlencode(params))
        if 'error'in result or result.get('exceededTransferLimit'):raise ValueError(result)
        sources.append(evidence);features.extend(result['features'])
    result=dict(result,features=features)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');folder=ROOT/'data/raw/dual_stops'/stamp;folder.mkdir(parents=True)
    save(folder/'points.json',result);save(folder/'layer.json',metadata);save(folder/'catalog.json',catalog)
    save(folder/'manifest.json',{'snapshot':stamp,'service_snapshot':snapshot,'requested_codes':codes,'found':len(result['features']),
        'license_id':catalog['result'].get('license_id'),'sources':sources})
    save(ROOT/'data/raw/dual_stops/latest.json',{'snapshot':stamp});print('DUAL_STOP_POINTS',len(result['features']),'/',len(codes),folder)

if __name__=='__main__':main()
