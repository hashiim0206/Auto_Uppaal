# xml_utils.py

import re
import xml.etree.ElementTree as ET


# ============================================================
#                     BASIC SANITIZER
# ============================================================

def sanitize_xml(text: str) -> str:
    """
    Cleans LLM output:
    - removes fences
    - extracts <nta> ... </nta>
    - never returns empty unless input empty
    """
    if not text:
        return ""

    text = text.replace("```xml", "").replace("```", "").strip()

    start = text.find("<nta")
    end = text.rfind("</nta>")

    if start == -1 or end == -1:
        return text.strip()

    cleaned = text[start:end + len("</nta>")].strip()

    if len(cleaned) < 10:
        return text.strip()

    return cleaned


# ============================================================
#                 MINIMAL MODEL OVERRIDE
# ============================================================

def force_minimal_model() -> str:
    """
    A guaranteed valid minimal UPPAAL model.
    """
    return """<nta>
  <declaration></declaration>

  <template>
    <name>Minimal</name>
    <location id="id0">
      <name>S</name>
    </location>
    <init ref="id0"/>
  </template>

  <system>
P = Minimal();
system P;
  </system>
</nta>"""


# ============================================================
#                   LOW LEVEL HELPERS
# ============================================================

def _strip_doctype_and_header(xml_text: str) -> str:
    lines = []
    for line in xml_text.splitlines():
        s = line.lstrip()
        if s.startswith("<?xml") or s.startswith("<!DOCTYPE"):
            continue
        lines.append(line)
    return "\n".join(lines)


def _remove_query_blocks(root: ET.Element):
    """
    Strict: remove any <query> junk the LLM might have inserted.
    Queries are handled externally by .q files.
    """
    for q in list(root.findall("query")):
        root.remove(q)


# ============================================================
#                   IDENTIFIER FIXER
# ============================================================

def _fix_identifier(name: str) -> str:
    """
    Make name a valid UPPAAL identifier.
    """
    if not name:
        return "X"

    name = re.sub(r"[^A-Za-z0-9_]", "_", name)

    if not re.match(r"[A-Za-z_]", name[0]):
        name = "X" + name

    return name


# ============================================================
#           FIX LOCATIONS / NAMES / IDS
# ============================================================

def _fix_location_names_and_ids(template: ET.Element):
    used_ids = set()
    counter = 0

    for loc in template.findall("location"):
        # Fix ID
        lid = loc.get("id")
        if not lid:
            lid = f"id{counter}"
        lid = _fix_identifier(lid)
        if lid in used_ids:
            lid = f"id{counter}"
        used_ids.add(lid)
        loc.set("id", lid)
        counter += 1

        # Fix location name
        nm = loc.find("name")
        if nm is not None and nm.text:
            nm.text = _fix_identifier(nm.text)


# ============================================================
#            LABEL NORMALISATION (GUARD/SYNC/ASSIGN)
# ============================================================

def _normalize_guard(label: ET.Element):
    if label.text:
        text = re.sub(r"[^A-Za-z0-9_<>=+*/!&| \t-]", "", label.text.strip())
        label.text = text


def _normalize_assignment(label: ET.Element):
    """
    Strict normalizer for assignment labels.

    We only keep simple 'var = number' assignments.
    If we cannot parse it safely, we drop the label entirely
    to avoid verifyta syntax errors.
    """
    txt = (label.text or "").strip()
    if not txt:
        label.text = None
        return

    # Remove semicolons and weird characters
    txt = txt.replace(";", "")
    txt = re.sub(r"[^A-Za-z0-9_=+\-*/ \t]", "", txt)

    # Try to match 'var = 123'
    m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([0-9]+)\s*$", txt)
    if not m:
        # Too weird → safer to drop than to break verifyta
        label.text = None
        return

    var, val = m.groups()
    label.text = f"{var} = {val}"


def _normalize_sync(label: ET.Element):
    text = (label.text or "").strip()
    text = re.sub(r"[^A-Za-z0-9!?_]", "", text)
    if "!" not in text and "?" not in text:
        text += "!"
    label.text = text


# ============================================================
#            FIX TRANSITIONS COMPLETELY
# ============================================================

