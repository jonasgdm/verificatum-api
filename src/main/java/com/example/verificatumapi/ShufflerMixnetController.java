package com.example.verificatumapi;

import org.springframework.web.bind.annotation.*;
import java.io.*;
import java.net.URL;
import java.nio.file.Files;
import java.util.*;
import java.util.concurrent.*;

@RestController
@RequestMapping("/shuffler")
public class ShufflerMixnetController {

    private static final int NUM_SERVERS = 3;
    private static final String BASE_DIR = "shuffler-demo";
    private static final String SESSION_ID = "ShuffleSession";
    private static final String ELECTION_NAME = "ShufflerNet";

    @PostMapping("/setup")
    public Map<String, String> setup(@RequestParam("publicKeyUrl") String keyUrl) {
        try {
            MixnetCommon.killHintPorts(List.of(4044, 4045, 4046));
            MixnetCommon.cleanAndPrepareBase(BASE_DIR, NUM_SERVERS);

            // Fetch public key file from guardian/public-key endpoint
            File publicKeyFile = new File(BASE_DIR + "/publicKey");
            try (InputStream in = new URL(keyUrl).openStream()) {
                Files.copy(in, publicKeyFile.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            }

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

            for (int i = 1; i <= NUM_SERVERS; i++) {
                File srcDir = new File(BASE_DIR + "/0" + i);
                for (int j = 1; j <= NUM_SERVERS; j++) {
                    if (i == j) continue;
                    File destDir = new File(BASE_DIR + "/0" + j);
                    Files.copy(new File(srcDir, "protInfo0" + i + ".xml").toPath(),
                               new File(destDir, "protInfo0" + i + ".xml").toPath(),
                               java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                }
            }

            for (int i = 1; i <= NUM_SERVERS; i++) {
                File dir = new File(BASE_DIR + "/0" + i);
                MixnetCommon.run(dir, "vmni", "-merge",
                        "protInfo01.xml", "protInfo02.xml", "protInfo03.xml"
                );
                // Set external public key
                MixnetCommon.run(dir, "vmn", "-setpk", "privInfo.xml", "protInfo.xml", "../../publicKey");
            }

            return Map.of("status", "Shuffler setup complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/receive-ciphertexts")
    public Map<String, String> receiveCiphertexts(@RequestBody byte[] ciphertexts) {
        try {
            File target = new File(BASE_DIR + "/01/ciphertexts");
            Files.write(target.toPath(), ciphertexts);
            for (int i = 2; i <= NUM_SERVERS; i++) {
                Files.copy(target.toPath(),
                        new File(BASE_DIR + "/0" + i + "/ciphertexts").toPath(),
                        java.nio.file.StandardCopyOption.REPLACE_EXISTING);
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
            ExecutorService executor = Executors.newFixedThreadPool(NUM_SERVERS);
            List<Future<?>> futures = new ArrayList<>();

            for (int i = 1; i <= NUM_SERVERS; i++) {
                final int idx = i;
                Thread.sleep(1000);
                futures.add(executor.submit(() -> {
                    File dir = new File(BASE_DIR + "/0" + idx);
                    try {
                        MixnetCommon.run(dir, "vmn", "-shuffle", "privInfo.xml", "protInfo.xml", "ciphertexts", "shuffled");
                    } catch (IOException | InterruptedException e) {
                        throw new RuntimeException(e);
                    }
                }));
            }

            for (Future<?> f : futures) f.get();
            executor.shutdown();

            File output = new File(BASE_DIR + "/01/shuffled");
            byte[] shuffled = Files.readAllBytes(output.toPath());
            return Map.of("status", "Shuffle complete", "bytes", Base64.getEncoder().encodeToString(shuffled));
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", "Shuffle failed: " + e.getMessage());
        }
    }
}
