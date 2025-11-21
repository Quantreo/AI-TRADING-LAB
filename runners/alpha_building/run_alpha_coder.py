# ==========================================================
#  QUANTREO ALPHA CODER RUNNER
# ==========================================================
from langchain_groq import ChatGroq
from pathlib import Path
from dotenv import load_dotenv
from agents.alpha_building.alpha_coder import AlphaCoderAgent
from core.utils.io import ensure_dir
import yaml
import os
import random

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()

# ==========================================================
#  2. Define paths and configuration
# ==========================================================
focus = "volatility_regime"
ROOT_DIR = Path(__file__).resolve().parents[2]
FORMULAS_DIR = ROOT_DIR / "outputs" / "tests" / "alphas" / focus / "formulas"
OUT_DIR      = ROOT_DIR / "outputs" / "tests" / "alphas" / focus / "code"
ensure_dir(OUT_DIR)

print(f"Alpha coder focus: {focus}")
print(f"Formulas directory: {FORMULAS_DIR}")
print(f"Output directory:   {OUT_DIR}")

# ==========================================================
#  3. Select one alpha_formula YAML
# ==========================================================
formula_files = sorted(FORMULAS_DIR.glob("*.yaml"))
if not formula_files:
    raise FileNotFoundError(f"No alpha_formula YAMLs found in {FORMULAS_DIR}")

formula_path = random.choice(formula_files)
print(f"Selected formula: {formula_path.name}")

with open(formula_path, "r", encoding="utf-8") as f:
    alpha_yaml = yaml.safe_load(f)

# ==========================================================
#  4. Initialize model and Alpha Coder Agent
# ==========================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.15
)
agent = AlphaCoderAgent(llm)

# ==========================================================
#  5. Generate and save alpha code
# ==========================================================
print("\nGenerating alpha code...")
code = agent.generate(alpha_yaml)

if code and agent.quick_sanity_check(code):
    agent.save(code, alpha_yaml, OUT_DIR)
    print("\nAlpha coding successful. Code saved.")
else:
    print("\nAlpha coding failed or code did not pass sanity checks.")

print("\n------------------------------------------------------------")
print("Alpha Coder Runner completed.")
print("------------------------------------------------------------\n")
