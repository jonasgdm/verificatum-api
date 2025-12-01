# verificatum-api/cli-front/screens/benchmark.py

from ui.spinner import run_with_spinner
from services import flask_api, verificatum_api
from app import mock_election
from infra.encryptors.parallel_encryptor import ParallelEncryptPool
import json
from utils.electionConfig_parser import load_election_config
import time
import os
import requests
from utils import log_parser
from rich.console import Console
import csv
import subprocess
from typing import Optional

# Quantidade a partir da qual pulamos o upload HTTP e fazemos a “gambiarra”
LARGE_N_THRESHOLD = 100

console = Console()
import re


def expand_ciphertexts_seed(src_path: str, dst_path: str, target_n: int) -> None:
    """
    Cria um arquivo 'dst_path' com exatamente 'target_n' linhas, repetindo
    ciclicamente as linhas do arquivo 'src_path'.

    Premissas: 1 ciphertext por linha (sem header).
    """
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"Seed de ciphertexts não encontrado: {src_path}")
    if target_n <= 0:
        raise ValueError("target_n deve ser > 0")

    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
        # Mantém linhas não vazias; garante '\n' no fim de cada uma
        seed_lines = [ln if ln.endswith("\n") else ln + "\n" for ln in f if ln.strip()]

    if not seed_lines:
        raise RuntimeError("Seed de ciphertexts está vazio.")

    # Se já tem >= target_n, só corta
    if len(seed_lines) >= target_n:
        with open(dst_path, "w", encoding="utf-8") as out:
            out.writelines(seed_lines[:target_n])
        return

    # Caso contrário, repete ciclicamente
    with open(dst_path, "w", encoding="utf-8") as out:
        for i in range(target_n):
            out.write(seed_lines[i % len(seed_lines)])


def parse_vmn_log(log_path: str) -> dict:
    """
    Lê o arquivo vmn.log (Verificatum) e extrai métricas relevantes.
    Retorna um dict com, por ex.:
      - computation_ms
      - execution_ms
      - network_ms
      - effective_ms
      - idle_ms
      - proof_size_bytes
      - sent_bytes, received_bytes, total_bytes
      - shuffled_count (se houver a linha 'Shuffle N ciphertexts.')
    """
    if not os.path.isfile(log_path):
        raise FileNotFoundError(f"vmn.log não encontrado: {log_path}")

    # regex para capturar o último número (coluna em ms/bytes) nas linhas de interesse
    re_ms = re.compile(r".*?(\d+)\s*$")
    re_bytes = re.compile(r".*?(\d+)\s*$")
    re_shuffle = re.compile(r"Shuffle\s+(\d+)\s+ciphertexts\.", re.IGNORECASE)

    res = {
        "execution_ms": None,
        "network_ms": None,
        "effective_ms": None,
        "idle_ms": None,
        "computation_ms": None,
        "proof_size_bytes": None,
        "sent_bytes": None,
        "received_bytes": None,
        "total_bytes": None,
        "shuffled_count": None,
    }

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()

            # quantidade de ciphertexts (opcional)
            m = re_shuffle.search(s)
            if m:
                try:
                    res["shuffled_count"] = int(m.group(1))
                except:
                    pass

            # Running time
            if s.startswith("- Execution"):
                m = re_ms.match(s)
                if m:
                    res["execution_ms"] = int(m.group(1))
            elif s.startswith("- Network"):
                m = re_ms.match(s)
                if m:
                    res["network_ms"] = int(m.group(1))
            elif s.startswith("- Effective"):
                m = re_ms.match(s)
                if m:
                    res["effective_ms"] = int(m.group(1))
            elif s.startswith("- Idle"):
                m = re_ms.match(s)
                if m:
                    res["idle_ms"] = int(m.group(1))
            elif s.startswith("- Computation"):
                m = re_ms.match(s)
                if m:
                    res["computation_ms"] = int(m.group(1))

            # Communication
            elif s.startswith("- Sent"):
                m = re_bytes.match(s)
                if m:
                    res["sent_bytes"] = int(m.group(1))
            elif s.startswith("- Received"):
                m = re_bytes.match(s)
                if m:
                    res["received_bytes"] = int(m.group(1))
            elif s.startswith("- Total"):
                m = re_bytes.match(s)
                if m:
                    res["total_bytes"] = int(m.group(1))

            # Proof size
            elif s.lower().startswith("proof size"):
                m = re_bytes.match(s)
                if m:
                    res["proof_size_bytes"] = int(m.group(1))

    # sanity mínima
    if res["computation_ms"] is None and res["execution_ms"] is None:
        raise RuntimeError("Não foi possível extrair métricas de tempo do vmn.log.")

    return res


