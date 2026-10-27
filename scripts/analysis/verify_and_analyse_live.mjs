import { ethers } from "ethers";
import fs from "fs"; import path from "path";
const RPCS = { sepolia: "https://ethereum-sepolia-rpc.publicnode.com", polygonAmoy: "https://rpc-amoy.polygon.technology" };
function stats(a){ if(!a.length) return null; const s=[...a].sort((x,y)=>x-y),n=s.length,mean=s.reduce((x,y)=>x+y,0)/n;
  const sd=Math.sqrt(s.reduce((x,y)=>x+(y-mean)**2,0)/n); const pct=p=>s[Math.min(n-1,Math.ceil(p/100*n)-1)];
  return {n,mean:+mean.toFixed(0),median:s[Math.floor(n/2)],sd:+sd.toFixed(0),min:s[0],max:s[n-1],p90:pct(90),p95:pct(95),cv:+(sd/mean).toFixed(3)}; }
const idx=[]; const perSession={};
for (const net of Object.keys(RPCS)) {
  const dir=path.join("results","live-network",net); if(!fs.existsSync(dir)) continue;
  const provider=new ethers.JsonRpcProvider(RPCS[net]);
  for (const f of fs.readdirSync(dir).filter(x=>x.startsWith("session_")&&x.endsWith(".json"))) {
    const s=JSON.parse(fs.readFileSync(path.join(dir,f)));
    const lats=[];
    for (const op of s.operations||[]) {
      if(!op.txHash) continue;
      let verified="unchecked", onchainBlock=null;
      try { const rc=await provider.getTransactionReceipt(op.txHash);
        if(rc){onchainBlock=rc.blockNumber; verified=(rc.status===op.status&&rc.blockNumber===op.block)?"MATCH":"MISMATCH";} else verified="NOT_FOUND"; }
      catch(e){ verified="RPC_ERR"; }
      idx.push({network:net,session:s.tag,op:op.label,txHash:op.txHash,block:op.block,onchainBlock,status:op.status,gasUsed:op.gasUsed,latencyMs:op.confirmationLatencyMs,verified});
      if(op.confirmationLatencyMs) lats.push(op.confirmationLatencyMs);
    }
    if(lats.length){ perSession[`${net}/${s.tag}/${(s.timestamp||'').slice(0,10)}`]=stats(lats); }
  }
}
fs.mkdirSync("results/live-network/processed",{recursive:true});
const header="network,session,op,txHash,block,onchainBlock,status,gasUsed,latencyMs,verified\n";
fs.writeFileSync("results/live-network/LIVE_TRANSACTION_INDEX.csv", header+idx.map(r=>Object.values(r).join(",")).join("\n"));
// session-to-session for sepolia (today's live confirmations)
const out={perSession, verifiedCount:idx.filter(r=>r.verified==="MATCH").length, total:idx.length,
  mismatches:idx.filter(r=>r.verified!=="MATCH").map(r=>({tx:r.txHash,v:r.verified}))};
fs.writeFileSync("results/live-network/processed/session_variability.json", JSON.stringify(out,null,2));
console.log("verified", out.verifiedCount, "/", out.total, "transactions");
console.log("per-session latency stats:"); for(const[k,v] of Object.entries(perSession)) console.log(" ",k, JSON.stringify(v));
