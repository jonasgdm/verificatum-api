package com.example.verificatumapi;

import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.IOException;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/verificatum")
public class VerificatumController {

    private static final int NUM_SERVERS = 3;
    private static final String BASE_DIR = "verificatum-demo";
    private static final String SESSION_ID = "SessionID";
    private static final String ELECTION_NAME = "Swedish Election";

    @PostMapping("/setup")
    public Map<String, String> setup() {
        try {
            for (int i = 1; i <= NUM_SERVERS; i++) {
                File serverDir = new File(BASE_DIR + "/0" + i);
                serverDir.mkdirs();

                // Step 0: Generate stub
                run("vmni", "-prot",
                        "-sid", SESSION_ID,
                        "-name", ELECTION_NAME,
                        "-nopart", String.valueOf(NUM_SERVERS),
                        "-thres", "2",
                        "-basedir", serverDir.getAbsolutePath()
                );

                // Step 1: Generate party info
                run("vmni", "-party",
                        "-name", "Mix-server 0" + i,
                        "-http", "http://localhost:804" + i,
                        "-hint", "localhost:404" + i,
                        "-basedir", serverDir.getAbsolutePath()
                );

                // Rename localProtInfo.xml to protInfo0X.xml
                new File(serverDir, "localProtInfo.xml")
                        .renameTo(new File(serverDir, "protInfo0" + i + ".xml"));
            }

            // Step 1: Cross-copy protocol files
            for (int i = 1; i <= NUM_SERVERS; i++) {
                File srcDir = new File(BASE_DIR + "/0" + i);
                for (int j = 1; j <= NUM_SERVERS; j++) {
                    if (i == j) continue;
                    File destDir = new File(BASE_DIR + "/0" + j);
                    File proto = new File(srcDir, "protInfo0" + i + ".xml");
                    File dest = new File(destDir, "protInfo0" + i + ".xml");
                    java.nio.file.Files.copy(proto.toPath(), dest.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                }
            }

            return Map.of("status", "Setup complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/keygen")
    public Map<String, String> keygen() {
        try {
            for (int i = 1; i <= NUM_SERVERS; i++) {
                File dir = new File(BASE_DIR + "/0" + i);

                // Step 2: Merge protocol files
                run("vmni", "-merge",
                        "-basedir", dir.getAbsolutePath(),
                        "protInfo01.xml", "protInfo02.xml", "protInfo03.xml"
                );

                // Generate public key
                run("vmn", "-keygen",
                        "-basedir", dir.getAbsolutePath(),
                        "publicKey"
                );
            }
            return Map.of("status", "Keygen complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/generate-ciphertexts")
    public Map<String, String> generateCiphertexts() {
        try {
            File dir = new File(BASE_DIR + "/01");
            run("vmnd", "-ciphs",
                    new File(dir, "publicKey").getAbsolutePath(),
                    "100", "ciphertexts"
            );

            for (int i = 2; i <= NUM_SERVERS; i++) {
                File src = new File(dir, "ciphertexts");
                File dest = new File(BASE_DIR + "/0" + i + "/ciphertexts");
                java.nio.file.Files.copy(src.toPath(), dest.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            }

            return Map.of("status", "Ciphertexts generated");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/mix")
    public Map<String, String> mix() {
        try {
            for (int i = 1; i <= NUM_SERVERS; i++) {
                File dir = new File(BASE_DIR + "/0" + i);
                run("vmn", "-mix",
                        "-basedir", dir.getAbsolutePath(),
                        "ciphertexts", "plaintexts"
                );
            }
            return Map.of("status", "Mixing complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    private static void run(String... command) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder(command);
        pb.inheritIO();
        Process p = pb.start();
        int exitCode = p.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Command failed: " + String.join(" ", command));
        }
    }
}
