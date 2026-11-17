// Isolated synthetic Cloudflare Agent Core using authoritative D1 Living Memory.
// Not a personal agent and not a replacement for previously verified lab Workers.
import {Agent,getAgentByName} from "agents";
import {startMemoryRun,wakeWithMemory,memoryReceipt} from "../../agent_core/src/memory_cycle.mjs";
import {blockWake} from "../../agent_core/src/core.mjs";
import {createMemoryManager} from "../../living_memory/src/manager.mjs";
import {createD1MemoryStore} from "../../living_memory/src/d1.mjs";
import {canHandleScheduledWake} from "./autonomous_support.mjs";
import {safeIntegratedStatus,canRestartUnarmedTrial} from "./integrated_support.mjs";

const MODEL="@cf/google/gemma-4-26b-a4b-it";
const INSTANCE="synthetic-core-memory-v1";
const initialState=()=>({
  schema:1,mode:"synthetic",runId:null,status:"not_started",
  intent:null,notes:[],events:[],wakes:0,modelCalls:0,toolCalls:0,
  daily:{date:"1970-01-01",wakes:0},nextWakeAt:null,reason:null,
  lastMemoryId:null,memoryWrites:0,memoryReads:0,memoryContexts:0
});
function json(value,status=200) {
  return Response.json(value,{status,headers:{
    "cache-control":"no-store",
    "x-content-type-options":"nosniff"
  }});
}
function authorized(request,env) {
  return typeof env.LAB_ADMIN_TOKEN==="string" &&
    env.LAB_ADMIN_TOKEN.length>=32 &&
    request.headers.get("authorization")==="Bearer "+env.LAB_ADMIN_TOKEN;
}

export class CoreMemoryAgent extends Agent {
  initialState=initialState();

  async scheduleNext({runId,at}) {
    const when=Date.parse(at);
    if(!Number.isFinite(when))throw Error("invalid_schedule");
    await this.schedule(new Date(when+2000),"wake",{runId,scheduledAt:at});
  }
  memoryPort() {
    return createMemoryManager(createD1MemoryStore(this.env.MEMORY_DB));
  }
  async startExperiment() {
    if(!this.env.MEMORY_DB || !this.env.AI)return {error:"binding_missing"};
    try {
      // RPC does not automatically initialize Agent SDK Lifecycle; without this,
      // a reported "scheduled" state may have zero persisted jobs/physical alarm.
      await this.lifecycle.start();
      const current=this.state;
      if(["running","scheduled"].includes(current?.status)) {
        const jobs=await this.listSchedules();
        const alarm=await this.ctx.storage.getAlarm();
        if(!canRestartUnarmedTrial(current,Array.isArray(jobs)?jobs.length:null,
            alarm,Date.now()))return {error:"already_running"};
      }
      const result=await startMemoryRun({
        runId:crypto.randomUUID(),
        save:async state=>this.setState(state),
        schedule:params=>this.scheduleNext(params)
      });
      if(result.status!=="scheduled")return {error:"schedule_failed"};
      // A successful RPC is not proof of a durable scheduled callback:
      // check both the SDK queue and the underlying Durable Object alarm.
      const jobs=await this.listSchedules();
      const alarm=await this.ctx.storage.getAlarm();
      if(!Array.isArray(jobs)||jobs.length===0||!Number.isFinite(alarm)){
        this.setState(blockWake(this.state,"schedule_failed"));
        return {error:"schedule_failed"};
      }
      return result;
    }catch{
      if(this.state?.status==="scheduled")
        this.setState(blockWake(this.state,"schedule_failed"));
      return {error:"start_failed"};
    }
  }
  async receipt(){
    await this.lifecycle.start();
    const result=safeIntegratedStatus(this.state??initialState());
    // Synthetic-only alarm diagnostics: never include payloads, memory texts,
    // SQL contents, internal DO identifiers or credentials.
    let jobs=null,alarmAt=null;
    try{
      const list=await this.listSchedules();
      jobs=Array.isArray(list)?list.length:null;
    }catch{}
    try{
      const alarm=await this.ctx.storage.getAlarm();
      if(typeof alarm==="number" && Number.isFinite(alarm))
        alarmAt=new Date(alarm).toISOString();
    }catch{}
    return {...result,scheduledJobCount:jobs,physicalAlarmAt:alarmAt};
  }
  async wake(payload) {
    if(!canHandleScheduledWake(this.state,payload))return;
    try{
      await wakeWithMemory({
        runId:payload.runId,
        load:async()=>this.state,
        save:async state=>this.setState(state),
        schedule:params=>this.scheduleNext(params),
        memory:this.memoryPort(),
        infer:async messages=>this.env.AI.run(MODEL,{
          messages,
          max_tokens:384,
          chat_template_kwargs:{enable_thinking:false}
        })
      });
    }catch{
      // State is already marked running before LLM/D1 effects. Never replay
      // an uncertain model call or uncertain D1 write after an exception.
      if(this.state?.status==="running")
        this.setState(blockWake(this.state,"tool_failed"));
    }
  }
}

export default {
  async fetch(request,env) {
    const path=new URL(request.url).pathname;
    if(request.method==="GET" && path==="/health")
      return json({lab:"synthetic-core-memory-d1-v1",
        ready:!!env.MEMORY_DB && !!env.AI});
    if(request.method==="GET" && path==="/status"){
      const agent=await getAgentByName(env.CoreMemoryAgent,INSTANCE);
      return json(await agent.receipt());
    }
    if(request.method==="POST" && path==="/trial/ready"){
      if(!authorized(request,env))return json({error:"unauthorized"},401);
      if(!env.MEMORY_DB || !env.AI)return json({error:"binding_missing"},503);
      return json({status:"authorized",memoryBound:true,modelBound:true});
    }
    if(request.method==="POST" && path==="/start"){
      if(!authorized(request,env))return json({error:"unauthorized"},401);
      if(!env.MEMORY_DB || !env.AI)return json({error:"binding_missing"},503);
      const agent=await getAgentByName(env.CoreMemoryAgent,INSTANCE);
      const response=await agent.startExperiment();
      return json(response,response.error?409:202);
    }
    return json({error:"not_found"},404);
  }
};