def run_script_concurrent_pair(
    script_name: str,
    inputs_exec1: list[str],
    inputs_exec2: list[str],
    description: str,
    scripts_dir_rel: str = "../../local-scripts",
) -> bool:
    """
    Roda script duas vezes em paralelo (par de nós) alimentando o stdin de cada um.
    Útil para scripts que ficam esperando o outro nó (ex.: shuffler-shuffle-local.sh).

    inputs_execX: lista de respostas para cada prompt da execução (uma string por linha).
      Ex. para shuffler-shuffle-local.sh (se pedir "nó local" e "total de nós"):
        inputs_exec1 = ["2", "3"]
        inputs_exec2 = ["3", "3"]
    """
    here = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.abspath(os.path.join(here, scripts_dir_rel))
    script_path = os.path.join(scripts_dir, script_name)
    if not os.path.exists(script_path):
        console.print(f"[red]Script não encontrado:[/red] {script_path}")
        return False

    console.print(f"[blue]{description} (execuções em paralelo)[/blue]")

    try:
        # 1ª execução (background, com stdin próprio)
        p1 = subprocess.Popen(
            ["bash", script_path],
            cwd=scripts_dir,
            stdin=subprocess.PIPE,
            stdout=None,
            stderr=None,
            text=True,
        )
        p1.stdin.write("\n".join(inputs_exec1) + "\n")
        p1.stdin.flush()

        # 2ª execução (também background)
        p2 = subprocess.Popen(
            ["bash", script_path],
            cwd=scripts_dir,
            stdin=subprocess.PIPE,
            stdout=None,
            stderr=None,
            text=True,
        )
        p2.stdin.write("\n".join(inputs_exec2) + "\n")
        p2.stdin.flush()

        # Aguarda as duas terminarem
        rc1 = p1.wait()
        rc2 = p2.wait()

        if rc1 != 0 or rc2 != 0:
            console.print(
                f"[red]Falha ao rodar {script_name} em paralelo[/red] rc1={rc1} rc2={rc2}"
            )
            return False

        console.print(f"[green]✓ {description} concluído[/green]")
        return True

    except Exception as e:
        console.print(f"[red]Erro ao rodar {script_name} em paralelo:[/red] {e}")
        return False


# -----------------------------
# Configurações do Benchmark
# -----------------------------
bench_sizes = [100, 500, 1000, 5000, 10000]
results = []
csv_path = "output/benchmark_results.csv"


# -----------------------------
# Utilidades HTTP/FS
# -----------------------------
def post_ciphertexts(file_path: str):
    """Envia o arquivo ciphertexts ao shuffler central."""
    url = "http://localhost:8080/shuffler/receive-ciphertexts"
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "text/plain")}
        resp = requests.post(url, files=files)
    return resp.json()


def fire_and_forget_post(url: str):
    """
    Dispara um POST sem bloquear (não espera resposta longa).
    Tenta 'curl' em background; se não houver curl, usa requests com timeout curtinho e ignora exceção.
    """
    try:
        with open(os.devnull, "wb") as devnull:
            subprocess.Popen(
                ["curl", "-fsS", "-X", "POST", url],
                stdout=devnull,
                stderr=devnull,
            )
        return
    except FileNotFoundError:
        # Sem curl, cai pro requests "best effort"
        pass

    try:
        requests.post(url, timeout=0.25)
    except Exception:
        pass  # esperado: não queremos bloquear


