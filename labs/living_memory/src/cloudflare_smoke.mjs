// Independent Phase 1 D1 smoke. Only fixed fabricated records, no agent data.
import {createMemoryManager} from "./manager.mjs";
import {createD1MemoryStore} from "./d1.mjs";

const json=(value,status=200)=>Response.json(value,{status,headers:{
  "cache-control":"no-store","x-content-type-options":"nosniff"
}});
const isId=value=>typeof value==="string" && /^[a-zA-Z0-9_-]{1,100}$/.test(value);

function authorized(request,env) {
  return typeof env.LAB_ADMIN_TOKEN==="string" && env.LAB_ADMIN_TOKEN.length>=32 &&
    request.headers.get("authorization")==="Bearer "+env.LAB_ADMIN_TOKEN;
}
export default {
  async fetch(request,env) {
    const path=new URL(request.url).pathname;
    if(request.method==="GET" && path==="/health")
      return json({lab:"living-memory-d1-v1",synthetic:true,ready:!!env.MEMORY_DB});
    if(request.method==="GET" && path==="/status")
      return json({lab:"living-memory-d1-v1",synthetic:true,
        databaseBound:!!env.MEMORY_DB,containsPersonalData:false});
    if(request.method!=="POST" || !["/trial/remember","/trial/revise","/trial/verify"].includes(path))
      return json({error:"not_found"},404);
    if(!authorized(request,env))return json({error:"unauthorized"},401);
    if(!env.MEMORY_DB)return json({error:"memory_not_configured"},503);
    const memory=createMemoryManager(createD1MemoryStore(env.MEMORY_DB));
    try {
      if(path==="/trial/remember") {
        const created=await memory.remember({kind:"experience",
          content:"A fabricated cobalt river under a simulated sky",confidence:0.7});
        const found=await memory.recall({situation:"cobalt river",tokenBudget:256});
        if(!found.records.some(r=>r.id===created.id))throw Error("recall_failed");
        return json({status:"remembered",id:created.id,revision:created.revision,
          found:true},200);
      }
      let input;
      try {input=await request.json();}catch {return json({error:"invalid_input"},400);}
      if(!isId(input?.id))return json({error:"invalid_id"},400);
      if(path==="/trial/revise") {
        const changed=await memory.revise(input.id,1,{
          content:"The fabricated river now looks turquoise",confidence:0.8});
        const derived=await memory.reinterpret(changed.id,{
          content:"My present interpretation is that the river's color changed"});
        const old=await memory.recall({situation:"cobalt",tokenBudget:256});
        const fresh=await memory.recall({situation:"turquoise",tokenBudget:256});
        if(old.records.some(r=>r.id===input.id) ||
           !fresh.records.some(r=>r.id===input.id))
          throw Error("fts_revision_inconsistent");
        return json({status:"revised",id:changed.id,revision:changed.revision,
          derivedId:derived.id,oldTermGone:true,newTermFound:true});
      }
      if(!isId(input.derivedId))return json({error:"invalid_id"},400);
      const original=await memory.read(input.id);
      const derivative=await memory.read(input.derivedId);
      const retrieved=await memory.recall({situation:"turquoise",tokenBudget:256});
      if(original?.revision!==2 || derivative?.derivedFrom!==input.id ||
        !retrieved.records.some(r=>r.id===input.id))
        throw Error("persistence_not_confirmed");
      return json({status:"verified",revision:original.revision,
        derivedFromVerified:true,recallVerified:true});
    } catch {
      // Never expose D1 SQL errors, record contents, stack traces or provider data.
      return json({error:"memory_trial_failed"},409);
    }
  }
};
