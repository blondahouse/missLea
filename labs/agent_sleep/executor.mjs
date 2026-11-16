// Stateless Deno Deploy Free candidate: synthetic and safe to retry.
const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store"}
});
export function createExecutorHandler(token) {
  return async function handle(request) {
    if (!token || request.headers.get("authorization") !== `Bearer ${token}`)
      return json({error:"unauthorized"}, 401);
    if (request.method !== "POST") return json({error:"method_not_allowed"}, 405);
    let data;
    try { data = await request.json(); } catch { return json({error:"invalid_json"}, 400); }
    if (!/^[a-f0-9-]{36}:[12]$/.test(data?.job_id ?? "") ||
        !Array.isArray(data?.values) || data.values.length !== 3 ||
        !data.values.every((n,i) => Number.isInteger(n) && n === [2,3,5][i]) ||
        !Number.isInteger(data?.prior_event_count) ||
        data.prior_event_count < 1 || data.prior_event_count > 3)
      return json({error:"invalid_task"}, 400);
    return json({
      count:data.values.length,
      sum:data.values.reduce((a,b) => a+b, 0),
      squares:data.values.reduce((a,b) => a+b*b, 0),
      prior_event_count:data.prior_event_count
    });
  };
}
if (import.meta.main) {
  const token = Deno.env.get("LAB_EXECUTOR_TOKEN");
  if (!token || token.length < 32) throw Error("LAB_EXECUTOR_TOKEN missing");
  Deno.serve(createExecutorHandler(token));
}
