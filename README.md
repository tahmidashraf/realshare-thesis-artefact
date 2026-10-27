# RealShare — ERC-1155 Fractional Real-Estate Tokenization (Performance Benchmark)

Reproducible benchmark suite for the **RealShare** fractional real-estate design: an
ERC-1155 contract (each property a token ID, fractionalised into fungible units),
evaluated on a local Hardhat EVM and on the **live Polygon Amoy** and **Ethereum Sepolia**
public testnets. This repository is the artefact for the MSc thesis *RealShare: an ERC-1155
Fractional Real-Estate Tokenization Platform*, and it holds the code, the raw results and
the reports behind Experiments 1-17 and the analytical assessment of Chapter 4.
[`REPRODUCIBILITY_MATRIX.md`](REPRODUCIBILITY_MATRIX.md) maps every measured result in the
thesis to a script, a command and a raw output file.

## On-chain deployment (independently verifiable)

| Network | Contract address | Deploy tx |
|---|---|---|
| Polygon Amoy | `0x40aBAe00C9308159e66Bf86fCF6E33df175732AE` | [`0x81f7bbf5…3b614d228`](https://amoy.polygonscan.com/tx/0x81f7bbf5789f9fe3afb3fa15246c5403e6a527db67d69bec104875c3b614d228) |
| Ethereum Sepolia | `0x40aBAe00C9308159e66Bf86fCF6E33df175732AE` | [`0x4123ee6b…db32008e`](https://sepolia.etherscan.io/tx/0x4123ee6bf7cc7ac56421cb5c97fb201c53589aa828a0fd3c4ed51a56db32008e) |

The full per-transaction hash list is in [`results/`](results/), and the live sessions are
indexed in [`results/live-network/LIVE_TRANSACTION_INDEX.csv`](results/live-network/LIVE_TRANSACTION_INDEX.csv).

## Layout

```
contracts/
  RealShareERC1155.sol         # contract under test
  baselines/RealShareERC721.sol, RealShareERC20.sol   # token-standard comparison baselines
scripts/experiments/
  exp04_network_comparison.js  # live deploy + workflow (gas + latency) per network
  exp05_gas_fees.js            # per-operation gas
  exp06_latency.js             # confirmation-latency sampling (EXP06_TXNS sets N)
  exp08_scalability.js         # concurrent-mint stress test (SCAL_LEVELS)
  exp_gasbench.js              # full local gas benchmark (workflow, scaling, ERC comparison, TPS, batch)
api/                           # REST API + Experiment 14 security suite (node exp14_security_test.js)
results/                       # machine-generated JSON results
```

## Quick start

```bash
npm install
npx hardhat compile                       # solc 0.8.27, EVM cancun
npx hardhat run scripts/experiments/exp_gasbench.js        # local gas benchmark

# Live runs require a funded test wallet in .env (copy .env.example):
EXP06_TXNS=100 npx hardhat run scripts/experiments/exp06_latency.js --network polygonAmoy
npx hardhat run scripts/experiments/exp04_network_comparison.js --network sepolia
```

Network names (`hardhat.config.js`): `polygonAmoy` (chainId 80002), `sepolia` (chainId 11155111).

## Security note

Never commit `.env` or any private key. The throwaway test wallet used for the testnet
runs holds only valueless testnet tokens; `.gitignore` excludes secrets.

## License

MIT — see [LICENSE](LICENSE).
