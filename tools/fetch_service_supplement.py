"""Add published trunk/dual records absent from the digital map snapshot."""
import json
from datetime import datetime, timezone
from fetch_services import ROOT,API,request,save
CODES={'D81','L81','H83','F63','Z63'}
def main():
 source=ROOT/'data/raw/services'/json.loads((ROOT/'data/raw/services/latest.json').read_text())['snapshot']
 selected={r['id'] for r in json.loads((source/'selected_catalog.json').read_text())}
 rows=[r for r in json.loads((source/'candidate_catalog.json').read_text()) if r['codigo']in CODES and r['id']not in selected]
 folder=ROOT/'data/raw/services/supplement_20260910';folder.mkdir(exist_ok=True);(folder/'details').mkdir(exist_ok=True)
 sources=[];records=[]
 for r in rows:
  raw,evidence=request(API+f'/api/v1/rutas/{r["id"]}/rutaDetalle')
  data={'color':raw.get('color'),'nombre':raw.get('nombre'),'estaciones':[{k:s.get(k) for k in ['id','codigo','nombre','direccion','posicion','sistema','color']} for s in raw.get('estaciones',[])],
    'horario':[{k:h.get(k) for k in ['tipoDia','inicio','fin']} for h in raw.get('horario',[])],'trazado':raw.get('trazado')}
  evidence['saved_sha256']=save(folder/'details'/f'{r["id"]}.json',data);sources.append(evidence)
  records.append(dict(r,metadata=r,scope_source='supplementary_verified_family'))
 save(folder/'selected_catalog.json',records);save(folder/'manifest.json',{'retrieved_at':datetime.now(timezone.utc).isoformat(),'source_catalog':str(source.relative_to(ROOT)),'records':len(records),'sources':sources})
 print([(r['id'],r['codigo'],r['nombre']) for r in records])
if __name__=='__main__':main()
