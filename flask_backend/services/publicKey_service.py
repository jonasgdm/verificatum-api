VERIFICATUM_API_BASE_URL = "http://localhost:8080/verificatum"


class VerificatumApiService:

    @staticmethod
    def get_key():
        try:
            with open("../cli-front/mixnet/mydemodir/Party01/publicKey", "rb") as f:
                key_bytes = f.read()
            return list(key_bytes)
        except FileNotFoundError:
            return {"error": True, "message": "Arquivo publicKey não encontrado."}
        except Exception as e:
            return {"error": True, "message": f"Erro ao ler publicKey: {str(e)}"}
