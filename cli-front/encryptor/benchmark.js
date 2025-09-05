// benchmark_scaling.js
const fs = require("fs");
const { initWithPublicKey, encryptOnce } = require("./encrypt_core");

const PUBLIC_KEY_HEX =
    "000000000200000000020100000020636f6d2e766572696669636174756d2e61726974686d2e4543715047726f75700100000005502d323536000000000200000000020100000021006b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c2960100000021004fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f500000000020100000021004095a8f8c26f35ca3ca472e8aa91f727bfd7ae12d6f7bdc89f23756d138fe59a0100000021000616da0edcf7b54861b200e0745ef3a8e9383e4c7a54fe572ea0ab25d088b29d";

function hexToJsonArray(hexStr) {
    const bytes = Buffer.from(hexStr, "hex");
    const arr = Array.from(bytes);
    return JSON.stringify(arr);
}

function runBenchmark(N) {
    const values = Array.from({ length: N }, (_, i) => "MSG" + i);
    const start = Date.now();
    for (const v of values) {
        encryptOnce(v);
    }
    const elapsed = (Date.now() - start) / 1000;
    return { N, elapsed, throughput: N / elapsed };
}

function main() {
    const os = require("os");
    console.log("CPUs lógicas:", os.cpus().length);
    console.log("Detalhes:", os.cpus());
    const publicKeyJson = hexToJsonArray(PUBLIC_KEY_HEX);
    initWithPublicKey(publicKeyJson);

    const testSizes = [50, 100, 500, 1000, 2000, 5000, 10000];
    const results = testSizes.map(runBenchmark);

    fs.writeFileSync("bench_results.json", JSON.stringify(results, null, 2));
    console.log("Resultados salvos em bench_results.json");
}

main();
