package com.example.verificatumapi;

import java.io.File;
import java.io.FileWriter;

import com.verificatum.protocol.Protocol;
import com.verificatum.protocol.ProtocolError;
import com.verificatum.protocol.ProtocolFormatException;
import com.verificatum.protocol.com.BullBoardBasicGen;
import com.verificatum.protocol.com.BullBoardBasicHTTPWGen;
import com.verificatum.protocol.elgamal.ProtocolElGamalGen;
import com.verificatum.protocol.elgamal.ProtocolElGamalInterface;
import com.verificatum.protocol.mixnet.MixNetElGamal;
import com.verificatum.protocol.mixnet.MixNetElGamalInterfaceFactory;
import com.verificatum.ui.UI;
import com.verificatum.ui.info.InfoGenerator;
import com.verificatum.ui.info.PrivateInfo;
import com.verificatum.ui.info.ProtocolInfo;
import com.verificatum.ui.tui.TConsole;
import com.verificatum.ui.tui.TextualUI;

public class VerificatumKeyGenerator {

    private static final int NUM_PARTIES = 3;
    
    public static void generateKeys(File baseDir) throws Exception {
        UI ui = new TextualUI(new TConsole());
        for (int i = 0; i < NUM_PARTIES; i++) {
            File dir = new File(baseDir, "server" + i);
            File privFile = new File(dir, "privInfo.xml");
            File protFile = new File(dir, "protInfo.xml");
            File pubKeyFile = new File(dir, "pubkey");

            // Load info files
            BullBoardBasicGen bbGen = new BullBoardBasicHTTPWGen();
            InfoGenerator generator = new ProtocolElGamalGen(bbGen);

            PrivateInfo priv = Protocol.getPrivateInfo(generator, privFile);
            ProtocolInfo prot = Protocol.getProtocolInfo(generator, protFile);

            // Create mix-net instance
            MixNetElGamal mixnet = new MixNetElGamal(priv, prot, ui);

            // Ensure priv/ directory and dummy seed exists (Verificatum requires it)
            File privDir = new File(dir, "priv");
            privDir.mkdirs();
            File seedFile = new File(privDir, "seed");
            if (!seedFile.exists()) {
                try (FileWriter writer = new FileWriter(seedFile)) {
                    writer.write("seed");
                }
            }

            try{
                ProtocolElGamalInterface rawInterface =
                new MixNetElGamalInterfaceFactory().getInterface("raw");
                // Run key generation
                mixnet.startServers();
                mixnet.setup();
                mixnet.generatePublicKey();
                rawInterface.writePublicKey(mixnet.getPublicKey(), pubKeyFile);
                mixnet.shutdown(mixnet.getLog());
            }
            catch (final ProtocolFormatException pfe) {
                throw new ProtocolError("Unable to get raw interface!", pfe);
            }
            
        }
    }
}
