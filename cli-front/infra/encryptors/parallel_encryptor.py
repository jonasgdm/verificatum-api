# parallel_encrypt_pool.py
import os
from typing import List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from infra.encryptors.node_daemon import NodeDaemonEncryptor  # usa o seu daemon atual
from ports.encrypt_port import EncryptPort


def _split_indices(n_items: int, n_parts: int) -> List[Tuple[int, int]]:
    """
    Retorna pares (start, end_exclusive) dividindo n_items em n_parts blocos
    o mais equilibrados possível. Mantém a ordem para permitir remontagem.
    """
    n_parts = max(1, min(n_parts, n_items))  # não criar mais partes que itens
    base, extra = divmod(n_items, n_parts)
    spans = []
    start = 0
    for i in range(n_parts):
        size = base + (1 if i < extra else 0)
        end = start + size
        spans.append((start, end))
        start = end
    return spans


class ParallelEncryptPool(EncryptPort):
    """
    Implementa EncryptPort usando um pool de daemons Node.
    - encrypt(): round-robin entre workers
    - encrypt_batch(): divide o lote, cifra em paralelo e recompõe na ordem
    """

    def __init__(
        self,
        public_key_str: str,
        script: str = "encryptor/daemon_encrypt.js",
        pool_size: Optional[int] = None,
        max_workers: Optional[int] = None,
    ):
        # Tamanho do pool default: ~#CPUs (ou override por ENV)
        env_pool = os.getenv("ENC_POOL_SIZE")
        if pool_size is None:
            pool_size = int(env_pool) if env_pool else max(1, (os.cpu_count() or 2) - 1)

        self._workers = [
            NodeDaemonEncryptor(public_key_str=public_key_str, script=script)
            for _ in range(pool_size)
        ]
        # ThreadPool para orquestrar as chamadas de cada worker (I/O bound + CPU no Node)
        self._executor = ThreadPoolExecutor(max_workers=max_workers or pool_size)
        self._rr = 0  # índice de round-robin

    def _next_worker(self) -> NodeDaemonEncryptor:
        w = self._workers[self._rr]
        self._rr = (self._rr + 1) % len(self._workers)
        return w

    # ---- API EncryptPort ----
    def encrypt(self, value: str) -> str:
        # encaminha para um worker via round-robin
        return self._next_worker().encrypt(value)

    def encrypt_batch(self, values: List[str]) -> List[str]:
        if not values:
            return []

        # Se só há um worker, delega direto (zero overhead)
        if len(self._workers) == 1:
            return self._workers[0].encrypt_batch(values)

        # Divide o lote em partes equilibradas (mantendo ordem via índices)
        spans = _split_indices(len(values), len(self._workers))
        futures = []
        for (start, end), worker in zip(spans, self._workers):
            chunk = values[start:end]
            if not chunk:
                continue
            futures.append(
                self._executor.submit(
                    lambda s=start, c=chunk, w=worker: (s, w.encrypt_batch(c))
                )
            )

        # Recompõe no lugar certo preservando a ordem do input
        result = [None] * len(values)
        for fut in as_completed(futures):
            start, enc_chunk = fut.result()
            result[start : start + len(enc_chunk)] = enc_chunk

        return result  # type: ignore[list-item]

    def close(self):
        # encerra limpo
        for w in self._workers:
            try:
                w.close()
            except Exception:
                pass
        self._executor.shutdown(wait=True)
