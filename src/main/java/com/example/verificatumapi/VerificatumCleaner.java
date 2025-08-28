package com.example.verificatumapi;

import java.io.*;

public class VerificatumCleaner {

    /* -------------- PUBLIC: Orquestração de limpeza -------------- */

    // Limpa TUDO do Guardian antes de setup (portas 8041.., 4041.. e processos presos ao baseDir)
    public static void resetGuardian(String baseDir, int numServers) {
        // 1) Mata processos com arquivos abertos dentro do baseDir
        killProcessesByDir(baseDir);

        // 2) Libera portas de todos os servidores
        for (int id = 1; id <= numServers; id++) {
            freeGuardianServer(id);
        }

        // 3) Limpa diretórios antigos (deixa o MixnetCommon.cleanAndPrepareBase recriar)
        deleteQuietly(new File(baseDir));
    }

    // *** NOVO ***: Limpa SOMENTE o nó local (antes de /guardian/setup-local nesse nó)
    public static void resetGuardianNode(String baseDir, int serverId) {
        // libera as portas desse nó
        freeGuardianServer(serverId);
        // mata processos que seguram arquivos no baseDir (se houver algo desse nó)
        killProcessesByDir(baseDir);
        // apaga apenas a pasta desse nó (0X)
        deleteQuietly(new File(baseDir + "/0" + serverId));
        // (o resto será recriado pelo setup-local e pela distribuição dos protInfo)
    }

    // Limpa TUDO do Shuffler antes de setup (portas 8051.., 4051.. e processos presos ao baseDir)
    public static void resetShuffler(String baseDir, int numServers) {
        killProcessesByDir(baseDir);
        for (int id = 1; id <= numServers; id++) {
            freeShufflerServer(id);
        }
        deleteQuietly(new File(baseDir));
    }

    // Libera portas do Guardian para um server específico (chamar antes de keygen/decrypt)
    public static void freeGuardianServer(int serverId) {
        int http = 8040 + serverId; // 8041, 8042, 8043...
        int hint = 4040 + serverId; // 4041, 4042, 4043...
        freePort(http, "tcp");
        freePort(hint, "udp"); // hint usa UDP
        freePort(hint, "tcp"); // alguns ambientes deixam TCP “preso”
    }

    // Libera portas do Shuffler para um server específico (antes de shuffle em cada nó)
    public static void freeShufflerServer(int serverId) {
        int http = 8050 + serverId; // 8051, 8052, 8053...
        int hint = 4050 + serverId; // 4051, 4052, 4053...
        freePort(http, "tcp");
        freePort(hint, "udp");
        freePort(hint, "tcp");
    }

    /* -------------- INTERNALS -------------- */

    private static void freePort(int port, String proto) {
        // Tenta com lsof…
        runQuiet("bash", "-c", "lsof -t -i" + proto.toUpperCase() + ":" + port + " | xargs -r kill -9");
        // …e com fuser (algumas distros respondem melhor no UDP)
        if ("udp".equalsIgnoreCase(proto)) {
            runQuiet("bash", "-c", "fuser -k " + port + "/udp || true"); // ignora erros
        } else {
            runQuiet("bash", "-c", "fuser -k " + port + "/tcp || true");
        }
    }

    // Mata qualquer processo com arquivo aberto dentro do diretório (recursivo)
    private static void killProcessesByDir(String dirPath) {
        File dir = new File(dirPath);
        if (!dir.exists()) return;

        // lsof +D varre recursivamente; funciona no Linux moderno.
        runQuiet("bash", "-c",
                "lsof -t +D '" + dir.getAbsolutePath() + "' 2>/dev/null | xargs -r kill -9");
    }

    private static void deleteQuietly(File f) {
        if (!f.exists()) return;
        if (f.isDirectory()) {
            File[] kids = f.listFiles();
            if (kids != null) for (File k : kids) deleteQuietly(k);
        }
        try { f.delete(); } catch (Exception ignore) {}
    }

    private static void runQuiet(String... cmd) {
        try {
            new ProcessBuilder(cmd).redirectErrorStream(true).start().waitFor();
        } catch (Exception ignore) {}
    }
}
