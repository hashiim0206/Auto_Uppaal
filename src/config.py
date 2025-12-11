# config.py

import os

# -----------------------
# LLM CONFIGURATION
# -----------------------

# DO NOT hardcode your key here.
# Set it in the environment instead:
#   setx GROQ_API_KEY "your_real_key_here"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Groq model
GROQ_MODEL = "llama-3.3-70b-versatile"

# -----------------------
# VERIFYTA CONFIGURATION
# -----------------------

# ABSOLUTE PATH TO verifyta.exe  (check this matches your install)
VERIFYTA_PATH = r"C:\Program Files\UPPAAL-5.0.0\app\bin\verifyta.exe"

# -----------------------
# OUTPUT DIRECTORY
# -----------------------

RESULT_DIR = os.path.join(os.getcwd(), "results")
os.makedirs(RESULT_DIR, exist_ok=True)
