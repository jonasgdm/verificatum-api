#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import os
from typing import List, Dict, Optional

import matplotlib.pyplot as plt


def read_rows(csv_path: str) -> List[Dict[str, str]]:
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    if not rows:
        raise ValueError(f"CSV vazio: {csv_path}")
    return rows


def to_float(v: Optional[str]) -> Optional[float]:
    if v is None:
        return None
    v = str(v).strip()
    if not v:
        return None
    try:
        return float(v)
    except Exception:
        return None


def ensure_outdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def plot_line(x, y, xlabel, ylabel, title, outpath):
    plt.figure()
    plt.plot(x, y, marker="o")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(outpath, dpi=160)
    # não chamamos plt.show() aqui; deixamos para o main decidir
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Plota gráficos de benchmark da mixnet a partir de um CSV."
    )
    parser.add_argument(
        "--csv",
        default="output/benchmark_results.csv",
        help="Caminho para o CSV (default: output/benchmark_results.csv)",
    )
    parser.add_argument(
        "--outdir",
        default="output/plots",
        help="Diretório de saída dos gráficos (default: output/plots)",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Exibe os gráficos ao final (além de salvar como PNG).",
    )
    args = parser.parse_args()

    ensure_outdir(args.outdir)
    rows = read_rows(args.csv)

    # Coleta colunas principais
    n = []
    elapsed_s = []
    throughput = []
    proof_size = []

    for row in rows:
        n_plaintexts = to_float(row.get("n_plaintexts"))
        elapsed = to_float(row.get("elapsed_s"))
        tput = to_float(row.get("throughput"))
        psize = to_float(row.get("proof_size_bytes"))

        # linhas possivelmente incompletas são ignoradas nos gráficos relevantes
        if n_plaintexts is not None:
            n.append(n_plaintexts)
        else:
            continue

        elapsed_s.append(elapsed if elapsed is not None else float("nan"))
        throughput.append(tput if tput is not None else float("nan"))
        proof_size.append(psize if psize is not None else float("nan"))

    if not n:
        raise ValueError("Nenhum dado válido encontrado no CSV.")

    # 1) Tempo total vs nº de plaintexts
    plot_line(
        x=n,
        y=elapsed_s,
        xlabel="# Plaintexts",
        ylabel="Tempo de Processsamento (s)",
        title="Tempo total vs nº de plaintexts",
        outpath=os.path.join(args.outdir, "tempo_vs_plaintexts.png"),
    )

    # 2) Throughput vs nº de plaintexts
    plot_line(
        x=n,
        y=throughput,
        xlabel="# Plaintexts",
        ylabel="Throughput (plaintexts/s)",
        title="Throughput vs nº de plaintexts",
        outpath=os.path.join(args.outdir, "throughput_vs_plaintexts.png"),
    )

    # 3) Tamanho da prova vs nº de plaintexts (se houver)
    if any(x is not None and x == x for x in proof_size):  # checa se não é todo NaN
        plot_line(
            x=n,
            y=proof_size,
            xlabel="# Plaintexts",
            ylabel="Tamanho da prova (bytes)",
            title="Tamanho da prova vs nº de plaintexts",
            outpath=os.path.join(args.outdir, "proofsize_vs_plaintexts.png"),
        )

    if args.show:
        # opcional: exibir o último gráfico gerado não faz sentido; em vez disso,
        # replotamos rapidamente usando os arquivos gerados:
        import matplotlib.image as mpimg

        for img_name in [
            "tempo_vs_plaintexts.png",
            "throughput_vs_plaintexts.png",
            "proofsize_vs_plaintexts.png",
        ]:
            img_path = os.path.join(args.outdir, img_name)
            if os.path.exists(img_path):
                plt.figure()
                plt.imshow(mpimg.imread(img_path))
                plt.axis("off")
                plt.title(img_name)
        plt.show()

    print(f"Gráficos salvos em: {args.outdir}")


if __name__ == "__main__":
    main()
