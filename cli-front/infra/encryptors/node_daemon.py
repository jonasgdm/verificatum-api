import json, subprocess, threading, queue, uuid
from typing import List


class NodeDaemonEncryptor:
    def __init__(
        self,
        public_key_str: str,
        script="encryptor/daemon_encrypt.js",
    ):

        self.proc = subprocess.Popen(
            ["node", script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._q = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()
        self._send({"type": "init", "publicKey": public_key_str})

    def _reader(self):
        for line in self.proc.stdout:
            try:
                self._q.put(json.loads(line))
            except Exception:
                pass

    def _send(self, obj):
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def _rpc(self, msg_type, payload):
        rid = str(uuid.uuid4())
        self._send({"type": msg_type, "id": rid, **payload})
        while True:
            resp = self._q.get()
            if resp.get("id") == rid:
                if resp.get("ok"):
                    return resp
                raise RuntimeError(resp.get("error"))

    def encrypt(
        self,
        value: str,
    ) -> str:
        r = self._rpc(
            "enc",
            {
                "value": value,
            },
        )
        return r["hex"]

    def encrypt_batch(
        self,
        values: List[str],
    ) -> List[str]:
        r = self._rpc(
            "enc_batch",
            {"values": values},
        )

        # se o daemon mandou estatísticas, mostra
        # if "stats" in r:
        #     count = r["stats"].get("count")
        #     elapsed = r["stats"].get("elapsed")
        #     print(f">{count} plaintexts cifrados em {elapsed:.2f} segundos")

        return r["hex_list"]

    def close(self):
        try:
            self._send({"type": "close"})
        except Exception:
            pass
        self.proc.terminate()
