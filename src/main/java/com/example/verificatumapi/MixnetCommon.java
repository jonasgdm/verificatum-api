package com.example.verificatumapi;

import java.io.*;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;
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

    public static String getLocalAddress() throws SocketException, UnknownHostException{
        Iterator<NetworkInterface> nis  = NetworkInterface.getNetworkInterfaces().asIterator();
        NetworkInterface ni;
        String local_address = InetAddress.getLocalHost().getHostAddress();
        while (nis.hasNext()) {
            ni = nis.next();
            Iterator<InetAddress> addresses = ni.getInetAddresses().asIterator();
            while (addresses.hasNext()) {
                String current_address = addresses.next().getHostAddress();
                System.out.println(current_address);
                local_address = current_address.contains("192.168") ? current_address : local_address;
            }
        }

        return local_address;
    }

    /* =====================
       Setup (local)
       ===================== */
    public static Map<String, String> setupLocal(String baseDir, String sessionId,
                                                 String electionName, int numServers, int thres, int serverId) {
        try {
            File dir = new File(baseDir + "/0" + serverId);
            dir.mkdirs();

            File filesDir = new File("/files");
            filesDir.mkdirs();

            String local_address = getLocalAddress();

            run(dir, "vmni", "-prot",
                    "-sid", sessionId,
                    "-name", electionName,
                    "-nopart", String.valueOf(numServers),
                    "-thres", String.valueOf(thres));

            run(dir, "vmni", "-party",
                    "-name", "GuardianMixServer_0" + serverId,
                    "-http", "http://" + local_address + ":804" + serverId,
                    "-hint", local_address + ":404" + serverId);

            String piName = "protInfo" + String.format("%02d", serverId) + ".xml";
            new File(dir, "localProtInfo.xml")
                .renameTo(new File(dir, piName));
            
            File piOrig = new File(dir, piName);
            File piDest = new File("/files/" + piName);
            
            Files.copy(piOrig.toPath(), piDest.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);

            return Map.of("status", "Setup local complete (server " + serverId + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", e.getMessage());
        }
    }

    /* =====================
       Merge (central)
       ===================== */
    public static Map<String, String> mergeCentral(String baseDir, int numServers) {
        try {
            File dir = new File(baseDir + "/files");
            List<String> args = new ArrayList<>();
            args.add("vmni"); args.add("-merge");
            for (int k = 1; k <= numServers; k++) {
                args.add("protInfo" + String.format("%02d", k) + ".xml");
            }
            run(dir, args.toArray(new String[0]));
            return Map.of("status", "Merge central completo.");
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
            // List<String> args = new ArrayList<>();
            // args.add("vmni"); args.add("-merge");
            // for (int k = 1; k <= numServers; k++) {
            //     args.add("protInfo" + String.format("%02d", k) + ".xml");
            // }
            // run(dir, args.toArray(new String[0]));

            File piOrig = new File("/files/protInfo.xml");
            File piDest = new File(dir, "protInfo.xml");
            Files.copy(piOrig.toPath(), piDest.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);

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
            VerificatumCleaner.freeGuardianServer(serverId);
            String serverDir = baseDir + "/" + String.format("%02d", serverId);
            File dir = new File(serverDir);
            run(dir, "vmn", "-keygen", "publicKey");

            NativeConverters.ensureGuardianPublicKeyNative(serverDir);
            
            File pkOrig = new File(serverDir + "/publicKey.native");
            File pkDest = new File("/files/publicKey");

            Files.copy(pkOrig.toPath(), pkDest.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);

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
            VerificatumCleaner.freeGuardianServer(serverId);
            File dir = new File(baseDir + "/0" + serverId);
            run(dir, "vmn", "-decrypt",
                "privInfo.xml", "protInfo.xml",
                "shuffled-ciphertexts", "plaintexts");
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

    public static void startKeygenDetached(String baseDir, int serverId) throws IOException, InterruptedException {
        File dir = new File(baseDir + "/0" + serverId);
        if (!dir.exists()) dir.mkdirs();

        // limpa log anterior para ficar legível
        File log = new File(dir, "vmn.log");
        if (log.exists()) log.delete();

        // nohup + background; saída vai para vmn.log
        String cmd = "nohup vmn -keygen publicKey >> vmn.log 2>&1 < /dev/null &";
        new ProcessBuilder("bash", "-lc", cmd)
                .directory(dir)
                .redirectErrorStream(true)
                .start()
                .waitFor(); // só espera o *spawn* do nohup, não o vmn
    }

    public static boolean waitForFile(File f, long timeoutMs) throws InterruptedException {
        long end = System.currentTimeMillis() + timeoutMs;
        while (System.currentTimeMillis() < end) {
            if (f.exists() && f.length() > 0) return true;
            Thread.sleep(500);
        }
        return false;
    }

    public static void startDecryptDetached(String baseDir, int serverId) throws IOException, InterruptedException {
        File dir = new File(baseDir + "/0" + serverId);
        if (!dir.exists()) dir.mkdirs();

        // limpa log anterior deste nó
        File log = new File(dir, "vmn.log");
        if (log.exists()) log.delete();

        // nohup + background; saída vai para vmn.log
        String cmd = "nohup vmn -decrypt shuffled-ciphertexts plaintexts >> vmn.log 2>&1 < /dev/null &";
        new ProcessBuilder("bash", "-lc", cmd)
                .directory(dir)
                .redirectErrorStream(true)
                .start()
                .waitFor(); // aguarda só o spawn, não o término do vmn
    }
}
