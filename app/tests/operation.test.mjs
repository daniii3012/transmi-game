import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {Operation,DEFAULTS,parameters,motion,motionAt} from '../dist/operation.mjs';
import {vehicleSpec} from '../dist/vehicles.mjs';
import {MetricPath} from '../dist/simulation.mjs';
import {travelProfile,travelAt} from '../dist/travel.mjs';
import {dayType,holidays,serviceWindows,dateNumber,validityState} from '../dist/calendar.mjs';
import {directionalFactor,generatedPassengers,EMPLOYMENT_CENTER} from '../dist/passengers.mjs';
const source=JSON.parse(fs.readFileSync(new URL('../dist/services.json',import.meta.url)));
const base={schema_version:2,scenario_date:'2026-09-10',vehicle:{length_m:18.5,width_m:2.5},stations:[{id:'a',xy:[0,0],name:'Portal Prueba',kind:'station',wagons:2},{id:'b',xy:[1000,0],name:'Centro',kind:'station',wagons:2},{id:'c',xy:[2000,0],name:'Terminal',kind:'station',wagons:2}]};
const route=(id='r',stops=['a','b','c'])=>({id,code:id,color:'#ff0000',name:'Test',family:id,ready:true,valid_from:'2026-01-01',valid_until:'2026-12-31',variant:'regular',calendar:[{days:'L-D',start:14400,end:82800}],points:[[0,0],[1000,0],[2000,0]],stops:stops.map(k=>({station_id:k,name:k,kind:'station',wagons:2,at_m:{a:0,b:1000,c:2000}[k]})),served_zones:['F'],zone:'F'});
const fixture=(routes=[route()])=>({...base,routes});
test('Bogotá civil dates and Colombian moved/floating holidays',()=>{assert.equal(dayType('2026-09-10'),'weekday');assert.equal(dayType('2026-09-12'),'saturday');assert.equal(dayType('2026-09-13'),'holiday');for(const d of ['2026-01-12','2026-03-23','2026-04-02','2026-04-03','2026-05-18','2026-06-08','2026-06-15','2026-08-17'])assert.ok(holidays(2026).has(d),d);assert.throws(()=>dateNumber('2026-02-30'));});
test('Calendar splits, weekend exceptions, expiry and overlapping windows',()=>{const r=route();r.calendar=[{days:'L-V',start:18000,end:20000},{days:'L-V',start:19000,end:21000}];assert.deepEqual(serviceWindows(r,'2026-09-10',[r]),[[18000,21000]]);assert.deepEqual(serviceWindows(r,'2026-09-12',[r]),[]);assert.deepEqual(serviceWindows(r,'2027-01-01',[r]),[]);});
test('Published validity is classified and may be operated past its end without rewriting it',()=>{
 const r=route();r.valid_from='2026-06-28';r.valid_until='2026-09-11';
 assert.equal(validityState(r,'2026-09-10'),'current');
 assert.equal(validityState(r,'2026-09-12'),'expired');
 assert.equal(validityState(r,'2026-06-01'),'future');
 // Sin la opción, la vigencia excluye el servicio; con ella conserva exactamente su ventana publicada.
 assert.deepEqual(serviceWindows(r,'2026-09-12',[r]),[]);
 assert.deepEqual(serviceWindows(r,'2026-09-12',[r],{beyondValidity:true}),serviceWindows(r,'2026-09-10',[r]));
 assert.deepEqual(serviceWindows(r,'2026-06-01',[r],{beyondValidity:true}),[[14400,82800]]);
 // Una variante posterior de la misma familia sigue reemplazando a la anterior aunque ambas estén vencidas.
 const nueva={...r,id:'nueva',valid_from:'2026-08-01',calendar:[{days:'L-D',start:14400,end:40000}]};
 assert.deepEqual(serviceWindows(r,'2026-09-12',[r,nueva],{beyondValidity:true}),[[40000,82800]]);
 // Un servicio sin datos nunca opera, tenga o no vigencia abierta.
 assert.deepEqual(serviceWindows({...r,ready:false},'2026-09-12',[r],{beyondValidity:true}),[]);
});
test('Operating past validity is an explicit boolean parameter',()=>{
 assert.equal(DEFAULTS.beyondValidity,true);
 assert.equal(parameters({}).beyondValidity,true);
 assert.equal(parameters({beyondValidity:false}).beyondValidity,false);
 assert.throws(()=>parameters({beyondValidity:'sí'}));
});
test('Ciclovía replaces overlapping regular departures only',()=>{const r=route(),c={...r,id:'cic',variant:'ciclovia',calendar:[{days:'D-F',start:25200,end:50400}]};assert.deepEqual(serviceWindows(r,'2026-09-13',[r,c]),[[14400,25200],[50400,82800]]);assert.deepEqual(serviceWindows(c,'2026-09-10',[r,c]),[]);});
test('Distance-domain speed respects metres, speed cap, acceleration and braking',()=>{const path=new MetricPath([[0,0],[2000,0]]),p=travelProfile(path,0,2000,13.333,.8,1.1);assert.equal(travelAt(p,0).speed,0);assert.equal(travelAt(p,p.duration).s,2000);assert.ok(travelAt(p,p.duration).speed<1e-8);for(let t=.1;t<p.duration;t+=.2){const a=travelAt(p,t-.1),b=travelAt(p,t);assert.ok(b.s>=a.s);assert.ok(b.speed<=13.333+1e-8);assert.ok((b.speed-a.speed)/.1<=.8+1e-6);assert.ok((a.speed-b.speed)/.1<=1.1+1e-6);}});
test('Tight bends slow buses and cannot create a shortcut',()=>{const straight=travelProfile(new MetricPath([[0,0],[200,0]]),0,200,13.333),bend=travelProfile(new MetricPath([[0,0],[100,0],[100,100]]),0,200,13.333);assert.ok(bend.duration>straight.duration);assert.equal(bend.distance,200);});
test('Short legs use a triangular acceleration profile',()=>{const m=motion(10,15);assert.equal(m.cruise,0);assert.ok(Math.abs(motionAt(m,m.duration).s-10)<1e-9);});
test('Backward and forward seek returns exactly the same trips and passengers',()=>{const s=new Operation(fixture());s.seek(86400+25250);const expected=structuredClone(s.buses);s.seek(86400+60000);s.seek(86400+25250);assert.deepEqual(s.buses,expected);});
test('Clock acceleration does not alter distance at the same simulated instant',()=>{const s=new Operation(fixture());s.seek(86400+25200);for(let i=1;i<=120;i++)s.seek(86400+25200+i);const a=structuredClone(s.buses);s.seek(86400+25200);s.seek(86400+25320);assert.deepEqual(s.buses,a);});
test('No vehicles created outside dispatch hours, trips may finish after closing',()=>{const r=route();r.calendar=[{days:'L-D',start:25200,end:25260}];const s=new Operation(fixture([r]));s.seek(86400+25290);assert.ok(s.buses.length);s.seek(86400+26000);assert.equal(s.buses.length,0);assert.ok(s.trips.every(t=>t.start>=86400+25200&&t.start<86400+25260));});
test('More frequent departures increase simultaneous fleet without changing geometry',()=>{const a=new Operation(fixture()),b=new Operation(fixture(),{params:{peakHeadway:120}});assert.ok(b.trips.length>a.trips.length);assert.equal(b.routes.get('r').path.length,a.routes.get('r').path.length);});
test('Crowded stopping points never block express services',()=>{const express=route('express',['a','c']),busy=Array.from({length:20},(_,i)=>route('slow'+i));const alone=new Operation(fixture([express]));const mixed=new Operation(fixture([express,...busy]));const trip=mixed.trips.find(t=>t.routeId==='express'&&t.start>86400);assert.equal(trip.stops.length,2);assert.equal(trip.moves[0].profile.distance,2000);assert.equal(trip.moves[0].profile.duration,alone.trips[0].moves[0].profile.duration);});
test('Two berths per wagon do not overlap reservations',()=>{const s=new Operation(fixture(Array.from({length:24},(_,i)=>route('r'+i))));const reservations=new Map();for(const t of s.trips){const r=s.routes.get(t.routeId);for(const [i,st] of t.stops.entries()){const key=r.stops[i].station_id+'/'+st.direction+'/'+st.wagon+'/'+st.slot;const values=reservations.get(key)||[];values.push(st);reservations.set(key,values);}}for(const events of reservations.values()){events.sort((a,b)=>a.open-b.open);for(let i=1;i<events.length;i++)assert.ok(events[i].open>=events[i-1].close-1e-8);}});
test('Passenger conservation and vehicle capacity hold at every stop',()=>{const s=new Operation(fixture(),{params:{demand:3}});for(const t of s.trips){let load=0;for(const st of t.stops){load+=st.board-st.alight;assert.equal(load,st.load);assert.ok(load>=0&&load<=t.capacity);assert.ok(st.left>=0);}assert.equal(load,0);}});
test('Boarding demand is independent of bus count and points toward centre AM / away PM',()=>{const st={xy:[EMPLOYMENT_CENTER[0]-10000,EMPLOYMENT_CENTER[1]],kind:'station',name:'Periferia'};assert.ok(directionalFactor(st,0,7*3600)>directionalFactor(st,Math.PI,7*3600));assert.ok(directionalFactor(st,0,18*3600)<directionalFactor(st,Math.PI,18*3600));const all=generatedPassengers(st,0,6*3600,8*3600,'2026-09-10',DEFAULTS),split=generatedPassengers(st,0,6*3600,7*3600,'2026-09-10',DEFAULTS)+generatedPassengers(st,0,7*3600,8*3600,'2026-09-10',DEFAULTS);assert.ok(Math.abs(all-split)<1e-8);});
test('Terminal reuse never assigns one bus to simultaneous trips',()=>{const r=route(),reverse={...route('back'),points:[[2000,0],[1000,0],[0,0]],stops:[...route().stops].reverse().map(s=>({...s,at_m:2000-s.at_m}))};const s=new Operation(fixture([r,reverse]));const byVehicle=new Map();for(const t of s.trips){const a=byVehicle.get(t.vehicle)||[];a.push(t);byVehicle.set(t.vehicle,a);}for(const trips of byVehicle.values()){trips.sort((a,b)=>a.start-b.start);for(let i=1;i<trips.length;i++)assert.ok(trips[i].start>=trips[i-1].end+DEFAULTS.turnaround-1e-8);}});
test('Selections change the simulated service set',()=>{const s=new Operation(fixture([route('one'),route('two')]),{selection:{mode:'route',route:'two'}});assert.deepEqual([...s.routes.keys()],['two']);});
test('Invalid operating parameters fail explicitly',()=>{assert.throws(()=>parameters({peakHeadway:0}));assert.throws(()=>parameters({demand:Infinity}));assert.throws(()=>parameters({mode:'random'}));});
test('Real M85 crops its reverse geometry and retains street stops',()=>{const r=source.routes.find(r=>r.id==='1315');assert.ok(r.ready);assert.ok(r.source_crop_m[0]>9000);assert.ok(r.length_m>11000&&r.length_m<12000);assert.equal(r.stops[0].at_m,0);assert.ok(r.stops.some(s=>s.kind==='street'));});
test('Missing and inconsistent official shapes are never admitted as playable',()=>{
 // The rule is asserted over the whole catalogue rather than over pinned identifiers: a record
 // that later gains a published shape should stop being pending without editing this test.
 for(const r of source.routes){
  const shaped=r.points.length>1&&r.stops.length>1;
  if(!shaped)assert.equal(r.ready,false,`${r.code}/${r.id} sin trazado utilizable no puede estar activo`);
  if(r.ready){
   assert.ok(shaped,`${r.code}/${r.id}`);
   assert.equal(r.issues.length,0,`${r.code}/${r.id} activo con incidencias`);
   for(let i=1;i<r.stops.length;i++)assert.ok(r.stops[i].at_m>r.stops[i-1].at_m,r.id);
  }
 }
 // 692 keeps returning neither shape nor stops, so it stays the pinned example of a pending record.
 assert.equal(source.routes.find(r=>r.id==='692').ready,false);
 assert.ok(source.routes.filter(r=>!r.ready).length>0);
});
test('A refreshed detail records which snapshot it came from',()=>{
 const refreshed=source.routes.filter(r=>r.detail_snapshot&&r.detail_snapshot.startsWith('refresh_'));
 for(const r of refreshed){
  assert.equal(r.ready,true,`${r.code}/${r.id}`);
  assert.ok(r.points.length>1&&r.stops.length>1);
  // Validity still comes from the base catalogue, never from the refreshed detail.
  assert.match(r.valid_until,/^\d{4}-\d{2}-\d{2}$/);
 }
 for(const r of source.routes)assert.ok(typeof r.detail_snapshot==='string'&&r.detail_snapshot.length>0,`${r.id} sin procedencia de detalle`);
});

