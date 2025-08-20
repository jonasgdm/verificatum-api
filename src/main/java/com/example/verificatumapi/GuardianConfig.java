package com.example.verificatumapi;

import java.util.List;

public class GuardianConfig {
    public boolean auto = false;
    public int numServers = 3;
    public int localServerId = 1;               // Guardian 1 is the entrypoint
    public String baseDir = "verificatum-guardian";
    public String sessionId = "GuardianSession";
    public String electionName = "Guardian_Election";
    public List<String> servers;                // e.g. ["user@10.0.0.2", "user@10.0.0.3"] for ids 2..N

    private static GuardianConfig instance;
    public static synchronized GuardianConfig get() {
        if (instance == null) instance = new GuardianConfig();
        return instance;
    }

    public void validateForAuto() {
        if (!auto) return;
        if (servers == null || servers.size() != (numServers - 1)) {
            throw new IllegalStateException("For auto=true, body.servers must list " +
                (numServers - 1) + " remotes (ids 2.." + numServers + ") in order.");
        }
    }
}
