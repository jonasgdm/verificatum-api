// GuardianMixnetController.java
package com.example.verificatumapi;

import org.springframework.web.bind.annotation.*;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.*;
import java.util.concurrent.*;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.core.io.FileSystemResource;
import java.nio.file.StandardCopyOption;

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

    @PostMapping(value = "/decrypt", produces = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<MultiValueMap<String, Object>> decrypt() {
        try {
            ExecutorService executor = Executors.newFixedThreadPool(NUM_SERVERS);
            List<Future<?>> futures = new ArrayList<>();
    
            for (int i = 1; i <= NUM_SERVERS; i++) {
                final int index = i;
                Thread.sleep(1000);
                futures.add(executor.submit(() -> {
                    File dir = new File(BASE_DIR + "/0" + index);
                    try {
                        MixnetCommon.run(dir, "vmn", "-decrypt", "shuffled-ciphertexts", "plaintexts");
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                }));
            }
    
            for (Future<?> f : futures) f.get();
            executor.shutdown();
    
            File dir01 = new File(BASE_DIR + "/01");
            File logs = new File(BASE_DIR + "/logs");
            logs.mkdirs();
    
            // Convert plaintexts to native format
            MixnetCommon.run(dir01, "vmnc", "-plain", "-outi", "native",
                    "protInfo.xml", "plaintexts", "plaintexts.native");
    
            File nativeFile = new File(dir01, "plaintexts.native");
            Files.copy(nativeFile.toPath(), new File(logs, "plaintexts.native").toPath(),
                    StandardCopyOption.REPLACE_EXISTING);
    
            // Prepare multipart response
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", new FileSystemResource(nativeFile));
    
            return ResponseEntity.ok()
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body);
    
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }    

    @GetMapping("/public-key")
    public byte[] getPublicKey() throws IOException {
        File key = new File(BASE_DIR + "/logs/publicKey");
        return Files.readAllBytes(key.toPath());
    }
}
