# prompts.py

"""
Prompt definitions for the Auto-UPPAAL pipeline.

Goal:
- Get the LLM to produce / repair UPPAAL XML that verifyta accepts
  for ANY number of templates.
- Keep queries external (not embedded in XML).
- Enforce bulletproof synchronisation formatting.
"""

GENERATOR_INSTR = """
You are an expert in UPPAAL.

Generate a COMPLETE, VALID UPPAAL XML model conforming to flat-1_6.dtd.

OUTPUT RULES (MUST FOLLOW STRICTLY)
-----------------------------------
1. Output ONLY XML inside a single <nta> ... </nta> root.
   - No markdown.
   - No explanations.
   - No XML declaration (<?xml ...?>).
   - No DOCTYPE.

2. TEMPLATES:
   - The model must contain one or more <template> blocks.
   - Each <template> MUST contain:
       <name>TemplateName</name>
       one or more <location id="..."><name>...</name></location>
       exactly one <init ref="someLocationId"/>

   - Location requirements:
       * Each location must have a unique id within its template.
       * Each location should have a <name> child with a valid identifier.
       * Identifiers: letters, digits, underscore; cannot start with a digit.

3. TRANSITIONS:
   Every transition MUST follow this canonical structure:

   <transition>
     <source ref="ID_SOURCE"/>
     <target ref="ID_TARGET"/>

     <!-- Only include labels if they are non-empty -->
     <!-- GUARD -->
     <label kind="guard">condition</label>

     <!-- SYNCHRONISATION -->
     <label kind="synchronisation">start!</label>
     or
     <label kind="synchronisation">start?</label>

     <!-- ASSIGNMENT -->
     <label kind="assignment">x = 0</label>
   </transition>

   - If there is no guard, omit the guard label entirely.
   - If there is no synchronisation, omit the synchronisation label.
   - If there is no assignment, omit the assignment label.

4. BULLETPROOF SYNCHRONISATION RULES (VERY IMPORTANT):
   - Synchronisation labels must match EXACTLY these patterns when used:
        <label kind="synchronisation">start!</label>
        <label kind="synchronisation">start?</label>
   - No leading or trailing spaces inside the label text.
   - No variants like:
       " start!", "start! ", "start !", "start ?", " start ? ", "start !"
   - No quotes around the channel name.
   - If the DESCRIPTION mentions another channel name (e.g. req, ack),
     use EXACTLY that name followed by ! or ?, with no spaces:
       <label kind="synchronisation">req!</label>
       <label kind="synchronisation">ack?</label>

5. DECLARATIONS:
   - If clocks, channels, or variables are required by the DESCRIPTION,
     declare them inside the top-level <declaration> element.
   - If no declarations are needed, <declaration> may be empty:
       <declaration></declaration>

6. SYSTEM BLOCK:
   - The system block MUST appear once and ONLY once, as:

   <system>
P = TemplateA();
Q = TemplateB();
R = TemplateC();
system P, Q, R;
   </system>

   - For a single template T, you may use:
       <system>
P = T();
system P;
       </system>

   - Do NOT use <process> or <templateInst> tags.
   - Do NOT duplicate process definitions.

7. QUERIES:
   - Do NOT include any <query> or <queries> elements.
   - Properties are handled externally and should NOT appear in the XML.

8. GENERAL:
   - The XML must be well-formed and accepted by UPPAAL verifyta.
   - Do not add extra templates, clocks, variables, or channels that are
     not mentioned in the DESCRIPTION unless clearly necessary
     to implement the described behavior.
"""


def build_generator_prompt(description: str, queries: list[str]) -> str:
    """
    Build the LLM prompt for initial model generation.

    - `description`: natural language description of the intended model.
    - `queries`: given only as context; they MUST NOT be embedded as <query>.
    """
    q = "\n".join(queries)
    return f"""{GENERATOR_INSTR}

DESCRIPTION (behavior to model):
{description}

PROPERTIES (context ONLY — do NOT embed <query> in XML):
{q}

Output ONLY a single valid <nta>...</nta> UPPAAL model.
"""


REPAIR_INSTR = """
You are repairing a broken UPPAAL XML model.

Your goal:
- Fix the XML so that UPPAAL verifyta accepts it.
- Preserve the intended behavior as much as possible.
- Enforce the same structural and synchronisation rules as the generator.
- Do NOT embed queries in the XML.
- Return ONLY the corrected <nta>...</nta> block.

REPAIR RULES (MUST FOLLOW STRICTLY)
-----------------------------------
1. ROOT:
   - Ensure there is exactly one <nta> root element.
   - Remove any XML declaration (<?xml ...?>) or DOCTYPE.

2. TEMPLATES:
   For each <template>:
   - Ensure it has a <name> with a valid identifier.
   - Ensure it has one or more <location id="..."><name>...</name></location>.
   - Ensure exactly one <init ref="..."/>:
       * If missing, add one referencing an existing location id.
       * If there are multiple, keep the first and remove the rest.
   - Fix invalid or duplicated location ids (within the template) by renaming.

3. TRANSITIONS:
   For each <transition>:
   - Ensure it has both <source ref="..."/> and <target ref="..."/>.
     If missing, pick a reasonable existing location within the same template.
   - Labels must follow the canonical schema:

     <transition>
       <source ref="ID_SOURCE"/>
       <target ref="ID_TARGET"/>

       <!-- optional labels, remove if invalid/empty -->
       <label kind="guard">...</label>
       <label kind="synchronisation">...</label>
       <label kind="assignment">...</label>
     </transition>

4. BULLETPROOF SYNCHRONISATION REPAIR:
   - If a synchronisation is required by the DESCRIPTION or the existing model,
     repair it to an EXACT canonical form with NO spaces:

       <label kind="synchronisation">start!</label>
       <label kind="synchronisation">start?</label>
       or for other channels mentioned in the model:
       <label kind="synchronisation">req!</label>
       <label kind="synchronisation">req?</label>

   - Strip any surrounding whitespace or weird characters.
   - Remove broken or empty synchronisation labels.

5. DECLARATIONS:
   - If channels/clocks/variables are used in labels or guards, ensure they
     are declared in the top-level <declaration> element.
   - If old declarations are malformed, fix their syntax or remove them
     and recreate a minimal correct declaration that matches usage.

6. SYSTEM BLOCK:
   - Remove any invalid or duplicated system definitions.
   - Recreate exactly ONE <system> block using process instantiations
     of all templates, for example:

       <system>
P0 = T0();
P1 = T1();
system P0, P1;
       </system>

   - Do NOT use <process> or <templateInst> tags.
   - Do NOT leave dangling or unused process names.

7. QUERIES:
   - Remove any <query> or <queries> elements from the XML.

8. OUTPUT:
   - Return ONLY the corrected <nta>...</nta> XML.
   - No markdown, no explanations, no comments.
"""


def build_repair_prompt(broken: str, verifier_msg: str, queries: list[str]) -> str:
    """
    Build the LLM prompt for repairing a broken UPPAAL XML string.

    - `broken`: the current (possibly invalid) XML.
    - `verifier_msg`: error output from verifyta to guide the repair.
    - `queries`: given only as context; must NOT be embedded as <query>.
    """
    qs = "\n".join(queries)
    return f"""{REPAIR_INSTR}

BROKEN XML (model to fix):
{broken}

VERIFYTA ERROR MESSAGE:
{verifier_msg}

PROPERTIES (context ONLY — do NOT embed into XML):
{qs}

Return ONLY the corrected <nta>...</nta> XML.
"""
