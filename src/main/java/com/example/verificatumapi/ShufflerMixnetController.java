package com.example.verificatumapi;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

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

            // Step 1: Download publicKeyNative
            File publicKeyNative = new File(BASE_DIR + "/publicKeyNative");
            try (InputStream in = new URL(keyUrl).openStream()) {
                Files.copy(in, publicKeyNative.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            }

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

            return Map.of("status", "Shuffler setup complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/receive-ciphertexts")
    public Map<String, String> receiveCiphertexts(@RequestParam("file") MultipartFile file) {
        try {
            File target = new File(BASE_DIR + "/01/ciphertexts");
            file.transferTo(target);
    
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
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }));
            }

            for (Future<?> f : futures) f.get();
            executor.shutdown();

            // Copy shuffled to all guardian nodes
            File shuffledFile = new File(BASE_DIR + "/01/shuffled");
            for (int i = 1; i <= NUM_SERVERS; i++) {
                File dest = new File("verificatum-guardian/0" + i + "/shuffled-ciphertexts");
                Files.copy(shuffledFile.toPath(), dest.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            }

            return Map.of("status", "Shuffle complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", "Shuffle failed: " + e.getMessage());
        }
    }
}
