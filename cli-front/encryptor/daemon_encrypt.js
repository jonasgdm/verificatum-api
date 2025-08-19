require("./min-vjsc-1.1.1.js");
const { encryptWithPublicKey } = require("./encrypt_core");
const readline = require("readline");

let publicKey = null;
const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });

function ok(obj) { process.stdout.write(JSON.stringify({ ok: true, ...obj }) + "\n"); }
function err(id, e) { process.stdout.write(JSON.stringify({ ok: false, id, error: String(e && e.stack || e) }) + "\n"); }
function toHex(jsonByteArrayString) {
    const arr = JSON.parse(jsonByteArrayString);     // array de bytes
    return Buffer.from(arr).toString("hex");         // hex para o Python
}

rl.on("line", (line) => {
    let msg; try { msg = JSON.parse(line); } catch { return; }
    (async () => {
        try {
            if (msg.type === "init") {
                publicKey = msg.publicKey;
                ok({ type: "init" });
            } else if (msg.type === "enc") {
                const out = encryptWithPublicKey(msg.value, publicKey);
                ok({ type: "enc", id: msg.id, hex: toHex(out) });
            } else if (msg.type === "enc_batch") {
                const hex_list = msg.values.map(v => toHex(encryptWithPublicKey(v, publicKey)));
                ok({ type: "enc_batch", id: msg.id, hex_list });
            } else if (msg.type === "close") {
                process.exit(0);
            }
        } catch (e) { err(msg.id, e); }
    })();
});