test('Zonal C15 never replaces trunk C15/H15 on Sundays',()=>{assert.ok(!source.routes.some(r=>r.id==='366'));const c=source.routes.find(r=>r.id==='3915'),h=source.routes.find(r=>r.id==='367');assert.ok(c.ready&&h.ready);assert.ok(c.paired_ids.includes(h.id));assert.ok(serviceWindows(c,'2026-09-13',source.routes).some(([a,b])=>a<=7*3600&&b>7*3600));});

test('Electric F63/Z63 always keeps 160 places',()=>{for(const id of ['5450','5451']){const r=source.routes.find(r=>r.id===id);assert.ok(r.ready&&r.dual);const s=new Operation({...source,routes:[r]},{});for(const v of s.vehicles){assert.equal(v.spec.capacity,160);assert.equal(v.spec.kind,'dual_electric');}}});
test('Vehicle type remains constant during reuse between opposite directions',()=>{const r=route(),reverse={...route('back'),points:[[2000,0],[1000,0],[0,0]],stops:[...route().stops].reverse().map(s=>({...s,at_m:2000-s.at_m}))};const s=new Operation(fixture([r,reverse]),{});for(const t of s.trips){assert.equal(t.capacity,s.vehicles[t.vehicle].spec.capacity);}assert.ok(s.vehicles.every(v=>v.spec.kind==='articulated'));});
test('Overnight departures and previous-day journeys remain visible after midnight',()=>{const r=route();r.calendar=[{days:'L-D',start:85800,end:87000}];const s=new Operation(fixture([r]));s.seek(86400+120);assert.ok(s.buses.length);assert.ok(s.buses.every(b=>b.id.startsWith('2026-09-09/')));const expected=structuredClone(s.buses);s.seek(86400+1800);assert.equal(s.buses.length,0);s.seek(86400+120);assert.deepEqual(s.buses,expected);});

