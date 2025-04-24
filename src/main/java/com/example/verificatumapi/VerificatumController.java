package com.example.verificatumapi;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.File;

@RestController
@RequestMapping("/verificatum")
public class VerificatumController {

    @GetMapping("/generate-stub")
    public String generateStub() {
        try {
            File outputFile = new File(System.getProperty("user.dir") + "/stub.xml");
            VerificatumInfoGenerator.generateStub("sid", "DemoMixNet", 3, 2, outputFile);
            return "Stub file generated at: " + outputFile.getAbsolutePath();
        } catch (Exception e) {
            return "Failed to generate stub: " + e.getMessage();
        }
    }
}
