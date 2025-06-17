import uuid
import random
import subprocess
import os
import json
import csv


class MockElection:
    def __init__(self, public_key_str: str, election_config: dict):
        self.public_key_str = public_key_str
        self.public_key_path = "public_key.json"  # Ex: "publicKey.json"
        self.config = election_config

        # Vai conter objetos AnyVote simulados
        self.gavt = []

        self.rdv = []

        # Códigos únicos por candidato (gerados a partir de config)
        self.candidate_codes = {}

        self.gen_candidate_codes()

        # Contagem agregada de votos por contest
        self.tally = {
            cargo: {cand: 0 for cand in candidatos}
            for cargo, candidatos in self.candidate_codes.items()
        }

    def gen_candidate_codes(self):
        """Gera os códigos dos candidatos para cada cargo com base no config."""

        for option in self.config["options"]:
            contest = option["contest"]
            qtd = option["candidates"]
            digits = option["digits"]

            if qtd > 0:
                start = int("9" * digits)
                self.candidate_codes[contest] = [start - j for j in range(qtd)]

    def gen_any_vote(self, tokenid) -> dict:
        """Gera e armazena um AnyVote simulado com token e atualização do tally."""
        encrypted_votes = []

        for contest, codes in self.candidate_codes.items():
            if not codes:
                continue

            escolhido = random.choice(codes)

            # Atualiza tally
            self.tally[contest][escolhido] += 1

            # Criptografa e adiciona à lista
            encrypted = self.encrypt(str(escolhido))
            encrypted_votes.append(encrypted)

        any_vote = {
            "tokenID": tokenid,
            "encryptedVotes": encrypted_votes,
            "metadata": {
                "hasBiometry": True,
                "votingMachineID": random.randint(1, self.config["numberBallots"]),
            },
        }

        self.gavt.append(any_vote)

        return any_vote

    def generate_conventional_vote(self):
        """Gera um voto convencional: escolhe 1 candidato por cargo, atualiza o tally e registra na RDV."""
        voto = []

        for cargo, candidatos in self.candidate_codes.items():
            escolhido = random.choice(candidatos)
            voto.append(escolhido)
            self.tally[cargo][escolhido] += 1  # atualiza contagem

        self.rdv.append(voto)

    def simulate(self):
        # Gera votos cifrados (anyVotes)
        for _ in range(self.config.get("anyVotes")):
            tokenid = str(uuid.uuid4())
            self.gen_any_vote(tokenid)

        # Gera votos convencionais (não cifrados)
        for _ in range(self.config.get("conventionalVotes")):
            self.generate_conventional_vote()

        # Gera votos duplicados (anyVotes com mesmo token)
        for _ in range(self.config.get("doubleVotes")):
            self.double_vote()

        self.export_gavt("json")
        self.export_gavt("csv")

    def export_ciphertexts(self):
        """Exporta os votos cifrados da gavt para arquivos .bt individuais."""
        raise NotImplementedError

    def encrypt(self, value: str) -> str:
        """Chama o script Node.js para cifrar o valor e retorna a string JSON do ByteTree cifrado."""
        result = subprocess.run(
            ["node", "encryptor/encrypt.js", self.public_key_path, value],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Erro ao cifrar: {result.stderr}")

        return result.stdout.strip()

    def double_vote(self):
        """Duplica um anyVote já existente na GAVT usando o mesmo tokenID."""
        if not self.gavt:
            raise ValueError("Não há anyVotes na GAVT para duplicar.")

        voto_original = random.choice(self.gavt)
        token_id = voto_original["tokenID"]

        # Gera novo voto com mesmo token (conteúdo criptografado será novo)
        return self.gen_any_vote(tokenid=token_id)

    def export_gavt(self, format="json"):
        os.makedirs("output", exist_ok=True)

        if format == "json":
            with open("output/gavt.json", "w", encoding="utf-8") as f:
                json.dump(self.gavt, f, ensure_ascii=False, indent=2)
        elif format == "csv":
            with open("output/gavt.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["tokenID", "encryptedVotes", "metadata"]
                )
                writer.writeheader()
                for voto in self.gavt:
                    writer.writerow(
                        {
                            "tokenID": voto["tokenID"],
                            "encryptedVotes": json.dumps(voto["encryptedVotes"]),
                            "metadata": json.dumps(voto["metadata"]),
                        }
                    )
        else:
            raise ValueError("Formato inválido: use 'json' ou 'csv'.")
