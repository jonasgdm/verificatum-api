// Carrega o VJSC modificado com global.verificatum
require("./min-vjsc-1.1.1.js");
const verificatum = global.verificatum;


/**
 * Cifra um plaintext usando uma chave pública no formato ByteTree.
 * 
 * @param {string} plaintext - Texto simples a ser cifrado (ex: "LULA").
 * @param {string} publicKeyJsonString - Chave pública como string JSON.
 * @returns {string} - Ciphertext serializado (ByteTree em base64 JSON).
 */

function encryptWithPublicKey(plaintext, publicKeyJsonString) {
    const pk = JSON.parse(publicKeyJsonString);
    const bt = verificatum.eio.ByteTree.readByteTreeFromByteArray(pk);
    const keyPGroup = verificatum.arithm.ECqPGroup.fromByteTree(bt.value[0].value[1]);
    const fullPublicKey = new verificatum.arithm.PPGroup(keyPGroup, 2).toElement(bt.value[1]);

    const randomSource = new verificatum.crypto.SHA256PRG();
    const eg = new verificatum.crypto.ElGamal(true, keyPGroup, randomSource, 20);
    const WIDTH = 1;
    const wpk = eg.widePublicKey(fullPublicKey, WIDTH);

    const seed = new verificatum.crypto.RandomDevice().getBytes(verificatum.crypto.SHA256PRG.seedLength);
    randomSource.setSeed(seed);

    const asciiBytes = [...plaintext].map((c) => c.charCodeAt(0));
    const encoded = wpk.pGroup.project(1).encode(asciiBytes);
    const encrypted = eg.encrypt(wpk, encoded);

    const e0 = encrypted.values[0].toByteTree();
    const e1 = encrypted.values[1].toByteTree();
    const root = new verificatum.eio.ByteTree([e0, e1]);
    return JSON.stringify(root.toByteArray());
}

module.exports = { encryptWithPublicKey };
