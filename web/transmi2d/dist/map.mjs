import * as THREE from './vendor/three.module.js';

export class NetworkMap {
  constructor(host, labels, data, onSelect) {
    this.host=host; this.labels=labels; this.data=data; this.onSelect=onSelect;
    this.center=[0,0]; this.mpp=30; this.selected=null; this.busSamples=[];
    this.renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
    this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));
    this.renderer.setClearColor('#e9efdf'); host.append(this.renderer.domElement);
    this.scene=new THREE.Scene();
    this.camera=new THREE.OrthographicCamera(-1,1,1,-1,.1,100); this.camera.position.z=20;
    this.paths=[];
    for(const c of data.corridors){
      const mesh=new THREE.Mesh(new THREE.BufferGeometry(),new THREE.MeshBasicMaterial({color:c.color,transparent:true,opacity:c.id.startsWith('TZ022')?.3:.67,depthTest:false}));
      mesh.renderOrder=1; this.scene.add(mesh); this.paths.push({c,mesh});
    }
    this.stopOuter=new THREE.InstancedMesh(new THREE.CircleGeometry(1,16),new THREE.MeshBasicMaterial({color:'#3a5d4a',depthTest:false}),data.stations.length);
    this.stopInner=new THREE.InstancedMesh(new THREE.CircleGeometry(1,16),new THREE.MeshBasicMaterial({color:'#fcfbf3',depthTest:false}),data.stations.length);
    this.stopOuter.renderOrder=2;this.stopInner.renderOrder=3;
    this.stopOuter.frustumCulled=false;this.stopInner.frustumCulled=false;
    this.scene.add(this.stopOuter,this.stopInner);
    this.marker=new THREE.Mesh(new THREE.RingGeometry(.7,1,24),new THREE.MeshBasicMaterial({color:'#173c30',depthTest:false}));
    this.marker.renderOrder=7;this.marker.visible=false;this.scene.add(this.marker);
    this.object=new THREE.Object3D(); this.w=1;this.h=1;
    this.resizeObserver=new ResizeObserver(()=>{this.resize();});this.resizeObserver.observe(host);
    this.resize(); this.fitNetwork(); this.bind();
  }
  fit(bounds){this.center=[(bounds[0]+bounds[2])/2,(bounds[1]+bounds[3])/2];this.mpp=Math.max((bounds[2]-bounds[0])/(this.w*.77),(bounds[3]-bounds[1])/(this.h*.77),.3);this.updateCamera();}
  fitNetwork(){this.fit(this.data.bounds);}
  fitPilot(){const p=this.data.patterns.find(p=>p.scenario==='pilot');this.fitPoints(p.points);}
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
      const vertices=[];const width=Math.max(c.id==='TZ009'?6:3.5,this.mpp*(c.id==='TZ009'?2.7:1.6));
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
    this.stopOuter.instanceMatrix.needsUpdate=true;this.stopInner.instanceMatrix.needsUpdate=true;
    }
    this.updateLabels();this.updateMarker();this.updateScale();
  }
  updateLabels(){
    this.labels.replaceChildren();const occupied=[];
    const priority=s=>['05101','05102','05103'].includes(s.id)?0:s.name.startsWith('Portal')?1:2;
    for(const s of [...this.data.stations].sort((a,b)=>priority(a)-priority(b))){
      if(this.mpp>14&&priority(s)>1)continue;
      const [x,y]=this.worldToScreen(s.xy); const width=Math.min(s.name.length*6.3+8,245), r=[x+10,y-10,x+10+width,y+12];
      if(x<0||y<85||r[2]>this.w-55||y>this.h-40||occupied.some(a=>r[0]<a[2]+5&&r[2]>a[0]-5&&r[1]<a[3]+5&&r[3]>a[1]-5))continue;
      const label=document.createElement('div');label.className='station-label';label.textContent=s.name;label.style.left=r[0]+'px';label.style.top=r[1]+'px';this.labels.append(label);occupied.push(r);
    }
  }
  updateScale(){const approx=this.mpp*100;const power=10**Math.floor(Math.log10(approx));const step=[1,2,5,10].find(n=>n*power>=approx)*power;const el=document.querySelector('#scale');el.textContent=step>=1000?(step/1000)+' km':step+' m';el.style.width=step/this.mpp+'px';}
  select(kind,id){this.selected={kind,id};this.updateMarker();}
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
  updateBuses(simulation, filter='all'){
    if(!this.busMesh||this.busCapacity<simulation.buses.length){
      if(this.busMesh){this.scene.remove(this.busMesh,this.busNose);this.busMesh.dispose();this.busNose.dispose();this.busMesh.geometry.dispose();this.busMesh.material.dispose();this.busNose.geometry.dispose();this.busNose.material.dispose();}
      this.busCapacity=Math.max(32,simulation.buses.length);
      const shape=new THREE.Shape();shape.moveTo(-.42,-.5);shape.lineTo(.3,-.5);shape.quadraticCurveTo(.5,-.5,.5,-.25);shape.lineTo(.5,.25);shape.quadraticCurveTo(.5,.5,.3,.5);shape.lineTo(-.42,.5);shape.quadraticCurveTo(-.5,.5,-.5,.35);shape.lineTo(-.5,-.35);shape.quadraticCurveTo(-.5,-.5,-.42,-.5);
      this.busMesh=new THREE.InstancedMesh(new THREE.ShapeGeometry(shape,4),new THREE.MeshBasicMaterial({depthTest:false}),this.busCapacity);
      this.busNose=new THREE.InstancedMesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({color:'#fff9df',depthTest:false}),this.busCapacity);
      this.busMesh.renderOrder=5;this.busNose.renderOrder=6;this.busMesh.frustumCulled=false;this.busNose.frustumCulled=false;
      this.busMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);this.busNose.instanceMatrix.setUsage(THREE.DynamicDrawUsage);this.scene.add(this.busMesh,this.busNose);
    }
    this.busSamples=[];let i=0;const color=new THREE.Color();
    for(const bus of simulation.buses){
      if(filter!=='all'&&filter!==bus.laneId)continue;
      const lane=simulation.lanes.get(bus.laneId),pose=lane.path.sample(bus.s);
      const side=Math.max(3,this.mpp*2.8),xy=[pose.xy[0]+Math.sin(pose.angle)*side,pose.xy[1]-Math.cos(pose.angle)*side];
      this.busSamples.push({id:bus.id,xy});
      const length=Math.max(simulation.vehicle.length_m,this.mpp*9),width=Math.max(simulation.vehicle.width_m,this.mpp*4);
      this.object.position.set(...xy,3);this.object.rotation.z=pose.angle;this.object.scale.set(length,width,1);this.object.updateMatrix();this.busMesh.setMatrixAt(i,this.object.matrix);
      color.set(bus.state==='dwell'?'#d29429':bus.state==='queue'?'#6e5440':lane.color);this.busMesh.setColorAt(i,color);
      this.object.position.set(xy[0]+Math.cos(pose.angle)*length*.23,xy[1]+Math.sin(pose.angle)*length*.23,3.1);this.object.scale.set(length*.12,width*.7,1);this.object.updateMatrix();this.busNose.setMatrixAt(i,this.object.matrix);i++;
    }
    this.busMesh.count=i;this.busNose.count=i;this.busMesh.instanceMatrix.needsUpdate=true;if(this.busMesh.instanceColor)this.busMesh.instanceColor.needsUpdate=true;this.busNose.instanceMatrix.needsUpdate=true;this.updateMarker();
  }
  render(){this.renderer.render(this.scene,this.camera);}
}
