import {metadata,categories,statuses,nodes,edges} from "./data.mjs";

const byId=new Map(nodes.map(n=>[n.id,n]));
const categoryById=new Map(categories.map(c=>[c.id,c]));
const statusById=new Map(statuses.map(s=>[s.id,s]));
const dom={
 diagram:document.getElementById("diagram"),
 links:document.getElementById("links"),
 detail:document.getElementById("detail"),
 viewport:document.getElementById("viewport"),
 filters:document.getElementById("filters"),
 legend:document.getElementById("legend"),
 search:document.getElementById("search"),
 match:document.getElementById("matchCount"),
 reset:document.getElementById("reset"),
 showEdges:document.getElementById("showEdges"),
 stats:document.getElementById("stats")
};
let selected="agent-sdk",category="all",query="",allLinks=false;
let activeStatuses=new Set(statuses.map(s=>s.id));

const escapeHtml=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const ownerNames={external:"EXT",internal:"OWN",hybrid:"MIX",policy:"POLICY"};
const ownerTitles={external:"External provider",internal:"Built by project",hybrid:"Own logic + external platform",policy:"Architecture policy"};
const svgNS="http://www.w3.org/2000/svg";
const iconMap={control:"⌘",runtime:"◉",compute:"◈",storage:"▤"};

function selectedMatch(n){
 const text=[n.title,n.provider,n.subtitle,n.detail,...n.tags].join(" ").toLocaleLowerCase("ru");
 return (category==="all"||category===n.stage)&&activeStatuses.has(n.status)&&(!query||text.includes(query));
}
function updateCounts(){
 const nums={
  total:nodes.length,
  real:nodes.filter(n=>n.status==="verified").length,
  code:nodes.filter(n=>n.status==="code").length,
  other:nodes.filter(n=>!["code","verified"].includes(n.status)).length
 };
 dom.stats.innerHTML=`
 <div class="stat"><b>${nums.total}</b><small>Components</small></div>
 <div class="stat"><b style="color:#7bdfbf">${nums.real}</b><small>Verified in environment*</small></div>
 <div class="stat"><b style="color:#8fc5ff">${nums.code}</b><small>Code / CI</small></div>
 <div class="stat"><b>${edges.length}</b><small>Relationships</small></div>`;
}
function nav(){
 dom.filters.innerHTML="";
 const options=[{id:"all",title:"All domains",icon:"◉",count:nodes.length},...categories.map(c=>({...c,icon:iconMap[c.id],count:nodes.filter(n=>n.stage===c.id).length}))];
 for(const item of options){
  const button=document.createElement("button");
  button.type="button";button.className="filter"+(category===item.id?" active":"");
  button.setAttribute("aria-pressed",category===item.id?"true":"false");
  button.innerHTML=`<span class="ficon">${item.icon}</span><span>${escapeHtml(item.title)}</span><span class="count">${item.count}</span>`;
  button.addEventListener("click",()=>{category=item.id;nav();applyFilters();});
  dom.filters.append(button);
 }
}
function legend(){
 dom.legend.innerHTML="";
 statuses.forEach(s=>{
  const el=document.createElement("button");el.type="button";
  const active=activeStatuses.has(s.id);el.className="legendItem"+(active?"":" off");
  el.setAttribute("aria-pressed",active?"true":"false");
  el.innerHTML=`<span class="legendDot" style="background:${s.color}"></span><span>${escapeHtml(s.title)}</span>`;
  el.addEventListener("click",()=>{
    if(activeStatuses.has(s.id)){
      if(activeStatuses.size===1){activeStatuses=new Set(statuses.map(x=>x.id));}
      else activeStatuses.delete(s.id);
    } else activeStatuses.add(s.id);
    legend();applyFilters();
  });
  dom.legend.append(el);
 });
}

