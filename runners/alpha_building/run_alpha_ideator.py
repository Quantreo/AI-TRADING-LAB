# ==========================================================
#  QUANTREO ALPHA IDEATOR RUNNER
# ==========================================================
from langchain_groq import ChatGroq
from agents.alpha_building.alpha_ideator import AlphaIdeatorAgent
from pathlib import Path
from dotenv import load_dotenv
from core.utils.io import ensure_dir
import yaml
import random

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()
random.seed()

# ==========================================================
#  2. Define paths and configuration
# ==========================================================
focus = "volatility" # trend | volatility | or any tag from a DSR observation
ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT_DIR / "outputs" / "features_info" / "dsr"
OUTPUT_DIR = ROOT_DIR / "outputs" / "tests" / "alphas" / focus / "concepts"
ensure_dir(OUTPUT_DIR)

print(f"Alpha ideation focus: {focus}")
print(f"Input directory: {INPUT_DIR}")
print(f"Output directory: {OUTPUT_DIR}")

# ==========================================================
#  3. Load DSR YAML files
# ==========================================================
yaml_files = list(INPUT_DIR.glob("*.yaml"))
if not yaml_files:
    raise FileNotFoundError(f"No YAML files found in {INPUT_DIR}")

# 1. Load all YAMLs and filter by tag
filtered = []
for f in yaml_files:
    with open(f, "r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp)
        if data.get("tag") == focus:
            filtered.append((f, data))

if not filtered:
    raise ValueError("No YAML files matched tag 'volatility'.")

# 2. Randomly select up to 8 files from the filtered list
subset_size = min(8, len(filtered))
subset = random.sample(filtered, k=subset_size)

print(f"Loaded {subset_size} YAML file(s) with tag='volatility':")
for f, _ in subset:
    print(f" - {f.name}")

# 3. Extract the YAML contents only
dsr_list = [data for _, data in subset]

# ==========================================================
#  4. Initialize model and Alpha Ideator Agent
# ==========================================================
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.55
)
agent = AlphaIdeatorAgent(llm, focus=focus)

# ==========================================================
#  5. Generate one alpha concept
# ==========================================================
print("\nGenerating alpha concept...")
alpha_concept = agent.ideate_alpha(dsr_list)

# ==========================================================
#  6. Save results
# ==========================================================
if alpha_concept:
    agent.save(alpha_concept, OUTPUT_DIR)
    print(f"\nAlpha ideation successful. Concept saved to {OUTPUT_DIR}")
else:
    print("\nAlpha ideation failed or no valid YAML returned.")

print("\n------------------------------------------------------------")
print("Alpha Ideator Runner completed.")
print("------------------------------------------------------------\n")
