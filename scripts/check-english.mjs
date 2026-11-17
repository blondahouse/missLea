// Repository-wide text language check. Architecture, code UI, fixtures and docs must be English.
import {readdirSync,readFileSync,statSync} from "node:fs";
import {join,relative,resolve} from "node:path";
const root=resolve(new URL("..",import.meta.url).pathname);
const extensions=new Set([".md",".html",".css",".mjs",".js",".ts",".py",".json",".yaml",".yml",".toml",".sh",".txt"]);
const ignored=new Set([".git","node_modules",".venv","venv","__pycache__","reports"]);
let checked=0;const offenders=[];
function walk(dir){
 for(const name of readdirSync(dir)){
  if(ignored.has(name))continue;
  const path=join(dir,name);
  if(statSync(path).isDirectory()){walk(path);continue;}
  const ext=name.slice(name.lastIndexOf(".")).toLowerCase();
  if(!extensions.has(ext))continue;
  checked++;
  const lines=readFileSync(path,"utf8").split("\n");
  for(let i=0;i<lines.length;i++){
   if(/[\u0400-\u04FF]/u.test(lines[i]))offenders.push(relative(root,path)+":"+(i+1));
  }
 }
}
walk(root);
if(offenders.length){console.error("Non-English Cyrillic text found:\n"+offenders.join("\n"));process.exitCode=1;}
else console.log("PASS: English-only text check ("+checked+" files)");
