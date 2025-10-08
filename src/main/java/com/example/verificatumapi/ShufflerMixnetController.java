package com.example.verificatumapi;

import org.springframework.core.io.FileSystemResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.HttpHeaders;

import java.io.*;
import java.net.URL;
import java.nio.file.Files;
import java.util.*;
import java.util.concurrent.*;

@RestController
@RequestMapping("/shuffler")
public class ShufflerMixnetController {

    private static final int NUM_SERVERS = 3;
    private static final String BASE_DIR = System.getProperty("user.dir") + "/shuffler-demo";
    private static final String SESSION_ID = "ShuffleSession";
    private static final String ELECTION_NAME = "ShufflerNet";
    private boolean auto_local = false;

    @PostMapping("/setup")
    public Map<String, String> setup(
            @RequestParam(defaultValue = "false") boolean auto,
            @RequestParam("publicKeyUrl") String keyUrl) {
        try {
            auto_local = auto;
            VerificatumCleaner.resetShuffler(BASE_DIR, NUM_SERVERS);
            MixnetCommon.cleanAndPrepareBase(BASE_DIR, NUM_SERVERS);

            // Step 1: Download publicKeyNative
            File publicKeyNative = new File(BASE_DIR + "/publicKeyNative");
            try (InputStream in = new URL(keyUrl).openStream()) {
                Files.copy(in, publicKeyNative.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            }
            
            if (auto_local) {       

                // Step 2: Set up mixnet party info
                for (int i = 1; i <= NUM_SERVERS; i++) {
                    File serverDir = new File(BASE_DIR + "/0" + i);
                    MixnetCommon.run(serverDir, "vmni", "-prot",
                            "-sid", SESSION_ID,
                            "-name", ELECTION_NAME,
                            "-nopart", String.valueOf(NUM_SERVERS),
                            "-thres", "2"
                    );
                    MixnetCommon.run(serverDir, "vmni", "-party",
                            "-name", "Shuffler_0" + i,
                            "-http", "http://localhost:805" + i,
                            "-hint", "localhost:405" + i
                    );
                    new File(serverDir, "localProtInfo.xml")
                            .renameTo(new File(serverDir, "protInfo0" + i + ".xml"));
                }

                // Step 3: Cross-copy protInfo files
                for (int i = 1; i <= NUM_SERVERS; i++) {
                    File src = new File(BASE_DIR + "/0" + i);
                    for (int j = 1; j <= NUM_SERVERS; j++) {
                        if (i == j) continue;
                        File dst = new File(BASE_DIR + "/0" + j);
                        Files.copy(new File(src, "protInfo0" + i + ".xml").toPath(),
                                new File(dst, "protInfo0" + i + ".xml").toPath(),
                                java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                    }
                }

                // Step 4: Merge protInfo and convert public key
                for (int i = 1; i <= NUM_SERVERS; i++) {
                    File dir = new File(BASE_DIR + "/0" + i);
                    MixnetCommon.run(dir, "vmni", "-merge",
                            "protInfo01.xml", "protInfo02.xml", "protInfo03.xml"
                    );
                    // Convert publicKeyNative → raw format expected by setpk
                    MixnetCommon.run(dir, "vmnc", "-pkey", "-ini", "native",
                            "protInfo.xml", "../publicKeyNative", "../publicKey");
                }

                // Step 5: Set external public key in raw format
                for (int i = 1; i <= NUM_SERVERS; i++) {
                    File dir = new File(BASE_DIR + "/0" + i);
                    MixnetCommon.run(dir, "vmn", "-setpk",
                            "privInfo.xml", "protInfo.xml", "../publicKey");
                }
            } else {
                File serverDir = new File(BASE_DIR + "/01");
                MixnetCommon.run(serverDir, "vmni", "-prot",
                        "-sid", SESSION_ID,
                        "-name", ELECTION_NAME,
                        "-nopart", String.valueOf(NUM_SERVERS),
                        "-thres", "2"
                );
                String localAddress = MixnetCommon.getLocalAddress();
                MixnetCommon.run(serverDir, "vmni", "-party",
                        "-name", "Shuffler_01",
                        "-http", "http://" + localAddress + ":8051",
                        "-hint", localAddress + ":4051"
                );
                new File(serverDir, "localProtInfo.xml")
                        .renameTo(new File(serverDir, "protInfo01" + ".xml"));
            }

            return Map.of("status", "Shuffler setup complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/setup-local")
    public Map<String, String> setupLocal(
            @RequestParam int serverId,
            @RequestParam(defaultValue = "3") int numServers,
            @RequestParam(defaultValue = "2") int thres,
            @RequestParam(defaultValue = "ShuffleSession") String sessionId,
            @RequestParam(defaultValue = "ShufflerNet") String electionName) {
        try {
            MixnetCommon.cleanAndPrepareBase(BASE_DIR, NUM_SERVERS);
            File serverDir = new File(BASE_DIR + "/0" + serverId);
            MixnetCommon.run(serverDir, "vmni", "-prot",
                    "-sid", sessionId,
                    "-name", electionName,
                    "-nopart", String.valueOf(numServers),
                    "-thres", String.valueOf(thres)
            );

            String localAddress = MixnetCommon.getLocalAddress();
            
            MixnetCommon.run(serverDir, "vmni", "-party",
                    "-name", "Shuffler_0" + serverId,
                    "-http", "http://" + localAddress + ":805" + serverId,
                    "-hint", localAddress + ":405" + serverId
            );
            new File(serverDir, "localProtInfo.xml")
                    .renameTo(new File(serverDir, "protInfo0" + serverId + ".xml"));

            return Map.of("status", "Setup local complete (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/merge-local")
    public Map<String, String> mergeLocal(
            @RequestParam int serverId,
            @RequestParam int numServers) {
        try {
            File serverDir = new File(BASE_DIR + "/0" + serverId);
            MixnetCommon.run(serverDir, "vmni", "-merge",
                    "protInfo01.xml", "protInfo02.xml", "protInfo03.xml" //ajustar para numServers
            );

            return Map.of("status", "Merge local complete (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/setpk-local")
    public Map<String, String> setpkLocal(
            @RequestParam int serverId) {
        try {
            File serverDir = new File(BASE_DIR + "/0" + serverId);
            // Convert publicKeyNative → raw format expected by setpk
            MixnetCommon.run(serverDir, "vmnc", "-pkey", "-ini", "native",
                    "protInfo.xml", "../publicKeyNative", "../publicKey");

            // Set external public key in raw format
            MixnetCommon.run(serverDir, "vmn", "-setpk",
                    "privInfo.xml", "protInfo.xml", "../publicKey");

            return Map.of("status", "Set public key local complete (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/receive-ciphertexts")
    public Map<String, String> receiveCiphertexts(@RequestParam("file") MultipartFile file) {
        try {
            File target = new File(BASE_DIR + "/01/ciphertexts");

            // Ensure the parent directory exists
            File parent = target.getParentFile();
            if (!parent.exists()) {
                parent.mkdirs();
            }

            // Save uploaded file to BASE_DIR/01/ciphertexts
            file.transferTo(target);

            if (auto_local) {
                // Copy ciphertext to other servers
                for (int i = 2; i <= NUM_SERVERS; i++) {
                    File dir = new File(BASE_DIR + "/0" + i);
                    if (!dir.exists()) {
                        dir.mkdirs();
                    }
                    Files.copy(target.toPath(),
                            new File(dir, "ciphertexts").toPath(),
                            java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                }
            }

            return Map.of("status", "Ciphertexts received and copied");
        } catch (IOException e) {
            e.printStackTrace();
            return Map.of("error", "Failed to save ciphertexts: " + e.getMessage());
        }
    }

    @PostMapping("/shuffle")
    public Map<String, String> shuffle() {
        try {
            if (auto_local) {
                ExecutorService executor = Executors.newFixedThreadPool(NUM_SERVERS);
                List<Future<?>> futures = new ArrayList<>();

                for (int i = 1; i <= NUM_SERVERS; i++) {
                    final int idx = i;
                    Thread.sleep(1000);
                    futures.add(executor.submit(() -> {
                        File dir = new File(BASE_DIR + "/0" + idx);
                        try {
                            // Step 1: Convert ciphertexts to raw format (if necessary)
                            MixnetCommon.run(dir, "vmnc", "-ciphs", "-ini", "native",
                                    "protInfo.xml", "ciphertexts", "ciphertextsRaw");

                            // Step 2: Shuffle using the raw ciphertexts
                            MixnetCommon.run(dir, "vmn", "-shuffle",
                                    "privInfo.xml", "protInfo.xml", "ciphertextsRaw", "shuffled");
                        } catch (IOException | InterruptedException e) {
                            e.printStackTrace();
                        }
                    }));
                }

                for (Future<?> f : futures) f.get();
                executor.shutdown();

                // Copy shuffled output to guardian nodes
                File shuffledFile = new File(BASE_DIR + "/01/shuffled");
                for (int i = 1; i <= NUM_SERVERS; i++) {
                    File dest = new File("verificatum-guardian/0" + i + "/shuffled-ciphertexts");
                    Files.copy(shuffledFile.toPath(), dest.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                }
                MixnetCommon.killAllHintPorts(4040, 4060);
            } else {
                return shuffleLocal(1);
            }

            return Map.of("status", "Shuffle complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", "Shuffle failed: " + e.getMessage());
        }
    }

    @PostMapping("/shuffle-local")
    public Map<String, String> shuffleLocal(
            @RequestParam int serverId) {
        try {
            ExecutorService executor = Executors.newFixedThreadPool(NUM_SERVERS);
            List<Future<?>> futures = new ArrayList<>();

            futures.add(executor.submit(() -> {
                File dir = new File(BASE_DIR + "/0" + serverId);
                try {
                    // Step 1: Convert ciphertexts to raw format (if necessary)
                    MixnetCommon.run(dir, "vmnc", "-ciphs", "-ini", "native",
                            "protInfo.xml", "ciphertexts", "ciphertextsRaw");

                    // Step 2: Shuffle using the raw ciphertexts
                    MixnetCommon.run(dir, "vmn", "-shuffle",
                            "privInfo.xml", "protInfo.xml", "ciphertextsRaw", "shuffled");
                } catch (IOException | InterruptedException e) {
                    e.printStackTrace();
                }
            }));

            for (Future<?> f : futures) f.get();
            executor.shutdown();

            return Map.of("status", "Shuffle complete (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", "Shuffle failed: " + e.getMessage());
        }
    }

    @GetMapping("/shuffled-ciphertexts")
    public ResponseEntity<FileSystemResource> getShuffledCiphertextsNative() {
        try {
            String baseDir = System.getProperty("user.dir") + "/shuffler-demo"; // keep consistent with your class
            File nativeFile = NativeConverters.ensureShufflerShuffledNative(baseDir);
            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=shuffled.native")
                    .contentLength(nativeFile.length())
                    .body(new FileSystemResource(nativeFile));
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping("/log")
    public ResponseEntity<FileSystemResource> getShufflerLog(
        @RequestParam int serverId) {
        try {
            String baseDir = System.getProperty("user.dir") + "/shuffler-demo";
            File log = NativeConverters.shufflerLogFile(baseDir, serverId);
            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=vmn.log")
                    .contentLength(log.length())
                    .body(new FileSystemResource(log));
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.notFound().build();
        }
    }
}
