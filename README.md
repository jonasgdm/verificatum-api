# API Verificatum – MixNet + Guardian (TCC Criptografia)

> **Sistema de MixNet com 3 nós (Shuffler) + Descriptografia Distribuída (Guardian)**  
> Baseado em **Verificatum VMN**, com API REST em Spring Boot.  

---

## Visão Geral

- **Shuffler**: Embaralha ciphertexts (ElGamal) usando MixNet com 3 servidores.
- **Guardian**: Gera chaves distribuídas e descriptografa o resultado final.

---

## Endpoints da API

### Base URL: `http://localhost:8080`

---

## 1. SHUFFLER (Embaralhamento)

### `POST /shuffler/setup` – Configurar Shuffler
```bash
curl -X POST "http://localhost:8080/shuffler/setup?publicKeyUrl="
```

| Parâmetro | Tipo | Descrição |
|---------|------|----------|
| `auto` | `boolean` | `true` = setup local automático (3 nós no mesmo PC) |
| `publicKeyUrl` | `string` | URL do enpoint no Guardian que disponibiliza a `publicKeyNative` (formato nativo) |

**Resposta**:
```json
{ "status": "Shuffler setup complete" }
```

---

### `POST /shuffler/receive-ciphertexts` – Receber Ciphertexts
```bash
curl -X POST http://localhost:8080/shuffler/receive-ciphertexts \
  -F "file=@ciphertexts"
```

> Arquivo binário no formato **nativo** (gerado pelo frontend ou `vmnc`).

**Resposta**:
```json
{ "status": "Ciphertexts received and copied" }
```

---

### `POST /shuffler/shuffle` – Executar Shuffle
```bash
curl -X POST http://localhost:8080/shuffler/shuffle
```

> Só funciona após `setup` + `receive-ciphertexts`.

**Resposta**:
```json
{ "status": "Shuffle complete" }
```

---

### `GET /shuffler/shuffled-ciphertexts` – Baixar Resultado
```bash
curl -OJ http://localhost:8080/shuffler/shuffled-ciphertexts
```

> Salva como `shuffled.native`

---

### `GET /shuffler/log?serverId=1` – Baixar Log do Nó
```bash
curl -OJ "http://localhost:8080/shuffler/log?serverId=1"
```

> Útil para debug: `Rejected proof`, `NullPointer`, etc.

---

## 2. GUARDIAN (Chave + Descriptografia)

### `POST /guardian/setup` – Configurar Guardian
```bash
curl -X POST "http://localhost:8080/guardian/setup?numServers=3&thres=2"
```

> Só o Guardian 1 (orquestrador) chama esse endpoint.

---

### `POST /guardian/keygen` – Gerar Chave Distribuída
```bash
curl -X POST http://localhost:8080/guardian/keygen
```

> Só o Guardian 1 (orquestrador) chama esse endpoint. Aguarda até 10 min para os demais nós iniciarem também o keygen localmente.

---

### `POST /guardian/decrypt` – Descriptografar
```bash
curl -X POST http://localhost:8080/guardian/decrypt -o plaintexts.native
```

> Requer `shuffled` copiado para `/guardian/0X/shuffled` em **todos os nós**.

**Retorno**: `plaintexts.native`

---

### `GET /guardian/public-key` – Baixar Chave Pública
```bash
curl -OJ http://localhost:8080/guardian/public-key
```

> Salva como `publicKey.native`

---

## Scripts para nós locais

Use os scripts em `local-scripts/`:

| Script | Onde Rodar | Descrição |
|-------|-----------|----------|
| `guardian-setup-local.sh` | Nós 2 e 3 | Gera `protInfo0X.xml` |
| `guardian-merge-local.sh` | Todos os nós | Junta `protInfo0*.xml` |
| `guardian-keygen-local.sh` | Nós 2 e 3 | Inicia keygen |
| `guardian-decrypt-local.sh` | Nós 2 e 3 | Faz decifração |
| `shuffler-setup-local.sh` | Nós 2 e 3 | Configura shuffler |
| `shuffler-merge-local.sh` | Todos | Junta `protInfo` |
| `shuffler-setpk-local.sh` | Todos | Define chave pública |
| `shuffler-shuffle-local.sh` | Nós 2 e 3 | Embaralha localmente |

> **Sempre copie arquivos entre nós via pendrive ou SCP**.

---

## Estrutura de Pastas

```
shuffler-demo/
├── 01/, 02/, 03/
│   ├── protInfo01.xml
│   ├── ciphertexts
│   ├── shuffled
│   └── vmn.log

verificatum-guardian/
├── 01/, 02/, 03/
│   ├── protInfo01.xml
│   ├── publicKey
│   ├── shuffled
│   ├── plaintexts
│   └── vmn.log
```

## Execução Completa (Passo a Passo)

1. Instalar API
	1. git clone https://github.com/jonasgdm/verificatum-api.git
	2. cd verificatum-api
	3. mvn clean install
	4. mvn spring-boot:run
2. Rodar API
	1. cd local-scripts/
	2. setup pelo front
	3. ./local-scripts/guardian-setup-local.sh (servers 2 e 3)
	4. transferir arquivos protInfo0x para pastas de todos servers (em todos os PCs)
	5. ./local-scripts/guardian-merge-local.sh (servers 1, 2 e 3)
	6. keygen pelo front
	7. ./local-scripts/guardian-keygen-local.sh (servers 2 e 3)
	8. shuffle setup pelo front
	9. ./local-scripts/shuffle-setup-local.sh (servers 2 e 3)
	10. transferir arquivos protInfo0x %% + publicKeyNative %% para todos servers
	11. ./local-scripts/shuffler-merge-local.sh
	12. ./local-scripts/shuffler-setpk-local.sh
	13. shuffle pelo front (falha e fica suspenso, mas entrega ciphertexts no 01)
	14. transferir ciphertexts do 01 para todos servers
	15. ./local-scripts/shuffler-shuffle-local.sh (servers 2 e 3)
	16. enter no front suspenso = sucesso
	17. transferir /shuffler-demo/0x/shuffled para /verificatum-guardian/0x/
	18. decrypt pelo front
	19. ./local-scripts/guardian-decrypt-local.sh (servers 2 e 3)

---