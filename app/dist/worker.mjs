import {Operation} from './operation.mjs?v=20260910.3';
let engine=null,generation=0;
self.onmessage=({data:m})=>{
 try{
  if(m.type==='init'){
   generation=m.generation;engine=null;
   const start=performance.now();engine=new Operation(m.data,m.config);engine.seek(m.time);
   self.postMessage({type:'ready',generation,buildMs:performance.now()-start,windows:engine.routeWindows,routeIds:[...engine.routes.keys()]});
  }
  if(m.generation!==generation||!engine)return;
  if(m.type==='sample'||m.type==='init'){
   engine.seek(m.time);self.postMessage({type:'state',generation,time:m.time,buses:engine.buses,stats:engine.stats()});
  }else if(m.type==='station')self.postMessage({type:'station',generation,id:m.id,...engine.stationStats(m.id)});
  else if(m.type==='depots')self.postMessage({type:'depots',generation,depots:engine.depotStats()});
 }catch(error){self.postMessage({type:'error',generation,message:error.message});}
};
