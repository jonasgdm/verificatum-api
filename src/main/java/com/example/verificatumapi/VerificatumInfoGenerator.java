package com.example.verificatumapi;

import com.verificatum.crypto.RandomDevice;
import com.verificatum.crypto.RandomSource;
import com.verificatum.protocol.com.BullBoardBasicGen;
import com.verificatum.protocol.com.BullBoardBasicHTTPWGen;
import com.verificatum.protocol.elgamal.ProtocolElGamalGen;
import com.verificatum.ui.info.InfoException;
import com.verificatum.ui.info.InfoGenerator;
import com.verificatum.ui.info.ProtocolInfo;

import java.io.File;

public class VerificatumInfoGenerator {

    public static void generateStub(String sessionId, String name, int numParties, int threshold, File outputFile) throws InfoException{
        final BullBoardBasicGen bullBoardBasicGen =
                new BullBoardBasicHTTPWGen();

        // Create the info generator
        InfoGenerator generator = new ProtocolElGamalGen(bullBoardBasicGen);

        // Initialize random source using default random device (/dev/urandom)
        RandomSource randomSource = new RandomDevice();

        // Generate default protocol info and fill required fields
        ProtocolInfo protocolInfo = generator.defaultProtocolInfo();

        protocolInfo.addValue("sid", sessionId);
        protocolInfo.addValue("name", name);
        protocolInfo.addValue("nopart", numParties);
        protocolInfo.addValue("thres", threshold);

        // Validate and write to file
        generator.validateLocal(protocolInfo);
        protocolInfo.toXML(outputFile);
    }
}
