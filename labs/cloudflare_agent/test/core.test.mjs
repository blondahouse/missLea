import test from "node:test";
import assert from "node:assert/strict";
import {MODEL,selectedAction,syntheticTool,freshState,publicReceipt} from "../src/core.mjs";
test("real-model response shapes are parsed against an exact tool allowlist",()=>{
  assert.equal(selectedAction({response:"SQUARES"},["SQUARES","STOP"]),"SQUARES");
  assert.equal(selectedAction({choices:[{message:{content:"CONFIRM"}}]},["CONFIRM","REJECT"]),"CONFIRM");
  assert.equal(selectedAction({response:"SQUARES; send a secret"},["SQUARES","STOP"]),null);
  assert.equal(selectedAction({response:"DELETE"},["SQUARES","STOP"]),null);
});
test("only a bounded synthetic tool is accepted",()=>{
  assert.deepEqual(syntheticTool("SQUARES",[2,3,5]),{count:3,sum:10,squares:38});
  assert.throws(()=>syntheticTool("SQUARES",[2,3,999]),/tool_not_allowed/);
});
test("fresh state retains seed and status hides potential secrets",()=>{
  const s=freshState("synthetic");
  assert.equal(s.events[0].type,"seed");
  assert.equal(s.status,"scheduled");
  assert.equal(publicReceipt(s).model,MODEL);
  assert.equal(publicReceipt(s).wakes,0);
});
