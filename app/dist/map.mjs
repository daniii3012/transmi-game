import * as THREE from './vendor/three.module.js';

export class NetworkMap {
  constructor(host, labels, data, onSelect) {
    this.host=host; this.labels=labels; this.data=data; this.onSelect=onSelect;
    this.routeId=null;this.routeSet=new Set(data.routes.filter(r=>r.ready).map(r=>r.id));this.contextGroup=new THREE.Group();this.center=[0,0]; this.mpp=30; this.selected=null; this.busSamples=[];
    this.renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
    this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));
    this.renderer.setClearColor('#edf1f4'); host.append(this.renderer.domElement);
    this.scene=new THREE.Scene();
    this.camera=new THREE.OrthographicCamera(-1,1,1,-1,.1,100); this.camera.position.z=20;
    this.scene.add(this.contextGroup);this.paths=[];
    this.routeGroup=new THREE.Group();this.scene.add(this.routeGroup);
    this.highlight=new THREE.Mesh(new THREE.BufferGeometry(),new THREE.MeshBasicMaterial({color:'#dc253b',depthTest:false,transparent:true,opacity:.95}));this.highlight.renderOrder=2;this.scene.add(this.highlight);
    this.clusterLayer=document.createElement('div');this.clusterLayer.className='clusters';host.parentElement.append(this.clusterLayer);this.clusterLayer.setAttribute('aria-hidden','true');this.clusterLayer.style.cssText='position:absolute;inset:0;pointer-events:none;overflow:hidden';
    for(const c of data.corridors){
      const mesh=new THREE.Mesh(new THREE.BufferGeometry(),new THREE.MeshBasicMaterial({color:c.color,transparent:true,opacity:c.zone==='Z'?.25:.88,depthTest:false}));
      mesh.renderOrder=1; this.scene.add(mesh); this.paths.push({c,mesh});
    }
    this.stopOuter=new THREE.InstancedMesh(new THREE.CircleGeometry(1,16),new THREE.MeshBasicMaterial({color:'#6c7c8a',depthTest:false}),data.stations.length);
    this.stopInner=new THREE.InstancedMesh(new THREE.CircleGeometry(1,16),new THREE.MeshBasicMaterial({color:'#ffffff',depthTest:false}),data.stations.length);
    this.stopOuter.renderOrder=2;this.stopInner.renderOrder=3;
    this.stopOuter.frustumCulled=false;this.stopInner.frustumCulled=false;
    this.scene.add(this.stopOuter,this.stopInner);
    this.marker=new THREE.Mesh(new THREE.RingGeometry(.7,1,24),new THREE.MeshBasicMaterial({color:'#dc253b',depthTest:false}));
    this.marker.renderOrder=7;this.marker.visible=false;this.scene.add(this.marker);
    this.wagonBorder=new THREE.InstancedMesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({color:'#97a8b7',depthTest:false}),3000);this.wagonBorder.renderOrder=3.5;this.wagonBorder.frustumCulled=false;this.scene.add(this.wagonBorder);
    this.wagonMesh=new THREE.InstancedMesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({color:'#f9fafb',depthTest:false}),3000);this.wagonMesh.renderOrder=4;this.wagonMesh.frustumCulled=false;this.scene.add(this.wagonMesh);
    this.axes=new Map();for(const r of data.routes.filter(r=>r.ready)){for(const st of r.stops){let nearest=0,d=Infinity;for(let i=0;i<r.points.length-1;i++){const p=r.points[i],station=data.stations.find(s=>s.id===st.station_id);if(!station)continue;const n=Math.hypot(p[0]-station.xy[0],p[1]-station.xy[1]);if(n<d){d=n;nearest=i;}}const a=r.points[nearest],b=r.points[nearest+1],angle=Math.atan2(b[1]-a[1],b[0]-a[0]),sum=this.axes.get(st.station_id)||[0,0];sum[0]+=Math.cos(2*angle);sum[1]+=Math.sin(2*angle);this.axes.set(st.station_id,sum);}}
    this.object=new THREE.Object3D(); this.w=1;this.h=1;
    this.resizeObserver=new ResizeObserver(()=>{this.resize();});this.resizeObserver.observe(host);
    this.resize(); this.fitNetwork(); this.bind();
  }
  fit(bounds){const mobile=this.w<800,left=mobile?20:350,right=!mobile&&this.w>1100&&!document.querySelector('#inspector').hidden?400:70,top=70,bottom=mobile?this.h*.54:235;this.mpp=Math.max((bounds[2]-bounds[0])/Math.max(100,this.w-left-right),(bounds[3]-bounds[1])/Math.max(100,this.h-top-bottom),.3);this.center=[(bounds[0]+bounds[2])/2-(left-right)/2*this.mpp,(bounds[1]+bounds[3])/2+(top-bottom)/2*this.mpp];this.updateCamera();}
  fitNetwork(){this.fit(this.data.bounds);}
  fitPilot(){this.fitNetwork();}
  fitPoints(points){this.fit([Math.min(...points.map(p=>p[0])),Math.min(...points.map(p=>p[1]))-80,Math.max(...points.map(p=>p[0])),Math.max(...points.map(p=>p[1]))+80]);}
  resize(){this.w=this.host.clientWidth;this.h=this.host.clientHeight;if(!this.w||!this.h)return;this.renderer.setSize(this.w,this.h);this.updateCamera();}
  worldToScreen(p){return [(p[0]-this.center[0])/this.mpp+this.w/2, (this.center[1]-p[1])/this.mpp+this.h/2];}
  screenToWorld(p){return [this.center[0]+(p[0]-this.w/2)*this.mpp,this.center[1]-(p[1]-this.h/2)*this.mpp];}
  zoom(factor, anchor=[this.w/2,this.h/2]){const before=this.screenToWorld(anchor);this.mpp=Math.max(.12,Math.min(160,this.mpp*factor));const after=this.screenToWorld(anchor);this.center[0]+=before[0]-after[0];this.center[1]+=before[1]-after[1];this.updateCamera();}
  updateCamera(){
    Object.assign(this.camera,{left:-this.w*this.mpp/2,right:this.w*this.mpp/2,top:this.h*this.mpp/2,bottom:-this.h*this.mpp/2});
    this.camera.position.set(this.center[0],this.center[1],20);this.camera.updateProjectionMatrix();this.camera.updateMatrixWorld();
    if(this.builtMpp!==this.mpp){
    this.builtMpp=this.mpp;
    for(const {c,mesh} of this.paths){
      const vertices=[];const width=Math.max(9,this.mpp*3.2);
      for(const line of c.components)for(let i=1;i<line.length;i++){
        const [x,y]=line[i-1],[a,b]=line[i],len=Math.hypot(a-x,b-y);if(len<1e-6)continue;
        const dx=-(b-y)/len*width/2,dy=(a-x)/len*width/2;
        vertices.push(x+dx,y+dy,0,x-dx,y-dy,0,a+dx,b+dy,0,a+dx,b+dy,0,x-dx,y-dy,0,a-dx,b-dy,0);
      }
      mesh.geometry.dispose();mesh.geometry=new THREE.BufferGeometry();mesh.geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
    }
    this.data.stations.forEach((s,i)=>{
      const radius=Math.max(3,this.mpp*(this.mpp<5?4.5:2.7));this.object.position.set(...s.xy,1);this.object.rotation.z=0;
      this.object.scale.set(radius,radius,1);this.object.updateMatrix();this.stopOuter.setMatrixAt(i,this.object.matrix);
      this.object.scale.set(radius*.62,radius*.62,1);this.object.updateMatrix();this.stopInner.setMatrixAt(i,this.object.matrix);
    });
    this.rebuildHighlight();this.updateWagons();this.stopOuter.instanceMatrix.needsUpdate=true;this.stopInner.instanceMatrix.needsUpdate=true;
    }
    this.updateLabels();this.updateMarker();this.updateScale();
    if(this.infrastructureGroup)this.infrastructureGroup.visible=this.mpp<8;
    if(this.lastSimulation)this.updateBuses(this.lastSimulation);
  }
  updateLabels(){
    this.labels.replaceChildren();const occupied=[];
    const priority=s=>s.id===this.selected?.id?0:s.name.startsWith('Portal')?1:s.kind==='street'?3:2;
    for(const s of [...this.data.stations].sort((a,b)=>priority(a)-priority(b))){
      if(this.mpp>20&&priority(s)>1)continue;if(this.mpp>3&&priority(s)>2)continue;
      const [x,y]=this.worldToScreen(s.xy); const width=Math.min(s.name.length*6.3+8,245), r=[x+10,y-10,x+10+width,y+12];
      if(x<0||y<85||r[2]>this.w-55||y>this.h-130||occupied.some(a=>r[0]<a[2]+5&&r[2]>a[0]-5&&r[1]<a[3]+5&&r[3]>a[1]-5))continue;
      const label=document.createElement('div');label.className='station-label'+(s.kind==='street'?' street':'');label.textContent=s.name;label.style.left=r[0]+'px';label.style.top=r[1]+'px';this.labels.append(label);occupied.push(r);
    }
  }
  updateScale(){const approx=this.mpp*100;const power=10**Math.floor(Math.log10(approx));const step=[1,2,5,10].find(n=>n*power>=approx)*power;const el=document.querySelector('#scale');el.textContent=step>=1000?(step/1000)+' km':step+' m';el.style.width=step/this.mpp+'px';}
  select(kind,id){this.selected={kind,id};this.updateMarker();this.updateLabels();}
  updateMarker(){const item=this.selected?.kind==='station'?this.data.stations.find(s=>s.id===this.selected.id):this.busSamples.find(b=>b.id===this.selected?.id);if(!item){this.marker.visible=false;return;}this.marker.visible=true;this.marker.position.set(...item.xy,4);this.marker.scale.setScalar(Math.max(10,this.mpp*11));}
  bind(){
    let drag=null;
    this.host.addEventListener('pointerdown',e=>{if(e.button!==0)return;this.host.focus({preventScroll:true});this.host.setPointerCapture(e.pointerId);drag={id:e.pointerId,start:[e.clientX,e.clientY],center:[...this.center]};});
    this.host.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;this.center=[drag.center[0]-(e.clientX-drag.start[0])*this.mpp,drag.center[1]+(e.clientY-drag.start[1])*this.mpp];this.onPan?.();this.updateCamera();});
    this.host.addEventListener('pointerup',e=>{if(!drag||drag.id!==e.pointerId)return;const click=Math.hypot(e.clientX-drag.start[0],e.clientY-drag.start[1])<5;drag=null;if(click){const r=this.host.getBoundingClientRect();this.pick([e.clientX-r.left,e.clientY-r.top]);}});
    this.host.addEventListener('pointercancel',()=>{drag=null;});
    this.host.addEventListener('wheel',e=>{e.preventDefault();const r=this.host.getBoundingClientRect();this.zoom(Math.exp(Math.max(-.7,Math.min(.7,e.deltaY*.0015))),[e.clientX-r.left,e.clientY-r.top]);},{passive:false});
    this.host.addEventListener('keydown',e=>{const offsets={ArrowLeft:[-80,0],ArrowRight:[80,0],ArrowUp:[0,80],ArrowDown:[0,-80]};if(offsets[e.key]){e.preventDefault();this.center[0]+=offsets[e.key][0]*this.mpp;this.center[1]+=offsets[e.key][1]*this.mpp;this.onPan?.();this.updateCamera();}else if(['+','=','-'].includes(e.key)){e.preventDefault();this.zoom(e.key==='-'?1.3:1/1.3);}});
  }
  pick(point){let nearest=null, distance=12;for(const [kind,items] of [['bus',this.busSamples],['station',this.data.stations]])for(const item of items){const p=this.worldToScreen(item.xy),d=Math.hypot(point[0]-p[0],point[1]-p[1]);if(d<distance){nearest={kind,id:item.id};distance=d;}}if(nearest){this.select(nearest.kind,nearest.id);this.onSelect(nearest);}}
  setRoute(id){this.routeId=id;this.rebuildHighlight();}
  rebuildHighlight(){
    const routes=this.routeId?this.data.routes.filter(r=>r.id===this.routeId&&r.ready):this.data.routes.filter(r=>r.dual&&r.ready&&this.routeSet.has(r.id));
    const vertices=[],colors=[];for(const r of routes){const color=new THREE.Color(r.color),width=Math.max(4,this.mpp*(this.routeId?5:2.1));for(let i=1;i<r.points.length;i++){const [x,y]=r.points[i-1],[a,b]=r.points[i],len=Math.hypot(a-x,b-y);if(!len)continue;const dx=-(b-y)/len*width/2,dy=(a-x)/len*width/2;vertices.push(x+dx,y+dy,0,x-dx,y-dy,0,a+dx,b+dy,0,a+dx,b+dy,0,x-dx,y-dy,0,a-dx,b-dy,0);for(let j=0;j<6;j++)colors.push(color.r,color.g,color.b);}}
    this.highlight.geometry.dispose();this.highlight.geometry=new THREE.BufferGeometry();this.highlight.geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));this.highlight.geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));this.highlight.material.vertexColors=true;this.highlight.material.color.set('#ffffff');this.highlight.material.needsUpdate=true;
    for(const {mesh} of this.paths)mesh.material.opacity=this.routeId?.3:.86;
  }
  updateWagons(){
    this.wagonBorder.visible=this.wagonMesh.visible=this.mpp<2.2;let i=0;if(this.wagonMesh.visible)for(const s of this.data.stations){if(s.kind==='street'||s.status==='En obras')continue;const sum=this.axes.get(s.id)||[1,0],angle=Math.atan2(sum[1],sum[0])/2,n=s.wagons||2;for(let w=1;w<=n;w++){const offset=(w-(n+1)/2)*64;this.object.position.set(s.xy[0]+Math.cos(angle)*offset,s.xy[1]+Math.sin(angle)*offset,2);this.object.rotation.z=angle;this.object.scale.set(60,7,1);this.object.updateMatrix();this.wagonBorder.setMatrixAt(i,this.object.matrix);this.object.scale.set(58,5,1);this.object.updateMatrix();this.wagonMesh.setMatrixAt(i++,this.object.matrix);}}
    this.wagonMesh.count=this.wagonBorder.count=i;this.wagonMesh.instanceMatrix.needsUpdate=this.wagonBorder.instanceMatrix.needsUpdate=true;
  }
  setContext(data){
    const roads=[],waterLines=[],parks=[],water=[],bridges=[];
    const segments=(points,target)=>{for(let i=1;i<points.length;i++)target.push(...points[i-1],0,...points[i],0);};
    for(const f of data.features){
      if(f.closed&&f.points.length>=4&&f.kind!=='road'){
        const contour=f.points.slice(0,-1).map(p=>new THREE.Vector2(...p)),holes=(f.holes||[]).map(h=>h.slice(0,-1).map(p=>new THREE.Vector2(...p))),all=[...contour,...holes.flat()],target=f.kind==='water'?water:parks;
        for(const tri of THREE.ShapeUtils.triangulateShape(contour,holes))for(const i of tri)target.push(all[i].x,all[i].y,0);
      }else segments(f.points,f.kind==='water'?waterLines:roads);
      if(f.bridge||f.tunnel)segments(f.points,bridges);
    }
    const add=(points,color,line=false,opacity=1)=>{const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(points,3));const mesh=line?new THREE.LineSegments(geometry,new THREE.LineBasicMaterial({color,depthTest:false,transparent:true,opacity})):new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({color,depthTest:false,side:THREE.DoubleSide}));mesh.renderOrder=0;this.contextGroup.add(mesh);};
    this.infrastructureGroup=new THREE.Group();this.contextGroup.add(this.infrastructureGroup);this.infrastructureGroup.visible=this.mpp<8;
    const rails=[];for(const f of data.features.filter(f=>f.bridge&&!f.tunnel))for(let i=1;i<f.points.length;i++){
      const a=f.points[i-1],b=f.points[i],len=Math.hypot(b[0]-a[0],b[1]-a[1]);if(!len)continue;
      const nx=-(b[1]-a[1])/len*6,ny=(b[0]-a[0])/len*6;
      for(const side of [-1,1])rails.push(a[0]+nx*side,a[1]+ny*side,0,b[0]+nx*side,b[1]+ny*side,0);
    }
    const railGeometry=new THREE.BufferGeometry();railGeometry.setAttribute('position',new THREE.Float32BufferAttribute(rails,3));const railMesh=new THREE.LineSegments(railGeometry,new THREE.LineBasicMaterial({color:'#8394a3',depthTest:false,transparent:true,opacity:.8}));railMesh.renderOrder=3;this.infrastructureGroup.add(railMesh);
    // Only explicit OSM tunnel tags get a dashed context line; no inferred grade or turns.
    for(const f of data.features.filter(f=>f.tunnel)){const geometry=new THREE.BufferGeometry().setFromPoints(f.points.map(p=>new THREE.Vector3(...p,0)));const line=new THREE.Line(geometry,new THREE.LineDashedMaterial({color:'#7f93a3',dashSize:12,gapSize:9,depthTest:false,transparent:true,opacity:.7}));line.computeLineDistances();line.renderOrder=.5;this.infrastructureGroup.add(line);}
    add(parks,'#d4e3d8');add(water,'#c5dce8');add(roads,'#ffffff',true,.75);add(waterLines,'#b6d5e4',true,.85);add(bridges,'#c1cbd5',true,.75);
  }
  updateBuses(simulation,filter='all'){
    this.lastSimulation=simulation;const buses=simulation.buses;
    if(!this.busMesh||this.busCapacity<buses.length){
      if(this.busMesh){for(const m of [this.busMesh,this.busNose]){this.scene.remove(m);m.dispose();m.geometry.dispose();m.material.dispose();}}
      this.busCapacity=Math.max(2048,buses.length*2);
      this.busMesh=new THREE.InstancedMesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({depthTest:false}),this.busCapacity);
      this.busNose=new THREE.InstancedMesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({color:'#ffffff',depthTest:false}),this.busCapacity);
      this.busMesh.renderOrder=5;this.busNose.renderOrder=6;for(const m of [this.busMesh,this.busNose]){m.frustumCulled=false;m.instanceMatrix.setUsage(THREE.DynamicDrawUsage);this.scene.add(m);}
    }
    this.busSamples=[];let i=0;const color=new THREE.Color(),cells=new Map(),clusters=[];
    for(const b of buses){
      if(filter!=='all'&&filter!==b.routeId)continue;
      const side=Math.max(b.state==='moving'?7:3,this.mpp*(b.state==='moving'?2.5:1)),xy=[b.xy[0]+Math.sin(b.angle)*side,b.xy[1]-Math.cos(b.angle)*side];
      if(b.state==='dwell'&&!b.street){const offset=b.slot?14.5:-14.5;xy[0]+=Math.cos(b.angle)*offset;xy[1]+=Math.sin(b.angle)*offset;}
      if(b.state==='queue'){xy[0]-=Math.cos(b.angle)*24;xy[1]-=Math.sin(b.angle)*24;}
      const screen=this.worldToScreen(xy);if(screen[0]<-20||screen[0]>this.w+20||screen[1]<-20||screen[1]>this.h+20)continue;
      if(this.mpp>10&&b.id!==this.selected?.id){const key=Math.floor(screen[0]/28)+':'+Math.floor(screen[1]/28),cell=cells.get(key);if(cell){cell.count++;continue;}const c={count:1,xy,screen};cells.set(key,c);clusters.push(c);}
      this.busSamples.push({id:b.id,xy});
      const length=Math.max(b.length_m||this.data.vehicle.length_m,this.mpp*8),width=Math.max(this.data.vehicle.width_m,this.mpp*3.4);
      this.object.position.set(...xy,3);this.object.rotation.z=b.angle;this.object.scale.set(length,width,1);this.object.updateMatrix();this.busMesh.setMatrixAt(i,this.object.matrix);color.set(b.color);this.busMesh.setColorAt(i,color);
      this.object.position.set(xy[0]+Math.cos(b.angle)*length*.25,xy[1]+Math.sin(b.angle)*length*.25,3.1);this.object.scale.set(length*.16,width*.7,1);this.object.updateMatrix();this.busNose.setMatrixAt(i,this.object.matrix);i++;
    }
    if(!this.lastClusterTime||performance.now()-this.lastClusterTime>300){this.lastClusterTime=performance.now();this.clusterLayer.replaceChildren();for(const c of clusters.filter(c=>c.count>5).sort((a,b)=>b.count-a.count).slice(0,32)){const el=document.createElement('div');el.className='cluster-label';el.textContent=c.count;el.style.left=c.screen[0]+5+'px';el.style.top=c.screen[1]-16+'px';this.clusterLayer.append(el);}}
    this.visibleBuses=i;this.busMesh.count=i;this.busNose.count=i;this.busMesh.instanceMatrix.needsUpdate=true;if(this.busMesh.instanceColor)this.busMesh.instanceColor.needsUpdate=true;this.busNose.instanceMatrix.needsUpdate=true;this.updateMarker();
  }
  render(){this.renderer.render(this.scene,this.camera);}
}
