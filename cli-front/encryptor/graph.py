import json
import matplotlib.pyplot as plt

with open("bench_results.json") as f:
    results = json.load(f)

Ns = [r["N"] for r in results]
times = [r["elapsed"] for r in results]
throughput = [r["throughput"] for r in results]

plt.figure(figsize=(8, 5))

plt.subplot(2, 1, 1)
plt.plot(Ns, times, marker="o")
plt.xlabel("Número de plaintexts")
plt.ylabel("Tempo (s)")
plt.title("Escalabilidade da Cifra (tempo vs N)")

plt.subplot(2, 1, 2)
plt.plot(Ns, throughput, marker="s", color="orange")
plt.xlabel("Número de plaintexts")
plt.ylabel("Throughput (msg/s)")
plt.title("Throughput")

plt.tight_layout()
plt.savefig("bench_plot.png")
plt.show()
