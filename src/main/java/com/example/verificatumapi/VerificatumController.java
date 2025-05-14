package com.example.verificatumapi;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;

import java.io.File;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/verificatum")
public class VerificatumController {

    @GetMapping("/setup")
    public Map<String, Map<String, Object>> setup() {
        Map<String, Map<String, Object>> response = new LinkedHashMap<>();
        File baseDir = new File(System.getProperty("user.dir"));
        String sessionId = "sid";
        String name = "DemoMixNet";
        int threshold = 2;

        try {
            // Run all setup steps
            VerificatumInfoGenerator.generateStub(sessionId, name, threshold, baseDir);
            VerificatumInfoGenerator.generateParty(baseDir);
            VerificatumInfoGenerator.mergeProtocolInfos(baseDir);

            // Collect and convert XML files
            for (int i = 0; i < 3; i++) {
                Map<String, Object> fileMap = new LinkedHashMap<>();
                File serverDir = new File(baseDir, "server" + i);

                for (String fileName : new String[]{"stub.xml", "privInfo.xml", "localProtInfo.xml", "protInfo.xml"}) {
                    File xmlFile = new File(serverDir, fileName);
                    if (xmlFile.exists()) {
                        Object json = convertXmlToJson(xmlFile);
                        fileMap.put(fileName, json);
                    }
                }

                response.put("server" + i, fileMap);
            }

            return response;

        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("Setup failed: " + e.getMessage());
        }
    }

    private Object convertXmlToJson(File xmlFile) throws Exception {
        XmlMapper xmlMapper = new XmlMapper();
        ObjectMapper jsonMapper = new ObjectMapper();
        return jsonMapper.convertValue(xmlMapper.readTree(xmlFile), Map.class);
    }

    @GetMapping("/generate-key")
    public Map<String, Object> generateKey() throws Exception {
        File baseDir = new File(System.getProperty("user.dir"));

        VerificatumKeyGenerator.generateKeys(baseDir);

        Map<String, Object> result = new HashMap<>();

        // Load the joint public key from server0 (they're all the same)
        File pubKeyFile = new File(baseDir, "server0/PublicKey");
        String publicKeyBase64 = VerificatumUtils.readByteTreeAsBase64(pubKeyFile);
        result.put("publicKey", publicKeyBase64);

        // Load private keys for each server (from Keys file)
        Map<String, String> privateKeys = new HashMap<>();
        for (int i = 0; i < 3; i++) {
            File keysFile = new File(baseDir, "server" + i + "/Keys");
            String privateKeyBase64 = VerificatumUtils.readPrivateKeyFromKeysFile(keysFile);
            privateKeys.put("server" + i, privateKeyBase64);
        }

        result.put("privateKeys", privateKeys);
        return result;
    }
}
