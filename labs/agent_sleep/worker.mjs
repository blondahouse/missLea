// Bounded synthetic Cloudflare Durable Object alarm. No LLM or real memory.
const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers: {"content-type":"application/json; charset=utf-8","cache-control":"no-store"}
});

export class LabClock {
  constructor(ctx, env) { this.ctx = ctx; this.env = env; }
  async fetch(request) {
    const path = new URL(request.url).pathname;
    if (request.method === "GET" && path === "/status")
      return json((await this.ctx.storage.get("lab")) ?? {status:"not_started"});
    if (request.method !== "POST" || path !== "/schedule")
      return json({error:"not_found"}, 404);
    if (!this.env.EXECUTOR_URL || !this.env.EXECUTOR_TOKEN)
      return json({error:"executor_not_configured"}, 503);
    if (!this.env.EXECUTOR_URL.startsWith("https://"))
      return json({error:"executor_requires_https"}, 503);
    const previous = await this.ctx.storage.get("lab");
    if (previous && ["scheduled","running","retrying"].includes(previous.status))
      return json({error:"already_active"}, 409);
    let input;
    try { input = await request.json(); } catch { return json({error:"invalid_json"}, 400); }
    const seconds = input?.delay_seconds ?? 10;
    if (!Number.isInteger(seconds) || seconds < 5 || seconds > 300)
      return json({error:"delay_out_of_range"}, 400);
    const until = Date.now() + seconds * 1000;
    const state = {
      status:"scheduled", run_id:crypto.randomUUID(), wakes:0, failures:0, max_wakes:2,
      events:[{type:"seed", decision:"calculate synthetic squares"}],
      next_at:new Date(until).toISOString()
    };
    await this.ctx.storage.put("lab", state);
    await this.ctx.storage.setAlarm(until);
    return json({status:state.status,run_id:state.run_id,next_at:state.next_at}, 202);
  }
  async alarm() {
    const state = await this.ctx.storage.get("lab");
    if (!state || !["scheduled","running","retrying"].includes(state.status)) return;
    state.status = "running";
    await this.ctx.storage.put("lab", state);
    try {
      // Alarm delivery can repeat; only side-effect-free tasks are allowed.
      const response = await fetch(this.env.EXECUTOR_URL, {
        method:"POST",
        headers:{
          "authorization":`Bearer ${this.env.EXECUTOR_TOKEN}`,
          "content-type":"application/json"
        },
        body:JSON.stringify({
          job_id:`${state.run_id}:${state.wakes + 1}`,
          values:[2,3,5], prior_event_count:state.events.length
        })
      });
      if (!response.ok) throw Error("executor_unavailable");
      const output = await response.json();
      const expected = {count:3,sum:10,squares:38};
      if (Object.keys(expected).some(k => output?.[k] !== expected[k]) ||
          output?.prior_event_count !== state.events.length)
        throw Error("invalid_result");
      state.events.push({
        type:"wake",job_id:`${state.run_id}:${state.wakes+1}`,result:expected
      });
      state.wakes += 1;
      state.failures = 0;
      if (state.wakes < state.max_wakes) {
        const next = Date.now() + 10000;
        state.status = "scheduled";
        state.next_at = new Date(next).toISOString();
        await this.ctx.storage.put("lab", state);
        await this.ctx.storage.setAlarm(next);
      } else {
        state.status = "completed";
        state.next_at = null;
        await this.ctx.storage.put("lab", state);
      }
    } catch {
      state.failures += 1;
      state.status = state.failures >= 2 ? "blocked" : "retrying";
      state.next_at = state.status === "retrying"
        ? new Date(Date.now() + 60000).toISOString() : null;
      await this.ctx.storage.put("lab", state);
      if (state.status === "retrying")
        await this.ctx.storage.setAlarm(Date.now() + 60000);
      // No exception bodies, token output or paid fallback.
    }
  }
}
export default {
  async fetch(request, env) {
    if (!env.LAB_ADMIN_TOKEN ||
        request.headers.get("authorization") !== `Bearer ${env.LAB_ADMIN_TOKEN}`)
      return json({error:"unauthorized"}, 401);
    const id = env.LAB_CLOCK.idFromName("anonymous-sleep-lab");
    return env.LAB_CLOCK.get(id).fetch(request);
  }
};
