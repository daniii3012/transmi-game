// Shared desktop/mobile chrome. The map always keeps the full viewport.
export function mountShell(){
 const body=document.body,sidebar=document.querySelector('#sidebar');
 const toggle=document.createElement('button');toggle.id='panel-toggle';toggle.type='button';toggle.setAttribute('aria-expanded','true');toggle.textContent='Red y rutas';sidebar.prepend(toggle);
 const more=document.createElement('details');more.id='more-menu';
 const summary=document.createElement('summary');summary.textContent='Más';summary.setAttribute('aria-label','Más opciones');more.append(summary);
 const menu=document.createElement('div');menu.className='more-options';more.append(menu);
 for(const button of document.querySelectorAll('[data-panel="depots"],[data-panel="settings"],[data-panel="data"],[data-panel="sources"]'))menu.append(button);
 document.querySelector('nav').append(more);
 const dateButton=document.createElement('button');dateButton.textContent='Fecha del escenario';dateButton.className='mobile-date';dateButton.type='button';menu.append(dateButton);
 dateButton.addEventListener('click',()=>{body.classList.toggle('time-expanded');more.open=false;});
 let expanded=true;
 const setExpanded=value=>{expanded=value;body.dataset.sheet=value?'open':'closed';toggle.setAttribute('aria-expanded',String(value));};
 toggle.addEventListener('click',()=>setExpanded(!expanded));
 const inspector=document.querySelector('#inspector');
 new MutationObserver(()=>{body.dataset.inspect=String(!inspector.hidden);}).observe(inspector,{attributes:true,attributeFilter:['hidden']});
 document.addEventListener('click',e=>{if(!more.contains(e.target))more.open=false;});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){more.open=false;if(!inspector.hidden)document.querySelector('#close-inspector')?.click();else setExpanded(false);}});
 setExpanded(true);body.dataset.panel='routes';
 return {show(name){body.dataset.panel=name;toggle.textContent=document.querySelector(`button[data-panel="${name}"]`)?.textContent||'Explorar';more.open=false;setExpanded(true);}};
}
