/* ============================================================
   Shiva Portal — data layer
   Two interchangeable backends behind one async API:
     • LocalStore    — localStorage (prototype, default)
     • SupabaseStore — real auth + Postgres + storage
   The app calls Store.* and never cares which is active.
   ============================================================ */
const SECTIONS=[
  {id:"dashboard",label:"Dashboard",ic:"▦"},
  {id:"project",label:"Project Roadmap",ic:"◎"},
  {id:"canvas",label:"Project Map",ic:"⬡"},
  {id:"tasks",label:"Tasks",ic:"✓"},
  {id:"documents",label:"Documents",ic:"▤"},
  {id:"research",label:"Research",ic:"⌕"},
  {id:"activity",label:"Activity",ic:"≣"},
  {id:"admin",label:"Admin · Users",ic:"⚙"},
  {id:"profile",label:"My Profile",ic:"◍"},
];
const ROLES={
  Owner:{all:true},
  Admin:{access:["dashboard","project","canvas","tasks","documents","research","activity","admin","profile"]},
  Manager:{access:["dashboard","project","canvas","tasks","documents","research","activity","profile"]},
  Member:{access:["dashboard","project","canvas","tasks","documents","research","profile"]},
  Viewer:{access:["dashboard","project","canvas","documents","research","profile"]},
};
function _uid(){return Math.random().toString(36).slice(2,10)}
function _date(off){const d=new Date();d.setDate(d.getDate()+(off||0));return d.toISOString().slice(0,10)}

/* ---------------- LOCAL ---------------- */
const LocalStore={
  mode:"local",
  KEY:"shiva_portal_v4",
  db:null,
  _load(){try{this.db=JSON.parse(localStorage.getItem(this.KEY))}catch(e){this.db=null}
    if(!this.db)this._seed();return this.db},
  _save(){localStorage.setItem(this.KEY,JSON.stringify(this.db))},
  _seed(){const now=Date.now();this.db={firstRun:true,session:null,
    users:[{id:_uid(),name:"Kuldeep",username:"kuldeep",password:"Shiva@2026",role:"Owner",
      access:SECTIONS.map(s=>s.id),status:"Active",created:now}],
    tasks:[
      {id:_uid(),title:"Day 1 · Install the MCP SDK",desc:"pip install + Claude Desktop as the client",assignee:"kuldeep",due:_date(1),priority:"High",status:"To do",phase:"P0",created:now},
      {id:_uid(),title:"Day 2 · Run benign_server.py",desc:"mcp dev — learn the tool call flow",assignee:"kuldeep",due:_date(2),priority:"High",status:"To do",phase:"P0",created:now},
      {id:_uid(),title:"Day 3 · Reproduce tool poisoning (attack #1)",desc:"The key demo — screen-record it",assignee:"kuldeep",due:_date(3),priority:"Critical",status:"To do",phase:"P0",created:now},
      {id:_uid(),title:"Day 4 · Write up attack #1 + push",desc:"docs/attacks/01-tool-poisoning.md",assignee:"kuldeep",due:_date(4),priority:"High",status:"To do",phase:"P0",created:now},
      {id:_uid(),title:"Day 5 · Read sources + run attacks #2 & #3",desc:"drift + escalation servers; log in evidence.md",assignee:"kuldeep",due:_date(5),priority:"Medium",status:"To do",phase:"P0",created:now},
      {id:_uid(),title:"Day 6 · Sketch the scanner's 3 checks",desc:"hidden instructions · perms · description hashing",assignee:"kuldeep",due:_date(6),priority:"Medium",status:"To do",phase:"P0",created:now},
      {id:_uid(),title:"Day 7 · Decision gate 0",desc:"In for Phase 1? Log it in improvements.md",assignee:"kuldeep",due:_date(7),priority:"Medium",status:"To do",phase:"P0",created:now}],
    docs:[],
    research:[{id:_uid(),title:"Simon Willison — MCP prompt injection",url:"https://simonwillison.net/tags/model-context-protocol/",category:"Reference",note:"Core read on why MCP has injection problems.",by:"kuldeep",date:now}],
    activity:[{id:_uid(),user:"system",action:"Portal initialised",time:now}]};
    this._save()},
  async init(){this._load()},
  firstRun(){return !!this.db.firstRun},
  async login(u,p){const f=this.db.users.find(x=>x.username===u&&x.password===p);
    if(!f)return{error:"Invalid username or password."};if(f.status!=="Active")return{error:"This account is deactivated."};
    this.db.session=u;this.db.firstRun=false;this._save();return{user:f}},
  async logout(){this.db.session=null;this._save()},
  sessionUser(){return this.db.session},
  async fetchAll(){return{users:this.db.users,tasks:this.db.tasks,docs:this.db.docs,research:this.db.research,activity:this.db.activity}},
  async addActivity(action){this.db.activity.unshift({id:_uid(),user:this.db.session||"system",action,time:Date.now()});
    this.db.activity=this.db.activity.slice(0,200);this._save()},
  async createUser(o){const u={id:_uid(),created:Date.now(),status:"Active",...o};this.db.users.push(u);this._save();return u},
  async updateUser(id,patch){const u=this.db.users.find(x=>x.id===id);if(u)Object.assign(u,patch);this._save()},
  async deleteUser(id){this.db.users=this.db.users.filter(x=>x.id!==id);this._save()},
  async updateSelf(patch){const u=this.db.users.find(x=>x.username===this.db.session);if(u)Object.assign(u,patch);this._save();return u},
  async createTask(o){const t={id:_uid(),created:Date.now(),status:"To do",...o};this.db.tasks.push(t);this._save();return t},
  async updateTask(id,patch){const t=this.db.tasks.find(x=>x.id===id);if(t)Object.assign(t,patch);this._save()},
  async deleteTask(id){this.db.tasks=this.db.tasks.filter(x=>x.id!==id);this._save()},
  async createDoc(o){const d={id:_uid(),date:Date.now(),...o};this.db.docs.unshift(d);this._save();return d},
  async deleteDoc(id){this.db.docs=this.db.docs.filter(x=>x.id!==id);this._save()},
  async createResearch(o){const r={id:_uid(),date:Date.now(),...o};this.db.research.unshift(r);this._save();return r},
  async resetAll(){localStorage.removeItem(this.KEY);this._seed()},
};