# -----------------------------
# Helpers de Scripts Locais
# -----------------------------
def run_local_script(
    script_name: str,
    times: int = 3,
    description: Optional[str] = None,
    scripts_dir_rel: str = "../../local-scripts",
) -> bool:
    """
    Executa um script do diretório indicado (padrão: ../../local-scripts) múltiplas vezes (um por nó).
    Ex.: guardian-setup-local.sh, shuffler-merge-local.sh, etc.
    Mantém entrada interativa se o .sh pedir input.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.abspath(os.path.join(here, scripts_dir_rel))
    script_path = os.path.join(scripts_dir, script_name)

    if not os.path.exists(script_path):
        console.print(f"[red]Script não encontrado:[/red] {script_path}")
        return False

    if not description:
        description = script_name

    console.print(f"[blue]Executando {description} ({times}x)...[/blue]")
    for i in range(times):
        console.print(f"[cyan]→ Execução {i+1}/{times}[/cyan]")
        try:
            subprocess.run(
                ["bash", script_path],
                check=True,
                stdin=None,  # se o script pedir input
                cwd=scripts_dir,  # caso o script use paths relativos internos
            )
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Falha ao rodar {script_name} (execução {i+1})[/red]")
            console.print(f"Erro: {e}")
            return False

    console.print(f"[green]✓ {description} concluído[/green]")
    return True


def copy_protinfos_to_all(base_dir_rel: str) -> bool:
    """
    Copia todos os protInfo*.xml entre 01/02/03 de base_dir.
    Ex.: base_dir_rel = "../../verificatum-guardian" ou "../../shuffler-demo"
    """
    here = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(here, base_dir_rel))
    if not os.path.isdir(base_dir):
        console.print(f"[red]Pasta não encontrada:[/red] {base_dir}")
        return False

    subprocess.run(
        [
            "bash",
            "-c",
            'for d in 01 02 03; do for s in 01 02 03; do cp -n "$s"/protInfo*.xml "$d"/ 2>/dev/null || true; done; done',
        ],
        check=True,
        cwd=base_dir,
    )
    return True


def distribute_ciphertexts_to_shuffler_nodes(src_ciphertexts_path: str) -> bool:
    """
    Copia o arquivo 'ciphertexts' gerado para shuffler-demo/01/ e replica para 02/ e 03/.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(here, "../../shuffler-demo"))

    if not os.path.isfile(src_ciphertexts_path):
        console.print(
            f"[red]Arquivo ciphertexts não encontrado:[/red] {src_ciphertexts_path}"
        )
        return False

    dest01 = os.path.join(base_dir, "01", "ciphertexts")
    os.makedirs(os.path.dirname(dest01), exist_ok=True)
    subprocess.run(["cp", "-f", src_ciphertexts_path, dest01], check=True)

    for d in ("02", "03"):
        dest = os.path.join(base_dir, d, "ciphertexts")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        subprocess.run(["cp", "-f", dest01, dest], check=True)

    console.print("[green]✓ ciphertexts distribuído para 01/02/03[/green]")
    return True


# -----------------------------
# Setup dos Guardiões
# -----------------------------
def setup_guardian() -> bool:
    # 1) Setup central (API)
    response_setup = run_with_spinner(
        lambda: verificatum_api.post_setup(), text="Inicializando setup..."
    )
    if not (
        response_setup
        and str(response_setup.get("status", "")).startswith("Setup complete")
    ):
        console.print("[red]Erro no setup[/red]")
        return False
    console.print("\n[bold green]✓ DONE[/bold green]")

    # 2) Setup local (3 nós)
    if not run_local_script(
        "guardian-setup-local.sh", description="Setup local dos nós"
    ):
        return False

    # 3) Copiar protInfos dentro de verificatum-guardian (01/02/03)
    console.print(
        "[blue]Copiando protInfo*.xml para verificatum-guardian/01/02/03...[/blue]"
    )
    if not copy_protinfos_to_all("../../verificatum-guardian"):
        return False
    console.print("[green]✓ protInfos copiados (guardian)[/green]")

    # 4) Merge local (3 nós)
    if not run_local_script(
        "guardian-merge-local.sh", description="Merge local dos nós"
    ):
        return False

    # 5) Keygen central (fire-and-forget) + keygen local nos nós
    console.print("[blue]Iniciando geração da chave pública...[/blue]")
    console.print("[blue]Disparando keygen central...[/blue]")
    fire_and_forget_post("http://localhost:8080/guardian/keygen")

    console.print("[blue]Executando guardian-keygen-local.sh nos 3 nós...[/blue]")
    if not run_local_script(
        "guardian-keygen-local.sh", description="Keygen local dos nós"
    ):
        console.print("[red]Falha no keygen local dos nós[/red]")
        return False

    return True


