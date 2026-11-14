// Disposable, synthetic probe. No user data, LLM calls or external dependencies.
export default {
  async fetch(request, env) {
    if (request.headers.get("X-Lab-Token") !== env.LAB_TOKEN) {
      return new Response("Forbidden", { status: 403 });
    }
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }
    let payload;
    try {
      payload = await request.json();
    } catch (_) {
      return new Response("Bad JSON", { status: 400 });
    }
    if (!Array.isArray(payload.values) || payload.values.length !== 3 ||
        !payload.values.every(x => Number.isSafeInteger(x))) {
      return new Response("Invalid values", { status: 400 });
    }
    const values = payload.values;
    const result = {
      count: values.length,
      sum: values.reduce((a, b) => a + b, 0),
      squares: values.reduce((a, b) => a + b * b, 0)
    };
    return Response.json({ result });
  }
};