function createDiagram(){
 for(const [i,c] of categories.entries()){
  const lane=document.createElement("section");
  lane.className="lane";lane.dataset.lane=c.id;
  lane.setAttribute("aria-label",c.title);
  lane.innerHTML=`<header class="laneHeader"><div class="laneNum">0${i+1} / SYSTEM DOMAIN</div><h3>${escapeHtml(c.title)}</h3><p>${escapeHtml(c.subtitle)}</p></header><div class="nodeList"></div>`;
  const list=lane.querySelector(".nodeList");
  for(const n of nodes.filter(n=>n.stage===c.id)){
    const status=statusById.get(n.status);
    const button=document.createElement("button");
    button.type="button";button.className="node";button.id="node-"+n.id;
    button.setAttribute("aria-label",n.title+", "+status.title);
    button.innerHTML=`
    <div class="nodeHead"><span class="nodeName">${escapeHtml(n.title)}</span><span class="statusDot" style="background:${status.color};color:${status.color}" title="${escapeHtml(status.title)}"></span></div>
    <div class="nodeSubtitle">${escapeHtml(n.subtitle)}</div>
    <div class="nodeFooter"><span class="providerTag">${escapeHtml(n.provider)}</span><span class="ownerTag ${n.owner}">${ownerNames[n.owner]}</span></div>`;
    button.addEventListener("click",()=>choose(n.id,true));
    list.append(button);
  }
  dom.diagram.append(lane);
 }
}
function createConnections(n){
 const outgoing=edges.filter(e=>e.from===n.id).map(e=>({id:e.to,label:"→ "+e.label}));
 const incoming=edges.filter(e=>e.to===n.id).map(e=>({id:e.from,label:"← "+e.label}));
 return [...outgoing,...incoming];
}
function renderDetail(){
 const n=byId.get(selected);
 if(!n){dom.detail.innerHTML='<div class="detailEmpty"><div class="glyph">⌘</div><h3>Select a component</h3></div>';return;}
 const status=statusById.get(n.status),cat=categoryById.get(n.stage);
 const related=createConnections(n);
 dom.detail.innerHTML=`
  <div class="detailOpen">
    <button id="closeDetail" type="button" class="toolButton detailClose" style="display:none;float:right" aria-label="Close details">✕</button>
    <div class="dKicker" style="color:${cat.tone}">${escapeHtml(cat.title)}</div>
    <h2>${escapeHtml(n.title)}</h2>
    <div class="metaLine">
      <span class="pillStatus"><span class="legendDot" style="background:${status.color}"></span>${escapeHtml(status.title)}</span>
      <span class="ownerTag ${n.owner}">${escapeHtml(ownerTitles[n.owner])}</span>
    </div>
    <div class="dProvider"><span>PROVIDER / TECHNOLOGY</span>${escapeHtml(n.provider)}</div>
    <p class="dDetail">${escapeHtml(n.detail)}</p>
    <div class="dSectionTitle">Mechanisms and interfaces</div>
    <div class="tags">${n.tags.map(t=>`<span class="tag">${escapeHtml(t)}</span>`).join("")}</div>
    <div class="dSectionTitle">Relationships <span style="color:#637d9a">(${related.length})</span></div>
    <div class="connections" id="connections">
      ${related.length?"":'<div style="color:#94a6bd;font-size:12px">No explicit relationships</div>'}
    </div>
    ${n.source?`<a class="dSource" href="${escapeHtml(n.source)}" target="_blank" rel="noopener noreferrer">↗ Open source / evidence</a>`:""}
  </div>`;
 const close=dom.detail.querySelector("#closeDetail");
 close?.addEventListener("click",()=>dom.detail.classList.remove("show"));
 for(const e of related){
  const target=byId.get(e.id);if(!target)continue;
  const button=document.createElement("button");button.type="button";button.className="connection";
  const title=document.createElement("b");title.textContent=target.title;
  const label=document.createElement("span");label.textContent=e.label;
  button.append(title,label);
  button.addEventListener("click",()=>choose(target.id,true));
  dom.detail.querySelector("#connections").append(button);
 }
}