def _fix_transitions(template: ET.Element):
    locs = template.findall("location")
    first = locs[0].get("id") if locs else "id0"

    for trans in template.findall("transition"):
        # Fix source
        src = trans.find("source")
        if src is None or not src.get("ref"):
            new = ET.Element("source", {"ref": first})
            if src is None:
                trans.insert(0, new)
            else:
                src.set("ref", first)

        # Fix target
        tgt = trans.find("target")
        if tgt is None or not tgt.get("ref"):
            new = ET.Element("target", {"ref": first})
            if tgt is None:
                trans.append(new)
            else:
                tgt.set("ref", first)

        # Fix labels
        for label in list(trans.findall("label")):
            kind = label.get("kind")

            if kind == "guard":
                _normalize_guard(label)
            elif kind == "assignment":
                _normalize_assignment(label)
            elif kind == "synchronisation":
                _normalize_sync(label)

            # Drop empty / broken labels
            if not label.text or not label.text.strip():
                trans.remove(label)


# ============================================================
#            FIX ENTIRE TEMPLATE BLOCK
# ============================================================

def _fix_template(template: ET.Element):
    """
    Structural repair for a single template (strict but pragmatic):
    - Ensure at least one location
    - Ensure exactly one init
    - Fix IDs and names
    - Fix transitions (sources/targets/labels)
    """

    # Ensure at least one location
    locs = template.findall("location")
    if not locs:
        loc = ET.SubElement(template, "location", {"id": "id0"})
        nm = ET.SubElement(loc, "name")
        nm.text = "S"
        locs = [loc]

    _fix_location_names_and_ids(template)

    locs = template.findall("location")
    ids = [loc.get("id") for loc in locs if loc.get("id")]

    # Ensure exactly one init
    inits = template.findall("init")
    if len(inits) == 0 and ids:
        ET.SubElement(template, "init", {"ref": ids[0]})
    elif len(inits) > 1:
        # keep the first, drop the rest
        for extra in inits[1:]:
            template.remove(extra)

    _fix_transitions(template)


# ============================================================
#         ALWAYS REBUILD <system> BLOCK (NO DUPLICATES)
# ============================================================

def _ensure_system_block(root: ET.Element, templates):
    """
    Completely replaces <system> block.
    Never uses LLM output. Strict and deterministic.
    """
    if not templates:
        return

    # Get template names
    names = []
    for tmpl in templates:
        name_elem = tmpl.find("name")
        if name_elem is not None and name_elem.text:
            names.append(name_elem.text.strip())

    if not names:
        return

    # Remove old system
    old = root.find("system")
    if old is not None:
        root.remove(old)

    sys_elem = ET.SubElement(root, "system")

    # One process
    if len(names) == 1:
        t = names[0]
        sys_elem.text = f"\nP = {t}();\nsystem P;\n"
        return

    # Multiple processes
    lines = []
    proc_names = []
    for i, t in enumerate(names):
        pname = f"P{i}"
        proc_names.append(pname)
        lines.append(f"{pname} = {t}();")
    lines.append(f"system {', '.join(proc_names)};")

    sys_elem.text = "\n" + "\n".join(lines) + "\n"


# ============================================================
#         ENSURE TEMPLATES HAVE NAMES (STRICT)
# ============================================================

def _ensure_template_name(template: ET.Element, index: int):
    """
    Strict requirement: every template must have a <name>.
    If missing or empty, we assign a generic name Template{index}.
    """
    name_elem = template.find("name")
    if name_elem is None:
        name_elem = ET.SubElement(template, "name")
        name_elem.text = f"Template{index}"
        return

    if not (name_elem.text and name_elem.text.strip()):
        name_elem.text = f"Template{index}"


# ============================================================
#    MAIN VALIDATOR — STRICT STRUCTURAL REPAIR + SYSTEM
# ============================================================

def validate_and_repair_xml(xml_text: str, queries: list[str]) -> str:
    """
    Strict validator:
    - requires <nta>
    - requires at least one <template>
    - enforces template names
    - repairs locations, inits, transitions
    - always rebuilds <system> block
    - DOES NOT infer declarations from queries (no hard-coding)
    """
    if not xml_text:
        return xml_text

    # Parse XML
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        # Try again without XML header / doctype
        try:
            cleaned = _strip_doctype_and_header(xml_text)
            root = ET.fromstring(cleaned)
        except ET.ParseError:
            # Too broken → let verifyta complain; we don't hallucinate a model
            return xml_text

    if root.tag != "nta":
        return xml_text

    # Remove any query blocks the LLM might have added
    _remove_query_blocks(root)

    # Fix templates
    templates = list(root.findall("template"))
    if not templates:
        # No templates at all — too broken to repair meaningfully
        return xml_text

    for idx, tmpl in enumerate(templates):
        _ensure_template_name(tmpl, idx)
        _fix_template(tmpl)

    # ALWAYS rebuild system block based on actual template names
    _ensure_system_block(root, templates)

    # STRICT: we do NOT try to guess or inject declarations from queries.
    # Whatever declarations the LLM provided are used as-is.

    return ET.tostring(root, encoding="unicode")
