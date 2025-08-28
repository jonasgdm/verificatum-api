package com.example.verificatumapi;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.*;
import org.springframework.core.io.FileSystemResource;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.*;

@RestController
@RequestMapping("/guardian")
public class GuardianMixnetController {

    private GuardianConfig cfg() { return GuardianConfig.get(); }

    /* =====================
       SETUP (front hits only Guardian 1)
       ===================== */
    @PostMapping("/setup")
    public Map<String, String> setup(
            @RequestParam(defaultValue = "false") boolean auto,
            @RequestParam(defaultValue = "3") int numServers,
            @RequestBody(required = false) Map<String, Object> body) {

        try {
            GuardianConfig c = cfg();
            c.auto = auto;
            c.numServers = numServers;
            c.baseDir = "verificatum-guardian";
            c.sessionId = "GuardianSession";
            c.electionName = "Guardian_Election";
            c.localServerId = 1;    

            // limpeza completa antes do setup
            VerificatumCleaner.resetGuardian(c.baseDir, c.numServers);

            // recria estrutura limpa
            MixnetCommon.cleanAndPrepareBase(c.baseDir, c.numServers);

            if (auto) {
                // Expect body.servers = ["user@ip_for_id2", "user@ip_for_id3", ...]
                @SuppressWarnings("unchecked")
                List<String> servers = (body != null) ? (List<String>) body.get("servers") : null;
                c.servers = servers;
                c.validateForAuto();

                // 1) Setup local serverId=1
                MixnetCommon.setupLocal(c.baseDir, c.sessionId, c.electionName, c.numServers, 1);

                // 2) Setup on remotes via SSH (serverId 2..N)
                for (int id = 2; id <= c.numServers; id++) {
                    String remote = c.servers.get(id - 2);
                    String cmd = "curl -sS -X POST http://localhost:8080/guardian/setup-local"
                            + " -d 'serverId=" + id + "&numServers=" + c.numServers
                            + "&sessionId=" + c.sessionId
                            + "&electionName=" + c.electionName + "'";
                    RemoteExecutor.executeSSH(remote, cmd);
                }

                // 3) Collect all protInfo0X.xml from remotes to Guardian 1
                collectProtInfos();

                // 4) Distribute all protInfo0X.xml to every server (including local)
                distributeProtInfos();

                // 5) Merge on every server
                MixnetCommon.mergeLocal(c.baseDir, c.numServers, 1);
                for (int id = 2; id <= c.numServers; id++) {
                    String remote = c.servers.get(id - 2);
                    String cmd = "curl -sS -X POST http://localhost:8080/guardian/merge-local"
                            + " -d 'serverId=" + id + "&numServers=" + c.numServers + "'";
                    RemoteExecutor.executeSSH(remote, cmd);
                }

            } else {
                // Manual (pendrive): only local node generates its protInfo0{serverId}.xml.
                // Users will run /setup-local on each machine and share files manually, then /merge-local.
                MixnetCommon.setupLocal(c.baseDir, c.sessionId, c.electionName, c.numServers, 1);
            }

            return Map.of("status", "Setup complete (" + (auto ? "auto" : "manual") + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    // Used locally in each Guardian (or via SSH by Guardian 1)
    @PostMapping("/setup-local")
    public Map<String, String> setupLocal(
            @RequestParam int serverId,
            @RequestParam int numServers,
            @RequestParam String sessionId,
            @RequestParam String electionName) {
        GuardianConfig c = cfg();
        // Keep config coherent if this node is also Guardian 1
        c.numServers = numServers;
        c.sessionId = sessionId;
        c.electionName = electionName;

        VerificatumCleaner.resetGuardianNode(c.baseDir, serverId);

        return MixnetCommon.setupLocal(c.baseDir, sessionId, electionName, numServers, serverId);
    }

    // Merge local protInfo0*.xml → protInfo.xml (manual or auto)
    @PostMapping("/merge-local")
    public Map<String, String> mergeLocal(
            @RequestParam int serverId,
            @RequestParam int numServers) {
        GuardianConfig c = cfg();
        c.numServers = numServers; // keep in sync
        return MixnetCommon.mergeLocal(c.baseDir, numServers, serverId);
    }

    /* =====================
       KEYGEN
       ===================== */
    @PostMapping("/keygen")
    public Map<String, String> keygen() {
        try {
            GuardianConfig c = cfg();
            ensureSetupConfigured(c);

            // sempre libere portas do nó 1 antes
            VerificatumCleaner.freeGuardianServer(1);

            if (c.auto) {
                // 1) inicia local em background
                MixnetCommon.startKeygenDetached(c.baseDir, 1);

                // 2) inicia remotos em background (curl retorna rápido)
                for (int id = 2; id <= c.numServers; id++) {
                    String remote = c.servers.get(id - 2);
                    String cmd = "curl -sS -X POST http://localhost:8080/guardian/keygen-local-async"
                            + " -d 'serverId=" + id + "'";
                    RemoteExecutor.executeSSH(remote, cmd);
                }
            } else {
                // manual: pode usar também o modo detached para manter consistência
                MixnetCommon.startKeygenDetached(c.baseDir, 1);
                // os outros nós devem chamar /guardian/keygen-local-async localmente
            }

            // 3) orquestrador aguarda *apenas* o arquivo do nó 1 (suficiente p/ saber que terminou)
            File pk1 = new File(c.baseDir + "/01/publicKey");
            boolean ok = MixnetCommon.waitForFile(pk1, 10 * 60 * 1000L); // timeout 10min
            if (!ok) {
                File log = new File(c.baseDir + "/01/vmn.log");
                throw new RuntimeException("Timeout aguardando keygen no nó 1. Ver log: " + log.getAbsolutePath());
            }

            // (opcional) já converte e deixa pronto pro front
            NativeConverters.ensureGuardianPublicKeyNative(c.baseDir);

            return Map.of("status", "Keygen complete (" + (c.auto ? "auto" : "manual") + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/keygen-local")
    public Map<String, String> keygenLocal(@RequestParam int serverId) {
        return MixnetCommon.keygenLocal(cfg().baseDir, serverId);
    }

    @PostMapping("/keygen-local-async")
    public Map<String, String> keygenLocalAsync(@RequestParam int serverId) {
        try {
            // libera portas desse nó antes de iniciar
            VerificatumCleaner.freeGuardianServer(serverId);
            MixnetCommon.startKeygenDetached(cfg().baseDir, serverId);
            return Map.of("status", "keygen started (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    /* =====================
       DECRYPT
       ===================== */
    @PostMapping(value = "/decrypt")
    public ResponseEntity<MultiValueMap<String, Object>> decrypt() {
        try {
            GuardianConfig c = cfg();
            ensureSetupConfigured(c);

            // libera portas do nó 1 antes de começar
            VerificatumCleaner.freeGuardianServer(1);

            if (c.auto) {
                // 1) inicia local (nó 1) em background
                MixnetCommon.startDecryptDetached(c.baseDir, 1);

                // 2) inicia remotos em background via SSH
                for (int id = 2; id <= c.numServers; id++) {
                    String remote = c.servers.get(id - 2);
                    String cmd = "curl -sS -X POST http://localhost:8080/guardian/decrypt-local-async"
                            + " -d 'serverId=" + id + "'";
                    RemoteExecutor.executeSSH(remote, cmd);
                }
            } else {
                // Manual: dispara só o local; demais nós devem chamar /decrypt-local-async por conta própria
                MixnetCommon.startDecryptDetached(c.baseDir, 1);
            }

            // 3) orquestrador aguarda o artefato do nó 1
            File dir01 = new File(c.baseDir + "/01");
            File plaintexts = new File(dir01, "plaintexts");
            boolean ok = MixnetCommon.waitForFile(plaintexts, 10 * 60 * 1000L); // timeout 10 min
            if (!ok) {
                File log = new File(dir01, "vmn.log");
                return ResponseEntity.status(HttpStatus.REQUEST_TIMEOUT).body(errorBody(
                        "Timeout aguardando decrypt no nó 1. Veja o log: " + log.getAbsolutePath()));
            }

            // 4) converte para nativo e devolve (como já fazíamos)
            MixnetCommon.run(dir01, "vmnc", "-plain", "-outi", "native",
                    "protInfo.xml", "plaintexts", "plaintexts.native");

            File nativeFile = new File(dir01, "plaintexts.native");

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", new FileSystemResource(nativeFile));

            return ResponseEntity.ok()
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body);

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorBody(e.getMessage()));
        }
    }

    private MultiValueMap<String, Object> errorBody(String msg) {
        MultiValueMap<String, Object> m = new LinkedMultiValueMap<>();
        m.add("error", msg);
        return m;
    }


    @PostMapping("/decrypt-local")
    public Map<String, String> decryptLocal(@RequestParam int serverId) {
        return MixnetCommon.decryptLocal(cfg().baseDir, serverId);
    }

    @PostMapping("/decrypt-local-async")
    public Map<String, String> decryptLocalAsync(@RequestParam int serverId) {
        try {
            // libera portas deste nó antes de iniciar
            VerificatumCleaner.freeGuardianServer(serverId);
            MixnetCommon.startDecryptDetached(cfg().baseDir, serverId);
            return Map.of("status", "decrypt started (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @GetMapping("/public-key")
    public ResponseEntity<FileSystemResource> getPublicKeyNative() {
        try {
            File nativePk = NativeConverters.ensureGuardianPublicKeyNative(GuardianConfig.get().baseDir);

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=publicKey.native")
                    .contentLength(nativePk.length())
                    .body(new FileSystemResource(nativePk));
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.notFound().build();
        }
    }

    /* =====================
       Helpers (auto)
       ===================== */

    private void ensureSetupConfigured(GuardianConfig c) {
        if (c == null || c.numServers <= 0) {
            throw new IllegalStateException("Call /guardian/setup first.");
        }
        if (c.auto) c.validateForAuto();
    }

    // Helper simples para detectar "localhost"
    private boolean isLocalHost(String remote) {
        if (remote == null) return false;
        // formatos típicos: "user@127.0.0.1", "user@localhost", "127.0.0.1", "localhost"
        String host = remote.contains("@") ? remote.substring(remote.indexOf("@") + 1) : remote;
        host = host.trim();
        return "127.0.0.1".equals(host) || "localhost".equalsIgnoreCase(host);
    }

    // Pull protInfoXX.xml from remotes into Guardian 1
    private void collectProtInfos() throws Exception {
        GuardianConfig c = cfg();
        for (int id = 2; id <= c.numServers; id++) {
            String remote = c.servers.get(id - 2);
            String fileName = String.format("protInfo%02d.xml", id);

            // Em cada remoto, esperamos em: <baseDir>/0{id}/protInfoXX.xml
            String remotePath = c.baseDir + "/0" + id + "/" + fileName;

            // No orquestrador, guardamos em: <baseDir>/0{id}/protInfoXX.xml
            File localDir = new File(c.baseDir + "/0" + id);
            localDir.mkdirs();
            String localPath = new File(localDir, fileName).getPath();

            if (isLocalHost(remote)) {
                // Mesmo host: nada a copiar via scp; apenas verifique se existe
                File f = new File(localPath);
                if (!f.exists()) {
                    // Se por algum motivo o setup-local escreveu em outro lugar, tente copiar localmente
                    // Mas como o caminho é o mesmo, normalmente não precisa fazer nada aqui.
                    throw new IllegalStateException("Arquivo esperado não existe localmente: " + localPath);
                }
            } else {
                // Host remoto de verdade: SCP
                RemoteExecutor.scpFrom(remote, remotePath, localPath);
            }
        }
        // O arquivo do próprio Guardian 1 é <baseDir>/01/protInfo01.xml (já criado no setup-local)
    }

    // Send all protInfoXX.xml to every server (including local)
    private void distributeProtInfos() throws Exception {
        GuardianConfig c = cfg();

        // 1) Colete as fontes locais (depois do collect, Guardian 1 tem todos)
        Map<Integer, File> src = new HashMap<>();
        for (int k = 1; k <= c.numServers; k++) {
            String fileName = String.format("protInfo%02d.xml", k);
            File f = new File(c.baseDir + "/0" + k + "/" + fileName);
            if (!f.exists()) {
                throw new IllegalStateException("Falta arquivo no orquestrador: " + f.getPath());
            }
            src.put(k, f);
        }

        // 2) Copie para o próprio Guardian 1 (destino: <baseDir>/01/protInfoXX.xml)
        File dir01 = new File(c.baseDir + "/01");
        dir01.mkdirs();
        for (int k = 1; k <= c.numServers; k++) {
            File dst = new File(dir01, String.format("protInfo%02d.xml", k));
            Files.copy(src.get(k).toPath(), dst.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        }

        // 3) Copie para cada remoto j = 2..N (destino: <baseDir>/0{j}/protInfoXX.xml)
        for (int j = 2; j <= c.numServers; j++) {
            String remote = c.servers.get(j - 2);
            for (int k = 1; k <= c.numServers; k++) {
                String fileName = String.format("protInfo%02d.xml", k);
                String remoteDest = c.baseDir + "/0" + j + "/" + fileName;

                if (isLocalHost(remote)) {
                    // Mesmo host: é só copiar localmente
                    File localDstDir = new File(c.baseDir + "/0" + j);
                    localDstDir.mkdirs();
                    File localDst = new File(localDstDir, fileName);
                    Files.copy(src.get(k).toPath(), localDst.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                } else {
                    RemoteExecutor.scpTo(src.get(k).getPath(), remote, remoteDest);
                }
            }
        }
    }
}