# -----------------------------
# Setup do Shuffler
# -----------------------------
def setup_shuffler() -> bool:
    # 1) Setup central do shuffler
    console.print("[blue]Configurando rede de mistura (shuffler central)...[/blue]")
    run_with_spinner(
        lambda: verificatum_api._post(
            "/shuffler/setup?publicKeyUrl=http://localhost:8080/guardian/public-key"
        ),
        text="Configurando rede de mistura...",
    )
    console.print("[green]✓ Shuffler central configurado[/green]")

    # 2) Setup local em 2 nós
    if not run_local_script(
        "shuffler-setup-local.sh",
        times=2,
        description="Shuffler setup local (2 nós)",
        scripts_dir_rel="../../local-scripts",
    ):
        return False

    # 3) Copiar protInfos dentro de shuffler-demo (01/02/03)
    console.print("[blue]Copiando protInfo*.xml para shuffler-demo/01/02/03...[/blue]")
    if not copy_protinfos_to_all("../../shuffler-demo"):
        return False
    console.print("[green]✓ protInfos copiados (shuffler)[/green]")

    # 4) Merge local em 3 nós
    if not run_local_script(
        "shuffler-merge-local.sh",
        times=3,
        description="Shuffler merge local (3 nós)",
        scripts_dir_rel="../../local-scripts",
    ):
        return False

    # 5) Set PK em 3 nós
    if not run_local_script(
        "shuffler-setpk-local.sh",
        times=3,
        description="Shuffler set PK local (3 nós)",
        scripts_dir_rel="../../local-scripts",
    ):
        return False

    return True


# -----------------------------
# Configuração da Eleição (client)
# -----------------------------
def setup_election_configs():
    """
    Lê a public key do guardian, instancia o pool de cifragem e o MockElection.
    Inclui uma pequena validação da chave pública para evitar fromhex(None).
    """
    config = load_election_config()
    hex_str = verificatum_api.get_publickey()
    if not isinstance(hex_str, str) or not hex_str.strip():
        raise RuntimeError("Public key não disponível. Tente novamente após o keygen.")

    try:
        key_bytes = bytes.fromhex(hex_str.strip())
    except ValueError as e:
        raise RuntimeError(f"Public key inválida (não-hex): {e}")

    key = json.dumps(list(key_bytes))

    encryptor = ParallelEncryptPool(
        key, script="encryptor/daemon_encrypt.js", pool_size=3, max_workers=4
    )
    app = mock_election.MockElection(key, config, encryptor)
    return app


