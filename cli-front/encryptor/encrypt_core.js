// encryptor/encrypt_core.js
require("./min-vjsc-1.1.1.js");
const verificatum = global.verificatum;

// ---- ESTADO PERSISTENTE (preparado no init) ----
let state = {
    ready: false,
    keyPGroup: null,
    wpk: null,
    eg_master: null,       // ElGamal com PRG mestre
    prg_master: null,      // PRG mestre (semeado 1x)
};

function initWithPublicKey(publicKeyJsonString) {
    const pk = JSON.parse(publicKeyJsonString);
    const bt = verificatum.eio.ByteTree.readByteTreeFromByteArray(pk);

    const keyPGroup = verificatum.arithm.ECqPGroup.fromByteTree(bt.value[0].value[1]);
    const fullPublicKey = new verificatum.arithm.PPGroup(keyPGroup, 2).toElement(bt.value[1]);

    // PRG mestre semeado UMA vez via RandomDevice
    const prg_master = new verificatum.crypto.SHA256PRG();
    const seed = new verificatum.crypto.RandomDevice().getBytes(verificatum.crypto.SHA256PRG.seedLength);
    prg_master.setSeed(seed);

    const eg_master = new verificatum.crypto.ElGamal(true, keyPGroup, prg_master, 20);
    const WIDTH = 1;
    const wpk = eg_master.widePublicKey(fullPublicKey, WIDTH);

    state = { ready: true, keyPGroup, wpk, eg_master, prg_master };
}

// Cifra UMA mensagem usando objetos já prontos
function encryptOnce(plaintext) {
    // Deriva uma seed fresca do PRG mestre (não chama RandomDevice de novo)
    const derived = state.prg_master.getBytes(verificatum.crypto.SHA256PRG.seedLength);
    const prg_local = new verificatum.crypto.SHA256PRG();
    prg_local.setSeed(derived);

    // Usa um ElGamal leve com o PRG derivado (mantém segurança e randômico único)
    const eg_local = new verificatum.crypto.ElGamal(true, state.keyPGroup, prg_local, 20);

    const ascii = [...plaintext].map(c => c.charCodeAt(0));
    const encoded = state.wpk.pGroup.project(1).encode(ascii);
    const encrypted = eg_local.encrypt(state.wpk, encoded);
    const btBytes = encrypted.toByteTree().toByteArray();
    return Buffer.from(btBytes).toString("hex");
    // const e0 = encrypted.values[0].toByteTree().toByteArray();
    // const e1 = encrypted.values[1].toByteTree().toByteArray();
    // const u8 = new Uint8Array(e0.length + e1.length);
    // u8.set(e0, 0);
    // u8.set(e1, e0.length);
    // return Buffer.from(u8).toString("hex"); // já retorna HEX
}

module.exports = { initWithPublicKey, encryptOnce };
