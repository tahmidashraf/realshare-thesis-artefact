# -*- coding: utf-8 -*-
"""Generate publication-quality figures from the processed token-benchmark CSVs.
Reads results/token-benchmarks/processed/*.csv; writes figures/token-benchmarks/*.png/pdf.
No hardcoded numbers - all values come from the executed benchmark output.
"""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PROC = os.path.join(ROOT, "results", "token-benchmarks", "processed")
FIG = os.path.join(ROOT, "figures", "token-benchmarks")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 150, "savefig.bbox": "tight"})
C1155, C20, C721 = "#1f77b4", "#2ca02c", "#d62728"

def readcsv(name):
    with open(os.path.join(PROC, name)) as f:
        return list(csv.DictReader(f))

def save(fig, base):
    fig.savefig(os.path.join(FIG, base + ".png"))
    fig.savefig(os.path.join(FIG, base + ".pdf"))
    plt.close(fig)

# ---- Fig 1: Benchmark A total gas vs units (log y) ----
A = readcsv("benchmarkA_single_holder.csv")
x = [int(r["units"]) for r in A]
fig, ax = plt.subplots(figsize=(6.2, 4))
ax.plot(x, [int(r["erc1155_gas"]) for r in A], "o-", color=C1155, label="ERC-1155")
ax.plot(x, [int(r["erc20_gas"]) for r in A], "s-", color=C20, label="ERC-20")
ax.plot(x, [int(r["erc721_gas"]) for r in A], "^-", color=C721, label="ERC-721 (1 NFT/fraction)")
ax.set_yscale("log"); ax.set_xlabel("Units issued to one holder"); ax.set_ylabel("Total gas (log)")
ax.set_title("Benchmark A: Single-holder issuance")
ax.legend()
save(fig, "figA_single_holder_gas")

# ---- Fig 2: Benchmark B gas per investor vs investors ----
B = readcsv("benchmarkB_multi_investor.csv")
xb = [int(r["investors"]) for r in B]
fig, ax = plt.subplots(figsize=(6.2, 4))
ax.plot(xb, [float(r["erc1155_perInvestor"]) for r in B], "o-", color=C1155, label="ERC-1155")
ax.plot(xb, [float(r["erc20_perInvestor"]) for r in B], "s-", color=C20, label="ERC-20")
ax.plot(xb, [float(r["erc721_perInvestor"]) for r in B], "^-", color=C721, label="ERC-721")
ax.set_xlabel("Number of investors (1 fraction each)"); ax.set_ylabel("Gas per investor")
ax.set_title("Benchmark B: Per-investor distribution cost")
ax.set_ylim(0, None); ax.legend()
save(fig, "figB_per_investor_gas")

# ---- Fig 3: Benchmark B total gas vs investors (shows tx-count regime) ----
fig, ax = plt.subplots(figsize=(6.2, 4))
ax.plot(xb, [int(r["erc1155_gas"]) for r in B], "o-", color=C1155, label="ERC-1155")
ax.plot(xb, [int(r["erc20_gas"]) for r in B], "s-", color=C20, label="ERC-20")
ax.plot(xb, [int(r["erc721_gas"]) for r in B], "^-", color=C721, label="ERC-721")
ax.set_xlabel("Number of investors"); ax.set_ylabel("Total distribution gas")
ax.set_title("Benchmark B: Total multi-investor distribution gas")
ax.legend()
save(fig, "figB_total_distribution_gas")

# ---- Fig 4: Benchmark C multi-property (grouped bars) ----
Cc = readcsv("benchmarkC_multi_property.csv")
props = [r["properties"] for r in Cc]
import numpy as np
idx = np.arange(len(props)); w = 0.27
fig, ax = plt.subplots(figsize=(6.6, 4))
ax.bar(idx - w, [int(r["erc1155_gas"]) / 1e6 for r in Cc], w, color=C1155, label="ERC-1155 (1 contract)")
ax.bar(idx,     [int(r["erc20_gas"]) / 1e6 for r in Cc], w, color=C20, label="ERC-20 (N contracts)")
ax.bar(idx + w, [int(r["erc721_gas"]) / 1e6 for r in Cc], w, color=C721, label="ERC-721 (1 contract)")
ax.set_xticks(idx); ax.set_xticklabels(props)
ax.set_xlabel("Number of properties"); ax.set_ylabel("Total gas (millions)")
ax.set_title("Benchmark C: Multi-property catalogue cost")
ax.legend()
save(fig, "figC_multi_property_gas")

print("Wrote figures to", FIG)
print(os.listdir(FIG))
