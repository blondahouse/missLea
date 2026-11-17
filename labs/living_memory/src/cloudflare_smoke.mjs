// Independent Phase 1 D1 smoke. Only fixed fabricated records, no agent data.
import {createMemoryManager} from "./manager.mjs";
import {createD1MemoryStore} from "./d1.mjs";

const json=(value,status=200)=>Response.json(value,{status,headers:{
  "cache-control":"no-store","x-content-type-options":"nosniff"
}});
const isId=value=>typeof value==="string" && /^[a-zA-Z0-9_-]{1,100}$/.test(value);

export function classifyD1Error(error) {
  const message=String(error?.message??"").toLowerCase();
  if(message.includes("malformed") || message.includes("corrupt")) return "index_integrity";
  if(message.includes("quota") || message.includes("limit exceeded")) return "resource_limit";
  if(message.includes("no such table")) return "schema_missing";
  if(message.includes("ambiguous column")) return "sql_ambiguous";
  if(message.includes("constraint") || message.includes("foreign key")) return "constraint";
  if(message.includes("revision_conflict")) return "revision_conflict";
  if(message.includes("fts5") || message.includes("full-text")) return "fts_index";
  if(message.includes("timeout") || message.includes("network")) return "transport";
  if(message.includes("d1_error")) return "d1_query";
  return "other";
}

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
    let stage="not_started";
    try {
      if(path==="/trial/remember") {
        stage="remember_write";
        const created=await memory.remember({kind:"experience",
          content:"A fabricated cobalt river under a simulated sky",confidence:0.7});
        stage="remember_recall";
        const found=await memory.recall({situation:"cobalt river",tokenBudget:256});
        if(!found.records.some(r=>r.id===created.id))throw Error("recall_failed");
        return json({status:"remembered",id:created.id,revision:created.revision,
          found:true},200);
      }
      stage="decode_input";
      let input;
      try {input=await request.json();}catch {return json({error:"invalid_input"},400);}
      if(!isId(input?.id))return json({error:"invalid_id"},400);
      if(path==="/trial/revise") {
        stage="revise_write";
        const changed=await memory.revise(input.id,1,{
          content:"The fabricated river now looks turquoise",confidence:0.8});
        stage="reinterpret_write";
        const derived=await memory.reinterpret(changed.id,{
          content:"My present interpretation is that the river's color changed"});
        stage="old_index_recall";
        const old=await memory.recall({situation:"cobalt",tokenBudget:256});
        stage="new_index_recall";
        const fresh=await memory.recall({situation:"turquoise",tokenBudget:256});
        if(old.records.some(r=>r.id===input.id) ||
           !fresh.records.some(r=>r.id===input.id))
          throw Error("fts_revision_inconsistent");
        return json({status:"revised",id:changed.id,revision:changed.revision,
          derivedId:derived.id,oldTermGone:true,newTermFound:true});
      }
      if(!isId(input.derivedId))return json({error:"invalid_id"},400);
      stage="verify_read_original";
      const original=await memory.read(input.id);
      stage="verify_read_derived";
      const derivative=await memory.read(input.derivedId);
      stage="verify_recall";
      const retrieved=await memory.recall({situation:"turquoise",tokenBudget:256});
      if(original?.revision!==2 || derivative?.derivedFrom!==input.id ||
        !retrieved.records.some(r=>r.id===input.id))
        throw Error("persistence_not_confirmed");
      return json({status:"verified",revision:original.revision,
        derivedFromVerified:true,recallVerified:true});
    } catch(error) {
      // This response is authenticated. Only fixed stage and category are allowed;
      // never leak database error text, record content, stack traces or SQL.
      return json({error:"memory_trial_failed",stage,
        category:classifyD1Error(error)},409);
    }
  }
};
