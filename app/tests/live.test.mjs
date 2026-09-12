import test from 'node:test';import assert from 'node:assert/strict';
import {groupByDestination,occupancyText,ageText,sameName} from '../dist/live.mjs';
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
