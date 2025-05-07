package com.example.verificatumapi;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/verificatum")
public class VerificatumController {

    @GetMapping("/generate-prot")
    public String generateProt() {
        return VerificatumInfoGenerator.generateProt("sid", "DemoMixNet", 3, 2);
    }

    @GetMapping("/generate-party")
    public String generateParty() {
        return VerificatumInfoGenerator.generateParty();
    }

    @GetMapping("/merge-prot")
    public String mergeProt() {
        return VerificatumInfoGenerator.mergeProt();
    }
}
