// GuardianMixnetController.java
package com.example.verificatumapi;

import org.springframework.web.bind.annotation.*;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.*;
import java.util.concurrent.*;

@RestController
@RequestMapping("/guardian")
public class GuardianMixnetController {

    private static final int NUM_SERVERS = 3;
    private static final String BASE_DIR = "verificatum-guardian";
    private static final String SESSION_ID = "GuardianSession";
    private static final String ELECTION_NAME = "Guardian_Election";

    @PostMapping("/setup")
    public Map<String, String> setup() {
        return MixnetCommon.setupMixnet(BASE_DIR, SESSION_ID, ELECTION_NAME, NUM_SERVERS);
    }

    @PostMapping("/keygen")
    public Map<String, String> keygen() {
        return MixnetCommon.keygen(BASE_DIR, NUM_SERVERS);
    }

    @PostMapping("/decrypt")
    public Map<String, String> decrypt() {
        return MixnetCommon.decrypt(BASE_DIR, NUM_SERVERS);
    }

    @GetMapping("/public-key")
    public byte[] getPublicKey() throws IOException {
        File key = new File(BASE_DIR + "/logs/publicKey");
        return Files.readAllBytes(key.toPath());
    }
}
