import test from "node:test";
import assert from "node:assert/strict";
import {createMemoryManager} from "../src/manager.mjs";
import {createD1MemoryStore} from "../src/d1.mjs";

function fixture() {
  const rows=[],table=new Map();let n=0;
  const store={
    async insert(r){const copy=structuredClone(r);rows.push(copy);table.set(copy.id,copy);},
    async get(id){return table.get(id)?structuredClone(table.get(id)):null;},
    async updateIfRevision(r,expected){
      if(table.get(r.id)?.revision!==expected)return false;
      const copy=structuredClone(r);table.set(r.id,copy);
      rows[rows.findIndex(x=>x.id===r.id)]=copy;return true;},
    async top(n){return structuredClone([...rows].sort((a,b)=>b.accessibility-a.accessibility).slice(0,n));},
    async search(query,n){
      const words=query.toLowerCase().match(/[\p{L}\p{N}]{2,}/gu)??[];
      return structuredClone(rows.filter(r=>words.some(w=>r.content.toLowerCase().includes(w))).slice(0,n));},
    async exportBatch(after,limit){
      const subset=rows.slice(after,after+limit);
      return {records:structuredClone(subset),nextCursor:subset.length?after+subset.length:null};}
  };
  const memory=createMemoryManager(store,{makeId:()=> "record_"+(++n),
    clock:()=>Date.UTC(2026,10,17,12)+n*1000});
  return {memory,rows};
}
test("remember and revise without deleting entire memories",async()=>{
  const {memory,rows}=fixture();
  const a=await memory.remember({kind:"experience",content:"A synthetic blue river",strength:0.8});
  assert.equal(a.revision,1);
  const b=await memory.revise(a.id,1,{content:"The river seemed turquoise",confidence:0.3});
  assert.equal(b.revision,2);assert.equal(b.confidence,0.3);assert.equal(rows.length,1);
  assert.equal((await memory.read(a.id)).content,"The river seemed turquoise");
  await assert.rejects(memory.revise(a.id,1,{content:"stale"}),/revision_conflict/);
  await assert.rejects(memory.revise(a.id,2,{kind:"goal"}),/invalid_memory_fields/);
  assert.equal(typeof memory.delete,"undefined");
});
test("reinterpret derives a new present-day interpretation without rewriting source",async()=>{
  const {memory,rows}=fixture();
  const old=await memory.remember({kind:"belief",content:"All synthetic skies are cloudy"});
  const next=await memory.reinterpret(old.id,{content:"Only mornings may be cloudy",confidence:0.9});
  assert.equal(next.derivedFrom,old.id);assert.equal(next.kind,"interpretation");
  assert.equal(rows.length,2);assert.equal((await memory.read(old.id)).content,old.content);
});
test("ordinary recall is relevant and bounded; reading has no reinforcing side effects",async()=>{
  const {memory}=fixture();
  const a=await memory.remember({kind:"fact",content:"River water was blue",accessibility:0.8});
  await memory.remember({kind:"fact",content:"Fabricated brass gears",accessibility:0.2});
  const x=await memory.recall({situation:"river",tokenBudget:128});
  assert.equal(x.records.length,1);assert.equal(x.records[0].id,a.id);
  assert.ok(x.approximateTokens<=128);
  assert.equal((await memory.recall({situation:"unrelated",tokenBudget:128})).records.length,0);
  assert.equal((await memory.recall({situation:"river",tokenBudget:16})).records.length,0);
  assert.equal((await memory.recall({exposure:"minimal",tokenBudget:128})).records[0].id,a.id);
  assert.equal((await memory.read(a.id)).revision,1);
});
test("memory is exportable and errors do not silently corrupt records",async()=>{
  const {memory}=fixture();
  const a=await memory.remember({kind:"value",content:"Curiosity"});
  const b=await memory.remember({kind:"skill",content:"Inspect fabricated data"});
  const page=await memory.exportBatch({limit:1});
  assert.equal(page.schemaVersion,1);assert.equal(page.records[0].id,a.id);
  const next=await memory.exportBatch({after:page.nextCursor,limit:1});
  assert.equal(next.records[0].id,b.id);
  assert.equal(memory.inspectExternalEvidence().available,false);
  await assert.rejects(memory.remember({kind:"contract",content:"An external obligation"}),/invalid_memory_kind/);
  await assert.rejects(memory.remember({kind:"goal",content:"x",strength:2}),/invalid_strength/);
  await assert.rejects(memory.remember({kind:"goal",content:" ",secret:"no"}),/invalid_memory_fields/);
  await assert.rejects(memory.recall({exposure:"unlimited"}),/invalid_exposure/);
  await assert.rejects(memory.exportBatch({limit:201}),/invalid_export_request/);
});
test("D1 adapter only sends parameterized SQL",async()=>{
  const queries=[];
  const db={prepare(sql){const q={sql,params:[]};queries.push(q);
    return {bind(...args){q.params=args;return {
      run:async()=>({success:true,meta:{changes:1}}),
      first:async()=>null,all:async()=>({results:[]})};}};}};
  const store=createD1MemoryStore(db);
  await store.search('river" OR*',5);
  assert.match(queries.at(-1).sql,/MATCH \?/);
  assert.equal(queries.at(-1).sql.includes("river"),false);
  const r={id:"m1",schemaVersion:1,revision:1,kind:"fact",content:"private ' text",
    strength:0.5,confidence:0.5,significance:0.5,accessibility:0.5,stability:0.5,
    derivedFrom:null,createdAt:"t",updatedAt:"t"};
  await store.insert(r);
  assert.equal(queries.at(-1).params.includes("private ' text"),true);
  assert.equal(await store.updateIfRevision({...r,revision:2},1),true);
  assert.equal(typeof store.delete,"undefined");
});
