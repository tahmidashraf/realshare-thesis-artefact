# -*- coding: utf-8 -*-
"""Figures for the extended (Stage 6/8 + DB) experiments, read from raw JSON."""
import json, glob, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
RAW = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures", "token-benchmarks")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 150, "savefig.bbox": "tight"})

def latest(pat):
    fs = sorted(glob.glob(pat)); return fs[-1] if fs else None
def save(fig, b):
    fig.savefig(os.path.join(FIG, b + ".png")); fig.savefig(os.path.join(FIG, b + ".pdf")); plt.close(fig)

# Local EVM throughput with error bars
f = latest(os.path.join(RAW, "token-benchmarks", "raw", "local_evm_throughput_*.json"))
if f:
    d = json.load(open(f))
    x = [l["level"] for l in d["levels"]]
    y = [l["tps"]["mean"] for l in d["levels"]]
    e = [l["tps"]["sd"] for l in d["levels"]]
    fig, ax = plt.subplots(figsize=(6.2, 4))
    ax.errorbar(x, y, yerr=e, fmt="o-", color="#1f77b4", capsize=4, label="mean ± SD (5 reps)")
    ax.set_xlabel("Concurrent mint submissions (local EVM)")
    ax.set_ylabel("Contract-execution throughput (tx/s)")
    ax.set_title("Local EVM contract-execution throughput (NOT network TPS)")
    ax.set_ylim(0, None); ax.legend()
    save(fig, "figX_local_evm_throughput")
    print("wrote figX_local_evm_throughput")

# DB fault recovery times (per scenario that has recoveryMs)
f = latest(os.path.join(RAW, "database-faults", "raw", "faults_*.json"))
if f:
    d = json.load(open(f))
    scen = [s for s in d["scenarios"] if isinstance(s.get("recoveryMs"), (int, float))]
    names = [f"#{s['no']}" for s in scen]
    vals = [s["recoveryMs"] for s in scen]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(names, vals, color="#2ca02c")
    ax.set_xlabel("Fault scenario"); ax.set_ylabel("Recovery time (ms)")
    ax.set_title(f"DB fault recovery times (mean {d['metrics']['meanRecoveryMs']} ms, P95 {d['metrics']['p95RecoveryMs']} ms)")
    plt.xticks(rotation=45, ha="right")
    save(fig, "figX_db_recovery_times")
    print("wrote figX_db_recovery_times")
