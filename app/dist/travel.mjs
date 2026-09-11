/** Distance-domain speed envelope: actual metres, acceleration, braking and bend limits. */
export function travelProfile(path,from,to,limit,a=.8,b=1.1){
 const distance=Math.max(0,to-from),n=Math.max(2,Math.ceil(distance/18)),s=new Float64Array(n+1),v=new Float64Array(n+1),times=new Float64Array(n+1);
 for(let i=0;i<=n;i++){
  s[i]=distance*i/n;const pos=from+s[i],p=path.sample(Math.max(0,pos-12)).xy,q=path.sample(pos).xy,r=path.sample(Math.min(path.length,pos+12)).xy;
  const u=[q[0]-p[0],q[1]-p[1]],w=[r[0]-q[0],r[1]-q[1]],ul=Math.hypot(...u),wl=Math.hypot(...w);
  const angle=ul>1&&wl>1?Math.acos(Math.max(-1,Math.min(1,(u[0]*w[0]+u[1]*w[1])/ul/wl))):0;
  const radius=angle>.04?Math.min(ul,wl)/angle:Infinity;
  v[i]=Math.min(limit,Math.max(3,Math.sqrt(1.15*radius)));
 }
 v[0]=0;v[n]=0;
 for(let i=1;i<=n;i++)v[i]=Math.min(v[i],Math.sqrt(v[i-1]**2+2*a*(s[i]-s[i-1])));
 for(let i=n-1;i>=0;i--)v[i]=Math.min(v[i],Math.sqrt(v[i+1]**2+2*b*(s[i+1]-s[i])));
 for(let i=1;i<=n;i++)times[i]=times[i-1]+2*(s[i]-s[i-1])/Math.max(.01,v[i]+v[i-1]);
 return {distance,duration:times[n],s,v,times};
}
export function travelAt(profile,time){
 const t=Math.min(profile.duration,Math.max(0,time));let lo=1,hi=profile.times.length-1;while(lo<hi){const mid=(lo+hi)>>1;if(profile.times[mid]<t)lo=mid+1;else hi=mid;}
 const i=lo,dt=t-profile.times[i-1],span=profile.times[i]-profile.times[i-1],a=span?(profile.v[i]-profile.v[i-1])/span:0;
 return {s:Math.min(profile.distance,profile.s[i-1]+profile.v[i-1]*dt+.5*a*dt*dt),speed:Math.max(0,profile.v[i-1]+a*dt)};
}
