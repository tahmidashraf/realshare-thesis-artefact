import { ethers } from "ethers";
// Verify the ORIGINAL 2026-06-21 evidence hashes are still on-chain (read-only, independent).
const checks = [
  ["Amoy deploy", "https://rpc-amoy.polygon.technology", "0x81f7bbf5789f9fe3afb3fa15246c5403e6a527db67d69bec104875c3b614d228", 40537293],
  ["Amoy mintFractions", "https://rpc-amoy.polygon.technology", "0x9cd9e0cb7d1f4732366b97effb6626b39f9adc68f3f8e6447e09ab9d4c1f9045", 40537303],
  ["Sepolia deploy", "https://ethereum-sepolia-rpc.publicnode.com", "0x4123ee6bf7cc7ac56421cb5c97fb201c53589aa828a0fd3c4ed51a56db32008e", 11108169],
  ["Sepolia mintFractions", "https://ethereum-sepolia-rpc.publicnode.com", "0x1cb04993bf57a48c3229bb02d24e1ae50c967545c4b57db225f3e93827f313a1", 11108173],
];
for (const [label, url, hash, expBlock] of checks) {
  try {
    const p = new ethers.JsonRpcProvider(url);
    const rc = await p.getTransactionReceipt(hash);
    if (!rc) { console.log(`${label}: NOT FOUND`); continue; }
    const ok = rc.status === 1 && rc.blockNumber === expBlock;
    console.log(`${label}: status=${rc.status} block=${rc.blockNumber} (expect ${expBlock}) -> ${ok ? "VERIFIED" : "MISMATCH"} gas=${rc.gasUsed}`);
  } catch (e) { console.log(`${label}: RPC error ${String(e.message).slice(0,50)}`); }
}
