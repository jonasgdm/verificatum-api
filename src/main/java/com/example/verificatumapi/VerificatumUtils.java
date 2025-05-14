package com.example.verificatumapi;

import com.verificatum.crypto.CryptoSKey;
import com.verificatum.crypto.RandomDevice;
import com.verificatum.crypto.RandomSource;
import com.verificatum.eio.ByteTreeReader;
import com.verificatum.eio.ByteTreeReaderF;
import com.verificatum.eio.Marshalizer;
import com.verificatum.protocol.ProtocolError;
import com.verificatum.ui.info.Info;
import com.verificatum.ui.info.InfoException;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Base64;
import java.util.ListIterator;

public class VerificatumUtils {

    /**
     * Clears all existing values of a field and inserts the new one.
     *
     * @param info      The info object (e.g. PartyInfo or PrivateInfo)
     * @param tag       The name of the XML field to override
     * @param newValue  The new value to insert
     * @throws InfoException If the value cannot be parsed or inserted
     */
    public static void overrideValue(Info info, String tag, String newValue) throws InfoException {
        ListIterator<Object> it = info.getValues(tag);
        while (it.hasNext()) {
            it.next();
            it.remove();
        }
        info.addValue(tag, newValue);
    }

public static String readByteTreeAsBase64(File file) throws IOException {
    byte[] bytes = Files.readAllBytes(file.toPath());
    return Base64.getEncoder().encodeToString(bytes);
}

public static String readPrivateKeyFromKeysFile(File keysFile) {
    try (ByteTreeReaderF reader = new ByteTreeReaderF(keysFile)) {

        if (reader.getRemaining() < 1) {
            throw new ProtocolError("Keys file is malformed: no children found.");
        }

        ByteTreeReader skeyReader = reader.getNextChild(); // First = secret key
        RandomSource randomSource = new RandomDevice();    // Use the same source as keygen
        int rbitlen = 128; // This should match keygen settings

        CryptoSKey skey = Marshalizer.unmarshalAux_CryptoSKey(skeyReader, randomSource, rbitlen);
        return Base64.getEncoder().encodeToString(skey.toByteTree().toByteArray());

    } catch (Exception e) {
        throw new ProtocolError("Failed to read private key from Keys file!", e);
    }
}
}
