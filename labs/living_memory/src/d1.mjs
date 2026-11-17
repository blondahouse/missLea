// Parameterized Cloudflare D1 adapter; no SQL access escapes this boundary.
export function createD1MemoryStore(db) {
  if(typeof db?.prepare!=="function") throw Error("missing_d1_binding");
  const columns="id,schema_version,revision,kind,content,strength,confidence,significance,accessibility,stability,derived_from,created_at,updated_at";
  const select="SELECT seq,"+columns+" FROM living_memory";
  const joinedSelect="SELECT "+("seq,"+columns).split(",").map(column=>"living_memory."+column).join(",")+" FROM living_memory";
  const decode=r=>r?{id:r.id,schemaVersion:r.schema_version,revision:r.revision,
    kind:r.kind,content:r.content,strength:r.strength,confidence:r.confidence,
    significance:r.significance,accessibility:r.accessibility,stability:r.stability,
    derivedFrom:r.derived_from,createdAt:r.created_at,updatedAt:r.updated_at}:null;
  async function get(id) {
    return decode(await db.prepare(select+" WHERE id=?").bind(id).first());
  }
  async function insert(r) {
    await db.prepare("INSERT INTO living_memory ("+columns+") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)")
      .bind(r.id,r.schemaVersion,r.revision,r.kind,r.content,r.strength,r.confidence,
        r.significance,r.accessibility,r.stability,r.derivedFrom,r.createdAt,r.updatedAt).run();
  }
  async function updateIfRevision(r,expected) {
    const result=await db.prepare("UPDATE living_memory SET revision=?,content=?,"+
      "strength=?,confidence=?,significance=?,accessibility=?,stability=?,updated_at=? "+
      "WHERE id=? AND revision=?")
      .bind(r.revision,r.content,r.strength,r.confidence,r.significance,
        r.accessibility,r.stability,r.updatedAt,r.id,expected).run();
    if(!result?.success) throw Error("update_unconfirmed");
    return result.meta?.changes===1;
  }
  async function top(limit) {
    const r=await db.prepare(select+" ORDER BY accessibility DESC,significance DESC,seq DESC LIMIT ?")
      .bind(limit).all();
    return (r.results??[]).map(decode);
  }
  async function search(situation,limit) {
    const words=situation.match(/[\p{L}\p{N}]{2,}/gu)?.slice(0,8)??[];
    if(!words.length) return [];
    const term=words.map(w=>'"'+w+'"*').join(" OR ");
    const r=await db.prepare(joinedSelect+" JOIN living_memory_fts ON "+
      "living_memory_fts.rowid=living_memory.seq WHERE living_memory_fts MATCH ? "+
      "ORDER BY bm25(living_memory_fts),living_memory.accessibility DESC LIMIT ?")
      .bind(term,limit).all();
    return (r.results??[]).map(decode);
  }
  async function exportBatch(after,limit) {
    const r=await db.prepare(select+" WHERE seq>? ORDER BY seq LIMIT ?").bind(after,limit).all();
    const rows=r.results??[];
    return {records:rows.map(decode),nextCursor:rows.length?rows.at(-1).seq:null};
  }
  return Object.freeze({get,insert,updateIfRevision,top,search,exportBatch});
}
