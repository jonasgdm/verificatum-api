package com.example.verificatumapi;

import java.io.*;
import java.nio.file.Files;
import java.util.*;
import java.util.concurrent.*;

public class MixnetCommon {

    public static void run(File workingDir, String... command) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder(command);
        pb.directory(workingDir);
        File log = new File(workingDir, "vmn.log");
        if (log.exists()) log.delete();
        pb.redirectOutput(log);
        pb.redirectErrorStream(true);
        Process p = pb.start();
        int exitCode = p.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Command failed: " + String.join(" ", command));
        }
    }

    public static void killHintPorts(List<Integer> ports) {
        for (int port : ports) {
            try {
                Process p = new ProcessBuilder("bash", "-c", "lsof -t -i :" + port)
                        .redirectErrorStream(true).start();
                p.waitFor();
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        Runtime.getRuntime().exec("kill -9 " + line);
                    }
                }
            } catch (Exception e) {
                System.err.println("Failed to kill process on port " + port + ": " + e.getMessage());
            }
        }
    }

    public static Map<String, String> setupMixnet(String baseDir, String sessionId, String electionName, int numServers) {
        try {
            killHintPorts(Arrays.asList(4041, 4042, 4043));
            cleanAndPrepareBase(baseDir, numServers);

            for (int i = 1; i <= numServers; i++) {
                File dir = new File(baseDir + "/0" + i);

                run(dir, "vmni", "-prot",
                        "-sid", sessionId,
                        "-name", electionName,
                        "-nopart", String.valueOf(numServers),
                        "-thres", "2");

                run(dir, "vmni", "-party",
                        "-name", "GuardianMixServer_0" + i,
                        "-http", "http://localhost:804" + i,
                        "-hint", "localhost:404" + i);

                new File(dir, "localProtInfo.xml")
                        .renameTo(new File(dir, "protInfo0" + i + ".xml"));
            }

            // Cross-copy protocol files
            for (int i = 1; i <= numServers; i++) {
                File srcDir = new File(baseDir + "/0" + i);
                for (int j = 1; j <= numServers; j++) {
                    if (i == j) continue;
                    File destDir = new File(baseDir + "/0" + j);
                    File src = new File(srcDir, "protInfo0" + i + ".xml");
                    File dst = new File(destDir, "protInfo0" + i + ".xml");
                    Files.copy(src.toPath(), dst.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                }
            }

            for (int i = 1; i <= numServers; i++) {
                File dir = new File(baseDir + "/0" + i);
                run(dir, "vmni", "-merge",
                        "protInfo01.xml", "protInfo02.xml", "protInfo03.xml");
            }

            return Map.of("status", "Setup complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    public static Map<String, String> keygen(String baseDir, int numServers) {
        try {
            ExecutorService executor = Executors.newFixedThreadPool(numServers);
            List<Future<?>> futures = new ArrayList<>();

            for (int i = 1; i <= numServers; i++) {
                final int index = i;
                Thread.sleep(1000);
                futures.add(executor.submit(() -> {
                    File dir = new File(baseDir + "/0" + index);
                    try {
                        run(dir, "vmn", "-keygen", "publicKey");
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }));
            }

            for (Future<?> f : futures) f.get();
            executor.shutdown();

            File dir = new File(baseDir + "/01");
            run(dir, "vmnc", "-pkey", "-outi", "native",
                    "protInfo.xml", "publicKey", "publicKeyNative");

            File logs = new File(baseDir, "logs");
            logs.mkdirs();
            Files.copy(new File(dir, "publicKeyNative").toPath(),
                    new File(logs, "publicKey").toPath(),
                    java.nio.file.StandardCopyOption.REPLACE_EXISTING);

            return Map.of("status", "Keygen complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    public static Map<String, String> decrypt(String baseDir, int numServers) {
        try {
            ExecutorService executor = Executors.newFixedThreadPool(numServers);
            List<Future<?>> futures = new ArrayList<>();

            for (int i = 1; i <= numServers; i++) {
                final int index = i;
                Thread.sleep(1000);
                futures.add(executor.submit(() -> {
                    File dir = new File(baseDir + "/0" + index);
                    try {
                        run(dir, "vmn", "-decrypt", "shuffled-ciphertexts", "plaintexts");
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }));
            }

            for (Future<?> f : futures) f.get();
            executor.shutdown();

            File dir = new File(baseDir + "/01/dir/nizkp/default");
            File logs = new File(baseDir + "/logs");
            logs.mkdirs();

            run(dir, "vmnc", "-plain", "-outi", "native",
                    "protInfo.xml", "Plaintexts.bt", "plaintexts");

            Files.copy(new File(dir, "plaintexts").toPath(),
                    new File(logs, "plaintexts").toPath(),
                    java.nio.file.StandardCopyOption.REPLACE_EXISTING);

            return Map.of("status", "Decryption complete");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    public static void cleanAndPrepareBase(String basePath, int numServers) throws IOException {
        File baseDir = new File(basePath);
        if (baseDir.exists()) {
            for (File child : baseDir.listFiles()) {
                deleteRecursive(child);
            }
        } else {
            baseDir.mkdirs();
        }

        for (int i = 1; i <= numServers; i++) {
            File dir = new File(basePath + "/0" + i);
            dir.mkdirs();
        }
    }

    public static void deleteRecursive(File file) {
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
