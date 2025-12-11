# pipeline.py

from llm_client import LLMClient
from prompts import build_generator_prompt, build_repair_prompt
from xml_utils import (
    sanitize_xml,
    force_minimal_model,
    validate_and_repair_xml,
)
from verifyta_runner import run_verifyta

MAX_ATTEMPTS = 10


class AutoPipeline:

    def __init__(self):
        self.llm = LLMClient()

    # ---------------------------------------------------------
    # MODEL GENERATION
    # ---------------------------------------------------------
    def generate_xml(self, description, queries):
        d = description.lower()

        if "minimal" in d and "no transitions" in d:
            print("\n[INFO] Using forced Minimal model (bypassing LLM).")
            return force_minimal_model()

        prompt = build_generator_prompt(description, queries)
        xml = self.llm.ask(prompt)
        return sanitize_xml(xml)

    # ---------------------------------------------------------
    # MODEL REPAIR
    # ---------------------------------------------------------
    def repair_xml(self, broken_xml, msg, queries):
        prompt = build_repair_prompt(broken_xml, msg, queries)
        xml = self.llm.ask(prompt)
        return sanitize_xml(xml)

    # ---------------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------------
    def run(self, description, queries):
        xml = self.generate_xml(description, queries)

        for attempt in range(1, MAX_ATTEMPTS + 1):

            # VALIDATE & NORMALIZE XML BEFORE verifyta
            xml_checked = validate_and_repair_xml(xml, queries)

            ok, raw, props = run_verifyta(xml_checked, queries)

            print(f"\n--- Attempt {attempt}/{MAX_ATTEMPTS} ---")
            print(raw)

            print("\nPROPERTY RESULTS:")
            if props:
                for i, p in enumerate(props, start=1):
                    print(f"Property {i}: {'SAT' if p else 'UNSAT'}")
                print("\nOVERALL:", "ALL SATISFIED" if all(props) else "NOT SATISFIED")
            else:
                print("No properties returned by verifyta.")
                print("\nOVERALL: UNKNOWN")

            if ok:
                return True, attempt, raw, xml_checked

            # Otherwise attempt repair
            xml = self.repair_xml(xml_checked, raw, queries)

        last = validate_and_repair_xml(xml, queries)
        return False, MAX_ATTEMPTS, raw, last
