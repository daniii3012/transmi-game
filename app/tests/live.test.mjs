import test from 'node:test';import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {groupByDestination,occupancyText,ageText,sameName,LiveFeed} from '../dist/live.mjs';
const bus=(label,destination,travelled_m=0)=>({id:label,label,destination,travelled_m,occupancy:'VACIO'});
// El servicio escribe los acentos descompuestos y el catálogo del proyecto también, pero eso es
// una coincidencia de origen, no un contrato: agrupar y emparejar tiene que resistir las dos formas.
const descompuesto='Av. Jiménez',compuesto='Av. Jiménez';

test('Buses of one destination stay together however the accent is encoded',()=>{
 const groups=groupByDestination([bus('T1',descompuesto),bus('T2',compuesto),bus('T3','Portal Américas')]);
 assert.equal(groups.length,2);
 assert.equal(groups[0].buses.length,2);
 assert.deepEqual(groups.map(g=>g.buses.length),[2,1]);
});

test('A live destination matches the catalogue name in either normal form',()=>{
 assert.ok(sameName(descompuesto,compuesto));
 assert.ok(!sameName('Portal Américas','Portal Suba'));
 assert.ok(!sameName(undefined,'Portal Américas'));
});

test('Buses inside a direction are ordered by how far along the route they are',()=>{
 const [group]=groupByDestination([bus('T1','P.SUBA',1200),bus('T2','P.SUBA',9000),bus('T3','P.SUBA',400)]);
 assert.deepEqual(group.buses.map(b=>b.label),['T2','T1','T3']);
});

test('An occupancy the service left empty is reported as missing, not as an empty bus',()=>{
 assert.equal(occupancyText('VACIO'),'Vacío');
 assert.equal(occupancyText('medio'),'Medio');
 assert.equal(occupancyText(''),'Sin dato');
 assert.equal(occupancyText(undefined),'Sin dato');
 assert.equal(occupancyText('LO QUE SEA'),'Sin dato');
});

test('The age of a reading is shown in seconds or minutes, and says so when there is none',()=>{
 assert.equal(ageText(12),'hace 12 s');
 assert.equal(ageText(89),'hace 89 s');
 assert.equal(ageText(240),'hace 4 min');
 assert.equal(ageText(null),'sin hora');
 assert.equal(ageText(undefined),'sin hora');
});

test('An empty reading produces no groups instead of an empty direction',()=>{
 assert.deepEqual(groupByDestination([]),[]);
 assert.deepEqual(groupByDestination(undefined),[]);
});

// Dos fallos reales que la pestaña no delataba: una llamada a un método que no existía dejaba el
// panel «consultando» para siempre, y el temporizador abortaba su propia lectura cuando esta
// tardaba más que el intervalo. Las dos cosas se comprueban aquí y no a ojo en el navegador.
test('Every method the application calls on the feed exists',async()=>{
 const fuente=await readFile(new URL('../dist/app.mjs',import.meta.url),'utf8');
 const usados=[...new Set([...fuente.matchAll(/live(?:Network)?\.([a-zA-Z]+)\(/g)].map(m=>m[1]))];
 assert.ok(usados.length>3,'se esperaban varias llamadas al feed');
 const feed=new LiveFeed({onState:()=>{}});
 for(const metodo of usados)assert.equal(typeof feed[metodo],'function',`falta ${metodo}() en LiveFeed`);
});

test('A reading slower than the interval is not cancelled by the next tick',async()=>{
 let enCurso=0,maximo=0,completadas=0;
 const original=globalThis.fetch;
 globalThis.fetch=async()=>{
  enCurso++;maximo=Math.max(maximo,enCurso);
  await new Promise(r=>setTimeout(r,120));
  enCurso--;completadas++;
  return {ok:true,json:async()=>({vehicles:[]})};
 };
 try{
  const estados=[];
  const feed=new LiveFeed({interval:20,onState:s=>estados.push(s.phase),url:()=>'x'});
  feed.select('red');
  feed.setActive(true);
  await new Promise(r=>setTimeout(r,400));
  feed.stop();
  assert.equal(maximo,1,'no puede haber dos lecturas en vuelo a la vez');
  assert.ok(completadas>=1,'alguna lectura tiene que completarse');
  assert.ok(estados.includes('ok'),'el panel nunca recibió una lectura');
 }finally{globalThis.fetch=original;}
});
