/* ============================================================
   Shiva Portal — Project Map (interactive linked canvas)
   A pan/zoom node-graph of the whole project structure, themed
   to match the portal. window.initCanvas() boots it into the
   markup that viewCanvas() injects.
   ============================================================ */
(function(){
const DOC="https://github.com/rudraxdevelopment98-cell/shiva/blob/claude/dazzling-galileo-j9yt04/docs/";
const CLR={root:"#8b5cf6",phase:"#6d5efc",build:"#22d3ee",hosted:"#34d399",threat:"#fb7185",platform:"#a855f7",cat:"#7c89b0"};

// id, x, y, category(color), title, sub, icon, details[], doc
const NODES=[
  {id:"root",x:200,y:1040,c:"root",t:"SHIVA",s:"MCP security",ic:"☩",big:1,
    d:["Own the detection + policy layer where AI agents meet their tools.","Open-source first, hosted product later."],doc:"overview/"},

  // categories
  {id:"cJourney",x:560,y:360,c:"cat",t:"Journey",s:"4 phases",ic:"◎",doc:"roadmap/"},
  {id:"cBuild",x:560,y:820,c:"cat",t:"What we build",s:"the product",ic:"🏗",doc:"architecture/"},
  {id:"cThreat",x:560,y:1340,c:"cat",t:"Threats",s:"what we defend",ic:"🛡",doc:"threat-model/"},
  {id:"cPlat",x:560,y:1740,c:"cat",t:"Platform",s:"this portal",ic:"🖥",doc:"platform/"},

  // journey
  {id:"p0",x:1000,y:200,c:"phase",t:"Phase 0",s:"Learn + Break · Wk 0-6",ic:"🧪",
    d:["Stand up MCP; reproduce 3 core attacks.","Publish a write-up per attack."],doc:"roadmap/"},
  {id:"p1",x:1000,y:360,c:"phase",t:"Phase 1",s:"OSS Scanner · M1-4",ic:"🔍",
    d:["Static analysis of MCP manifests → risk report.","CLI + CI check."],doc:"roadmap/"},
  {id:"p2",x:1000,y:520,c:"phase",t:"Phase 2",s:"Gateway · M4-10",ic:"🚦",
    d:["Runtime proxy: log, allowlist, block drift.","The SOC pipeline — your edge."],doc:"architecture/"},
  {id:"p3",x:1000,y:680,c:"phase",t:"Phase 3",s:"Hosted · M10-18",ic:"🏛",
    d:["Registry, central policy, compliance.","The part enterprises pay for."],doc:"roadmap/"},

  // build
  {id:"range",x:1000,y:830,c:"build",t:"Attack Range",s:"benchmark",ic:"🎯",
    d:["Library of malicious servers.","Hero give-first asset + leaderboard."],doc:"improvements/"},
  {id:"scanner",x:1000,y:960,c:"build",t:"Scanner",s:"static · OSS",ic:"🔍",doc:"architecture/",
    d:["Catches poisoning before trust."]},
  {id:"gateway",x:1000,y:1090,c:"build",t:"Gateway",s:"runtime · OSS",ic:"🚦",doc:"architecture/",
    d:["Logs + allowlists + blocks at runtime."]},
  {id:"registry",x:1480,y:830,c:"hosted",t:"Registry",s:"hosted",ic:"📒",doc:"architecture/",d:["Server reputation scoring."]},
  {id:"policy",x:1480,y:960,c:"hosted",t:"Central Policy",s:"hosted",ic:"⚙",doc:"architecture/",d:["Policy across many agents/teams."]},
  {id:"comp",x:1480,y:1090,c:"hosted",t:"Compliance",s:"hosted",ic:"📑",doc:"architecture/",d:["NIST · EU AI Act reporting."]},

  // threats
  {id:"poison",x:1000,y:1240,c:"threat",t:"Tool Poisoning",s:"attack #1",ic:"①",doc:"threat-model/",
    d:["Hidden instructions inside tool metadata."]},
  {id:"drift",x:1000,y:1360,c:"threat",t:"Drift / Rug-pull",s:"attack #2",ic:"②",doc:"threat-model/",
    d:["Description changes after trust is granted."]},
  {id:"cross",x:1000,y:1480,c:"threat",t:"Cross-tool Esc.",s:"attack #3",ic:"③",doc:"threat-model/",
    d:["One tool's output steers the next call."]},
  {id:"cred",x:1000,y:1600,c:"threat",t:"Credential Theft",s:"exfiltration",ic:"⑤",doc:"threat-model/",
    d:["Servers holding OAuth tokens get drained."]},

  // platform
  {id:"auth",x:1000,y:1700,c:"platform",t:"Auth",s:"sign in",ic:"🔐",doc:"platform/",d:["Username + password login."]},
  {id:"rbac",x:1000,y:1820,c:"platform",t:"Access Control",s:"roles + grants",ic:"🛡",doc:"platform/",
    d:["Owner · Admin · Manager · Member · Viewer.","Per-section access."]},
  {id:"admin",x:1000,y:1940,c:"platform",t:"Admin",s:"users + audit",ic:"⚙",doc:"platform/",d:["Create users, assign roles."]},
];
const EDGES=[
  ["root","cJourney"],["root","cBuild"],["root","cThreat"],["root","cPlat"],
  ["cJourney","p0"],["cJourney","p1"],["cJourney","p2"],["cJourney","p3"],
  ["cBuild","range"],["cBuild","scanner"],["cBuild","gateway"],
  ["range","scanner"],["range","gateway"],["scanner","registry"],["gateway","policy"],["registry","policy"],["policy","comp"],
  ["cThreat","poison"],["cThreat","drift"],["cThreat","cross"],["cThreat","cred"],
  ["cPlat","auth"],["cPlat","rbac"],["cPlat","admin"],["auth","rbac"],["rbac","admin"],
];

let cam={x:0,y:0,z:1},adj={};
window.initCanvas=function(){
  const stage=document.getElementById("cvstage"),svg=document.getElementById("cvedges"),vp=document.getElementById("cvvp");
  if(!stage)return;
  stage.querySelectorAll(".cv-node").forEach(n=>n.remove());svg.innerHTML="";adj={};
  NODES.forEach(n=>adj[n.id]=new Set());
  EDGES.forEach(([a,b])=>{const na=NODES.find(n=>n.id===a),nb=NODES.find(n=>n.id===b);if(!na||!nb)return;
    adj[a].add(b);adj[b].add(a);
    const p=document.createElementNS("http://www.w3.org/2000/svg","path");
    const mx=(na.x+nb.x)/2,my=(na.y+nb.y)/2,dx=nb.x-na.x,dy=nb.y-na.y;
    p.setAttribute("d",`M ${na.x} ${na.y} C ${mx} ${na.y}, ${mx} ${nb.y}, ${nb.x} ${nb.y}`);
    p.setAttribute("class","cv-edge");p.dataset.a=a;p.dataset.b=b;svg.appendChild(p);});
  NODES.forEach(n=>{const d=document.createElement("div");d.className="cv-node"+(n.big?" big":"");
    d.style.setProperty("--clr",CLR[n.c]);d.style.left=n.x+"px";d.style.top=n.y+"px";d.dataset.id=n.id;
    d.innerHTML=`<div class="t"><span class="ic">${n.ic}</span>${n.t}</div>${n.s?`<div class="s">${n.s}</div>`:""}`;
    d.onmouseenter=()=>focus(n.id);d.onmouseleave=()=>{if(!sel)unfocus()};
    d.onclick=e=>{e.stopPropagation();openDetail(n)};stage.appendChild(d);});
  vp.onmousedown=e=>{drag=true;vp.classList.add("grab");sx=e.clientX;sy=e.clientY;c0={...cam}};
  window.addEventListener("mousemove",mv);window.addEventListener("mouseup",()=>{drag=false;vp.classList.remove("grab")});
  vp.onclick=e=>{if(e.target===vp||e.target===stage||e.target===svg)closeDetail()};
  vp.onwheel=e=>{e.preventDefault();const r=vp.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;
    const wx=(mx-cam.x)/cam.z,wy=(my-cam.y)/cam.z;cam.z=Math.max(.3,Math.min(2,cam.z*(e.deltaY<0?1.12:.89)));
    cam.x=mx-wx*cam.z;cam.y=my-wy*cam.z;apply()};
  fit();
};
let drag=false,sx,sy,c0,sel=null;
function mv(e){if(!drag)return;cam.x=c0.x+(e.clientX-sx);cam.y=c0.y+(e.clientY-sy);apply()}
function apply(){const s=document.getElementById("cvstage");if(s)s.style.transform=`translate(${cam.x}px,${cam.y}px) scale(${cam.z})`}
function fit(){const vp=document.getElementById("cvvp");if(!vp)return;let a=1e9,b=1e9,c=-1e9,d=-1e9;
  NODES.forEach(n=>{a=Math.min(a,n.x);b=Math.min(b,n.y);c=Math.max(c,n.x);d=Math.max(d,n.y)});
  const pad=140;a-=pad;b-=pad;c+=pad;d+=pad;const w=c-a,h=d-b,W=vp.clientWidth,H=vp.clientHeight;
  cam.z=Math.min(W/w,H/h,1);cam.x=(W-w*cam.z)/2-a*cam.z;cam.y=(H-h*cam.z)/2-b*cam.z;apply()}
window.cvFit=fit;
window.cvZoom=function(f){const vp=document.getElementById("cvvp");const W=vp.clientWidth/2,H=vp.clientHeight/2;
  const wx=(W-cam.x)/cam.z,wy=(H-cam.y)/cam.z;cam.z=Math.max(.3,Math.min(2,cam.z*f));cam.x=W-wx*cam.z;cam.y=H-wy*cam.z;apply()};
function focus(id){document.querySelectorAll(".cv-edge").forEach(e=>{const on=e.dataset.a===id||e.dataset.b===id;
    e.classList.toggle("hl",on);e.classList.toggle("dim",!on)});
  document.querySelectorAll(".cv-node").forEach(n=>n.classList.toggle("dim",n.dataset.id!==id&&!adj[id]?.has(n.dataset.id)))}
function unfocus(){document.querySelectorAll(".cv-edge").forEach(e=>e.classList.remove("hl","dim"));
  document.querySelectorAll(".cv-node").forEach(n=>n.classList.remove("dim"))}
function openDetail(n){sel=n.id;focus(n.id);
  document.querySelectorAll(".cv-node").forEach(e=>e.classList.toggle("sel",e.dataset.id===n.id));
  const p=document.getElementById("cvpanel");p.style.setProperty("--clr",CLR[n.c]);
  p.innerHTML=`<div class="cvp-x" onclick="cvCloseDetail()">✕</div>
    <div class="cvp-h"><span class="cvp-ic" style="background:${CLR[n.c]}">${n.ic}</span><div><b>${n.t}</b><div class="cvp-s">${n.s||""}</div></div></div>
    ${n.d?`<ul>${n.d.map(x=>`<li>${x}</li>`).join("")}</ul>`:""}
    ${n.doc?`<a href="${DOC}${n.doc}" target="_blank">Open full write-up ↗</a>`:""}`;
  p.classList.add("open")}
window.cvCloseDetail=function(){sel=null;unfocus();const p=document.getElementById("cvpanel");if(p)p.classList.remove("open");
  document.querySelectorAll(".cv-node").forEach(e=>e.classList.remove("sel"))};
})();
