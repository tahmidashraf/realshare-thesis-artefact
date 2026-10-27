/**
 * Verify that every transaction hash recorded in the live-network session files (and the
 * existing exp04/exp06 evidence) exists on-chain and matches the recorded block/status.
 * Usage: npx hardhat run scripts/analysis/verify_transaction_hashes.js --network polygonAmoy
 * (run per network; needs read-only RPC access, no funded wallet).
 *
 * Also builds LIVE_TRANSACTION_INDEX.csv from all recorded sessions.
 */
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const netDir = path.join(__dirname, "..", "..", "results", "live-network", hre.network.name);
  const rows = [];
  if (fs.existsSync(netDir)) {
    for (const f of fs.readdirSync(netDir).filter((x) => x.endsWith(".json"))) {
      const s = JSON.parse(fs.readFileSync(path.join(netDir, f), "utf8"));
      for (const op of s.operations || []) {
        if (!op.txHash) continue;
        let verified = "unverified", onchainBlock = null;
        try {
          const rc = await hre.ethers.provider.getTransactionReceipt(op.txHash);
          if (rc) { onchainBlock = rc.blockNumber; verified = (rc.blockNumber === op.blockNumber && rc.status === op.status) ? "MATCH" : "MISMATCH"; }
          else verified = "NOT_FOUND";
        } catch (e) { verified = "RPC_ERROR"; }
        rows.push({ session: s.tag, op: op.label, txHash: op.txHash, recordedBlock: op.blockNumber, onchainBlock, status: op.status, verified });
      }
    }
  }
  const csvPath = path.join(__dirname, "..", "..", "results", "live-network", `LIVE_TRANSACTION_INDEX_${hre.network.name}.csv`);
  const header = "session,op,txHash,recordedBlock,onchainBlock,status,verified\n";
  fs.writeFileSync(csvPath, header + rows.map((r) => `${r.session},${r.op},${r.txHash},${r.recordedBlock},${r.onchainBlock},${r.status},${r.verified}`).join("\n"));
  console.log(`Verified ${rows.length} transactions on ${hre.network.name}. Wrote ${csvPath}`);
  const bad = rows.filter((r) => r.verified !== "MATCH");
  if (bad.length) { console.error(`${bad.length} unverified/mismatched:`, bad.slice(0, 5)); process.exitCode = 2; }
}

main().catch((e) => { console.error(e); process.exit(1); });
