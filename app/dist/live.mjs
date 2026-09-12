// Buses reales, leídos por el servidor local. Es la única parte del simulador que depende de la
// red: no alimenta el escenario ni el planificador, solo se dibuja encima. Sin servidor local
// —por ejemplo en lo publicado— la sonda falla y el panel lo explica en vez de fingir datos.

export const OCCUPANCY={VACIO:'Vacío',MEDIO:'Medio',LLENO:'Lleno'};
// El servicio y el catálogo del proyecto vienen de la misma familia de datos y escriben los
// acentos descompuestos; comparar normalizado evita depender de esa coincidencia.
export const sameName=(a,b)=>(a||'').normalize('NFC')===(b||'').normalize('NFC');
export const occupancyText=value=>OCCUPANCY[(value||'').trim().toUpperCase()]||'Sin dato';
export function ageText(seconds){
 if(!Number.isFinite(seconds))return 'sin hora';
 if(seconds<90)return `hace ${Math.round(seconds)} s`;
 return `hace ${Math.round(seconds/60)} min`;
}
export function groupByDestination(buses){
 const groups=new Map();
 for(const bus of buses||[]){const key=(bus.destination||'').normalize('NFC');if(!groups.has(key))groups.set(key,[]);groups.get(key).push(bus);}
 return [...groups].map(([destination,list])=>({destination,buses:list.sort((a,b)=>(b.travelled_m||0)-(a.travelled_m||0))}))
  .sort((a,b)=>b.buses.length-a.buses.length||a.destination.localeCompare(b.destination,'es'));
}

export class LiveFeed{
 // Rutas relativas: bajo GitHub Pages la aplicación vive en un subdirectorio y una ruta absoluta
 // apuntaría fuera del sitio.
 // `url` decide a qué endpoint se pregunta, así una misma mecánica de sondeo sirve para la
 // instantánea de la red y para el seguimiento de un servicio.
 constructor({interval=20000,onState,url=code=>`./api/en-vivo/buses?ruta=${encodeURIComponent(code)}`}={}){this.interval=interval;this.onState=onState;this.url=url;this.code=null;this.active=false;this.timer=null;this.sequence=0;this.controller=null;this.status=null;}
 async probe(){
  try{
   const response=await fetch('./api/en-vivo/estado',{cache:'no-store'});
   if(!response.ok)throw new Error(String(response.status));
   this.status=await response.json();
  }catch{this.status={available:false};}
  return this.status;
 }
 select(code){if(code===this.code)return;this.code=code||null;this.emit({phase:this.code?'loading':'idle'});if(this.active)this.refresh();}
 setActive(active){
  if(active===this.active)return;
  this.active=active;clearInterval(this.timer);this.timer=null;
  if(!active){this.controller?.abort();return;}
  this.refresh();this.timer=setInterval(()=>this.refresh(),this.interval);
 }
 async refresh(){
  if(!this.code||!this.active)return;
  const sequence=++this.sequence;this.controller?.abort();this.controller=new AbortController();
  try{
   const response=await fetch(this.url(this.code),{cache:'no-store',signal:this.controller.signal});
   const payload=await response.json();
   if(sequence!==this.sequence)return;
   if(!response.ok)return this.emit({phase:'error',message:payload.detail||'El servidor local no pudo responder.',payload});
   this.emit({phase:'ok',payload});
  }catch(error){
   if(error.name==='AbortError'||sequence!==this.sequence)return;
   this.emit({phase:'error',message:'No hay respuesta del servidor local. ¿Sigue abierta su Terminal?'});
  }
 }
 emit(state){this.onState?.({code:this.code,...state});}
 stop(){this.active=false;clearInterval(this.timer);this.timer=null;this.controller?.abort();}
}