test('Bus sizes are fixed by route, easy routes are articulated and M51/F51 biarticulated',()=>{for(const code of ['1','2','3','4','5','6','7','8','M51','F51']){const specs=Array.from({length:20},(_,i)=>vehicleSpec({code,length_m:25000},DEFAULTS,i));assert.equal(new Set(specs.map(v=>v.kind)).size,1);assert.equal(specs[0].capacity,['M51','F51'].includes(code)?240:160);}assert.equal(vehicleSpec({code:'M85',dual:true},DEFAULTS,1).capacity,80);});
test('Vehicle cruise variation is stable and bounded by ±5 km/h',()=>{const values=Array.from({length:50},(_,i)=>vehicleSpec({code:'1'},DEFAULTS,i).speedOffset);assert.ok(new Set(values).size>1);assert.ok(values.every(v=>v>=-5&&v<=5));assert.equal(DEFAULTS.cruiseKmh,60);assert.equal(DEFAULTS.streetKmh,50);});
test('Irregular departures and bounded peak reinforcements are deterministic',()=>{const d=fixture();d.stations=d.stations.map(s=>({...s,demand_profile:{hourly:Array(24).fill(100000)}}));const a=new Operation(d),b=new Operation(d),plain=new Operation(d,{params:{reinforcements:false}});assert.deepEqual(a.trips.map(t=>t.id),b.trips.map(t=>t.id));assert.ok(a.trips.some(t=>t.reinforcement));assert.ok(a.trips.length>plain.trips.length);assert.ok(a.trips.length<plain.trips.length*1.25);});
test('F23 has one published playable destination after user correction',()=>{const routes=source.routes.filter(r=>r.code==='F23');assert.equal(routes.length,1);assert.equal(routes[0].id,'396');assert.ok(source.excluded.some(r=>r.id==='10082'));});

