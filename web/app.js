/* ============================================================
   Shiva Portal — client-side prototype (localStorage backed)
   Sections: Dashboard · Project · Tasks · Documents · Research
             · Activity · Admin (users/roles) · Profile
   NOTE: data is stored in THIS browser. For real multi-user across
   devices, connect a backend (Supabase) — see docs/platform.md.
   ============================================================ */
const DB_KEY="shiva_portal_v1";
const SECTIONS=[
  {id:"dashboard",label:"Dashboard",ic:"▦"},
  {id:"project",label:"Project Roadmap",ic:"◎"},
  {id:"tasks",label:"Tasks",ic:"✓"},
  {id:"documents",label:"Documents",ic:"▤"},
  {id:"research",label:"Research",ic:"⌕"},
  {id:"activity",label:"Activity",ic:"≣"},
  {id:"admin",label:"Admin · Users",ic:"⚙"},
  {id:"profile",label:"My Profile",ic:"◍"},
];
const ROLES={
  Owner:    {all:true},
  Admin:    {access:["dashboard","project","tasks","documents","research","activity","admin","profile"]},
  Manager:  {access:["dashboard","project","tasks","documents","research","activity","profile"]},
  Member:   {access:["dashboard","project","tasks","documents","research","profile"]},
  Viewer:   {access:["dashboard","project","documents","research","profile"]},
};
const AV_COLORS=["#4f46e5","#0891b2","#7c3aed","#db2777","#ea580c","#16a34a","#2563eb","#9333ea"];

/* ---------- storage ---------- */
let DB=load();
function load(){try{return JSON.parse(localStorage.getItem(DB_KEY))||seed()}catch(e){return seed()}}
function save(){localStorage.setItem(DB_KEY,JSON.stringify(DB))}
function seed(){
  const now=Date.now();
  const db={users:[{id:uid(),name:"Kuldeep",username:"kuldeep",password:"Shiva@2026",role:"Owner",
      access:SECTIONS.map(s=>s.id),status:"Active",created:now}],
    tasks:[
      {id:uid(),title:"Install MCP SDKs (Python + TypeScript)",desc:"Day 1 of Phase 0",assignee:"kuldeep",
        due:date(+1),priority:"High",status:"To do",created:now},
      {id:uid(),title:"Build first MCP server (read_file tool)",desc:"Day 2 of Phase 0",assignee:"kuldeep",
        due:date(+2),priority:"High",status:"To do",created:now},
      {id:uid(),title:"Reproduce tool poisoning (attack #1)",desc:"Day 3 — the key demo",assignee:"kuldeep",
        due:date(+3),priority:"Critical",status:"To do",created:now},
    ],
    docs:[],
    research:[
      {id:uid(),title:"Simon Willison — MCP prompt injection",url:"https://simonwillison.net/tags/model-context-protocol/",
        category:"Reference",note:"Core read on why MCP has injection problems.",by:"kuldeep",date:now},
    ],
    activity:[{id:uid(),user:"system",action:"Portal initialised",time:now}],
    session:null,firstRun:true};
  localStorage.setItem(DB_KEY,JSON.stringify(db));return db;
}
function reseedConfirm(){if(confirm("Reset ALL portal data (users, tasks, documents)? This cannot be undone.")){
  localStorage.removeItem(DB_KEY);location.reload();}}

