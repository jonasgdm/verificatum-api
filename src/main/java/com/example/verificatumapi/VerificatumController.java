package com.example.verificatumapi;

import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/verificatum")
public class VerificatumController {

    private static final int NUM_SERVERS = 3;
    private static final String BASE_DIR = "verificatum-demo";
    private static final String SESSION_ID = "SessionID";
    private static final String ELECTION_NAME = "Swedish_Election";

    @PostMapping("/setup")
    public Map<String, String> setup() {
        try {
            // Clean the entire base directory (except the base itself)
            File baseDir = new File(BASE_DIR);
            if (baseDir.exists()) {
                for (File f : baseDir.listFiles()) {
                    deleteRecursive(f); // delete 01/, 02/, 03/, logs/
                }
            } else {
                baseDir.mkdirs(); // ensure it exists
            }

            for (int i = 1; i <= NUM_SERVERS; i++) {
                File serverDir = new File(BASE_DIR + "/0" + i);
                serverDir.mkdirs();

                // Step 0: Generate stub
                run(serverDir, "vmni", "-prot",
                        "-sid", SESSION_ID,
                        "-name", ELECTION_NAME,
                        "-nopart", String.valueOf(NUM_SERVERS),
                        "-thres", "2"
                );

                // Step 1: Generate party info
                run(serverDir, "vmni", "-party",
                        "-name", "MixServer_0" + i,
                        "-http", "http://localhost:804" + i,
                        "-hint", "localhost:404" + i
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

            for (int i = 1; i <= NUM_SERVERS; i++) {
                File dir = new File(BASE_DIR + "/0" + i);

                // Step 2: Merge protocol files
                run(dir, "vmni", "-merge",
                        "protInfo01.xml", "protInfo02.xml", "protInfo03.xml"
                );
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
            ExecutorService executor = Executors.newFixedThreadPool(NUM_SERVERS);
            List<Future<?>> futures = new ArrayList<>();

            for (int i = 1; i <= NUM_SERVERS; i++) {
                final int index = i;
                Thread.sleep(1000);
                futures.add(executor.submit(() -> {
                    File dir = new File(BASE_DIR + "/0" + index);

                    // Keygen
                    try {
                        run(dir, "vmn", "-keygen", "publicKey");
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    } catch (InterruptedException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }));
            }

            // Wait for all servers to finish
            for (Future<?> future : futures) {
                future.get();  // Will throw if any subprocess failed
            }

            executor.shutdown();

            File publicKeyDir = new File(BASE_DIR + "/01");
            run(publicKeyDir, "vmnc", "-pkey", "-outi", "native",
                    "protInfo.xml", "publicKey", "publicKeyNative");
            File publicKeyNativeOrig = new File(publicKeyDir, "publicKeyNative");
            File logsDir = new File(BASE_DIR, "/logs");
            logsDir.mkdirs();
            File publicKeyNativeDest = new File(logsDir, "publicKey");
            java.nio.file.Files.copy(publicKeyNativeOrig.toPath(), publicKeyNativeDest.toPath(),
                                            java.nio.file.StandardCopyOption.REPLACE_EXISTING);
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
            run(dir, "vmnd", "-ciphs",
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
            ExecutorService executor = Executors.newFixedThreadPool(NUM_SERVERS);
            List<Future<?>> futures = new ArrayList<>();

            for (int i = 1; i <= NUM_SERVERS; i++) {
                final int index = i;
                Thread.sleep(1000);
                futures.add(executor.submit(() -> {
                    File dir = new File(BASE_DIR + "/0" + index);
                    try {
                        run(dir, "vmn", "-mix", "ciphertexts", "plaintexts");
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    } catch (InterruptedException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }));
            }

            for (Future<?> future : futures) {
                future.get(); // Wait for each mix-server to finish
            }

            executor.shutdown();

            File serverDir = new File(BASE_DIR + "/01");
            File nizkpDir = new File(BASE_DIR + "/01/dir/nizkp/default");
            File proofsDir = new File(BASE_DIR + "/01/dir/nizkp/default/proofs");
            File logsDir = new File(BASE_DIR + "/logs");
            File protInfoOrig = new File(serverDir, "protInfo.xml");
            File protInfoNizkpDest = new File(nizkpDir, "protInfo.xml");
            File protInfoProofsDest = new File(proofsDir, "protInfo.xml");
            java.nio.file.Files.copy(protInfoOrig.toPath(), protInfoNizkpDest.toPath());
            java.nio.file.Files.copy(protInfoOrig.toPath(), protInfoProofsDest.toPath());

            run(nizkpDir, "vmnc", "-ciphs", "-outi", "native",
                    "protInfo.xml", "Ciphertexts.bt", "ciphertexts");
            File ciphertextsNativeOrig = new File(nizkpDir, "ciphertexts");
            logsDir.mkdirs();
            File ciphertextsNativeDest = new File(logsDir, "ciphertexts");
            java.nio.file.Files.copy(ciphertextsNativeOrig.toPath(), ciphertextsNativeDest.toPath(),
                                            java.nio.file.StandardCopyOption.REPLACE_EXISTING);

            run(nizkpDir, "vmnc", "-plain", "-outi", "native",
                    "protInfo.xml", "Plaintexts.bt", "plaintexts");
            File plaintextsNativeOrig = new File(nizkpDir, "plaintexts");
            logsDir.mkdirs();
            File plaintextsNativeDest = new File(logsDir, "plaintexts");
            java.nio.file.Files.copy(plaintextsNativeOrig.toPath(), plaintextsNativeDest.toPath(),
                                            java.nio.file.StandardCopyOption.REPLACE_EXISTING);

            run(proofsDir, "vmnc", "-ciphs", "-outi", "native",
                    "protInfo.xml", "Ciphertexts01.bt", "outputNode01");
            File outputNode01Orig = new File(proofsDir, "outputNode01");
            logsDir.mkdirs();
            File outputNode01Dest = new File(logsDir, "outputNode01");
            java.nio.file.Files.copy(outputNode01Orig.toPath(), outputNode01Dest.toPath(),
                                            java.nio.file.StandardCopyOption.REPLACE_EXISTING);

            run(proofsDir, "vmnc", "-ciphs", "-outi", "native",
                    "protInfo.xml", "Ciphertexts02.bt", "outputNode02");
            File outputNode02Orig = new File(proofsDir, "outputNode02");
            logsDir.mkdirs();
            File outputNode02Dest = new File(logsDir, "outputNode02");
            java.nio.file.Files.copy(outputNode02Orig.toPath(), outputNode02Dest.toPath(),
                                            java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            return Map.of("status", "Mixing complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    @PostMapping("/verify")
    public Map<String, String> verify(){
        try {
            ExecutorService executor = Executors.newFixedThreadPool(NUM_SERVERS);
            List<Future<?>> futures = new ArrayList<>();

            for (int i = 1; i <= NUM_SERVERS; i++) {
                final int index = i;
                Thread.sleep(1000);
                futures.add(executor.submit(() -> {
                    File dir = new File(BASE_DIR + "/0" + index);
                    try {
                        run(dir, "vmnv", "-mix", "protInfo.xml", "dir/nizkp/default");
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    } catch (InterruptedException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }));
            }

            for (Future<?> future : futures) {
                future.get(); // Wait for each mix-server to finish
            }

            executor.shutdown();
            return Map.of("status", "Successful verification");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    private static void run(File workingDir, String... command) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder(command);
        pb.directory(workingDir);
        File log = new File(workingDir, "vmn.log");
        log.delete();
        pb.redirectOutput(log);
        pb.redirectErrorStream(true);
        Process p = pb.start();
        int exitCode = p.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Command failed: " + String.join(" ", command));
        }
    }
    
    private static void deleteRecursive(File file) {
        if (file.isDirectory()) {
            File[] files = file.listFiles();
            if (files != null) {
                for (File child : files) {
                    deleteRecursive(child);
                }
            }
        }
        file.delete();
    }

}