# ==========================================================
#  QUANTREO STRATEGY BLOCK RUNNER
# ==========================================================
from langchain_groq import ChatGroq
from agents.strategy_conception.strategy_builder import StrategyBuilder
from pathlib import Path
from dotenv import load_dotenv
from core.utils.io import ensure_dir
import yaml
import random

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()
random.seed()  # Reset random seed for reproducibility

# ==========================================================
#  2. Define paths and configuration
# ==========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT_DIR / "outputs" / "alphas" / "bundles"
OUTPUT_DIR = ROOT_DIR / "outputs" / "tests" / "strategies" / "strategy_yaml"
ensure_dir(OUTPUT_DIR)

print(f"Input directory: {INPUT_DIR}")
print(f"Output directory: {OUTPUT_DIR}")

# ==========================================================
#  3. Load alpha YAML files
# ==========================================================
yaml_files = list(INPUT_DIR.glob("*.yaml"))
if not yaml_files:
    raise FileNotFoundError(f"No alpha YAMLs found in {INPUT_DIR}")

# Select a random subset of 10 alpha YAMLs
subset_size = min(10, len(yaml_files))
subset = random.sample(yaml_files, k=subset_size)

print(f"Loaded {subset_size} alpha YAML file(s):")
for f in subset:
    print(f" - {f.name}")

# Parse selected YAMLs into Python dictionaries
alphas = []
for file in subset:
    with open(file, "r", encoding="utf-8") as f:
        alphas.append(yaml.safe_load(f))

# ==========================================================
#  4. Initialize model and Strategy Block Agent
# ==========================================================
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.65
)
agent = StrategyBuilder(llm)

# ==========================================================
#  5. Generate strategy block
# ==========================================================
print("\nGenerating strategy block...")
block = agent.build_strategy(alphas)

# ==========================================================
#  6. Save results
# ==========================================================
if block:
    agent.save(block, OUTPUT_DIR)
    print(f"\nStrategy block generation successful — saved to {OUTPUT_DIR}")
else:
    print("\n❌ Strategy block generation failed or invalid YAML returned.")

print("\n------------------------------------------------------------")
print("Strategy Block Runner completed.")
print("------------------------------------------------------------\n")
