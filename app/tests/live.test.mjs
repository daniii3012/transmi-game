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

test('Every method the application calls on the map exists',async()=>{
 // La misma guarda que para el feed: un método que desaparezca de NetworkMap rompe la pestaña
 // entera en tiempo de ejecución, sin que nada lo señale antes.
 const {NetworkMap}=await import('../dist/map.mjs');
 const fuente=await readFile(new URL('../dist/app.mjs',import.meta.url),'utf8');
 const usados=[...new Set([...fuente.matchAll(/\bmap\.([a-zA-Z]+)\(/g)].map(m=>m[1]))];
 assert.ok(usados.length>10,'se esperaban muchas llamadas al mapa');
 for(const metodo of usados)assert.equal(typeof NetworkMap.prototype[metodo],'function',`falta ${metodo}() en NetworkMap`);
});

test('In the live tab a real bus wins the station underneath',async()=>{
 const {NetworkMap}=await import('../dist/map.mjs');
 // Casi todo bus real se dibuja sobre una estación, así que la más cercana al cursor casi siempre
 // es la de debajo. Se ejercita pick() sobre un objeto mínimo: construir el mapa pediría WebGL.
 const elegido=[];
 const mapa={
  center:[0,0],mpp:1,w:100,h:100,busSamples:[],
  data:{stations:[{id:'estacion',xy:[0,0]}]},
  liveVisual:[{id:'bus-gps',xy:[3,0]}],networkVehicles:[{id:'bus-red',xy:[4,0]}],
  worldToScreen:NetworkMap.prototype.worldToScreen,pick:NetworkMap.prototype.pick,
  select(kind,id){elegido.push([kind,id]);},onSelect(){},
 };
 const sobreLaEstacion=[50,50];
 mapa.simulationVisible=false;mapa.pick(sobreLaEstacion);
 assert.deepEqual(elegido.at(-1),['realbus','bus-gps'],'la lectura GPS va primero');
 // La instantánea ancla sus vehículos a la parada, así que ahí no hay margen: manda la distancia.
 mapa.liveVisual=[];mapa.pick(sobreLaEstacion);
 assert.deepEqual(elegido.at(-1),['station','estacion'],'la instantánea no tapa la estación');
 mapa.data.stations=[{id:'estacion',xy:[9,0]}];mapa.pick(sobreLaEstacion);
 assert.deepEqual(elegido.at(-1),['realbus','bus-red'],'pero sí gana cuando está más cerca');
 mapa.data.stations=[{id:'estacion',xy:[0,0]}];
 mapa.networkVehicles=[];mapa.pick(sobreLaEstacion);
 assert.deepEqual(elegido.at(-1),['station','estacion'],'sin buses cerca sigue eligiéndose la estación');
 // El margen es para apuntar al bus, no para tapar la estación: un bus a 8 px no se la queda.
 mapa.liveVisual=[{id:'bus-lejos',xy:[8,0]}];mapa.pick(sobreLaEstacion);
 assert.deepEqual(elegido.at(-1),['station','estacion'],'un bus claramente aparte no gana');
 // Fuera de la pestaña manda la distancia, como siempre.
 mapa.simulationVisible=true;mapa.liveVisual=[{id:'bus-gps',xy:[3,0]}];
 mapa.pick(sobreLaEstacion);
 assert.deepEqual(elegido.at(-1),['station','estacion']);
});

test('The whole-system snapshot eases between readings instead of jumping',async()=>{
 const {NetworkMap}=await import('../dist/map.mjs');
 // Se ejercita la mecánica de interpolación sola: construir el mapa pediría WebGL.
 const mapa={updateNetwork(){},setNetworkBuses:NetworkMap.prototype.setNetworkBuses,animateNetwork:NetworkMap.prototype.animateNetwork};
 mapa.setNetworkBuses([{id:'a',xy:[0,0]},{id:'b',xy:[10,10]}]);
 mapa.setNetworkBuses([{id:'a',xy:[100,0]},{id:'c',xy:[5,5]}]);
 assert.deepEqual(mapa.networkVehicles.find(v=>v.id==='a').xy,[0,0],'un vehículo conocido arranca donde estaba');
 assert.deepEqual(mapa.networkVehicles.find(v=>v.id==='c').xy,[5,5],'uno nuevo aparece ya en su sitio');
 mapa.animateNetwork(mapa.networkStart+600);
 const medio=mapa.networkVehicles.find(v=>v.id==='a').xy[0];
 assert.ok(medio>0&&medio<100,`a mitad del trayecto se esperaba un punto intermedio, no ${medio}`);
 mapa.animateNetwork(mapa.networkStart+5000);
 assert.deepEqual(mapa.networkVehicles.find(v=>v.id==='a').xy,[100,0],'al terminar se queda en la posición leída');
 assert.ok(mapa.networkSettled,'y deja de animarse');
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
