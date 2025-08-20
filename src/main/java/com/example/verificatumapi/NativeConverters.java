// NativeConverters.java
package com.example.verificatumapi;

import java.io.File;
import java.io.IOException;

public class NativeConverters {

    /** Ensures a native public key exists (guardian side), returns the file to serve. */
    public static File ensureGuardianPublicKeyNative(String baseDir) throws IOException, InterruptedException {
        File dir01 = new File(baseDir + "/01");
        File protInfo = new File(dir01, "protInfo.xml");
        File pkRaw = new File(dir01, "publicKey");
        File pkNative = new File(dir01, "publicKey.native");

        if (!protInfo.exists() || !pkRaw.exists()) {
            throw new IOException("Missing protInfo.xml or publicKey under " + dir01.getAbsolutePath());
        }

        // Convert only if native is missing or older than raw
        if (!pkNative.exists() || pkNative.lastModified() < pkRaw.lastModified()) {
            // vmnc -pkey -outi native protInfo.xml publicKey publicKey.native
            MixnetCommon.run(dir01, "vmnc", "-pkey", "-outi", "native",
                    "protInfo.xml", "publicKey", "publicKey.native");
        }
        return pkNative;
    }

    /** Ensures a native shuffled-ciphertexts file exists (shuffler side), returns file to serve. */
    public static File ensureShufflerShuffledNative(String shufflerBaseDir) throws IOException, InterruptedException {
        File dir01 = new File(shufflerBaseDir + "/01");
        File protInfo = new File(dir01, "protInfo.xml");
        File shuffledRaw = new File(dir01, "shuffled");
        File shuffledNative = new File(dir01, "shuffled.native");

        if (!protInfo.exists() || !shuffledRaw.exists()) {
            throw new IOException("Missing protInfo.xml or shuffled under " + dir01.getAbsolutePath());
        }

        // Convert only if native is missing or older than raw
        if (!shuffledNative.exists() || shuffledNative.lastModified() < shuffledRaw.lastModified()) {
            // vmnc -ciphs -outi native protInfo.xml shuffled shuffled.native
            MixnetCommon.run(dir01, "vmnc", "-ciphs", "-outi", "native",
                    "protInfo.xml", "shuffled", "shuffled.native");
        }
        return shuffledNative;
    }

    /** Returns the shuffler vmn.log (no conversion). */
    public static File shufflerLogFile(String shufflerBaseDir) throws IOException {
        File log = new File(shufflerBaseDir + "/01/vmn.log");
        if (!log.exists()) {
            throw new IOException("Log not found: " + log.getAbsolutePath());
        }
        return log;
    }
}
