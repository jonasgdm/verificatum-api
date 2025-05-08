package com.example.verificatumapi;

import com.verificatum.crypto.RandomDevice;
import com.verificatum.crypto.RandomSource;
import com.verificatum.protocol.com.BullBoardBasicGen;
import com.verificatum.protocol.com.BullBoardBasicHTTPWGen;
import com.verificatum.protocol.elgamal.ProtocolElGamalGen;
import com.verificatum.ui.info.*;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class VerificatumInfoGenerator {

    private static final int NUM_PARTIES = 3;

    public static void generateStub(String sessionId, String name, int threshold, File baseDir) throws InfoException {
        BullBoardBasicGen bbGen = new BullBoardBasicHTTPWGen();
        InfoGenerator generator = new ProtocolElGamalGen(bbGen);
        RandomSource randomSource = new RandomDevice();

        ProtocolInfo stub = generator.defaultProtocolInfo();
        stub.addValue("sid", sessionId);
        stub.addValue("name", name);
        stub.addValue("nopart", NUM_PARTIES);
        stub.addValue("thres", threshold);

        generator.validateLocal(stub);

        for (int i = 0; i < NUM_PARTIES; i++) {
            File dir = new File(baseDir, "server" + i);
            dir.mkdirs();
            File stubFile = new File(dir, "stub.xml");
            stub.toXML(stubFile);
        }
    }

    public static void generateParty(File baseDir) throws Exception {
        BullBoardBasicGen bbGen = new BullBoardBasicHTTPWGen();
        InfoGenerator generator = new ProtocolElGamalGen(bbGen);
        RandomSource randomSource = new RandomDevice();

        for (int i = 0; i < NUM_PARTIES; i++) {
            File dir = new File(baseDir, "server" + i);
            File stubFile = new File(dir, "stub.xml");
            File privFile = new File(dir, "privInfo.xml");
            File localProtFile = new File(dir, "localProtInfo.xml");

            ProtocolInfo stub = generator.newProtocolInfo().parse(stubFile.getAbsolutePath());

            PrivateInfo priv = generator.defaultPrivateInfo(stub, randomSource);
            VerificatumUtils.overrideValue(priv, "name", "MixServer" + i);
            VerificatumUtils.overrideValue(priv, "dir", dir.getAbsolutePath());
            VerificatumUtils.overrideValue(priv, "httpl", "http://localhost:" + (8040 + i));
            VerificatumUtils.overrideValue(priv, "hintl", "localhost:" + (4040 + i));
            priv.toXML(privFile);

            PartyInfo party = generator.defaultPartyInfo(stub, priv, randomSource);
            VerificatumUtils.overrideValue(party, "name", "MixServer" + i);
            VerificatumUtils.overrideValue(party, "http", "http://localhost:" + (8040 + i));
            VerificatumUtils.overrideValue(party, "hint", "localhost:" + (4040 + i));

            stub.addPartyInfo(party);
            generator.validateLocal(stub);
            stub.toXML(localProtFile);
        }
    }

    public static void mergeProtocolInfos(File baseDir) throws InfoException {
        BullBoardBasicGen bbGen = new BullBoardBasicHTTPWGen();
        InfoGenerator generator = new ProtocolElGamalGen(bbGen);

        List<File> localProtInfos = new ArrayList<>();
        for (int i = 0; i < NUM_PARTIES; i++) {
            localProtInfos.add(new File(baseDir, "server" + i + "/localProtInfo.xml"));
        }

        for (int i = 0; i < NUM_PARTIES; i++) {
            ProtocolInfo merged = generator.newProtocolInfo().parse(localProtInfos.get(0).getAbsolutePath());

            for (int j = 1; j < localProtInfos.size(); j++) {
                ProtocolInfo pi = generator.newProtocolInfo().parse(localProtInfos.get(j).getAbsolutePath());
                merged.addPartyInfos(pi);
            }

            generator.validate(merged);
            File output = new File(baseDir, "server" + i + "/protInfo.xml");
            merged.toXML(output);
        }
    }
}
