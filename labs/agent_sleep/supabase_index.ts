// Supabase Edge Function bootstrap. Deploy this as index.ts with executor.mjs
// from the same laboratory directory. JWT gateway verification disabled: the
// exact secret Bearer token is checked by the tested handler itself.
import { createExecutorHandler } from "./executor.mjs";
const token = Deno.env.get("LAB_EXECUTOR_TOKEN") ?? "";
if (token.length < 32) throw Error("LAB_EXECUTOR_TOKEN missing");
Deno.serve(createExecutorHandler(token));
