"""Map an aggregate daily validation snapshot to logical stations. No transactions."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build():
 src=ROOT/'data/processed/validations_20260909.json';raw=json.loads(src.read_text());curated=json.loads((ROOT/'data/curated/validation_stations.json').read_text())
 services=json.loads((ROOT/'app/dist/services.json').read_text());byid={str(int(s['id'])):s for s in services['stations'] if s['id'].isdigit()};profiles={};unmatched=[]
 for row in raw['hourly_counts']:
  code=row['station_code'];sid=curated['aliases'].get(code,str(int(code)) if code.isdigit() else '')
  if code in curated['excluded']:continue
  if sid not in byid:
   if code not in unmatched:unmatched.append(code)
   continue
  p=profiles.setdefault(sid,{'station_id':sid,'name':byid[sid]['name'],'hourly':[0]*24,'source_codes':[]})
  p['hourly'][int(row['hour'].split(':')[0])]+=row['total']
  if code not in p['source_codes']:p['source_codes'].append(code)
 for p in profiles.values():p['total']=sum(p['hourly'])
 return {'source_url':raw['source_url'],'source_date':raw['period'],'source_sha256':raw['source_sha256'],'aggregate_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
  'observed_validations':raw['rows_aggregated'],'matched_validations':sum(p['total']for p in profiles.values()),'unmatched_codes':unmatched,'profiles':list(profiles.values()),
  'limitations':['Un único miércoles observado: comparación histórica, no predicción de septiembre entero.','La dirección y el destino se estiman. Validaciones no equivalen a OD completo ni necesariamente a nuevos pasajes pagados.','Otros días de semana reutilizan el perfil; fines de semana son una reducción estimada.','Correspondencias de accesos/temporales curadas en validation_stations.json.']}
if __name__=='__main__':
 d=build();(ROOT/'app/dist/demand.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n');print('Demand profiles',len(d['profiles']),'matched',d['matched_validations'],'unmatched',d['unmatched_codes'])