# -----------------------------
# Tela principal
# -----------------------------
def show(_=None):
    print("benchmark")

    # Pergunta quantidade de votos a cifrar/embaralhar
    try:
        raw = input("Informe o número de votos para o benchmark (ex.: 200): ").strip()
        n = int(raw)
        if n <= 0:
            raise ValueError
    except Exception:
        console.print("[yellow]Entrada inválida. Usando 200 votos por padrão.[/yellow]")
        n = 200

    # SETUP GUARDIAN
    if not setup_guardian():
        console.print("[red]Erro no setup do guardian[/red]")
        return

    # SETUP SHUFFLER
    if not setup_shuffler():
        console.print("[red]Erro no setup do shuffler[/red]")
        return

    console.print(f"[blue]Rodando benchmark com {n} plaintexts...[/blue]")

    # --- Decide modo (manual vs normal) ANTES de gerar os plaintexts ---
    out_path = "output/ciphertexts"
    use_manual = n > LARGE_N_THRESHOLD
    seed_n = min(100, n) if use_manual else n

    console.print(
        f"[magenta]n={n}, threshold={LARGE_N_THRESHOLD} → "
        f"Modo {'MANUAL (sem HTTP, seed='+str(seed_n)+')' if use_manual else 'NORMAL (HTTP)'}[/magenta]"
    )

    # Instancia app de cifragem
    app = setup_election_configs()

    # --- GERAÇÃO: só gera 'seed_n' se for modo manual! ---
    console.print(f"[blue]→ Gerando {seed_n} plaintext(s)...[/blue]")
    app.generate_plaintexts(seed_n)
    app.finalize_encryption()

    if use_manual:
        # MODO MANUAL (sem HTTP): exporta seed e infla até n
        seed_path = "output/ciphertexts_seed"
        console.print(f"[blue]→ Exportando seed para {seed_path}...[/blue]")
        app.export_ciphertexts_only(seed_path)

        # Sanidade: contar linhas da seed
        try:
            with open(seed_path, "r", encoding="utf-8", errors="ignore") as _f:
                _lines = sum(1 for _ in _f if _.strip())
            console.print(
                f"[cyan]Seed tem {_lines} linhas (esperado ~{seed_n}).[/cyan]"
            )
        except Exception as e:
            console.print(
                f"[yellow]Aviso: não deu p/ contar linhas da seed:[/yellow] {e}"
            )

        console.print(f"[blue]→ Inflando seed até {n} linhas em {out_path}...[/blue]")
        expand_ciphertexts_seed(seed_path, out_path, n)

        console.print(
            "[blue]→ Distribuindo ciphertexts inflado para 01/02/03...[/blue]"
        )
        if not distribute_ciphertexts_to_shuffler_nodes(out_path):
            return

        # Etapa manual (sem HTTP)
        console.print("\n[yellow bold]⚠ Etapa manual (sem HTTP)![/yellow bold]")
        console.print(
            "[yellow]Abra outro terminal e execute:[/yellow]\n"
            "  cd verificatum-api/local-scripts\n"
            "  bash shuffler-shuffle-local.sh  # em cada nó (ex.: 2 e 3)\n\n"
            "[yellow]Depois que os nós terminarem o shuffle local, pressione Enter aqui.[/yellow]"
        )
        input("\nPressione Enter quando terminar o shuffle manual... ")

    else:
        # MODO NORMAL (com HTTP)
        console.print(f"[blue]→ Exportando ciphertexts para {out_path}...[/blue]")
        app.export_ciphertexts_only(out_path)

        console.print("[blue]→ Enviando ciphertexts ao shuffler central...[/blue]")
        post_ciphertexts(out_path)

        console.print("[blue]→ Disparando shuffle central (sem bloqueio)...[/blue]")
        fire_and_forget_post("http://localhost:8080/shuffler/shuffle")

        console.print("[blue]→ Distribuindo ciphertexts para 01/02/03...[/blue]")
        if not distribute_ciphertexts_to_shuffler_nodes(out_path):
            return

    # Continuação
    console.print(
        "[green]✓ Continuação do benchmark após shuffle manual/central[/green]"
    )

    # Etapa manual do shuffle local (você roda em outro terminal)
    console.print("[green]✓ Continuação do benchmark após shuffle manual[/green]")

    # 5) Coleta métricas direto do vmn.log do shuffler
    vmn_log_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../shuffler-demo/01/vmn.log")
    )
    try:
        summary = parse_vmn_log(vmn_log_path)
    except Exception as e:
        console.print(f"[yellow]Aviso: falha ao ler/parsing vmn.log:[/yellow] {e}")
        summary = {"computation_ms": 0, "proof_size_bytes": None}

    elapsed = (summary.get("computation_ms") or 0) / 1000
    proof_size = summary.get("proof_size_bytes")

    # 6) Salva CSV (apenas 1 linha nesta execução)
    row = {
        "n_plaintexts": n,
        "elapsed_s": elapsed,
        "throughput": n / elapsed if elapsed > 0 else 0,
        "proof_size_bytes": proof_size,
    }
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    write_header = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    console.print(f"[green]✓ Resultado salvo ({csv_path})[/green]")