test('OSM station placements remain on each directed route and keep stop order',async()=>{const {placeVisit}=await import('../dist/station-layouts.mjs');const {hash}=await import('../dist/operation.mjs');const layouts=JSON.parse(fs.readFileSync(new URL('../dist/station_layouts.json',import.meta.url)));const byId=new Map(layouts.stations.map(l=>[l.station_id,l]));let located=0;const ricaurte=new Set();for(const r of source.routes.filter(r=>r.ready)){const path=new MetricPath(r.points),visits=r.stops.map((s,i)=>{const p=placeVisit({...r,path},i,byId.get(s.station_id),hash(r.family));if(p){located++;assert.ok(p.at_m>=0&&p.at_m<=path.length);assert.ok(Math.abs(p.at_m-s.at_m)<=400.01);assert.ok(p.placement_source.startsWith('https://www.openstreetmap.org/'));if(s.station_id==='7111')ricaurte.add(p.platform_id);}return p?.at_m??s.at_m;});for(let i=1;i<visits.length;i++)assert.ok(visits[i]>visits[i-1],r.code);}assert.ok(located>100);assert.ok(ricaurte.size>=4);for(const id of ['7000','3000','5000'])assert.ok(byId.get(id).platforms.filter(p=>p.closed&&p.role==='platform_trunk').length>=2);});
test('Measured day-type profiles replace the estimated weekend reduction',()=>{
 const demand=JSON.parse(fs.readFileSync(new URL('../dist/demand.json',import.meta.url)));
 assert.ok(demand.profiles.length>100);
 for(const p of demand.profiles){
  assert.ok(p.hourly_by_day_type,`${p.station_id} sin perfil por tipo de día`);
  for(const kind of ['weekday','saturday','holiday']){
   const hourly=p.hourly_by_day_type[kind];
   assert.equal(hourly.length,24,`${p.station_id}/${kind}`);
   assert.ok(hourly.every(v=>Number.isFinite(v)&&v>=0),`${p.station_id}/${kind}`);
   assert.ok(p.days_observed[kind]>=1,`${p.station_id}/${kind} sin días observados`);
  }
  // The legacy field must stay the weekday profile so an older reader keeps working.
  assert.deepEqual(p.hourly,p.hourly_by_day_type.weekday,p.station_id);
 }
 const station={...base.stations[0],demand_profile:demand.profiles.find(p=>p.station_id==='2000')};
 const rate=(date)=>generatedPassengers(station,0,8*3600,8*3600+600,date,parameters({}));
 // A Sunday must now come out of the measured Sunday profile, not a 0,55 factor on a Wednesday.
 const semana=rate('2026-09-10'),domingo=rate('2026-09-13'),sabado=rate('2026-09-12');
 assert.ok(semana>0&&sabado>0&&domingo>0);
 assert.ok(domingo<sabado&&sabado<semana,`domingo ${domingo} sábado ${sabado} semana ${semana}`);
 assert.ok(domingo/semana<0.55,'el domingo medido debe quedar por debajo del factor estimado que reemplaza');
 // A station without a profile keeps the estimated path and still responds to the day type.
 const sinPerfil={...base.stations[0]};
 assert.ok(generatedPassengers(sinPerfil,0,8*3600,8*3600+600,'2026-09-10',parameters({}))>0);
});
