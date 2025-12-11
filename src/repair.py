# repair.py

from typing import List
from prompts import build_repair_prompt
from xml_utils import strip_non_xml
from llm_client import LLMClient


def repair_xml(broken_xml: str, verifier_output: str, queries: List[str], llm: LLMClient) -> str:
    """
    Ask the LLM to repair the broken XML using verifyta's error output.
    Returns the new XML text (may still be wrong; pipeline will check).
    """
    prompt = build_repair_prompt(broken_xml, verifier_output, queries)
    reply = llm.ask(prompt)
    return strip_non_xml(reply)
