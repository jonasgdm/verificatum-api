package com.example.verificatumapi;

import java.io.*;
import java.nio.file.Files;
import java.util.*;

public class MixnetCommon {

    /* =====================
       Execução de comandos
       ===================== */
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
            throw new RuntimeException("Command failed (" + exitCode + "): " + String.join(" ", command)
                                       + " (cwd=" + workingDir.getAbsolutePath() + ")");
        }
    }

    /* =====================
       Setup (local)
       ===================== */
    public static Map<String, String> setupLocal(String baseDir, String sessionId,
                                                 String electionName, int numServers, int serverId) {
        try {
            File dir = new File(baseDir + "/0" + serverId);
            dir.mkdirs();

            run(dir, "vmni", "-prot",
                    "-sid", sessionId,
                    "-name", electionName,
                    "-nopart", String.valueOf(numServers),
                    "-thres", "2");

            run(dir, "vmni", "-party",
                    "-name", "GuardianMixServer_0" + serverId,
                    "-http", "http://localhost:804" + serverId,
                    "-hint", "localhost:404" + serverId);

            new File(dir, "localProtInfo.xml")
                    .renameTo(new File(dir, "protInfo0" + serverId + ".xml"));

            return Map.of("status", "Setup local complete (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    /* =====================
       Merge (local)
       ===================== */
    public static Map<String, String> mergeLocal(String baseDir, int numServers, int serverId) {
        try {
            File dir = new File(baseDir + "/0" + serverId);
            List<String> args = new ArrayList<>();
            args.add("vmni"); args.add("-merge");
            for (int k = 1; k <= numServers; k++) {
                args.add("protInfo0" + (k < 10 ? "0" + k : k) + ".xml"); // keep 0X names
            }
            run(dir, args.toArray(new String[0]));
            return Map.of("status", "Merge local complete (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    /* =====================
       Keygen (local)
       ===================== */
    public static Map<String, String> keygenLocal(String baseDir, int serverId) {
        try {
            File dir = new File(baseDir + "/0" + serverId);
            run(dir, "vmn", "-keygen", "publicKey");
            return Map.of("status", "Keygen local complete (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    /* =====================
       Decrypt (local)
       ===================== */
    public static Map<String, String> decryptLocal(String baseDir, int serverId) {
        try {
            File dir = new File(baseDir + "/0" + serverId);
            run(dir, "vmn", "-decrypt", "shuffled-ciphertexts", "plaintexts");
            return Map.of("status", "Decrypt local complete (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    /* =====================
       Auxiliares (limpeza, portas)
       ===================== */
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
            if (files != null) for (File child : files) deleteRecursive(child);
        }
        file.delete();
    }

    public static void killHintPorts(List<Integer> ports) {
        for (int port : ports) {
            try {
                Process p = new ProcessBuilder("bash", "-c", "lsof -t -i :" + port)
                        .redirectErrorStream(true).start();
                p.waitFor();
                try (BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()))) {
                    String line;
                    while ((line = r.readLine()) != null) {
                        Runtime.getRuntime().exec("kill -9 " + line);
                    }
                }
            } catch (Exception e) {
                System.err.println("Failed to kill process on port " + port + ": " + e.getMessage());
            }
        }
    }

    public static void killAllHintPorts(int startPort, int endPort) {
        List<Integer> ports = new ArrayList<>();
        for (int p = startPort; p <= endPort; p++) ports.add(p);
        killHintPorts(ports);
    }
}
