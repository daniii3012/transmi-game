/** Vehicle capacity and type are stable for a bus throughout depot reuse. */
export function vehicleSpec(route,params,seed){
 if(route.vehicle_profile?.type==='dual_articulated_electric')return {kind:'dual_electric',capacity:160,length:18.5,label:'Dual articulado eléctrico',typeSource:'Publicado para F63/Z63'};
 if(route.dual)return {kind:'dual',capacity:80,length:12,label:'Padrón dual',typeSource:'Tipo asignado como estimación de familia'};
 if(seed%100<params.biarticulatedShare)return {kind:'biarticulated',capacity:params.biarticulatedCapacity,length:27.2,label:'Biarticulado',typeSource:'Mezcla estimada'};
 return {kind:'articulated',capacity:params.capacity,length:18.5,label:'Articulado',typeSource:'Asignación estimada'};
}