/* ---------- helpers ---------- */
function uid(){return Math.random().toString(36).slice(2,10)}
function date(off){const d=new Date();d.setDate(d.getDate()+(off||0));return d.toISOString().slice(0,10)}
function fmt(ts){const d=new Date(ts);return d.toLocaleDateString(undefined,{day:"numeric",month:"short"})+" "+d.toLocaleTimeString(undefined,{hour:"2-digit",minute:"2-digit"})}
function esc(s){return(s==null?"":String(s)).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function avatarColor(name){let h=0;for(const c of name)h=(h*31+c.charCodeAt(0))%AV_COLORS.length;return AV_COLORS[h]}
function initials(name){return name.split(/\s+/).map(w=>w[0]).join("").slice(0,2).toUpperCase()}
function me(){return DB.users.find(u=>u.username===DB.session)}
function can(sec){const u=me();return u&&u.access.includes(sec)}
function logAct(action){DB.activity.unshift({id:uid(),user:DB.session||"?",action,time:Date.now()});
  DB.activity=DB.activity.slice(0,200);save()}
function genUsername(name){let base=name.trim().split(/\s+/)[0].toLowerCase().replace(/[^a-z]/g,"")||"user";
  let u=base;let n=1;while(DB.users.some(x=>x.username===u)){u=base+n;n++}return u}
function genPassword(){const U="ABCDEFGHJKLMNPQRSTUVWXYZ",l="abcdefghijkmnpqrstuvwxyz",d="23456789",s="!@#$%&*";
  const pick=set=>set[Math.floor(Math.random()*set.length)];let p=[pick(U),pick(U),pick(l),pick(l),pick(l),pick(d),pick(d),pick(d),pick(s),pick(s)];
  for(let i=p.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[p[i],p[j]]=[p[j],p[i]]}return p.join("")}

/* ---------- auth ---------- */
function doLogin(){
  const u=document.getElementById("li-user").value.trim();
  const p=document.getElementById("li-pass").value;
  const found=DB.users.find(x=>x.username===u&&x.password===p);
  const err=document.getElementById("li-err");
  if(!found){err.textContent="Invalid username or password.";return}
  if(found.status!=="Active"){err.textContent="This account is deactivated.";return}
  DB.session=found.username;DB.firstRun=false;save();logAct("Signed in");
  boot();
}
function logout(){logAct("Signed out");DB.session=null;save();boot()}

/* ---------- boot / render shell ---------- */
let route="dashboard";
function boot(){
  const u=me();
  if(!u){document.getElementById("login").classList.remove("hidden");document.getElementById("app").style.display="none";
    const hint=document.getElementById("li-hint");hint.style.display=DB.firstRun?"block":"none";return}
  document.getElementById("login").classList.add("hidden");
  document.getElementById("app").style.display="block";
  if(!can(route))route="dashboard";
  renderShell();renderRoute();
}
function go(r){if(!can(r))return;route=r;renderRoute();
  document.querySelectorAll(".side a.nav").forEach(a=>a.classList.toggle("active",a.dataset.r===r));}

function renderShell(){
  const u=me();
  const nav=SECTIONS.filter(s=>u.access.includes(s.id));
  const main=nav.filter(s=>!["admin","profile"].includes(s.id));
  const sys=nav.filter(s=>["admin","profile"].includes(s.id));
  const myTasks=DB.tasks.filter(t=>t.assignee===u.username&&t.status!=="Done").length;
  const item=s=>`<a class="nav ${s.id===route?'active':''}" data-r="${s.id}" onclick="go('${s.id}')">
     <span class="ic">${s.ic}</span>${s.label}${s.id==='tasks'&&myTasks?`<span class="count">${myTasks}</span>`:''}</a>`;
  document.getElementById("app").innerHTML=`<div class="shell">
   <aside class="side">
     <div class="brand"><div class="l">☩</div><div><b>SHIVA</b><small>PROJECT PORTAL</small></div></div>
     <nav>
       <div class="navlbl">WORKSPACE</div>${main.map(item).join("")}
       ${sys.length?`<div class="navlbl">ACCOUNT</div>${sys.map(item).join("")}`:""}
     </nav>
     <div class="me">
       <div class="av" style="background:${avatarColor(u.name)}">${initials(u.name)}</div>
       <div style="flex:1;min-width:0"><div class="nm">${esc(u.name)}</div><div class="rl">${u.role}</div></div>
       <button class="btn ghost sm" title="Sign out" onclick="logout()" style="color:#94a3b8">⎋</button>
     </div>
   </aside>
   <main class="main">
     <div class="topbar">
       <div class="crumb">Shiva / <b id="crumb">Dashboard</b></div>
       <div class="search"><input placeholder="Search…" oninput="quickSearch(this.value)"></div>
       <div class="iconbtn" title="Reset demo data" onclick="reseedConfirm()">⟳</div>
     </div>
     <div class="content" id="content"></div>
   </main></div>`;
}
function renderRoute(){
  const map={dashboard:viewDashboard,project:viewProject,tasks:viewTasks,documents:viewDocuments,
    research:viewResearch,activity:viewActivity,admin:viewAdmin,profile:viewProfile};
  const sec=SECTIONS.find(s=>s.id===route);
  document.getElementById("crumb").textContent=sec?sec.label:"Dashboard";
  document.getElementById("content").innerHTML=(map[route]||viewDashboard)();
}
function quickSearch(q){if(route!=="tasks"&&route!=="documents"&&route!=="admin")return;
  const t=q.toLowerCase();document.querySelectorAll("[data-srch]").forEach(el=>{
    el.style.display=el.dataset.srch.toLowerCase().includes(t)?"":"none"})}

/* ============ VIEWS ============ */
function viewDashboard(){
  const u=me();
  const myTasks=DB.tasks.filter(t=>t.assignee===u.username);
  const myDone=myTasks.filter(t=>t.status==="Done").length;
  const allDone=DB.tasks.filter(t=>t.status==="Done").length;
  const prog=DB.tasks.length?Math.round(allDone/DB.tasks.length*100):0;
  const stat=(ic,bg,v,l,sub,sc)=>`<div class="stat"><div class="ic" style="background:${bg.s};color:${bg.c}">${ic}</div>
    <div class="v">${v}</div><div class="l">${l}</div>${sub?`<div class="sub" style="color:${sc||'var(--muted)'}">${sub}</div>`:''}</div>`;
  const todays=myTasks.filter(t=>t.status!=="Done").slice(0,5);
  return `<div class="page-h"><div><h1>Welcome back, ${esc(u.name.split(" ")[0])}</h1>
     <p>Here's what's happening across the Shiva project today.</p></div></div>
   <div class="grid c4" style="margin-bottom:16px">
     ${stat("✓",{s:"var(--primary-soft)",c:"var(--primary)"},myDone+"/"+myTasks.length,"My tasks done")}
     ${stat("◷",{s:"var(--amber-soft)",c:"var(--amber)"},myTasks.length-myDone,"My open tasks")}
     ${stat("◎",{s:"var(--blue-soft)",c:"var(--blue)"},"Phase 0","Current phase","Learn + Break","var(--blue)")}
     ${stat("◭",{s:"var(--green-soft)",c:"var(--green)"},DB.users.length,"Team members")}
   </div>
   <div class="grid c3">
     <div class="card" style="grid-column:span 2">
       <div class="hd"><h3>My tasks today</h3><div class="actions">${can('tasks')?`<button class="btn sm" onclick="go('tasks')">View all</button>`:''}</div></div>
       <div class="bd">${todays.length?`<div class="tlist">${todays.map(taskRow).join("")}</div>`:emptyState("✓","No open tasks. You're all caught up.")}</div>
     </div>
     <div class="card">
       <div class="hd"><h3>Overall progress</h3></div>
       <div class="bd">
         <div style="font-size:30px;font-weight:700">${prog}%</div>
         <div class="l" style="color:var(--muted);margin:2px 0 12px">${allDone} of ${DB.tasks.length} tasks complete</div>
         <div class="pbar"><i style="width:${prog}%"></i></div>
         <div style="margin-top:18px" class="navlbl-x"></div>
         ${miniRoadmap()}
       </div>
     </div>
   </div>
   <div class="card" style="margin-top:16px">
     <div class="hd"><h3>Recent activity</h3>${can('activity')?`<div class="actions"><button class="btn sm" onclick="go('activity')">All activity</button></div>`:''}</div>
     <div class="bd" style="padding-top:6px">${activityList(DB.activity.slice(0,6))}</div>
   </div>`;
}
function miniRoadmap(){
  const phases=[["P0","Phase 0","active"],["P1","Phase 1",""],["P2","Phase 2",""],["P3","Phase 3",""]];
  return `<div style="display:flex;gap:8px;margin-top:8px">${phases.map(p=>`
    <div style="flex:1;text-align:center">
      <div style="height:6px;border-radius:99px;background:${p[2]==='active'?'var(--primary)':'#eef1f6'}"></div>
      <div style="font-size:10.5px;color:var(--muted);margin-top:6px;font-weight:600">${p[1]}</div>
    </div>`).join("")}</div>`;
}
function taskRow(t){
  const done=t.status==="Done";
  const pr={Critical:"red",High:"amber",Medium:"blue",Low:"grey"}[t.priority]||"grey";
  return `<div class="titem ${done?'done':''}">
    <div class="cb ${done?'on':''}" onclick="toggleTask('${t.id}')">${done?'✓':''}</div>
    <div style="flex:1;min-width:0"><div class="tt">${esc(t.title)}</div>
      <div class="meta">Due ${t.due} · <span class="badge ${pr}" style="padding:1px 7px">${t.priority}</span></div></div>
    <div class="userc"><div class="avatar" style="width:26px;height:26px;background:${avatarColor(assigneeName(t.assignee))}">${initials(assigneeName(t.assignee))}</div></div>
  </div>`;
}
function assigneeName(un){const u=DB.users.find(x=>x.username===un);return u?u.name:un}

function viewProject(){
  const steps=[["1","Phase 0","Learn + Break · Wk 0-6","active"],["2","Phase 1","OSS Scanner · M1-4",""],
    ["3","Phase 2","Runtime Gateway · M4-10",""],["4","Phase 3","Hosted Layer · M10-18",""]];
  const docs=[["Roadmap","roadmap/"],["Architecture","architecture/"],["Threat model","threat-model/"],
    ["Platform / RBAC","platform/"],["Improvements","improvements/"]];
  const DOC="https://github.com/rudraxdevelopment98-cell/shiva/blob/claude/dazzling-galileo-j9yt04/docs/";
  return `<div class="page-h"><div><h1>Project Roadmap</h1><p>The 18-month plan, by phase, with decision gates.</p></div></div>
   <div class="card"><div class="bd" style="padding:30px 26px">
     <div class="stepper">${steps.map(s=>`<div class="step ${s[3]}">
       <div class="dot">${s[3]==='done'?'✓':s[0]}</div><div class="t">${s[1]}</div><div class="s">${s[2]}</div></div>`).join("")}</div>
   </div></div>
   <div class="grid c2" style="margin-top:16px">
     <div class="card"><div class="hd"><h3>Phase 0 — current focus</h3><span class="badge amber">In progress</span></div>
       <div class="bd"><ul style="margin:0;padding-left:18px;line-height:1.9;color:#334155">
         <li>Stand up MCP locally; build your own servers + client.</li>
         <li>Reproduce tool poisoning, drift/rug-pull, cross-tool escalation.</li>
         <li>Publish a write-up per attack — learning + credibility.</li>
       </ul></div></div>
     <div class="card"><div class="hd"><h3>Reference documents</h3></div>
       <div class="bd"><div class="tlist">${docs.map(d=>`<div class="titem">
         <div style="flex:1"><div class="tt">${d[0]}</div><div class="meta">Markdown · GitHub</div></div>
         <a class="btn sm" href="${DOC}${d[1]}" target="_blank">Open ↗</a></div>`).join("")}</div></div></div>
   </div>`;
}

function viewTasks(){
  const u=me();const canAssign=["Owner","Admin","Manager"].includes(u.role);
  const cols=[["To do","grey"],["In progress","blue"],["Done","green"]];
  const list=DB.tasks.slice().sort((a,b)=>a.due.localeCompare(b.due));
  return `<div class="page-h"><div><h1>Tasks</h1><p>Daily task allocation and tracking.</p></div>
     <div class="actions">${canAssign?`<button class="btn primary" onclick="openTaskModal()">+ New task</button>`:''}</div></div>
   <div class="grid c3" style="margin-bottom:16px">${cols.map(c=>{const n=DB.tasks.filter(t=>t.status===c[0]).length;
     return `<div class="stat"><div class="v">${n}</div><div class="l">${c[0]}</div>
       <div class="pbar" style="margin-top:10px"><i style="width:${DB.tasks.length?n/DB.tasks.length*100:0}%"></i></div></div>`}).join("")}</div>
   <div class="card"><table class="tbl"><thead><tr><th>Task</th><th>Assignee</th><th>Due</th><th>Priority</th><th>Status</th><th></th></tr></thead>
   <tbody>${list.map(t=>{
     const pr={Critical:"red",High:"amber",Medium:"blue",Low:"grey"}[t.priority]||"grey";
     const st={["To do"]:"grey",["In progress"]:"blue",Done:"green"}[t.status];
     return `<tr data-srch="${esc(t.title)} ${esc(assigneeName(t.assignee))}">
       <td><div class="tt" style="font-weight:600">${esc(t.title)}</div><div class="meta" style="color:var(--muted);font-size:12px">${esc(t.desc||"")}</div></td>
       <td><div class="userc"><div class="avatar" style="background:${avatarColor(assigneeName(t.assignee))}">${initials(assigneeName(t.assignee))}</div><span class="nm">${esc(assigneeName(t.assignee))}</span></div></td>
       <td>${t.due}</td><td><span class="badge ${pr}">${t.priority}</span></td>
       <td><span class="badge ${st}"><span class="dot" style="background:currentColor"></span>${t.status}</span></td>
       <td style="text-align:right"><select onchange="setTaskStatus('${t.id}',this.value)" style="width:auto;padding:6px 8px;font-size:12px">
         ${["To do","In progress","Done"].map(s=>`<option ${s===t.status?'selected':''}>${s}</option>`).join("")}</select></td></tr>`}).join("")}
   </tbody></table>${list.length?'':emptyState("✓","No tasks yet.")}</div>`;
}
function viewDocuments(){
  const u=me();const canUp=["Owner","Admin","Manager","Member"].includes(u.role);
  return `<div class="page-h"><div><h1>Documents</h1><p>Upload and share project files. Stored in your browser (prototype).</p></div>
     <div class="actions">${canUp?`<label class="btn primary">+ Upload<input type="file" style="display:none" onchange="uploadDoc(this)"></label>`:''}</div></div>
   <div class="card"><table class="tbl"><thead><tr><th>Name</th><th>Category</th><th>Size</th><th>Uploaded by</th><th>Date</th><th></th></tr></thead>
   <tbody>${DB.docs.map(d=>`<tr data-srch="${esc(d.name)}">
     <td><div style="display:flex;align-items:center;gap:10px"><span style="font-size:18px">▤</span><b>${esc(d.name)}</b></div></td>
     <td><span class="badge indigo">${d.category}</span></td><td>${d.size}</td>
     <td>${esc(assigneeName(d.by))}</td><td>${fmt(d.date)}</td>
     <td style="text-align:right">${d.data?`<a class="btn sm" href="${d.data}" download="${esc(d.name)}">Download</a> `:''}
       <button class="btn sm danger" onclick="delDoc('${d.id}')">Delete</button></td></tr>`).join("")}
   </tbody></table>${DB.docs.length?'':emptyState("▤","No documents yet. Upload your first file.")}</div>`;
}
function viewResearch(){
  const u=me();const canAdd=["Owner","Admin","Manager","Member"].includes(u.role);
  return `<div class="page-h"><div><h1>Research</h1><p>Curated sources, notes and reading for the project.</p></div>
     <div class="actions">${canAdd?`<button class="btn primary" onclick="openResearchModal()">+ Add entry</button>`:''}</div></div>
   <div class="grid c2">${DB.research.map(r=>`<div class="card"><div class="bd">
     <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px"><span class="badge indigo">${r.category}</span>
       <span style="margin-left:auto;font-size:11.5px;color:var(--muted)">${fmt(r.date)}</span></div>
     <div style="font-weight:700;font-size:15px;margin-bottom:6px">${esc(r.title)}</div>
     <div style="color:#475569;font-size:13px;line-height:1.55">${esc(r.note||"")}</div>
     ${r.url?`<a class="btn sm" style="margin-top:12px" href="${esc(r.url)}" target="_blank">Open source ↗</a>`:''}
   </div></div>`).join("")||emptyState("⌕","No research entries yet.")}</div>`;
}
function viewActivity(){
  return `<div class="page-h"><div><h1>Activity</h1><p>Audit trail of everything happening in the portal.</p></div></div>
   <div class="card"><div class="bd">${activityList(DB.activity)}</div></div>`;
}
function activityList(items){
  if(!items.length)return emptyState("≣","No activity yet.");
  return `<div class="tlist">${items.map(a=>`<div class="titem">
    <div class="avatar" style="background:${avatarColor(a.user)}">${a.user==='system'?'◆':initials(assigneeName(a.user))}</div>
    <div style="flex:1"><div class="tt" style="font-weight:500">${esc(a.user==='system'?'System':assigneeName(a.user))} — ${esc(a.action)}</div>
      <div class="meta">${fmt(a.time)}</div></div></div>`).join("")}</div>`;
}

function viewAdmin(){
  const u=me();
  if(!["Owner","Admin"].includes(u.role))return emptyState("🔒","You don't have access to user administration.");
  return `<div class="page-h"><div><h1>Admin · Users</h1><p>Create accounts, assign roles and section access.</p></div>
     <div class="actions"><button class="btn primary" onclick="openUserModal()">+ Add user</button></div></div>
   <div class="card"><table class="tbl"><thead><tr><th>User</th><th>Role</th><th>Access</th><th>Status</th><th>Created</th><th></th></tr></thead>
   <tbody>${DB.users.map(x=>`<tr data-srch="${esc(x.name)} ${esc(x.username)} ${x.role}">
     <td><div class="userc"><div class="avatar" style="background:${avatarColor(x.name)}">${initials(x.name)}</div>
       <div><div class="nm">${esc(x.name)}</div><div class="un">@${esc(x.username)}</div></div></div></td>
     <td><span class="badge ${x.role==='Owner'?'indigo':x.role==='Admin'?'blue':'grey'}">${x.role}</span></td>
     <td><span style="font-size:12px;color:var(--muted)">${x.access.length} sections</span></td>
     <td><span class="badge ${x.status==='Active'?'green':'red'}">${x.status}</span></td>
     <td>${fmt(x.created)}</td>
     <td style="text-align:right">
       ${x.username!==DB.session?`<button class="btn sm" onclick="toggleUserStatus('${x.id}')">${x.status==='Active'?'Disable':'Enable'}</button>
       ${x.role!=='Owner'?`<button class="btn sm danger" onclick="delUser('${x.id}')">Remove</button>`:''}`:'<span style="color:var(--faint);font-size:12px">you</span>'}</td>
   </tr>`).join("")}</tbody></table></div>
   <div class="foot">Prototype — accounts live in this browser only. Connect Supabase for real cross-device login (see docs/platform.md).</div>`;
}
function viewProfile(){
  const u=me();
  return `<div class="page-h"><div><h1>My Profile</h1><p>Your account details and password.</p></div></div>
   <div class="grid c2">
     <div class="card"><div class="hd"><h3>Account</h3></div><div class="bd">
       <div style="display:flex;align-items:center;gap:14px;margin-bottom:18px">
         <div class="avatar" style="width:56px;height:56px;font-size:20px;background:${avatarColor(u.name)}">${initials(u.name)}</div>
         <div><div style="font-weight:700;font-size:17px">${esc(u.name)}</div><div style="color:var(--muted)">@${esc(u.username)} · ${u.role}</div></div>
       </div>
       <label class="field"><span>Display name</span><input id="pf-name" value="${esc(u.name)}"></label>
       <button class="btn primary" onclick="saveProfile()">Save changes</button>
     </div></div>
     <div class="card"><div class="hd"><h3>Change password</h3></div><div class="bd">
       <label class="field"><span>Current password</span><input id="pf-cur" type="password" placeholder="••••••••"></label>
       <label class="field"><span>New password</span><input id="pf-new" type="password" placeholder="At least 6 characters"></label>
       <div id="pf-msg" style="font-size:12.5px;margin-bottom:10px;min-height:16px"></div>
       <button class="btn primary" onclick="changePassword()">Update password</button>
     </div></div>
   </div>
   <div class="card" style="margin-top:16px"><div class="hd"><h3>My access</h3></div>
     <div class="bd"><div class="checks">${SECTIONS.map(s=>`<label style="cursor:default">
       <input type="checkbox" disabled ${u.access.includes(s.id)?'checked':''}> ${s.label}</label>`).join("")}</div></div></div>`;
}
function emptyState(ic,msg){return `<div class="empty"><div class="ic">${ic}</div>${esc(msg)}</div>`}

/* ============ ACTIONS ============ */
function toggleTask(id){const t=DB.tasks.find(x=>x.id===id);if(!t)return;
  t.status=t.status==="Done"?"To do":"Done";save();logAct((t.status==="Done"?"Completed":"Reopened")+" task: "+t.title);renderRoute();renderShell&&go(route)}
function setTaskStatus(id,s){const t=DB.tasks.find(x=>x.id===id);if(!t)return;t.status=s;save();
  logAct("Set '"+t.title+"' → "+s);renderRoute()}

function openTaskModal(){
  const opts=DB.users.filter(u=>u.status==="Active").map(u=>`<option value="${u.username}">${esc(u.name)}</option>`).join("");
  modal("New task",`
    <label class="field"><span>Title</span><input id="t-title" placeholder="e.g. Reproduce drift attack"></label>
    <label class="field"><span>Description</span><input id="t-desc" placeholder="Short detail"></label>
    <div class="row"><label class="field"><span>Assign to</span><select id="t-assignee">${opts}</select></label>
      <label class="field"><span>Due date</span><input id="t-due" type="date" value="${date(1)}"></label></div>
    <label class="field"><span>Priority</span><select id="t-pri"><option>Critical</option><option selected>High</option><option>Medium</option><option>Low</option></select></label>`,
    "Create task",()=>{
      const title=val("t-title");if(!title)return alert("Title required");
      DB.tasks.push({id:uid(),title,desc:val("t-desc"),assignee:val("t-assignee"),due:val("t-due"),
        priority:val("t-pri"),status:"To do",created:Date.now()});
      save();logAct("Created task: "+title);closeModal();renderRoute();renderShell();go(route);
    });
}
function openResearchModal(){
  modal("Add research entry",`
    <label class="field"><span>Title</span><input id="r-title" placeholder="Source / paper title"></label>
    <label class="field"><span>URL (optional)</span><input id="r-url" placeholder="https://…"></label>
    <label class="field"><span>Category</span><select id="r-cat"><option>Reference</option><option>Paper</option><option>Disclosure</option><option>Competitor</option><option>Note</option></select></label>
    <label class="field"><span>Note</span><textarea id="r-note" rows="3" placeholder="Why it matters"></textarea></label>`,
    "Add entry",()=>{const title=val("r-title");if(!title)return alert("Title required");
      DB.research.unshift({id:uid(),title,url:val("r-url"),category:val("r-cat"),note:val("r-note"),by:DB.session,date:Date.now()});
      save();logAct("Added research: "+title);closeModal();renderRoute();});
}
function openUserModal(){
  const checks=SECTIONS.map(s=>`<label><input type="checkbox" class="acc" value="${s.id}" checked> ${s.label}</label>`).join("");
  modal("Add user",`
    <label class="field"><span>Full name</span><input id="u-name" placeholder="e.g. Asha Patel"></label>
    <label class="field"><span>Role</span><select id="u-role" onchange="applyRoleAccess(this.value)">
      ${Object.keys(ROLES).filter(r=>r!=="Owner").map(r=>`<option ${r==='Member'?'selected':''}>${r}</option>`).join("")}</select></label>
    <div class="field"><span>Section access</span><div class="checks">${checks}</div></div>`,
    "Create account",()=>{
      const name=val("u-name");if(!name)return alert("Name required");
      const access=[...document.querySelectorAll(".acc:checked")].map(c=>c.value);
      const username=genUsername(name),password=genPassword();
      DB.users.push({id:uid(),name,username,password,role:val("u-role"),access,status:"Active",created:Date.now()});
      save();logAct("Created account for "+name+" (@"+username+")");closeModal();
      showCreds(name,username,password);
    });
  setTimeout(()=>applyRoleAccess("Member"),0);
}
function applyRoleAccess(role){const def=ROLES[role];const set=def.all?SECTIONS.map(s=>s.id):def.access;
  document.querySelectorAll(".acc").forEach(c=>c.checked=set.includes(c.value))}
function showCreds(name,username,password){
  modal("Account created ✓",`
    <p style="margin:0 0 4px;color:#334155">Share these credentials with <b>${esc(name)}</b>. The password is shown once — copy it now.</p>
    <div class="cred"><div><span>Username</span><b id="cu">${esc(username)}</b></div>
      <div><span>Password</span><b id="cp">${esc(password)}</b></div></div>
    <button class="btn" style="margin-top:12px" onclick="navigator.clipboard.writeText('Portal login\\nUser: ${username}\\nPass: ${password}');this.textContent='Copied ✓'">Copy credentials</button>`,
    "Done",()=>{closeModal();renderRoute();renderShell();go(route)},true);
}
function toggleUserStatus(id){const x=DB.users.find(u=>u.id===id);if(!x)return;
  x.status=x.status==="Active"?"Disabled":"Active";save();logAct((x.status==="Active"?"Enabled":"Disabled")+" @"+x.username);renderRoute()}
function delUser(id){const x=DB.users.find(u=>u.id===id);if(!x||!confirm("Remove "+x.name+"?"))return;
  DB.users=DB.users.filter(u=>u.id!==id);save();logAct("Removed @"+x.username);renderRoute()}

function uploadDoc(input){const f=input.files[0];if(!f)return;
  const size=(f.size/1024).toFixed(0)+" KB";const cat=f.type.includes("pdf")?"PDF":f.type.includes("image")?"Image":"File";
  const done=data=>{DB.docs.unshift({id:uid(),name:f.name,category:cat,size,data,by:DB.session,date:Date.now()});
    save();logAct("Uploaded document: "+f.name);renderRoute()};
  if(f.size<=1500000){const r=new FileReader();r.onload=()=>done(r.result);r.readAsDataURL(f)}
  else{alert("File over 1.5 MB — stored as a reference only (prototype limit).");done(null)}}
function delDoc(id){if(!confirm("Delete this document?"))return;DB.docs=DB.docs.filter(d=>d.id!==id);save();logAct("Deleted a document");renderRoute()}

function saveProfile(){const u=me();const n=val("pf-name").trim();if(n){u.name=n;save();logAct("Updated profile");renderShell();go(route)}}
function changePassword(){const u=me();const cur=val("pf-cur"),nw=val("pf-new");const msg=document.getElementById("pf-msg");
  if(cur!==u.password){msg.style.color="var(--red)";msg.textContent="Current password is incorrect.";return}
  if(nw.length<6){msg.style.color="var(--red)";msg.textContent="New password must be at least 6 characters.";return}
  u.password=nw;save();logAct("Changed password");msg.style.color="var(--green)";msg.textContent="Password updated ✓";
  document.getElementById("pf-cur").value="";document.getElementById("pf-new").value="";}

/* ---------- modal util ---------- */
function modal(title,body,okLabel,onOk,hideCancel){
  const bg=document.createElement("div");bg.className="modal-bg";bg.id="modal";
  bg.innerHTML=`<div class="modal"><div class="mh"><h3>${title}</h3><span class="x" onclick="closeModal()">✕</span></div>
    <div class="mb">${body}</div><div class="mf">${hideCancel?'':'<button class="btn" onclick="closeModal()">Cancel</button>'}
    <button class="btn primary" id="modal-ok">${okLabel}</button></div></div>`;
  document.body.appendChild(bg);document.getElementById("modal-ok").onclick=onOk;
  bg.addEventListener("mousedown",e=>{if(e.target===bg)closeModal()});}
function closeModal(){const m=document.getElementById("modal");if(m)m.remove()}
function val(id){const e=document.getElementById(id);return e?e.value:""}

/* ---------- start ---------- */
window.addEventListener("keydown",e=>{if(e.key==="Enter"&&!document.getElementById("app").style.display.includes("block")&&document.getElementById("li-user"))doLogin()});
boot();
