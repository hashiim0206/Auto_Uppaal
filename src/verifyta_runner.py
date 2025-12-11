# verifyta_runner.py

import subprocess
import tempfile
import os

from config import VERIFYTA_PATH


def run_verifyta(xml_text: str, queries: list[str]):
    """
    Writes XML + queries to temp files, executes verifyta,
    returns (ok, raw_output, property_results).
    """

    # Write XML safely
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml", mode="w", encoding="utf-8") as f_xml:
        f_xml.write(xml_text)
        f_xml.flush()
        os.fsync(f_xml.fileno())
        xml_path = f_xml.name

    # Write queries
    with tempfile.NamedTemporaryFile(delete=False, suffix=".q", mode="w", encoding="utf-8") as f_q:
        f_q.write("\n".join(queries))
        f_q.flush()
        os.fsync(f_q.fileno())
        query_path = f_q.name

    try:
        result = subprocess.run(
            [VERIFYTA_PATH, xml_path, query_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception as e:
        return False, str(e), []

    raw_output = result.stdout + result.stderr

    # Parse property results
    properties = []
    lines = raw_output.splitlines()
    for line in lines:
        if "Formula" in line:
            if "NOT satisfied" in line:
                properties.append(False)
            elif "satisfied" in line:
                properties.append(True)

    # Valid = all properties satisfied + returncode 0
    ok = result.returncode == 0 and all(properties) if properties else False

    return ok, raw_output, properties
