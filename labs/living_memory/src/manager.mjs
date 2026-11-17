// Unified Living Memory v1: subjective records, not operational state or credentials.
export const SCHEMA_VERSION = 1;
const KINDS = new Set(["experience","fact","skill","belief","goal","value","interpretation"]);
const WEIGHTS = ["strength","confidence","significance","accessibility","stability"];
const EXPOSURE = {minimal:3,ordinary:8,deep:16,reflection:24};
function assertId(id) {
  if(typeof id!=="string" || !/^[a-zA-Z0-9_-]{1,100}$/.test(id)) throw Error("invalid_memory_id");
  return id;
}
function content(text) {
  if(typeof text!=="string" || !text.trim() || text.length>16000) throw Error("invalid_memory_content");
  return text.trim();
}
function fields(input,allowed) {
  if(!input || typeof input!=="object" || Array.isArray(input) ||
    Object.keys(input).some(key=>!allowed.includes(key))) throw Error("invalid_memory_fields");
}
function weights(input,defaults={}) {
  const out={};
  for(const key of WEIGHTS) {
    const n=input[key]===undefined?(defaults[key]??0.5):input[key];
    if(typeof n!=="number" || !Number.isFinite(n) || n<0 || n>1) throw Error("invalid_"+key);
    out[key]=n;
  }
  return out;
}
export function createMemoryManager(store,{clock=Date.now,makeId=()=>crypto.randomUUID()}={}) {
  for(const name of ["insert","get","updateIfRevision","search","top","exportBatch"])
    if(typeof store?.[name]!=="function") throw Error("invalid_memory_store");
  const timestamp=()=>{
    const value=new Date(clock());
    if(!Number.isFinite(value.getTime())) throw Error("invalid_clock");
    return value.toISOString();
  };
  async function read(id) {return store.get(assertId(id));}
  async function remember(input) {
    fields(input,["kind","content",...WEIGHTS]);
    if(!KINDS.has(input.kind) || input.kind==="interpretation") throw Error("invalid_memory_kind");
    const time=timestamp();
    const r={id:assertId(makeId()),schemaVersion:SCHEMA_VERSION,revision:1,
      kind:input.kind,content:content(input.content),...weights(input),
      derivedFrom:null,createdAt:time,updatedAt:time};
    await store.insert(r);
    return r;
  }
  async function revise(id,expectedRevision,patch) {
    assertId(id);
    if(!Number.isSafeInteger(expectedRevision)||expectedRevision<1) throw Error("invalid_expected_revision");
    fields(patch,["content",...WEIGHTS]);
    if(Object.keys(patch).length===0) throw Error("empty_revision");
    const old=await read(id);
    if(!old) throw Error("memory_not_found");
    if(old.revision!==expectedRevision) throw Error("revision_conflict");
    const next={...old,revision:expectedRevision+1,updatedAt:timestamp(),
      content:Object.hasOwn(patch,"content")?content(patch.content):old.content,
      ...weights(patch,old)};
    if(!await store.updateIfRevision(next,expectedRevision)) throw Error("revision_conflict");
    return next;
  }
  async function reinterpret(id,input) {
    fields(input,["content",...WEIGHTS]);
    const old=await read(id);
    if(!old) throw Error("memory_not_found");
    const time=timestamp();
    const next={id:assertId(makeId()),schemaVersion:SCHEMA_VERSION,revision:1,
      kind:"interpretation",content:content(input.content),...weights(input),
      derivedFrom:old.id,createdAt:time,updatedAt:time};
    await store.insert(next);
    return next;
  }
  async function recall({situation="",exposure="ordinary",tokenBudget=256}={}) {
    if(!Object.hasOwn(EXPOSURE,exposure)) throw Error("invalid_exposure");
    if(typeof situation!=="string" || situation.length>1024) throw Error("invalid_situation");
    if(!Number.isSafeInteger(tokenBudget)||tokenBudget<16||tokenBudget>4096)
      throw Error("invalid_token_budget");
    const candidates=exposure==="minimal"?await store.top(EXPOSURE[exposure])
      :await store.search(situation,EXPOSURE[exposure]);
    const records=[],seen=new Set();
    let used=0;
    for(const r of candidates) {
      if(seen.has(r.id)) continue;
      seen.add(r.id);
      const cost=Math.ceil(r.content.length/4)+16;
      if(used+cost>tokenBudget) continue;
      used+=cost;
      records.push({id:r.id,kind:r.kind,content:r.content,revision:r.revision,
        confidence:r.confidence,significance:r.significance});
    }
    return {schemaVersion:SCHEMA_VERSION,exposure,approximateTokens:used,records};
  }
  async function exportBatch({after=0,limit=100}={}) {
    if(!Number.isSafeInteger(after)||after<0||!Number.isSafeInteger(limit)||
      limit<1||limit>200) throw Error("invalid_export_request");
    return {schemaVersion:SCHEMA_VERSION,...await store.exportBatch(after,limit)};
  }
  return Object.freeze({remember,read,revise,reinterpret,recall,exportBatch,
    inspectExternalEvidence:()=>({available:false,reason:"not_integrated"})});
}
