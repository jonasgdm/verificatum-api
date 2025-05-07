package com.example.verificatumapi;

import com.verificatum.crypto.RandomDevice;
import com.verificatum.crypto.RandomSource;
import com.verificatum.protocol.Protocol;
import com.verificatum.protocol.ProtocolDefaults;
import com.verificatum.protocol.com.BullBoardBasicGen;
import com.verificatum.protocol.com.BullBoardBasicHTTPWGen;
import com.verificatum.protocol.elgamal.ProtocolElGamalGen;
import com.verificatum.ui.info.*;
import com.verificatum.vcr.VCR;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.ListIterator;

public class VerificatumInfoGenerator {

    static final int NUM_SERVERS = 3;

    public static String generateProt(String sid, String name, int numParties, int threshold) {
        try {
            BullBoardBasicGen bbGen = new BullBoardBasicHTTPWGen();
            InfoGenerator generator = new ProtocolElGamalGen(bbGen);
            ProtocolInfo dpi = generator.defaultProtocolInfo();

            dpi.addValue("sid", sid);
            dpi.addValue("name", name);
            dpi.addValue("nopart", numParties);
            dpi.addValue("thres", threshold);

            for (int i = 0; i < NUM_SERVERS; i++) {
                File dir = new File("server" + i);
                if (!dir.exists()) dir.mkdirs();

                File stubFile = new File(dir, "stub.xml");
                dpi.toXML(stubFile);
            }

            return "Stub files generated successfully.";
        } catch (Exception e) {
            return "Failed to generate stub files: " + e.getMessage();
        }
    }

    public static String generateParty() {
        try {
            final BullBoardBasicGen bbGen = new BullBoardBasicHTTPWGen();
            final InfoGenerator generator = new ProtocolElGamalGen(bbGen);
            final RandomSource randomSource = new RandomDevice();
    
            final int numParties = 3;
            final File baseDir = new File(System.getProperty("user.dir"));
    
            for (int i = 0; i < numParties; i++) {
                File dir = new File(baseDir, "server" + i);
                File stubFile = new File(dir, "stub.xml");
                File privFile = new File(dir, "privInfo.xml");
                File localProtFile = new File(dir, "localProtInfo.xml");
    
                ProtocolInfo stub = generator.newProtocolInfo();
                stub.parse(stubFile.getAbsolutePath());
    
                PrivateInfo priv = generator.defaultPrivateInfo(stub, randomSource);
    
                // Manually insert required fields (replacing Opt)
                String partyName = "MixServer" + i;
                String http = "http://localhost:" + (8040 + i);
                String hint = "localhost:" + (4040 + i);
    
                priv.addValue("name", partyName);
                priv.addValue("dir", dir.getAbsolutePath());
                overrideValue(priv, "httpl", http);
                overrideValue(priv, "hintl", hint);
                priv.toXML(privFile);
    
                // Generate PartyInfo
                PartyInfo party = generator.defaultPartyInfo(stub, priv, randomSource);
    
                // Transfer fields manually (replicating transferValues and optionalCopyStore)
                party.addValue("name", partyName);
                overrideValue(party, "http", http);
                overrideValue(party, "hint", hint);
    
                stub.addPartyInfo(party);
                generator.validateLocal(stub);
                stub.toXML(localProtFile);
            }
    
            return "Private and party info files generated for all mix servers.";
    
        } catch (Exception e) {
            e.printStackTrace();
            return "Failed to generate party info: " + e.getMessage();
        }
    }    

    public static String mergeProt() {
        try {
            BullBoardBasicGen bbGen = new BullBoardBasicHTTPWGen();
            InfoGenerator generator = new ProtocolElGamalGen(bbGen);

            ProtocolInfo pi = generator.newProtocolInfo();
            File mergedFile = new File("merged.xml");
            List<String> paths = new ArrayList<>();

            for (int i = 0; i < NUM_SERVERS; i++) {
                paths.add("server" + i + "/localProtInfo.xml");
            }

            pi.parse(paths.get(0));

            for (int i = 1; i < paths.size(); i++) {
                ProtocolInfo tpi = generator.newProtocolInfo();
                tpi.parse(paths.get(i));
                pi.addPartyInfos(tpi);
            }

            generator.validate(pi);

            for (int i = 0; i < NUM_SERVERS; i++) {
                File outFile = new File("server" + i + "/protInfo.xml");
                pi.toXML(outFile);
            }

            mergedFile.delete();
            pi.toXML(mergedFile);

            return "Merged protocol info files successfully.";
        } catch (Exception e) {
            return "Failed to merge protocol info files: " + e.getMessage();
        }
    }
    
    public static void overrideValue(Info info, String key, String newValue) throws InfoException {
        ListIterator<Object> it = info.getValues(key);
        while (it.hasNext()) {
            it.next();
            it.remove();  // Removes all existing values one by one
        }
        info.addValue(key, newValue);  // Now add your intended value
    }
}
