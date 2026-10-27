/**
 * Analyse the multi-investor token benchmark raw JSON into processed CSVs and a summary.
 * Usage: node scripts/analysis/analyse_token_benchmarks.js [rawfile.json]
 */
const fs = require("fs");
const path = require("path");

const RAW_DIR = path.join(__dirname, "..", "..", "results", "token-benchmarks", "raw");
const PROC_DIR = path.join(__dirname, "..", "..", "results", "token-benchmarks", "processed");

function latestRaw() {
  const files = fs.readdirSync(RAW_DIR).filter((f) => f.startsWith("multi_investor_") && f.endsWith(".json"));
  files.sort();
  return path.join(RAW_DIR, files[files.length - 1]);
}

const rawFile = process.argv[2] || latestRaw();
const d = JSON.parse(fs.readFileSync(rawFile, "utf8"));
const g = (x) => (x && x.totalGas && typeof x.totalGas === "object" ? x.totalGas.mean : (x && x.totalGas) || "");

// Benchmark A CSV
let a = "units,erc1155_gas,erc1155_gasPerUnit,erc20_gas,erc20_gasPerUnit,erc721_gas,erc721_gasPerUnit,erc721_tokenIds\n";
for (const X of Object.keys(d.A)) {
  const r = d.A[X];
  a += `${X},${g(r.erc1155)},${r.erc1155.gasPerUnit.toFixed(1)},${g(r.erc20)},${r.erc20.gasPerUnit.toFixed(1)},${g(r.erc721)},${r.erc721.gasPerUnit.toFixed(1)},${r.erc721.tokenIds}\n`;
}
fs.writeFileSync(path.join(PROC_DIR, "benchmarkA_single_holder.csv"), a);

// Benchmark B CSV
let b = "investors,erc1155_gas,erc1155_perInvestor,erc1155_tx,erc20_gas,erc20_perInvestor,erc721_gas,erc721_perInvestor,erc1155_individual_gas\n";
for (const X of Object.keys(d.B)) {
  const r = d.B[X];
  b += `${X},${r.erc1155.totalGas},${r.erc1155.gasPerInvestor.toFixed(1)},${r.erc1155.txCount},${r.erc20.totalGas},${r.erc20.gasPerInvestor.toFixed(1)},${r.erc721.totalGas},${r.erc721.gasPerInvestor.toFixed(1)},${r.erc1155_individual ? r.erc1155_individual.totalGas : ""}\n`;
}
fs.writeFileSync(path.join(PROC_DIR, "benchmarkB_multi_investor.csv"), b);

// Benchmark C CSV
let c = "properties,erc1155_gas,erc1155_contracts,erc20_gas,erc20_contracts,erc721_gas,erc721_contracts\n";
for (const P of Object.keys(d.C)) {
  const r = d.C[P];
  c += `${P},${r.erc1155.totalGas},1,${r.erc20.totalGas},${r.erc20.deployedContracts},${r.erc721.totalGas},1\n`;
}
fs.writeFileSync(path.join(PROC_DIR, "benchmarkC_multi_property.csv"), c);

// Summary markdown
let s = `# Token-Standard Benchmark — Processed Summary\n\n`;
s += `Source raw file: \`${path.basename(rawFile)}\`\n\n`;
s += `Environment: solc ${d.env.solc}; OZ ${d.env.openzeppelin}; Hardhat ${d.env.hardhat}; ethers ${d.env.ethers}; `;
s += `Node ${d.env.node}; ${d.env.os}; ${d.env.cpu} (${d.env.cpuCores} cores, ${d.env.ramGB} GB); block gas limit ${d.env.blockGasLimit}; reps ${d.env.reps}.\n\n`;

s += `## Determinism check\n\n`;
for (const [k, v] of Object.entries(d.determinism || {})) {
  s += `- ${k}: gas = ${v.gas.mean}, SD = ${v.gas.sd}, identical across ${v.samples} runs = ${v.allIdentical}\n`;
}

s += `\n## Benchmark A — single-holder issuance (gas per unit is amortised, not a per-write cost)\n\n`;
s += `| Units | ERC-1155 gas | ERC-20 gas | ERC-721 gas | ERC-721 token IDs |\n|--:|--:|--:|--:|--:|\n`;
for (const X of Object.keys(d.A)) { const r = d.A[X]; s += `| ${X} | ${g(r.erc1155)} | ${g(r.erc20)} | ${g(r.erc721)} | ${r.erc721.tokenIds} |\n`; }

s += `\n## Benchmark B — multi-investor distribution (1 unit to each of X investors)\n\n`;
s += `| Investors | ERC-1155 gas (tx) | per investor | ERC-20 gas | per inv. | ERC-721 gas | per inv. |\n|--:|--:|--:|--:|--:|--:|--:|\n`;
for (const X of Object.keys(d.B)) {
  const r = d.B[X];
  s += `| ${X} | ${r.erc1155.totalGas} (${r.erc1155.txCount}) | ${r.erc1155.gasPerInvestor.toFixed(0)} | ${r.erc20.totalGas} | ${r.erc20.gasPerInvestor.toFixed(0)} | ${r.erc721.totalGas} | ${r.erc721.gasPerInvestor.toFixed(0)} |\n`;
}

s += `\n## Benchmark C — multiple properties (ERC-1155 one contract vs ERC-20 one-contract-per-property)\n\n`;
s += `| Properties | ERC-1155 gas (1 contract) | ERC-20 gas (N contracts) | ERC-721 gas (1 contract) |\n|--:|--:|--:|--:|\n`;
for (const P of Object.keys(d.C)) { const r = d.C[P]; s += `| ${P} | ${r.erc1155.totalGas} | ${r.erc20.totalGas} (${r.erc20.deployedContracts}) | ${r.erc721.totalGas} |\n`; }

s += `\n## Benchmark D — secondary transfers\n\n`;
s += `- ERC-1155 one-to-one transfer: ${d.D.erc1155.oneToOne} gas; two-id batch: ${d.D.erc1155.batchTwoIds} gas.\n`;
if (d.D.oneToMany10) s += `- One-to-many (10 recipients): ERC-1155 ${d.D.oneToMany10.erc1155.totalGas} (${d.D.oneToMany10.erc1155.gasPerRecipient.toFixed(0)}/recipient); ERC-20 ${d.D.oneToMany10.erc20.totalGas} (${d.D.oneToMany10.erc20.gasPerRecipient.toFixed(0)}/recipient).\n`;
if (d.D.manyToOne5) s += `- Many-to-one (5 senders): ERC-1155 ${d.D.manyToOne5.erc1155.totalGas} (${d.D.manyToOne5.erc1155.gasPerSender.toFixed(0)}/sender).\n`;

fs.writeFileSync(path.join(PROC_DIR, "SUMMARY.md"), s);
console.log("Wrote processed CSVs + SUMMARY.md to", PROC_DIR);