/* ---------------- SUPABASE ---------------- */
function SupabaseStore(url,key){
  const sb=window.supabase.createClient(url,key);
  const EMAIL=u=>`${u}@shiva.local`;
  let _session=null,_profile=null;
  const rowU=p=>({id:p.id,name:p.name,username:p.username,role:p.role,access:p.access||[],status:p.status,created:new Date(p.created_at).getTime()});
  return {
    mode:"cloud", sb,
    async init(){const {data}=await sb.auth.getSession();_session=data.session;
      if(_session){const {data:p}=await sb.from("profiles").select("*").eq("id",_session.user.id).single();_profile=p;}},
    firstRun(){return false},
    async login(u,p){const {data,error}=await sb.auth.signInWithPassword({email:EMAIL(u),password:p});
      if(error)return{error:"Invalid username or password."};_session=data.session;
      const {data:prof}=await sb.from("profiles").select("*").eq("id",data.user.id).single();
      if(prof&&prof.status!=="Active"){await sb.auth.signOut();return{error:"This account is deactivated."}}
      _profile=prof;return{user:rowU(prof)}},
    async logout(){await sb.auth.signOut();_session=null;_profile=null},
    sessionUser(){return _profile?_profile.username:null},
    async fetchAll(){
      const [u,t,d,r,a]=await Promise.all([
        sb.from("profiles").select("*").order("created_at"),
        sb.from("tasks").select("*").order("due"),
        sb.from("documents").select("*").order("created_at",{ascending:false}),
        sb.from("research").select("*").order("created_at",{ascending:false}),
        sb.from("activity").select("*").order("created_at",{ascending:false}).limit(200)]);
      return{users:(u.data||[]).map(rowU),
        tasks:(t.data||[]).map(x=>({id:x.id,title:x.title,desc:x.descr,assignee:x.assignee,due:x.due,priority:x.priority,status:x.status,phase:x.phase||"P0"})),
        docs:(d.data||[]).map(x=>({id:x.id,name:x.name,category:x.category,size:x.size,data:x.url,by:x.uploaded_by,date:new Date(x.created_at).getTime()})),
        research:(r.data||[]).map(x=>({id:x.id,title:x.title,url:x.url,category:x.category,note:x.note,by:x.created_by,date:new Date(x.created_at).getTime()})),
        activity:(a.data||[]).map(x=>({id:x.id,user:x.actor,action:x.action,time:new Date(x.created_at).getTime()}))};},
    async addActivity(action){await sb.from("activity").insert({actor:this.sessionUser()||"system",action})},
    async createUser(o){ // calls a secure edge function (service_role) to make the auth user
      const {data,error}=await sb.functions.invoke("admin-create-user",{body:{name:o.name,username:o.username,password:o.password,role:o.role,access:o.access}});
      if(error)throw error;return o},
    async updateUser(id,patch){const p={};if(patch.status)p.status=patch.status;await sb.from("profiles").update(p).eq("id",id)},
    async deleteUser(id){await sb.functions.invoke("admin-create-user",{body:{deleteId:id}})},
    async updateSelf(patch){const p={};if(patch.name)p.name=patch.name;if(p.name)await sb.from("profiles").update(p).eq("id",_session.user.id);
      if(patch.password)await sb.auth.updateUser({password:patch.password});if(patch.name&&_profile)_profile.name=patch.name;return _profile},
    async createTask(o){await sb.from("tasks").insert({title:o.title,descr:o.desc,assignee:o.assignee,due:o.due,priority:o.priority,status:"To do",phase:o.phase||"P0"})},
    async updateTask(id,patch){const p={};["status","priority","due"].forEach(k=>{if(patch[k]!=null)p[k]=patch[k]});await sb.from("tasks").update(p).eq("id",id)},
    async deleteTask(id){await sb.from("tasks").delete().eq("id",id)},
    async createDoc(o){let url=o.data;
      if(o.file){const path=`${Date.now()}_${o.file.name}`;const up=await sb.storage.from("documents").upload(path,o.file);
        if(!up.error)url=sb.storage.from("documents").getPublicUrl(path).data.publicUrl;}
      await sb.from("documents").insert({name:o.name,category:o.category,size:o.size,url,uploaded_by:this.sessionUser()})},
    async deleteDoc(id){await sb.from("documents").delete().eq("id",id)},
    async createResearch(o){await sb.from("research").insert({title:o.title,url:o.url,category:o.category,note:o.note,created_by:this.sessionUser()})},
    async resetAll(){alert("Reset is only available in local mode.")},
  };
}

/* ---------------- pick backend ---------------- */
let Store;
(function(){
  const c=window.SHIVA_CONFIG||{};
  if(c.SUPABASE_URL&&c.SUPABASE_ANON_KEY&&window.supabase){
    try{Store=SupabaseStore(c.SUPABASE_URL,c.SUPABASE_ANON_KEY);}catch(e){console.error(e);Store=LocalStore;}
  }else Store=LocalStore;
  window.Store=Store;
})();
