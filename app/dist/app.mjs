import {NetworkMap} from './map.mjs?v=20260910.3';
import {DAY,addDays,dayType,dateNumber,dateEligible,serviceWindows,demandPeriod} from './calendar.mjs?v=20260910.3';
import {DEFAULTS,parameters} from './operation.mjs?v=20260910.3';
import {registerSimulationTools} from './webmcp.mjs?v=20260910.3';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const el=(tag,text,cls)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;};
const fmt=n=>Math.round(n).toLocaleString('es-CO');
const timeText=s=>new Date(Math.floor(((s%DAY)+DAY)%DAY)*1000).toISOString().slice(11,19);
const stateNames={moving:'En recorrido',dwell:'Puertas abiertas',queue:'Esperando atención'};
let toastTimer;
function toast(message){$('#toast').textContent=message;$('#toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').hidden=true,4500);}
try{
 const [response,contextResponse,demandResponse]=await Promise.all([fetch('./services.json',{cache:'no-store'}),fetch('./context.json',{cache:'no-store'}),fetch('./demand.json',{cache:'no-store'})]);
 if(!response.ok)throw new Error('No se pudieron cargar los servicios locales.');
 const data=await response.json();if(demandResponse.ok){data.demand=await demandResponse.json();const profiles=new Map(data.demand.profiles.map(p=>[p.station_id,p]));for(const s of data.stations){const p=profiles.get(s.id);if(p)s.demand_profile=p;}}const routeById=new Map(data.routes.map(r=>[r.id,r]));
 let saved=null;try{saved=JSON.parse(localStorage.getItem('transmi-scenario-v2'));if(saved?.revision!==data.revision)saved=null;}catch{}
 let config={date:data.scenario_date,params:{...DEFAULTS},selection:{mode:'all'}};
 let clock={time:DAY+7*3600,speed:1,paused:false};
 if(saved){try{saved.config.params=parameters(saved.config.params);dateNumber(saved.config.date);if(!Number.isFinite(saved.clock.time)||saved.clock.time<DAY||saved.clock.time>=2*DAY||![1,8,32,120].includes(saved.clock.speed))throw Error();if(!['all','route','zones'].includes(saved.config.selection.mode))throw Error();if(saved.config.selection.mode==='route'&&!routeById.get(saved.config.selection.route)?.ready)throw Error();if(saved.config.selection.mode==='zones'&&!saved.config.selection.zones?.length)throw Error();config=saved.config;clock={...clock,...saved.clock,paused:true};}catch{saved=null;}}
 let selection=null,following=false,focusedRoute=null,activePanel='routes',generation=0,ready=false,pendingSample=false,lastUI=0,lastList=0,lastInspect=0,lastSample=0,windows={},snap={buses:[],stats:{}};
 let selectedZones=new Set(config.selection.zones||[]);const map=new NetworkMap($('#canvas-host'),$('#labels'),data,onSelect);
 if(contextResponse.ok)map.setContext(await contextResponse.json());
 let worker=new Worker('./worker.mjs?v=20260910.3',{type:'module'});
 function badge(r){const b=el('span',r.code,'route-code');b.style.setProperty('--route',r.color);const rgb=r.color.match(/[0-9a-f]{2}/gi)?.map(s=>parseInt(s,16));if(rgb?.length===3&&rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722>155)b.style.setProperty('--route-ink','#24303f');return b;}
 function row(label,value,parent=$('#selection')){const r=el('div',undefined,'metric-row');r.append(el('span',label),el('strong',value));parent.append(r);return r;}
 function rebuild({fit=false}={}){
  generation++;const messageHandler=worker.onmessage,errorHandler=worker.onerror;worker.terminate();worker=new Worker('./worker.mjs?v=20260910.3',{type:'module'});worker.onmessage=messageHandler;worker.onerror=errorHandler;ready=false;pendingSample=false;$('#loading').hidden=false;$('#loading').textContent='Calculando despachos y estaciones…';$('#error').hidden=true;
  following=false;selection=null;$('#inspector').hidden=true;map.selected=null;map.updateMarker();
  if(config.selection.mode==='route'){focusedRoute=config.selection.route;map.setRoute(focusedRoute);}else{focusedRoute=null;map.setRoute(null);}
  map.routeSet=new Set(data.routes.filter(r=>r.ready&&(config.selection.mode==='all'||config.selection.mode==='route'&&r.id===config.selection.route||config.selection.mode==='zones'&&config.selection.zones.some(z=>r.served_zones.includes(z)||r.zone===z))).map(r=>r.id));map.rebuildHighlight();
  worker.postMessage({type:'init',generation,data,config,time:clock.time});syncControls();renderRoutes();
  $('#view-title').textContent=config.selection.mode==='all'?'Toda la red':config.selection.mode==='route'?`${routeById.get(config.selection.route)?.code||''} · ${routeById.get(config.selection.route)?.name||''}`:'Troncales '+config.selection.zones.join(' · ');
  if(fit)fitSelection();
 }
 function fitSelection(){const r=routeById.get(focusedRoute);if(r?.points.length)map.fitPoints(r.points);else if(config.selection.mode==='zones'){const points=data.routes.filter(r=>map.routeSet.has(r.id)).flatMap(r=>r.points);if(points.length)map.fitPoints(points);}else map.fitNetwork();}
 function sample(){if(ready&&!pendingSample&&snap.time!==clock.time){pendingSample=true;worker.postMessage({type:'sample',generation,time:clock.time});}}
 worker.onmessage=({data:m})=>{
  if(m.generation!==generation)return;
  if(m.type==='error'){ready=false;$('#loading').hidden=true;$('#error').hidden=false;$('#error').textContent='No se pudo preparar el escenario: '+m.message;return;}
  if(m.type==='ready'){ready=true;windows=m.windows;$('#loading').hidden=true;renderRoutes();if(activePanel==='depots')worker.postMessage({type:'depots',generation});}
  if(m.type==='state'){pendingSample=false;snap=m;map.updateBuses(snap);updateUI();}
  if(m.type==='station'&&selection?.kind==='station'&&selection.id===m.id)renderStation(m);
  if(m.type==='depots')renderDepots(m.depots);
 };
 worker.onerror=e=>{$('#loading').hidden=true;$('#error').hidden=false;$('#error').textContent='No pudo iniciarse el motor: '+e.message;ready=false;};
 function jump(value){clock.time=value;if(clock.time<DAY||clock.time>=2*DAY){const day=Math.floor(clock.time/DAY)-1;config.date=addDays(config.date,day);clock.time-=day*DAY;rebuild();}else{sample();updateUI();}following=false;}
 function syncControls(displayMode=config.selection.mode){
  $('#date').value=config.date;$$('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===displayMode));$('#zone-options').hidden=displayMode!=='zones';
  $('#peak').value=config.params.peakHeadway/60;$('#offpeak').value=config.params.offpeakHeadway/60;$('#demand').value=config.params.demand;$('#demand-value').textContent=config.params.demand+'×';$('#demand-mode').value=config.params.mode;$('#bio-capacity').value=config.params.biarticulatedCapacity;$('#bio-share').value=config.params.biarticulatedShare;$('#bio-value').textContent=config.params.biarticulatedShare+'%';$('#cruise').value=config.params.cruiseKmh;$('#street-speed').value=config.params.streetKmh;
  $$('[data-speed]').forEach(b=>b.classList.toggle('active',Number(b.dataset.speed)===clock.speed));$('#pause').textContent=clock.paused?'▶':'Ⅱ';$('#pause').setAttribute('aria-label',clock.paused?'Reanudar':'Pausar');
 }
 function status(r){if(!r.ready)return 'Datos pendientes';if(!dateEligible(r,config.date))return 'Fuera de vigencia';const w=serviceWindows(r,config.date,data.routes);if(!w.length)return 'Sin servicio este día';if(!w.some(([a,b])=>clock.time-DAY>=a&&clock.time-DAY<b))return 'Fuera de horario';return map.routeSet.has(r.id)?'En operación':'Disponible · fuera de selección';}
 function renderRoutes(){
  const search=$('#search').value.normalize('NFD').replace(/\p{Diacritic}/gu,'').toLowerCase(),dual=$('#only-dual').checked;
  const routes=data.routes.filter(r=>(!dual||r.dual)&&`${r.code} ${(r.paired_ids||[]).map(id=>routeById.get(id)?.code||'').join(' ')} ${r.name} ${r.stops.map(s=>s.name).join(' ')}`.normalize('NFD').replace(/\p{Diacritic}/gu,'').toLowerCase().includes(search)).sort((a,b)=>Number(b.ready)-Number(a.ready)||a.code.localeCompare(b.code,'es',{numeric:true})||a.name.localeCompare(b.name));
  $('#list-count').textContent=routes.length+' servicios y variantes';$('#route-total').textContent=data.counts.map_records;
  const counts=new Map();for(const b of snap.buses)counts.set(b.routeId,(counts.get(b.routeId)||0)+1);
  const fragment=document.createDocumentFragment();for(const r of routes){const b=el('button',undefined,'route-row'+(focusedRoute===r.id?' selected':''));b.dataset.routeId=r.id;b.setAttribute('aria-label',`${r.code} a ${r.name}, ${status(r)}`);b.append(badge(r));const text=el('div',undefined,'route-text');text.append(el('strong',r.name),el('small',`${r.dual?'Dual · ':''}${status(r)}`));b.append(text,el('span',counts.get(r.id)||'','route-count'));b.onclick=()=>selectRoute(r.id);fragment.append(b);}$('#route-list').replaceChildren(fragment);
 }
 function selectRoute(id){const r=routeById.get(id);focusedRoute=id;following=false;selection={kind:'route',id};map.selected=null;map.updateMarker();map.setRoute(id);renderRoute(r);if(r.points.length)map.fitPoints(r.points);renderRoutes();if(config.selection.mode==='route'&&r.ready&&config.selection.route!==id){config.selection.route=id;rebuild();selection={kind:'route',id};renderRoute(r);}}
 function onSelect(value){selection=value;following=false;$('#inspector').hidden=false;map.select(value.kind,value.id);if(value.kind==='station')requestStation();else renderBus();}
 function renderRoute(r){
  const panel=$('#selection');panel.replaceChildren(badge(r),el('span',r.dual?'  SERVICIO DUAL':'  SERVICIO TRONCAL','eyebrow'),el('h2',r.name));$('#inspector').hidden=false;
  row('Recorrido',r.length_m?(r.length_m/1000).toFixed(2)+' km':'Pendiente');row('Paradas',r.stops.length);row('Estado',status(r));
  const mates=(r.paired_ids||[]).map(id=>routeById.get(id)).filter(Boolean);for(const mate of mates){const btn=el('button','Ver sentido '+mate.code+' → '+mate.name,'full');btn.onclick=()=>selectRoute(mate.id);panel.append(btn);}
  const w=serviceWindows(r,config.date,data.routes);for(const [a,b] of w)row('Salidas publicadas',timeText(a).slice(0,5)+'–'+timeText(b).slice(0,5)+(b>DAY?' (+1 día)':''));
  if(r.ready){const b=el('button','Simular solo este servicio','primary full');b.onclick=()=>{config.selection={mode:'route',route:r.id};rebuild({fit:true});selection={kind:'route',id:r.id};renderRoute(r);};panel.append(b);const f=el('button','Seguir un bus de esta ruta','full');f.onclick=()=>followBus(r.id);panel.append(f);}
  for(const issue of r.issues)panel.append(el('p',issue,'muted'));
  const list=el('ol',undefined,'stop-list');for(const s of r.stops){const li=el('li',undefined,s.kind==='street'?'street':'');const b=el('button',s.name);b.onclick=()=>{const st=data.stations.find(st=>st.id===s.station_id);if(st){map.center=[...st.xy];map.mpp=.8;map.updateCamera();onSelect({kind:'station',id:st.id});}};li.append(b,el('small',`${s.kind==='street'?'Paradero en calle':'Estación'}${s.coordinate_source==='route_linear_reference_estimated'?' · ubicación aproximada':''}`));list.append(li);}panel.append(list);
  panel.append(el('p','Horarios publicados; frecuencias, ocupación y asignación a vagones estimadas.','muted'));const source=el('a','Detalle de la fuente ↗');source.href=r.source_url;source.target='_blank';source.rel='noreferrer';panel.append(source);
 }
 function followBus(routeId){const b=snap.buses.find(b=>!routeId||b.routeId===routeId);if(!b){toast('No hay buses de este servicio a esta hora. Prueba otra hora o inclúyelo en la simulación.');return;}selection={kind:'bus',id:b.id};map.select('bus',b.id);following=true;map.mpp=.9;map.center=[...b.xy];map.updateCamera();renderBus();}
 function renderBus(){
  const b=snap.buses.find(b=>b.id===selection?.id);if(!b){if(selection?.kind==='bus'){$('#selection').replaceChildren(el('h2','Viaje finalizado'),el('p','El bus pasa a regulación en la terminal antes de estar disponible de nuevo.','muted'));following=false;}return;}
  const p=$('#selection');p.replaceChildren(badge(b),el('span','  '+b.vehicleId,'eyebrow'),el('h2',b.pattern),el('div',stateNames[b.state]+(b.street?' · calle':''),'bus-state'));$('#inspector').hidden=false;
  row('Velocidad',b.speed_kmh.toFixed(0)+' km/h');row('Tipo de bus',b.busType);$('#selection').append(el('p',b.typeSource,'muted'));row('A bordo',`${b.load} / ${b.capacity}`);const track=el('div',undefined,'load-track'),fill=el('i');fill.style.width=b.load/b.capacity*100+'%';track.append(fill);p.append(track);row(b.state==='moving'?'Próxima parada':'Parada',b.next_stop);row('Punto de atención',b.street?'Paradero calle':'Vagón '+b.wagon+' · est.');row('Recorrido',(b.s/1000).toFixed(2)+' km');row('Atención pendiente',b.delay>0?b.delay.toFixed(0)+' s':'Sin espera');
  const button=el('button',following?'Dejar de seguir':'Seguir este bus','primary full');button.id='follow';button.onclick=()=>{following=!following;if(following){map.mpp=.9;map.center=[...b.xy];map.updateCamera();}renderBus();};p.append(button);const route=el('button','Ver paradas de '+b.code,'full');route.onclick=()=>selectRoute(b.routeId);p.append(route);
 }
 function requestStation(){const s=data.stations.find(s=>s.id===selection?.id);if(!s)return;$('#selection').replaceChildren(el('span',s.kind==='street'?'PARADERO EN CALLE':'ESTACIÓN','eyebrow'),el('h2',s.name),el('p','Consultando próximos servicios…','muted'));$('#inspector').hidden=false;if(ready)worker.postMessage({type:'station',generation,id:s.id});}
 function renderStation(info){
  const s=data.stations.find(s=>s.id===info.id);if(!s)return;const p=$('#selection');p.replaceChildren(el('span',s.kind==='street'?'PARADERO EN CALLE':'ESTACIÓN','eyebrow'),el('h2',s.name));row('Estado publicado',s.status);if(s.demand_profile){row('Validaciones de referencia',fmt(s.demand_profile.total));p.append(el('p','Archivo oficial del 9 sep. 2026. El reparto por sentido se estima.','muted'));}
  if(s.kind!=='street'){row('Vagones',s.wagons?String(s.wagons)+' · publicados':'2 · estimados');const diagram=el('div',undefined,'wagon-diagram');for(let i=1;i<=(s.wagons||2);i++){const w=el('span','V'+i,info.buses.some(b=>b.wagon===i)?'busy':'');diagram.append(w);}p.append(diagram);row('Carriles por sentido','Atención + paso');}
  if(s.coordinate_source==='route_linear_reference_estimated')p.append(el('p','Ubicación aproximada sobre el trazado publicado.','muted'));
  row('Pasajeros esperando',fmt(info.waiting)+' · est.');row('Servicios seleccionados',info.routes.length);p.append(el('h2','Próximas llegadas'));
  if(!info.upcoming.length)p.append(el('p','Sin llegadas en los próximos 30 minutos dentro del escenario seleccionado.','muted'));
  for(const arrival of info.upcoming){const b=el('button',undefined,'route-row');const r=routeById.get(arrival.routeId);b.append(badge(r));const text=el('div',undefined,'route-text');text.append(el('strong',arrival.name),el('small',Math.max(0,Math.ceil((arrival.arrival-clock.time)/60))+' min'+(s.kind==='street'?'':' · Vagón '+arrival.wagon)));b.append(text);b.onclick=()=>selectRoute(r.id);p.append(b);}
  p.append(el('p','Distribución operativa de vagones estimada. Los expresos usan el carril de paso.','muted'));
 }
 function renderDepots(depots){const p=$('#depot-list');p.replaceChildren();if(!depots.length)p.append(el('p','No hay salidas para esta selección y fecha.','muted'));for(const d of depots){const r=el('div',undefined,'depot-row'),b=el('button',d.name);b.onclick=()=>{const station=data.stations.find(s=>s.id===d.id);if(station){map.center=[...station.xy];map.mpp=1.3;map.updateCamera();onSelect({kind:'station',id:d.id});}};r.append(b,el('small',`${fmt(d.departures)} salidas hoy · ${fmt(d.reserve)} buses disponibles`),el('small',Number.isFinite(d.next)?'Próxima salida '+timeText(d.next).slice(0,5):'Sin más salidas programadas'));p.append(r);}}
 function updateUI(){const s=snap.stats;$('#active-count').textContent=fmt(s.fleet||0);$('#onboard-count').textContent=fmt(s.onboard||0);$('#dwell-count').textContent=fmt(s.dwell||0);$('#queue-count').textContent=fmt(s.queue||0);if(document.activeElement!==$('#time'))$('#time').value=timeText(clock.time);if(document.activeElement!==$('#scrub'))$('#scrub').value=Math.floor(clock.time%DAY);$('#day-type').textContent=dayType(config.date)==='holiday'?'Domingo / festivo':new Date(config.date+'T12:00:00Z').toLocaleDateString('es-CO',{weekday:'long'});$('#period').textContent=demandPeriod(clock.time,config.date,config.params.mode)==='peak'?'Hora pico':'Hora valle';}
 function switchPanel(name){activePanel=name;$$('[data-panel]').forEach(b=>b.classList.toggle('nav-active',b.dataset.panel===name));$$('.panel').forEach(p=>p.hidden=p.id!==name+'-panel');if(name==='depots'&&ready)worker.postMessage({type:'depots',generation});}
 $$('[data-panel]').forEach(b=>b.onclick=()=>switchPanel(b.dataset.panel));
 $$('[data-mode]').forEach(b=>b.onclick=()=>{if(b.dataset.mode==='all'){config.selection={mode:'all'};rebuild({fit:true});}else if(b.dataset.mode==='zones'){syncControls('zones');toast('Elige una o varias troncales y pulsa «Simular selección».');}else{const r=routeById.get(focusedRoute)||data.routes.find(r=>r.ready&&r.code==='1');config.selection={mode:'route',route:r.id};rebuild({fit:true});selection={kind:'route',id:r.id};renderRoute(r);}});
 for(const z of data.zones.filter(z=>z.id!=='?')){const b=el('button',undefined,'zone-button');b.style.setProperty('--zone',z.color);b.append(el('b',z.id),el('span',z.name));b.classList.toggle('active',selectedZones.has(z.id));b.setAttribute('aria-pressed',selectedZones.has(z.id));b.onclick=()=>{if(selectedZones.has(z.id))selectedZones.delete(z.id);else selectedZones.add(z.id);b.classList.toggle('active',selectedZones.has(z.id));b.setAttribute('aria-pressed',selectedZones.has(z.id));};$('#zones').append(b);}
 $('#apply-zones').onclick=()=>{if(!selectedZones.size){toast('Selecciona al menos una troncal.');return;}config.selection={mode:'zones',zones:[...selectedZones]};rebuild({fit:true});};
 $('#search').oninput=renderRoutes;$('#only-dual').onchange=renderRoutes;$('#demand').oninput=()=>$('#demand-value').textContent=$('#demand').value+'×';
 $('#bio-share').oninput=()=>$('#bio-value').textContent=$('#bio-share').value+'%';
 $('#settings-form').onsubmit=e=>{e.preventDefault();config.params=parameters({...config.params,biarticulatedCapacity:Number($('#bio-capacity').value),biarticulatedShare:Number($('#bio-share').value),peakHeadway:Number($('#peak').value)*60,offpeakHeadway:Number($('#offpeak').value)*60,demand:Number($('#demand').value),mode:$('#demand-mode').value,cruiseKmh:Number($('#cruise').value),streetKmh:Number($('#street-speed').value)});rebuild();toast('Escenario reconstruido con la nueva operación.');};
 $('#date').onchange=()=>{if(!$('#date').value)return;config.date=$('#date').value;rebuild();};$('#time').onchange=()=>{if(!$('#time').value)return;const p=$('#time').value.split(':').map(Number);jump(DAY+p[0]*3600+p[1]*60+(p[2]||0));};
 $('#scrub').oninput=()=>{$('#time').value=timeText(Number($('#scrub').value));};$('#scrub').onchange=()=>jump(DAY+Number($('#scrub').value));$('#back').onclick=()=>jump(clock.time-900);$('#forward').onclick=()=>jump(clock.time+900);$('#pause').onclick=()=>{clock.paused=!clock.paused;syncControls();};
 $$('[data-speed]').forEach(b=>b.onclick=()=>{clock.speed=Number(b.dataset.speed);syncControls();});
 $('#zoom-in').onclick=()=>map.zoom(1/1.4);$('#zoom-out').onclick=()=>map.zoom(1.4);$('#fit').onclick=()=>{following=false;fitSelection();};$('#context-toggle').onclick=()=>{map.contextGroup.visible=!map.contextGroup.visible;$('#context-toggle').setAttribute('aria-pressed',map.contextGroup.visible);};map.onPan=()=>following=false;
 $('#close-inspector').onclick=()=>{selection=null;following=false;map.selected=null;map.updateMarker();$('#inspector').hidden=true;focusedRoute=config.selection.mode==='route'?config.selection.route:null;map.setRoute(focusedRoute);};
 $('#save').onclick=()=>{try{localStorage.setItem('transmi-scenario-v2',JSON.stringify({revision:data.revision,config,clock}));toast('Escenario guardado. Se restaurará pausado al abrirlo.');}catch{toast('No se pudo guardar en este dispositivo.');}};
 const coverage=el('div',undefined,'coverage-grid');for(const [value,label] of [[data.counts.map_records,'registros del mapa'],[data.counts.map_codes,'códigos distintos'],[data.counts.ready,'variantes utilizables'],[data.counts.pending,'registros pendientes']]){const box=el('div');box.append(el('strong',value),el('span',label));coverage.append(box);}$('#coverage').append(coverage);if(data.demand)$('#coverage').append(el('p',fmt(data.demand.matched_validations)+' validaciones del 9 sep. 2026 enlazadas por estación y hora. No equivalen a una matriz origen-destino.','muted'));
 for(const r of data.routes.filter(r=>!r.ready)){const d=el('details');d.append(el('summary',r.code+' · '+r.name),el('p',r.issues.join(' ')));$('#pending-list').append(d);}
 for(const r of data.excluded||[]){const p=el('p',r.code+' · '+r.name+': excluida del alcance troncal.','muted');$('#pending-list').append(p);}
 let last=performance.now();document.addEventListener('visibilitychange',()=>{last=performance.now();});
 function frame(now){const dt=(now-last)/1000;last=now;if(!document.hidden){if(ready&&!clock.paused&&document.activeElement!==$('#scrub')&&document.activeElement!==$('#time')){clock.time+=dt*clock.speed;if(clock.time>=2*DAY)jump(clock.time);}if(now-lastSample>=50){sample();lastSample=now;}
  if(following&&selection?.kind==='bus'){const b=snap.buses.find(b=>b.id===selection.id);if(b){map.center=[...b.xy];if(now-lastUI>100)map.updateCamera();}}
  map.render();if(now-lastUI>200){updateUI();lastUI=now;}if(now-lastList>5000){if(activePanel==='routes'&&!$('#route-list').contains(document.activeElement))renderRoutes();if(activePanel==='depots'&&ready)worker.postMessage({type:'depots',generation});lastList=now;}
  if(now-lastInspect>1000&&!$('#inspector').contains(document.activeElement)){if(selection?.kind==='bus')renderBus();if(selection?.kind==='station'&&ready)worker.postMessage({type:'station',generation,id:selection.id});lastInspect=now;}}
 requestAnimationFrame(frame);}
 const dispose=registerSimulationTools(document.modelContext,{read:()=>({...snap.stats,date:config.date,paused:clock.paused,speed:clock.speed,selected:selection}),control:input=>{if('paused'in input)clock.paused=input.paused;if('speed'in input)clock.speed=input.speed;syncControls();}});
 window.addEventListener('pagehide',()=>{worker.terminate();dispose?.();},{once:true});
 document.addEventListener('keydown',e=>{if(e.code==='Space'&&!['INPUT','SELECT','BUTTON','TEXTAREA'].includes(e.target.tagName)){e.preventDefault();clock.paused=!clock.paused;syncControls();}});
 rebuild();requestAnimationFrame(frame);
}catch(error){$('#loading').hidden=true;$('#error').hidden=false;$('#error').textContent='No fue posible abrir el simulador. '+error.message;console.error(error);}
