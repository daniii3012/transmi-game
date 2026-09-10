import {NetworkMap} from './map.mjs';
import {Simulation,FixedClock} from './simulation.mjs';
import {registerSimulationTools} from './webmcp.mjs';
const $=s=>document.querySelector(s);
const stateNames={moving:'En recorrido',dwell:'Puertas abiertas · parada',queue:'Esperando paso',terminal:'Regulación de ensayo'};
const choices={pilot:[8,24,64],load:[100,1000,3000]};
const make=(tag,text,className)=>{const e=document.createElement(tag);e.textContent=text;if(className)e.className=className;return e;};
const clockText=seconds=>new Date(Math.floor(seconds+1e-7)*1000).toISOString().slice(11,19);
try {
 const response=await fetch('./network.json');if(!response.ok)throw new Error('No se pudo cargar la cartografía local.');
 const data=await response.json();let sim,clock,filter='all',selection=null,following=false,uiElapsed=1;
 let coreMs=0,frameMs=0,frameCount=0,frameTotal=0;
 $('#simulation-controls').innerHTML='<label for="fleet">Buses · cambia y reinicia el ensayo</label><select id="fleet"></select><div class="time-row"><span id="clock" class="clock">00:00:00</span><button id="pause" class="primary" aria-label="Pausar simulación">Pausa</button><label class="visually-hidden" for="speed">Velocidad del reloj</label><select id="speed"><option value="1">1×</option><option value="8">8×</option><option value="32">32×</option></select></div><div class="fleet-stats"><div><strong id="active-count">0</strong><span>Buses del ensayo</span></div><div><strong id="stop-count">0</strong><span>Paradas atendidas</span></div></div><button id="pick-bus" style="width:100%;margin-top:16px">Seguir un bus</button>';
 const map=new NetworkMap($('#canvas-host'),$('#labels'),data,onSelect);
 function onSelect(value){selection=value;following=false;map.select(value.kind,value.id);renderSelection();}
 function showView(which){following=false;if(which==='pilot'){map.fitPilot();$('#view-title').textContent='Américas · Mandalay–Marsella';}else{map.fitNetwork();$('#view-title').textContent='Bogotá · cartografía de referencia';}}
 map.onPan=()=>{following=false;};
 function reset(scenario=$('#scenario').value,fleet=Number($('#fleet').value)||choices[scenario][1]){
   sim=new Simulation(data,{scenario,fleet});clock=new FixedClock(sim);clock.speed=Number($('#speed').value);filter='all';selection=null;following=false;map.selected=null;
   $('#scenario').value=scenario;$('#fleet').replaceChildren(...choices[scenario].map(n=>{const o=make('option',n.toLocaleString('es-CO'));o.value=n;return o;}));$('#fleet').value=fleet;
   $('#pattern').replaceChildren(new Option('Todos los recorridos del ensayo','all'),...[...sim.lanes.values()].map(p=>new Option(p.label,p.id)));
   $('#scenario-note').textContent=scenario==='pilot'?'Mandalay → Av. Boyacá → Marsella. Dos sentidos de ensayo, distancias reales.':'Carga sintética en componentes separados. Sin rutas comerciales, conexiones ni frecuencias oficiales.';
   showView(scenario==='pilot'?'pilot':'network');updateUI();renderSelection();
 }
 function control(input){if('paused'in input)clock.paused=input.paused;if('speed'in input)clock.speed=input.speed;updateUI();}
 function renderSelection(){
   const panel=$('#selection');panel.replaceChildren();
   if(selection?.kind==='station'){
     const s=data.stations.find(s=>s.id===selection.id);panel.append(make('div','ESTACIÓN '+s.id,'eyebrow'),make('h2',s.name));
     const relevant=[...sim.lanes.values()].filter(l=>l.stops.some(stop=>stop.station_id===s.id));
     panel.append(make('p',relevant.length?`${relevant.length} sentidos de ensayo la incluyen. La detención usa su proyección sobre el eje; vagones y puertas reales siguen pendientes.`:'Punto de la cartografía de referencia. No está incluido como parada en este escenario.'));
   }else if(selection?.kind==='bus'){
     const b=sim.inspect(selection.id);if(!b){selection=null;return renderSelection();}
     panel.append(make('div',b.id+' · ARTICULADO DE ENSAYO','eyebrow'),make('h2',b.pattern),make('div',stateNames[b.state],'bus-state'));
     for(const [key,value] of [['Velocidad',b.speed_kmh.toFixed(0)+' km/h'],['Próxima parada',b.next_stop],['Paradas atendidas',String(b.stopsServed)]]){const row=make('div','','metric-row');row.append(make('span',key),make('strong',value));panel.append(row);}
     const button=make('button',following?'Dejar de seguir':'Seguir este bus');button.id='follow';button.onclick=()=>{following=!following;if(following){map.mpp=Math.min(map.mpp,1.6);map.center=b.xy;map.updateCamera();}renderSelection();};panel.append(button);
   }else if(filter!=='all'){
     const p=sim.lanes.get(filter);panel.append(make('div','RECORRIDO DE ENSAYO','eyebrow'),make('h2',p.label),make('p',(p.path.length/1000).toFixed(2)+' km de eje geográfico · parada de ensayo de '+p.dwell_s+' s'));
     const list=make('ol','','stop-list');for(const stop of p.stops)list.append(make('li',stop.name));panel.append(list);
   }else{
     panel.append(make('div','OBSERVAR LA OPERACIÓN','eyebrow'),make('h2','Cada bus conserva su recorrido'),make('p','Rojo o color del corredor: circulando. Ámbar: atendiendo una parada. Marrón: en cola. Selecciona un bus o una estación.'));
   }
 }
 function updateUI(){
   const stats=sim.stats();$('#clock').textContent=clockText(stats.time_s);$('#active-count').textContent=stats.fleet.toLocaleString('es-CO');$('#stop-count').textContent=stats.stops.toLocaleString('es-CO');
   $('#pause').textContent=clock.paused?'Continuar':'Pausa';$('#pause').setAttribute('aria-label',clock.paused?'Reanudar simulación':'Pausar simulación');$('#speed').value=clock.speed;
   const backlog=clock.pending>1?' · reloj recuperando '+clock.pending.toFixed(1)+' s':'';
   $('#map-status').textContent=`${stats.moving} circulando · ${stats.dwell} en parada · ${stats.queue} en cola · ${stats.terminal} regulando${backlog}`;
   if(selection?.kind==='bus'){
     // Keep the focused action node stable while refreshing live text.
     const b=sim.inspect(selection.id),panel=$('#selection');
     if(b&&panel.querySelector('.bus-state')){panel.querySelector('h2').textContent=b.pattern;panel.querySelector('.bus-state').textContent=stateNames[b.state];const values=panel.querySelectorAll('.metric-row strong');[b.speed_kmh.toFixed(0)+' km/h',b.next_stop,String(b.stopsServed)].forEach((v,i)=>values[i].textContent=v);const button=$('#follow');if(button)button.textContent=following?'Dejar de seguir':'Seguir este bus';}
   }
 }
 $('#scenario').onchange=()=>reset($('#scenario').value,choices[$('#scenario').value][1]);
 $('#fleet').onchange=()=>reset();$('#speed').onchange=()=>control({speed:Number($('#speed').value)});$('#pause').onclick=()=>control({paused:!clock.paused});
 $('#pattern').onchange=()=>{filter=$('#pattern').value;selection=null;following=false;map.selected=null;if(filter!=='all'){map.fitPoints(sim.lanes.get(filter).points);$('#view-title').textContent=sim.lanes.get(filter).label;}renderSelection();};
 $('#pick-bus').onclick=()=>{const b=sim.buses.find(b=>filter==='all'||filter===b.laneId);if(!b)return;onSelect({kind:'bus',id:b.id});following=true;map.mpp=1.2;map.center=sim.inspect(b.id).xy;map.updateCamera();renderSelection();};
 $('#pilot-view').onclick=()=>showView('pilot');$('#network-view').onclick=()=>showView('network');
 $('#zoom-in').onclick=()=>map.zoom(1/1.4);$('#zoom-out').onclick=()=>map.zoom(1.4);
 reset('pilot',24);
 const disposeTools=registerSimulationTools(document.modelContext,{read:()=>({...sim.stats(),paused:clock.paused,speed:clock.speed,selected:selection,core_ms_last_frame:coreMs,frame_ms_average:frameMs}),control});
 window.addEventListener('pagehide',()=>disposeTools?.(),{once:true});
 let previous=performance.now();
 document.addEventListener('visibilitychange',()=>{previous=performance.now();});
 function frame(now){
   const dt=(now-previous)/1000;previous=now;
   if(!document.hidden){
     const begin=performance.now();clock.advance(dt);coreMs=performance.now()-begin;
     if(following&&selection?.kind==='bus'){const b=sim.inspect(selection.id);if(b&&filter!=='all'&&filter!==b.laneId){filter=b.laneId;$('#pattern').value=filter;}if(b&&Math.hypot(b.xy[0]-map.center[0],b.xy[1]-map.center[1])>map.mpp*1.5){map.center=b.xy;map.updateCamera();}}
     map.updateBuses(sim,filter);map.render();uiElapsed+=dt;
     frameTotal+=performance.now()-begin;frameCount++;if(uiElapsed>.2){frameMs=frameTotal/frameCount;frameTotal=0;frameCount=0;uiElapsed=0;updateUI();}
   }
   requestAnimationFrame(frame);
 }
 requestAnimationFrame(frame);
} catch(error){$('#error').hidden=false;$('#error').textContent='No fue posible abrir el mapa. '+error.message;console.error(error);}
