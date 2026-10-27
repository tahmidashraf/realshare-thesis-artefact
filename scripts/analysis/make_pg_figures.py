import json, glob, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
FIG = os.path.join("figures", "token-benchmarks"); os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size":11,"axes.grid":True,"grid.alpha":0.3,"figure.dpi":150,"savefig.bbox":"tight"})
d = json.load(open(sorted(glob.glob("results/postgres/raw/pg_concurrency_*.json"))[-1]))
isos = ["READ COMMITTED","REPEATABLE READ","SERIALIZABLE"]; cols={"READ COMMITTED":"#1f77b4","REPEATABLE READ":"#2ca02c","SERIALIZABLE":"#d62728"}
def series(iso,key): return [(r["workers"],r[key]) for r in d["matrix"] if r["isolation"]==iso]
# throughput
fig,ax=plt.subplots(figsize=(6.2,4))
for iso in isos:
    s=series(iso,"throughputMean"); ax.plot([x for x,_ in s],[y for _,y in s],"o-",color=cols[iso],label=iso)
ax.set_xlabel("Concurrent workers"); ax.set_ylabel("Throughput (events/s)"); ax.set_title("PostgreSQL throughput vs concurrency by isolation level"); ax.legend()
fig.savefig(os.path.join(FIG,"figX_pg_throughput.png")); fig.savefig(os.path.join(FIG,"figX_pg_throughput.pdf")); plt.close(fig)
# retries
fig,ax=plt.subplots(figsize=(6.2,4))
for iso in isos:
    s=series(iso,"serializationRetriesMean"); ax.plot([x for x,_ in s],[y for _,y in s],"s-",color=cols[iso],label=iso)
ax.set_xlabel("Concurrent workers"); ax.set_ylabel("Serialization retries (handled)"); ax.set_title("PostgreSQL serialization retries vs concurrency"); ax.legend()
fig.savefig(os.path.join(FIG,"figX_pg_retries.png")); fig.savefig(os.path.join(FIG,"figX_pg_retries.pdf")); plt.close(fig)
print("wrote figX_pg_throughput, figX_pg_retries")
