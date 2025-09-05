import re


def parse_shuffle_summary(text: str):
    summary = {}
    comm = {}

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("- Execution"):
            summary["execution_ms"] = int(line.split()[-1])
        elif line.startswith("- Network"):
            summary["network_ms"] = int(line.split()[-1])
        elif line.startswith("- Effective"):
            summary["effective_ms"] = int(line.split()[-1])
        elif line.startswith("- Idle"):
            summary["idle_ms"] = int(line.split()[-1])
        elif line.startswith("- Computation"):
            summary["computation_ms"] = int(line.split()[-1])
        elif line.startswith("- Sent"):
            comm["sent_bytes"] = int(line.split()[-1])
        elif line.startswith("- Received"):
            comm["received_bytes"] = int(line.split()[-1])
        elif line.startswith("- Total"):
            comm["total_bytes"] = int(line.split()[-1])
        elif line.startswith("Proof size:"):
            summary["proof_size_bytes"] = int(line.split()[-1])

    if comm:
        summary["communication"] = comm
    return summary
