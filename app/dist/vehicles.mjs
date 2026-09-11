/** A route has one stable size; assignments without source remain explicit estimates. */
export function vehicleSpec(route,params={},seed=0){
 const variation=[-5,-2,0,2,5][seed%5];
 if(route.vehicle_profile?.type==='dual_articulated_electric')return {kind:'dual_electric',capacity:160,length:18.5,label:'Dual articulado eléctrico',typeSource:'Tipo publicado',speedOffset:variation};
 if(route.dual)return {kind:'dual',capacity:80,length:12,label:'Padrón dual',typeSource:'Asignación estimada por servicio',speedOffset:variation};
 const easy=/^[1-8]$/.test(route.code),reported=['M51','F51'].includes(route.code);
 const biarticulated=!easy&&(reported||route.length_m>=18000);
 return {kind:biarticulated?'biarticulated':'articulated',capacity:biarticulated?240:160,length:biarticulated?27.2:18.5,label:biarticulated?'Biarticulado':'Articulado',typeSource:easy||reported?'Asignación indicada por el usuario':'Asignación estimada por recorrido',speedOffset:variation};
}
