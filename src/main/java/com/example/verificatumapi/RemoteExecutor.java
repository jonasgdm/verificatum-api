package com.example.verificatumapi;

import java.io.BufferedReader;
import java.io.InputStreamReader;

public class RemoteExecutor {

    // SSH command (assumes keys are set; disables host key prompts)
    public static void executeSSH(String remoteHost, String command) throws Exception {
        ProcessBuilder pb = new ProcessBuilder(
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                remoteHost, command
        );
        Process p = pb.start();
        int exit = p.waitFor();
        if (exit != 0) {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(p.getErrorStream()))) {
                String line;
                while ((line = reader.readLine()) != null) System.err.println(line);
            }
            throw new RuntimeException("SSH command failed on " + remoteHost);
        }
    }

    public static void scpTo(String localPath, String remoteHost, String remotePath) throws Exception {
        ProcessBuilder pb = new ProcessBuilder(
                "scp",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                localPath, remoteHost + ":" + remotePath
        );
        Process p = pb.start();
        if (p.waitFor() != 0) throw new RuntimeException("SCP to failed: " + localPath + " → " + remoteHost + ":" + remotePath);
    }

    public static void scpFrom(String remoteHost, String remotePath, String localPath) throws Exception {
        ProcessBuilder pb = new ProcessBuilder(
                "scp",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                remoteHost + ":" + remotePath, localPath
        );
        Process p = pb.start();
        if (p.waitFor() != 0) throw new RuntimeException("SCP from failed: " + remoteHost + ":" + remotePath + " → " + localPath);
    }
}
