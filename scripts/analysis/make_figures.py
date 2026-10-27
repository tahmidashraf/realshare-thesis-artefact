"""
Phase 17 figure generation: regenerate every publication figure from RAW JSON as vector PDF.
Replaces the removed subjective radar chart with interpretable decompositions. No hand-entered
values; each figure reads a results file.

Run: python scripts/analysis/make_figures.py
Outputs: REVISION/figures/*.pdf (+ .png preview)
"""
import json, glob, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
OUT = os.path.join(ROOT, "REVISION", "figures")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 10, "figure.dpi": 120, "axes.grid": True, "grid.alpha": 0.3})


def latest(pattern):
    fs = sorted(glob.glob(os.path.join(ROOT, pattern)))
    return fs[-1] if fs else None


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def fig_amount_amortization(g):
    w1 = g["W1_amount_amortization"]
    q = [r["amount"] for r in w1["rows"]]
    total = [r["gas"] for r in w1["rows"]]
    per = [r["gasPerUnit"] for r in w1["rows"]]
    fig, ax1 = plt.subplots(figsize=(5, 3.2))
    ax1.plot(q, total, "o-", color="C0", label="total gas (flat)")
    ax1.axhline(w1["coldFirstCredit"]["gas"], ls="--", color="C3", label="cold first credit")
    ax1.set_xscale("log"); ax1.set_xlabel("mint amount q"); ax1.set_ylabel("total gas", color="C0")
    ax1.set_ylim(0, max(total) * 1.6)
    ax2 = ax1.twinx()
    ax2.plot(q, per, "s-", color="C1", label="gas per unit = total/q")
    ax2.set_yscale("log"); ax2.set_ylabel("gas per unit", color="C1"); ax2.grid(False)
    ax1.set_title("W1: amount amortization (one write, flat total)")
    l1, la1 = ax1.get_legend_handles_labels(); l2, la2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, la1 + la2, fontsize=7, loc="center right")
    save(fig, "fig_amount_amortization")


def fig_lifecycle(g):
    w4 = g["W4_portfolio"]["scenarios"]
    labels = [f"{s['P']}x{s['N']}" for s in w4]
    x = np.arange(len(labels)); wd = 0.27
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    ax.bar(x - wd, [s["erc1155"]["totalGas"] / 1e6 for s in w4], wd, label="ERC-1155")
    ax.bar(x, [s["erc721"]["totalGas"] / 1e6 for s in w4], wd, label="ERC-721")
    ax.bar(x + wd, [s["erc20"]["totalGas"] / 1e6 for s in w4], wd, label="ERC-20 (per-property)")
    ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_xlabel("properties x investors"); ax.set_ylabel("total gas (millions)")
    ax.set_title("W4: lifecycle gas by standard"); ax.legend(fontsize=8)
    save(fig, "fig_lifecycle_gas")


def fig_fl_recall(fl):
    runs = fl["runs"]
    ds = sorted(set(r["dataset"][:24] for r in runs))
    methods = ["fedavg", "cw_fedavg", "scaffold", "cbw_fed", "centralized"]
    fig, axes = plt.subplots(1, len(ds), figsize=(4.2 * len(ds), 3.2), squeeze=False)
    for j, dname in enumerate(ds):
        ax = axes[0][j]
        rs = [r for r in runs if r["dataset"][:24] == dname]
        alphas = sorted({(r["alpha"] if r["alpha"] is not None else 2.0) for r in rs})
        for m in methods:
            ys = []
            for a in alphas:
                vals = [r["agg"][m]["recall"]["mean"] for r in rs
                        if (r["alpha"] if r["alpha"] is not None else 2.0) == a
                        and m in r["agg"] and "recall" in r["agg"][m]]
                ys.append(np.mean(vals) if vals else np.nan)
            ax.plot([("IID" if a == 2.0 else a) for a in alphas], ys, "o-",
                    label=m, lw=2 if m == "cbw_fed" else 1)
        ax.set_xlabel("Dirichlet alpha (skew ->)"); ax.set_ylabel("high-risk recall")
        ax.set_title(dname); ax.legend(fontsize=7)
    fig.suptitle("RQ3: minority recall vs skew (mean over configs)")
    save(fig, "fig_fl_recall_vs_skew")


def fig_privacy(pv):
    rows = pv["mia_vs_defense"]
    z = [r["z"] for r in rows]; auc = [r["auc"] for r in rows]; mia = [r["mia_auc"] for r in rows]
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.plot(z, auc, "o-", label="model utility (AUC)")
    ax.plot(z, mia, "s-", label="attack success (MIA AUC)")
    ax.axhline(0.5, ls=":", color="gray", label="MIA random (0.5)")
    ax.set_xlabel("DP noise multiplier z"); ax.set_ylabel("score")
    ax.set_title("RQ4: privacy-utility (MIA near-random even at z=0)")
    ax.legend(fontsize=8)
    save(fig, "fig_privacy_utility")


def fig_block_util(bl):
    u = bl["utilization"]
    fig, ax = plt.subplots(figsize=(5, 3.2))
    keys = ["p25", "p50", "p75", "p95", "max"]
    ax.bar(keys, [u[k] * 100 for k in keys], color="C0")
    ax.axhline(u["mean"] * 100, ls="--", color="C3", label=f"mean {u['mean']*100:.1f}%")
    ax.set_ylabel("block gas utilization (%)")
    ax.set_title(f"RQ2: Polygon block-gas utilization (limit {bl['gasLimit']['median']/1e6:.0f}M)")
    ax.legend(fontsize=8)
    save(fig, "fig_block_utilization")


def main():
    g = latest("results/token-benchmarks/semantic_gasbench_*.json")
    if g:
        gj = json.load(open(g)); fig_amount_amortization(gj); fig_lifecycle(gj)
    fl = os.path.join(ROOT, "fl_benchmark_scoped.json")
    if os.path.exists(fl): fig_fl_recall(json.load(open(fl)))
    pv = os.path.join(ROOT, "fl", "fl_privacy_results.json")
    if os.path.exists(pv): fig_privacy(json.load(open(pv)))
    bl = latest("results/live-network/block_availability_polygon_*.json")
    if bl: fig_block_util(json.load(open(bl)))
    print("figures in", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
