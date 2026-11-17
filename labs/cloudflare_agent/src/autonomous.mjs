// Cloudflare-only integration for the portable, synthetic Agent Core.
// A separate Worker/DO leaves the verified AnonymousFreeAgent untouched.
import { Agent, getAgentByName } from "agents";
import { startRun, wake as runCoreWake } from "../../agent_core/src/runtime.mjs";
import { blockWake } from "../../agent_core/src/core.mjs";
import { canHandleScheduledWake, safeStatus } from "./autonomous_support.mjs";

const MODEL = "@cf/google/gemma-4-26b-a4b-it";
const INSTANCE = "synthetic-agent-core-v0";
const json = (value, status = 200) => Response.json(value, {
  status, headers: {
    "cache-control": "no-store",
    "x-content-type-options": "nosniff"
  }
});
const emptyState = () => ({
  schema: 1, mode: "synthetic", runId: null, status: "not_started",
  intent: null, notes: [], events: [], wakes: 0, modelCalls: 0, toolCalls: 0,
  daily: {date: "1970-01-01", wakes: 0},
  nextWakeAt: null, reason: null
});

export class SyntheticCoreAgent extends Agent {
  initialState = emptyState();

  // A safety margin prevents an early callback from being ignored.
  async scheduleNext({runId, at}) {
    const timestamp = Date.parse(at);
    if (!Number.isFinite(timestamp)) throw Error("invalid_schedule");
    await this.schedule(new Date(timestamp + 2000), "wake", {runId, scheduledAt: at});
  }

  async startExperiment() {
    if (["scheduled", "running"].includes(this.state?.status))
      return {error: "already_running"};
    const runId = crypto.randomUUID();
    try {
      return await startRun({
        runId, save: async state => this.setState(state),
        schedule: params => this.scheduleNext(params)
      });
    } catch {
      return {error: "start_failed"};
    }
  }

  async getReceipt() { return safeStatus(this.state ?? emptyState()); }

  async wake(payload) {
    if (!canHandleScheduledWake(this.state, payload)) return;
    try {
      await runCoreWake({
        runId: payload.runId,
        load: async () => this.state,
        save: async state => this.setState(state),
        schedule: params => this.scheduleNext(params),
        infer: async messages => {
          // Short verification timing only; intent/tool remain model-chosen.
          const guided = [
            {...messages[0], content: messages[0].content +
              " For this bounded integration test, if possible plan a follow-up wake" +
              " in 60 to 90 seconds so continuity can be observed."},
            messages[1]
          ];
          return await this.env.AI.run(MODEL, {
            messages: guided,
            max_tokens: 256,
            chat_template_kwargs: {enable_thinking: false}
          });
        }
      });
    } catch {
      // An interrupted inference must not be replayed automatically.
      if (this.state?.status === "running") {
        this.setState(blockWake(this.state, "model_or_quota_failed"));
      }
    }
  }
}

export default {
  async fetch(request, env) {
    const pathname = new URL(request.url).pathname;
    if (request.method === "GET" && pathname === "/health")
      return json({lab: "synthetic-agent-core-v0", ready: !!env.AI});
    if (request.method === "GET" && pathname === "/")
      return json({lab: "synthetic-agent-core-v0", synthetic: true,
        message: "Autonomous research agent. No personal or production data."});
    if (request.method === "GET" && pathname === "/status") {
      const agent = await getAgentByName(env.SyntheticCoreAgent, INSTANCE);
      return json(await agent.getReceipt());
    }
    if (request.method === "POST" && pathname === "/start") {
      if (!env.LAB_ADMIN_TOKEN || env.LAB_ADMIN_TOKEN.length < 32 ||
          request.headers.get("authorization") !== "Bearer " + env.LAB_ADMIN_TOKEN)
        return json({error: "unauthorized"}, 401);
      const agent = await getAgentByName(env.SyntheticCoreAgent, INSTANCE);
      const response = await agent.startExperiment();
      return json(response, response.error ? 409 : 202);
    }
    return json({error: "not_found"}, 404);
  }
};
