// encryptor/daemon_encrypt.js
require("./min-vjsc-1.1.1.js");
const readline = require("readline");
const { initWithPublicKey, encryptOnce } = require("./encrypt_core");

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });

function ok(obj) { process.stdout.write(JSON.stringify({ ok: true, ...obj }) + "\n"); }
function err(id, e) { process.stdout.write(JSON.stringify({ ok: false, id, error: String(e && e.stack || e) }) + "\n"); }

rl.on("line", (line) => {

    let msg; try { msg = JSON.parse(line); } catch { return; }
    try {
        if (msg.type === "init") {
            initWithPublicKey(msg.publicKey);
            ok({ type: "init", ready: true });
        } else if (msg.type === "enc") {
            const hex = encryptOnce(msg.value);
            ok({ type: "enc", id: msg.id, hex });
        } else if (msg.type === "enc_batch") {
            console.error("PID", process.pid, "encrypting batch of", (msg.values || []).length);
            const start = Date.now();
            const hex_list = (msg.values || []).map(v => encryptOnce(v));
            const elapsed = (Date.now() - start) / 1000; // segundos
            const count = msg.values.length
            ok({ type: "enc_batch", id: msg.id, hex_list, stats: { count, elapsed } });
        } else if (msg.type === "close") {
            process.exit(0);
        } else {
            throw new Error("unknown_type");
        }
    } catch (e) { err(msg.id, e); }
});
