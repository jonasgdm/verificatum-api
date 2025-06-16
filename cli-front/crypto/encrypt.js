// encrypt.js
const fs = require("fs");
const path = require("path");
const verificatum = require("vjsc");

function initRandomSource() {
    const randomSource = new verificatum.crypto.RandomDevice();
    const seed = randomSource.getBytes(verificatum.crypto.SHA256PRG.seedLength);
    const prg = new verificatum.crypto.SHA256PRG();
    prg.setSeed(seed);
    return prg;
}

function encryptValue(message, publicKeyPath) {
    const pubkeyBytes = fs.readFileSync(publicKeyPath);
    const bt = verificatum.eio.ByteTree.readByteTreeFromByteArray(pubkeyBytes);

    // Valida estrutura
    const keyPGroup = verificatum.arithm.ECqPGroup.fromByteTree(bt.value[0].value[1]);
    const fullPublicKey = new verificatum.arithm.PPGroup(keyPGroup, 2).toElement(bt.value[1]);

    const WIDTH = 1; // igual à config do protinfo
    const prg = initRandomSource();
    const eg = new verificatum.crypto.ElGamal(true, keyPGroup, prg, 20);
    const wpk = eg.widePublicKey(fullPublicKey, WIDTH);

    // Codifica a mensagem
    const asciiBytes = message.split("").map((c) => c.charCodeAt(0));
    const encoded = wpk.pGroup.project(1).encode(asciiBytes);
    const encrypted = eg.encrypt(wpk, encoded);

    // ByteTree format
    const encrypted0 = encrypted.values[0].toByteTree();
    const encrypted1 = encrypted.values[1].toByteTree();
    const root = new verificatum.eio.ByteTree([encrypted0, encrypted1]);
    return root.toByteArray();
}

// ==== CLI Entry Point ====
const args = process.argv.slice(2);
if (args.length < 1) {
    console.error("Uso: node encrypt.js <mensagem> [<caminho_para_chave_publica>]");
    process.exit(1);
}

const message = args[0];
const publicKeyPath = args[1] || path.join(__dirname, "../verificatum-demo/logs/publicKey");

const ciphertext = encryptValue(message, publicKeyPath);
process.stdout.write(Buffer.from(ciphertext));
