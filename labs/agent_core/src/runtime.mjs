import {
  initialState, beginWake, modelMessages, parseDecision, syntheticTool,
  finishWake, blockWake, publicReceipt
} from "./core.mjs";

// Injected ports: storage, scheduling, inference. No provider SDK in the core.
export async function startRun({runId, save, schedule, clock = Date.now}) {
  const state = initialState(runId, clock());
  await save(state);
  try {
    await schedule({runId, at: state.nextWakeAt});
    return publicReceipt(state);
  } catch {
    const blocked = blockWake(state, "schedule_failed");
    await save(blocked);
    return publicReceipt(blocked);
  }
}
export async function wake({runId, load, save, infer, schedule, clock = Date.now}) {
  const current = await load();
  const transition = beginWake(current, runId, clock());
  if (transition.kind === "ignored") return publicReceipt(current);
  if (transition.kind === "paused") {
    await save(transition.state);
    return publicReceipt(transition.state);
  }
  if (transition.kind === "deferred") {
    await save(transition.state);
    try {
      await schedule({runId, at: transition.state.nextWakeAt});
      return publicReceipt(transition.state);
    } catch {
      const blocked = blockWake(transition.state, "schedule_failed");
      await save(blocked);
      return publicReceipt(blocked);
    }
  }

  // Persist before inference. Interrupted calls stay running; never blind replay.
  const running = transition.state;
  await save(running);
  let decision;
  try {
    decision = parseDecision(await infer(modelMessages(running)));
  } catch (error) {
    const reason = error?.message === "invalid_decision"
      ? "invalid_decision" : "model_or_quota_failed";
    const blocked = blockWake(running, reason);
    await save(blocked);
    return publicReceipt(blocked);
  }
  let observation = null;
  try {
    if (decision.tool !== null) observation = syntheticTool(decision.tool);
  } catch {
    const blocked = blockWake(running, "tool_failed");
    await save(blocked);
    return publicReceipt(blocked);
  }
  const next = finishWake(running, decision, observation, clock());
  await save(next);
  if (next.status === "scheduled") {
    try {
      await schedule({runId, at: next.nextWakeAt});
    } catch {
      const blocked = blockWake(next, "schedule_failed");
      await save(blocked);
      return publicReceipt(blocked);
    }
  }
  return publicReceipt(next);
}
