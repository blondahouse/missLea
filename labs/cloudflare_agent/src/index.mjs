import { Agent, getAgentByName } from "agents";
import { MODEL, MAX_WAKES, selectedAction, syntheticTool, freshState, publicReceipt } from "./core.mjs";

const responseJson = (value, status=200) =>
  Response.json(value, {status,headers:{"cache-control":"no-store"}});
const INSTANCE = "anonymous-v1";

export class AnonymousFreeAgent extends Agent {
  initialState = {
    runId:null, status:"not_started", wakes:0, modelCalls:0,
    events:[],nextAt:null,blockedReason:null
  };

  async startExperiment() {
    const current = this.state;
    if (["scheduled","running"].includes(current?.status))
      return {error:"already_running"};
    const runId = crypto.randomUUID();
    this.setState(freshState(runId));
    try {
      await this.schedule(15, "wake", {runId});
      return {status:"scheduled",runId};
    } catch {
      this.setState({...this.state,status:"blocked",nextAt:null,blockedReason:"schedule_failed"});
      return {error:"schedule_failed"};
    }
  }

  async getReceipt() { return publicReceipt(this.state); }

  async wake(payload) {
    const current = this.state;
    if (!payload?.runId || payload.runId !== current?.runId ||
        current?.status !== "scheduled" || current.wakes >= MAX_WAKES) return;
    const step = current.wakes + 1;
    this.setState({...current,status:"running",nextAt:null});
    try {
      let action, toolResult=null;
      if (step === 1) {
        const prompt = current.events[0]?.decision;
        const ai = await this.env.AI.run(MODEL,{
          messages:[
            {role:"system",content:"You are an anonymous synthetic test agent. Choose a permitted tool. Reply with ONLY SQUARES or STOP, no other text."},
            {role:"user",content:`Saved earlier decision: ${prompt}. The SQUARES tool calculates sum of squares for [2,3,5]. Choose your next action.`}
          ],
          max_tokens:24,
          chat_template_kwargs:{enable_thinking:false}
        });
        action = selectedAction(ai,["SQUARES","STOP"]);
        if (action !== "SQUARES") throw Error("invalid_model_action");
        toolResult = syntheticTool(action,[2,3,5]);
      } else {
        const prior = current.events.find(x => x.type === "wake" && x.action === "SQUARES");
        if (!prior || prior.result?.squares !== 38) throw Error("missing_prior_memory");
        const ai = await this.env.AI.run(MODEL,{
          messages:[
            {role:"system",content:"You are an anonymous synthetic test agent. Reply with ONLY CONFIRM or REJECT, no other text."},
            {role:"user",content:`From stored earlier experience: SQUARES [2,3,5] yielded ${prior.result.squares}. If the result equals 38, choose CONFIRM; otherwise REJECT.`}
          ],
          max_tokens:24,
          chat_template_kwargs:{enable_thinking:false}
        });
        action = selectedAction(ai,["CONFIRM","REJECT"]);
        if (action !== "CONFIRM") throw Error("invalid_memory_confirmation");
      }
      const next = {
        ...this.state, wakes:step,modelCalls:step,
        events:[...current.events,{type:"wake",action,result:toolResult}]
      };
      if (step < MAX_WAKES) {
        next.status="scheduled";
        next.nextAt=new Date(Date.now()+15000).toISOString();
        this.setState(next);
        try {
          await this.schedule(15,"wake",{runId:current.runId});
        } catch {
          this.setState({...next,status:"blocked",nextAt:null,blockedReason:"schedule_failed"});
        }
      } else {
        this.setState({...next,status:"completed",nextAt:null});
      }
    } catch(error) {
      const safeReason = ["invalid_model_action","missing_prior_memory","invalid_memory_confirmation"]
        .includes(error?.message) ? error.message : "model_or_quota_failed";
      this.setState({...this.state,status:"blocked",nextAt:null,blockedReason:safeReason});
    }
  }
}

const page = () => new Response(`<!doctype html><html lang="ru"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Anonymous Cloudflare Agent Lab</title>
<style>body{font:16px system-ui;line-height:1.5;max-width:34rem;margin:2rem auto;padding:0 1rem}
button,input{font:inherit;padding:.7rem;width:100%;margin:.4rem 0;box-sizing:border-box}
pre{white-space:pre-wrap;overflow-wrap:anywhere}small{color:#666}</style>
<h2>Anonymous Agent — Cloudflare Free</h2>
<p>Два самостоятельных пробуждения, два реальных вызова Workers AI и память в Durable Object.</p>
<label>Лабораторный пароль запуска<input id="token" type="password" autocomplete="off"></label>
<button id="start">Запустить</button><button id="check">Проверить состояние</button>
<pre id="status">Проверка...</pre><small>Нет личности, личных данных и внешних платных API.</small>
<script>
const out=document.getElementById("status");
async function refresh(){
 try{const r=await fetch("/status",{cache:"no-store"});out.textContent=JSON.stringify(await r.json(),null,2);}
 catch {out.textContent="Не удалось проверить состояние";}}
document.getElementById("check").onclick=refresh;
document.getElementById("start").onclick=async()=>{
 const input=document.getElementById("token"), token=input.value;input.value="";
 try{const r=await fetch("/start",{method:"POST",headers:{authorization:"Bearer "+token}});
 out.textContent=JSON.stringify(await r.json(),null,2);}
 catch{out.textContent="Запуск не удался";}
};
refresh();
</script></html>`,{
  headers:{
    "content-type":"text/html; charset=utf-8",
    "cache-control":"no-store",
    "x-content-type-options":"nosniff",
    "referrer-policy":"no-referrer",
    "content-security-policy":"default-src 'none'; connect-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
  }
});

export default {
  async fetch(request,env) {
    const pathname=new URL(request.url).pathname;
    if(request.method==="GET" && pathname==="/") return page();
    if(request.method==="GET" && pathname==="/health")
      return responseJson({lab:"cloudflare-only-free-agent",ready:!!env.AI});
    if(request.method==="GET" && pathname==="/status"){
      const agent=await getAgentByName(env.AnonymousFreeAgent,INSTANCE);
      return responseJson(await agent.getReceipt());
    }
    if(request.method==="POST" && pathname==="/start"){
      if(!env.LAB_ADMIN_TOKEN || env.LAB_ADMIN_TOKEN.length<32 ||
        request.headers.get("authorization")!==`Bearer ${env.LAB_ADMIN_TOKEN}`)
        return responseJson({error:"unauthorized"},401);
      const agent=await getAgentByName(env.AnonymousFreeAgent,INSTANCE);
      const result=await agent.startExperiment();
      return responseJson(result,result.error?409:202);
    }
    return responseJson({error:"not_found"},404);
  }
};
