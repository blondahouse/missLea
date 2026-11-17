// Isolated synthetic Cloudflare Agent Core using authoritative D1 Living Memory.
// Not a personal agent and not a replacement for previously verified lab Workers.
import {Agent,getAgentByName} from "agents";
import {startMemoryRun,resumeMemoryRun,wakeWithMemory,memoryReceipt} from "../../agent_core/src/memory_cycle.mjs";
import {blockWake} from "../../agent_core/src/core.mjs";
import {createMemoryManager} from "../../living_memory/src/manager.mjs";
import {createD1MemoryStore} from "../../living_memory/src/d1.mjs";
import {canHandleScheduledWake} from "./autonomous_support.mjs";
import {safeIntegratedStatus,canStartFreshTrial,scheduledCallbackRejection} from "./integrated_support.mjs";

const MODEL="@cf/google/gemma-4-26b-a4b-it";
const INSTANCE="synthetic-core-memory-v1";
const initialState=()=>({
  schema:1,mode:"synthetic",runId:null,status:"not_started",
  intent:null,notes:[],events:[],wakes:0,modelCalls:0,toolCalls:0,
  daily:{date:"1970-01-01",wakes:0},nextWakeAt:null,reason:null,
  lastMemoryId:null,memoryWrites:0,memoryReads:0,memoryContexts:0,
  decisionRepairs:0,lastDecisionValidationCode:null,resumeCount:0,lastResumeAt:null
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
      // Never silently replace a blocked/paused run or drop its last D1 pointer.
      const jobs=await this.listSchedules();
      const alarm=await this.ctx.storage.getAlarm();
      if(!canStartFreshTrial(current,Array.isArray(jobs)?jobs.length:null,
          alarm,Date.now()))return {error:"already_started"};
      const result=await startMemoryRun({
        runId:crypto.randomUUID(),
        save:async state=>this.setState(state),
        schedule:params=>this.scheduleNext(params)
      });
      if(result.status!=="scheduled")return {error:"schedule_failed"};
      // A successful RPC is not proof of a durable scheduled callback:
      // check both the SDK queue and the underlying Durable Object alarm.
      const scheduledJobs=await this.listSchedules();
      const scheduledAlarm=await this.ctx.storage.getAlarm();
      if(!Array.isArray(scheduledJobs)||scheduledJobs.length===0||!Number.isFinite(scheduledAlarm)){
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
  async resumeExperiment(expectedRunId,expectedWakes) {
    if(!this.env.MEMORY_DB || !this.env.AI)return {error:"binding_missing"};
    await this.lifecycle.start();
    const state=this.state;
    if(typeof expectedRunId!=="string" || expectedRunId!==state?.runId ||
       !Number.isSafeInteger(expectedWakes) || expectedWakes!==state?.wakes)
      return {error:"state_changed"};
    // A previously scheduled task is never cloned or superseded.
    const jobs=await this.listSchedules();
    const alarm=await this.ctx.storage.getAlarm();
    if(!Array.isArray(jobs)||jobs.length!==0||alarm!==null)
      return {error:"pending_alarm"};
    let result;
    try {
      result=await resumeMemoryRun({
        load:async()=>this.state,
        save:async next=>this.setState(next),
        schedule:params=>this.scheduleNext(params)
      });
    }catch(error){
      const safe=new Set(["resume_not_safe","resume_budget_exhausted"]);
      return {error:safe.has(error?.message)?error.message:"resume_failed"};
    }
    if(result.status!=="scheduled")return {error:"schedule_failed"};
    // Verify an actual persisted SDK schedule AND physical alarm before success.
    const afterJobs=await this.listSchedules();
    const afterAlarm=await this.ctx.storage.getAlarm();
    if(!Array.isArray(afterJobs)||afterJobs.length!==1||
       !Number.isFinite(afterAlarm)){
      this.setState(blockWake(this.state,"schedule_failed"));
      return {error:"schedule_failed"};
    }
    return result;
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
    const current=this.state;
    // A scheduled job can disappear after firing even if a strict callback
    // guard declines its payload. Keep only bounded synthetic diagnostics.
    if(current?.schema===1 && current?.mode==="synthetic"){
      const reason=scheduledCallbackRejection(current,payload);
      const state={...current,
        callbackAttempts:Math.min(20,(current.callbackAttempts??0)+1),
        callbackRejectCode:reason,
        callbackRejected:Math.min(20,(current.callbackRejected??0)+(reason?1:0))};
      this.setState(state);
    }
    if(!canHandleScheduledWake(this.state,payload))return;
    let phase="memory_port";
    try{
      const underlying=this.memoryPort();
      const memory={};
      for(const method of ["read","recall","remember","revise","reinterpret"]) {
        memory[method]=async (...args)=>{
          phase="memory_"+method;
          return underlying[method](...args);
        };
      }
      phase="cycle_entry";
      await wakeWithMemory({
        runId:payload.runId,
        load:async()=>{phase="load_state";return this.state;},
        save:async state=>{
          phase=state.status==="running"?"persist_running":"persist_outcome";
          return this.setState(state);
        },
        schedule:async params=>{
          phase="schedule_next";
          return this.scheduleNext(params);
        },
        memory,
        infer:async messages=>{
          phase="model_inference";
          return this.env.AI.run(MODEL,{
            messages,
            max_tokens:384,
            chat_template_kwargs:{enable_thinking:false}
          });
        }
      });
    }catch{
      // Catch failures even BEFORE the first "running" save (e.g. a missing
      // D1 port). Never leave an accepted one-shot callback as "scheduled":
      // a consumed alarm would otherwise silently strand the experiment.
      const current=this.state;
      if(["scheduled","running"].includes(current?.status)) {
        this.setState({...blockWake(current,"tool_failed"),
          callbackFailurePhase:phase});
      }
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
    if(request.method==="POST" && path==="/resume"){
      if(!authorized(request,env))return json({error:"unauthorized"},401);
      if(!env.MEMORY_DB || !env.AI)return json({error:"binding_missing"},503);
      let payload;
      try {
        if(Number(request.headers.get("content-length"))>512)
          return json({error:"invalid_request"},400);
        payload=await request.json();
        if(!payload||typeof payload!=="object"||Array.isArray(payload)||
           Object.keys(payload).length!==2 ||
           typeof payload.expectedRunId!=="string" ||
           !Number.isSafeInteger(payload.expectedWakes))
          return json({error:"invalid_request"},400);
      }catch{return json({error:"invalid_request"},400);}
      const agent=await getAgentByName(env.CoreMemoryAgent,INSTANCE);
      const response=await agent.resumeExperiment(payload.expectedRunId,payload.expectedWakes);
      return json(response,response.error?409:202);
    }
    return json({error:"not_found"},404);
  }
};
