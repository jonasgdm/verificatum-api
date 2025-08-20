package com.example.verificatumapi;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.*;
import org.springframework.core.io.FileSystemResource;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;

import java.io.File;
import java.io.IOException;
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

            if (c.auto) {
                // local
                MixnetCommon.keygenLocal(c.baseDir, 1);
                // remotes
                for (int id = 2; id <= c.numServers; id++) {
                    String remote = c.servers.get(id - 2);
                    String cmd = "curl -sS -X POST http://localhost:8080/guardian/keygen-local"
                            + " -d 'serverId=" + id + "'";
                    RemoteExecutor.executeSSH(remote, cmd);
                }
            } else {
                // manual: only run local; others must run /keygen-local themselves
                MixnetCommon.keygenLocal(c.baseDir, 1);
            }

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

    /* =====================
       DECRYPT
       ===================== */
    @PostMapping(value = "/decrypt")
    public ResponseEntity<MultiValueMap<String, Object>> decrypt() {
        try {
            GuardianConfig c = cfg();
            ensureSetupConfigured(c);

            if (c.auto) {
                // local
                MixnetCommon.decryptLocal(c.baseDir, 1);
                // remotes
                for (int id = 2; id <= c.numServers; id++) {
                    String remote = c.servers.get(id - 2);
                    String cmd = "curl -sS -X POST http://localhost:8080/guardian/decrypt-local"
                            + " -d 'serverId=" + id + "'";
                    RemoteExecutor.executeSSH(remote, cmd);
                }
            } else {
                // manual: only run local; others must run /decrypt-local themselves
                MixnetCommon.decryptLocal(c.baseDir, 1);
            }

            // Return Guardian 1 result as multipart (plaintexts.native)
            File dir01 = new File(c.baseDir + "/01");
            File logs = new File(c.baseDir + "/logs");
            logs.mkdirs();

            MixnetCommon.run(dir01, "vmnc", "-plain", "-outi", "native",
                    "protInfo.xml", "plaintexts", "plaintexts.native");

            File nativeFile = new File(dir01, "plaintexts.native");
            Files.copy(nativeFile.toPath(), new File(logs, "plaintexts.native").toPath(),
                    StandardCopyOption.REPLACE_EXISTING);

            MultiValueMap<String, Object> resp = new LinkedMultiValueMap<>();
            resp.add("file", new FileSystemResource(nativeFile));
            return ResponseEntity.ok()
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(resp);

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }

    @PostMapping("/decrypt-local")
    public Map<String, String> decryptLocal(@RequestParam int serverId) {
        return MixnetCommon.decryptLocal(cfg().baseDir, serverId);
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

    // Pull protInfo0X.xml from remotes into Guardian 1
    private void collectProtInfos() throws Exception {
        GuardianConfig c = cfg();
        for (int id = 2; id <= c.numServers; id++) {
            String remote = c.servers.get(id - 2);
            String remotePath = c.baseDir + "/0" + id + "/protInfo0" + id + ".xml";
            File localDir = new File(c.baseDir + "/0" + id);
            localDir.mkdirs();
            String localPath = localDir.getPath() + "/protInfo0" + id + ".xml";
            RemoteExecutor.scpFrom(remote, remotePath, localPath);
        }
        // Ensure our own file exists locally already (01)
        // (generated by setupLocal)
    }

    // Send all protInfo0X.xml to every server (including local)
    private void distributeProtInfos() throws Exception {
        GuardianConfig c = cfg();

        // Prepare local source files (Guardian 1 has all after collect)
        Map<Integer, File> src = new HashMap<>();
        for (int k = 1; k <= c.numServers; k++) {
            File f = new File(c.baseDir + "/0" + k + "/protInfo0" + k + ".xml");
            if (!f.exists()) {
                throw new IllegalStateException("Missing file on orchestrator: " + f.getPath());
            }
            src.put(k, f);
        }

        // 1) Copy into local /0j for j=1
        for (int k = 1; k <= c.numServers; k++) {
            File dst = new File(c.baseDir + "/01/protInfo0" + k + ".xml");
            Files.copy(src.get(k).toPath(), dst.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }

        // 2) Copy to each remote j=2..N
        for (int j = 2; j <= c.numServers; j++) {
            String remote = c.servers.get(j - 2);
            // ensure remote /0j exists (it does after setup-local)
            for (int k = 1; k <= c.numServers; k++) {
                RemoteExecutor.scpTo(
                        src.get(k).getPath(),
                        remote,
                        c.baseDir + "/0" + j + "/protInfo0" + k + ".xml"
                );
            }
        }
    }
}