let drawPending=false;
function queueLines(){
 if(drawPending)return;
 drawPending=true;
 requestAnimationFrame(()=>{drawPending=false;drawLines();});
}
function drawLines(){
 const board=dom.diagram,svg=dom.links;const box=board.getBoundingClientRect();
 if(!box.width||!box.height)return;
 const width=board.offsetWidth,height=board.offsetHeight;
 svg.setAttribute("viewBox",`0 0 ${width} ${height}`);
 svg.setAttribute("width",String(width));svg.setAttribute("height",String(height));
 svg.replaceChildren();
 const list=edges.filter(e=>allLinks||e.from===selected||e.to===selected);
 for(const e of list){
   const from=byId.get(e.from),to=byId.get(e.to);
   const a=document.getElementById("node-"+e.from),b=document.getElementById("node-"+e.to);
   if(!a||!b)continue;
   if(!selectedMatch(from)||!selectedMatch(to))continue;
   const ra=a.getBoundingClientRect(),rb=b.getBoundingClientRect();
   const isFocused=e.from===selected||e.to===selected;
   const rightwards=ra.left<rb.left;
   const sameLane=from.stage===to.stage;
   let x1,x2,y1=ra.top-box.top+ra.height/2,y2=rb.top-box.top+rb.height/2;
   if(sameLane){x1=ra.right-box.left-10;x2=rb.right-box.left-10;}
   else if(rightwards){x1=ra.right-box.left-4;x2=rb.left-box.left+4;}
   else{x1=ra.left-box.left+4;x2=rb.right-box.left-4;}
   const drift=sameLane?Math.min(62,30+Math.abs(y2-y1)*.06):Math.max(38,Math.abs(x2-x1)*.42);
   const c1x=x1+(sameLane?drift:(rightwards?drift:-drift));
   const c2x=x2+(sameLane?drift:(rightwards?-drift:drift));
   const path=document.createElementNS(svgNS,"path");
   path.setAttribute("d",`M ${x1.toFixed(1)} ${y1.toFixed(1)} C ${c1x.toFixed(1)} ${y1.toFixed(1)}, ${c2x.toFixed(1)} ${y2.toFixed(1)}, ${x2.toFixed(1)} ${y2.toFixed(1)}`);
   path.setAttribute("fill","none");
   path.setAttribute("stroke",isFocused?"#a1caff":"#537395");
   path.setAttribute("stroke-width",isFocused?"1.8":"1");
   path.setAttribute("opacity",isFocused?"0.76":"0.13");
   if(!isFocused)path.setAttribute("stroke-dasharray","3 5");
   svg.append(path);
 }
}
function applyFilters(){
 let count=0;
 for(const n of nodes){
  const el=document.getElementById("node-"+n.id);
  const pass=selectedMatch(n);if(pass)count++;
  if(el)el.classList.toggle("dimmed",!pass);
  if(el)el.classList.toggle("active",selected===n.id);
 }
 dom.match.textContent=`${count} of ${nodes.length} components · ${allLinks?"all":"links to selected node"}`;
 dom.showEdges.setAttribute("aria-pressed",allLinks?"true":"false");
 dom.showEdges.classList.toggle("active",allLinks);
 queueLines();
}

function centerNode(id){
 const el=document.getElementById("node-"+id);if(!el)return;
 const v=dom.viewport,ev=el.getBoundingClientRect(),vr=v.getBoundingClientRect();
 v.scrollTo({left:Math.max(0,v.scrollLeft+(ev.left-vr.left)-v.clientWidth/2+ev.width/2),
             top:Math.max(0,v.scrollTop+(ev.top-vr.top)-v.clientHeight/2+ev.height/2),
             behavior:window.matchMedia("(prefers-reduced-motion: reduce)").matches?"instant":"smooth"});
}
function choose(id,center=false){
 if(!byId.has(id))return;
 selected=id;renderDetail();applyFilters();
 if(center)centerNode(id);
 if(window.matchMedia("(max-width: 1150px)").matches)dom.detail.classList.add("show");
}
function reset(){
 category="all";query="";dom.search.value="";selected="agent-sdk";
 activeStatuses=new Set(statuses.map(s=>s.id));allLinks=false;
 nav();legend();renderDetail();applyFilters();
 dom.detail.classList.remove("show");
 dom.viewport.scrollTo({left:0,top:0,behavior:"smooth"});
}

updateCounts();createDiagram();nav();legend();choose(selected);
dom.search.addEventListener("input",e=>{query=e.target.value.trim().toLocaleLowerCase("ru");applyFilters();});
dom.reset.addEventListener("click",reset);
dom.showEdges.addEventListener("click",()=>{allLinks=!allLinks;applyFilters();});
window.addEventListener("resize",queueLines,{passive:true});
document.fonts?.ready.then(queueLines).catch(()=>{});
window.addEventListener("keydown",e=>{
 if(e.key==="/"&&document.activeElement?.tagName!=="INPUT"){e.preventDefault();dom.search.focus();}
 if(e.key==="Escape"){dom.detail.classList.remove("show");if(document.activeElement===dom.search){dom.search.blur();}}
});
