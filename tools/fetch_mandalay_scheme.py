"""Cache the public, bounded Mandalay station scheme and its provenance."""
import datetime, hashlib, json, urllib.parse, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://gis.transmilenio.gov.co/arcgis/rest/services/Troncal/consulta_esquemas_estaciones/FeatureServer/0'
OUT = ROOT / 'data/research/mandalay_scheme_20260909'
FIELDS = 'objectid,estacion,tipo,nombre,secciontipo,id_vagon,id_conexion,id_entrada,area_m2,Shape__Area,Shape__Length'
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'manifest.json').exists():
        print('Using cached scheme:',OUT); return
    params={'where':"estacion='Mandalay'",'outFields':FIELDS,'returnGeometry':'true','outSR':'4326','f':'geojson'}
    url=BASE+'/query?'+urllib.parse.urlencode(params)
    raw=urllib.request.urlopen(url,timeout=30).read(); payload=json.loads(raw)
    if payload.get('type')!='FeatureCollection' or len(payload.get('features',[]))!=9:
        raise ValueError('Unexpected scheme; inspect upstream changes before importing.')
    meta=urllib.request.urlopen(BASE+'?f=pjson',timeout=30).read()
    (OUT/'scheme.geojson').write_bytes(raw);(OUT/'layer.metadata.json').write_bytes(meta)
    manifest={'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_url':url,
        'layer_url':BASE,'license_status':'Not established for this service. Do not inherit CC BY from the separate geographic catalog.',
        'copyright':'TransMilenio S.A.','features':len(payload['features']),
        'sha256':{'scheme.geojson':hashlib.sha256(raw).hexdigest(),'layer.metadata.json':hashlib.sha256(meta).hexdigest()},
        'note':'Polygon scheme; not a construction survey or proof of current operation. Conflicting tipo/nombre fields retained.'}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
