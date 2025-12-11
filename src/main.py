# main.py

import os
from pipeline import AutoPipeline
from config import RESULT_DIR


def main():
    print("Auto-UPPAAL (Groq + verifyta)")

    print("Describe your model:")
    description_lines = []
    while True:
        line = input()
        if not line.strip():
            break
        description_lines.append(line)
    description = "\n".join(description_lines)

    print("\nEnter UPPAAL queries (one per line). Empty line to finish:")
    queries = []
    while True:
        line = input()
        if not line.strip():
            break
        queries.append(line.strip())

    pipe = AutoPipeline()
    ok, attempts, msg, xml = pipe.run(description, queries)

    # Decide output filename
    if ok:
        out_name = "output_success.xml"
    else:
        out_name = "output_failed.xml"

    out_path = os.path.join(RESULT_DIR, out_name)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)

    print("\n--- RESULT ---")
    print("Valid:", ok)
    print("Attempts:", attempts)
    print("Verifier message:\n", msg)
    print("\nSaved at:", out_path)


if __name__ == "__main__":
    main()
