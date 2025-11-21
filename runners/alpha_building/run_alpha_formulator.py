# ==========================================================
#  QUANTREO ALPHA FORMULATOR RUNNER — single concept
# ==========================================================
from langchain_groq import ChatGroq
from agents.alpha_building.alpha_formulator import AlphaFormulatorAgent
from pathlib import Path
from dotenv import load_dotenv
from core.utils.io import ensure_dir
import yaml
import random
import os

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()
seed = os.getenv("ALPHA_FORMULATOR_SEED")
if seed is not None:
    random.seed(int(seed))
else:
    random.seed()

# ==========================================================
#  2. Define paths and configuration
# ==========================================================
focus = "volatility_regime"  # <trend | mean_reversion | volatility_regime | filter | risk | position_sizing>
ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT_DIR / "outputs" / "tests" / "alphas" / focus / "concepts"
OUTPUT_DIR = ROOT_DIR / "outputs" / "tests" / "alphas" / focus / "formulas"
ensure_dir(OUTPUT_DIR)

print(f"Alpha formulation focus: {focus}")
print(f"Input directory: {INPUT_DIR}")
print(f"Output directory: {OUTPUT_DIR}")

# ==========================================================
#  3. Pick ONE concept YAML
# ==========================================================
concept_files = list(INPUT_DIR.glob("*.yaml"))
if not concept_files:
    raise FileNotFoundError(f"No alpha_concept YAMLs found in {INPUT_DIR}")

concept_file = random.choice(concept_files)
print("Selected concept file:")
print(f" - {concept_file.name}")

concept = yaml.safe_load(concept_file.read_text(encoding="utf-8"))

# ==========================================================
#  4. Initialize model and Agent
# ==========================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.35
)
agent = AlphaFormulatorAgent(llm)

# ==========================================================
#  5. Generate and save ONE formula
# ==========================================================
print("\nGenerating alpha formula...")
alpha_yaml = agent.formulate_alpha(concept)

if alpha_yaml:
    # basename identique à celui du concept (sans extension)
    basename = concept_file.stem
    # meta utile pour le traçage
    alpha_yaml.setdefault("meta", {})
    alpha_yaml["meta"]["concept_file"] = concept_file.name

    agent.save(alpha_yaml, OUTPUT_DIR, basename=basename)
    print(f"\n[SUCCESS] Formula saved to {OUTPUT_DIR / (basename + '.yaml')}")
else:
    print("\n[FAIL] Alpha formulation failed or invalid YAML.")

print("\n------------------------------------------------------------")
print("Alpha Formulator Runner completed.")
print("------------------------------------------------------------\n")
