const fs = require("fs");
const path = require("path");

(async () => {
    try {
        const wasmPath = path.join(__dirname, "muladd.wasm");
        const wasmBytes = fs.readFileSync(wasmPath);

        const results = await WebAssembly.instantiate(wasmBytes, { env: {} });

        const wasm_muladd_loop = results.instance.exports.muladd_loop;
        const offset = results.instance.exports.get_buffer();
        const memory = new Uint32Array(results.instance.exports.memory.buffer, offset, 8989);

        // Teste simples: zera o buffer, roda muladd_loop com valores pequenos
        memory.fill(0);
        const xlen = 5;
        const start = 0;
        const end = 5;
        const Y = 123456;
        const i = 0;
        const c = 0;

        const carry = wasm_muladd_loop(xlen, start, end, Y, i, c);

        console.log("✅ muladd.wasm carregado com sucesso.");
        console.log("📦 Resultado carry:", carry);
        console.log("🧠 Buffer (primeiros 10):", memory.slice(0, 10));
    } catch (err) {
        console.error("❌ Erro ao carregar ou rodar muladd.wasm:");
        console.error(err);
    }
})();
