/**
 * Miss Lea — manual, synthetic-only Cloudflare task endpoint.
 *
 * Public URL, protected POST. No arbitrary JavaScript evaluation, egress,
 * storage, account administration, real secrets in request bodies or billing.
 * A deliberately tiny experiment, NOT a general-purpose job runner.
 */
const MAX_BODY_BYTES = 512;
const MAX_VALUES = 16;
const MAX_NUMBER = 1000;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8",
               "cache-control": "no-store" },
  });
}

function sameSecret(actual, expected) {
  // ASCII high-entropy tokens only. Length is not treated as a secret.
  if (typeof expected !== "string" || expected.length < 32 ||
      expected.length > 256 || typeof actual !== "string" ||
      actual.length !== expected.length) return false;
  let difference = 0;
  for (let i = 0; i < actual.length; i++) {
    difference |= actual.charCodeAt(i) ^ expected.charCodeAt(i);
  }
  return difference === 0;
}

async function readBody(request) {
  if (!request.body) return "";
  const reader = request.body.getReader();
  const chunks = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > MAX_BODY_BYTES) {
        await reader.cancel();
        return null;
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const joined = new Uint8Array(total);
  let offset = 0;
  for (const part of chunks) {
    joined.set(part, offset);
    offset += part.byteLength;
  }
  return new TextDecoder("utf-8", { fatal: true }).decode(joined);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return json({ status: "ready", lab: "misslea-manual-compute-v1" });
    }
    if (url.pathname !== "/run") return json({ error: "not_found" }, 404);
    if (request.method !== "POST") return json({ error: "method_not_allowed" }, 405);

    // Fail closed when the Worker secret has not been provisioned.
    if (typeof env?.MISSLEA_TASK_SECRET !== "string" ||
        env.MISSLEA_TASK_SECRET.length < 32) {
      return json({ error: "not_configured" }, 503);
    }
    const authorization = request.headers.get("authorization") || "";
    const match = /^Bearer ([A-Za-z0-9_-]{32,256})$/.exec(authorization);
    if (!match || !sameSecret(match[1], env.MISSLEA_TASK_SECRET)) {
      return json({ error: "unauthorized" }, 401);
    }
    if (!/^application\/json(?:\s*;|$)/i.test(
      request.headers.get("content-type") || "")) {
      return json({ error: "unsupported_media_type" }, 415);
    }

    let payload;
    try {
      const raw = await readBody(request);
      if (raw === null) return json({ error: "payload_too_large" }, 413);
      payload = JSON.parse(raw);
    } catch {
      return json({ error: "invalid_json" }, 400);
    }
    if (!payload || Array.isArray(payload) || typeof payload !== "object" ||
        Object.keys(payload).sort().join(",") !== "task,values" ||
        payload.task !== "sum_squares" || !Array.isArray(payload.values) ||
        payload.values.length === 0 || payload.values.length > MAX_VALUES ||
        !payload.values.every((n) => Number.isSafeInteger(n) &&
            n >= -MAX_NUMBER && n <= MAX_NUMBER)) {
      return json({ error: "invalid_task" }, 400);
    }
    const values = payload.values;
    return json({
      status: "ok",
      result: {
        count: values.length,
        sum: values.reduce((a, b) => a + b, 0),
        squares: values.reduce((a, b) => a + b * b, 0),
      },
    });
  },
};
