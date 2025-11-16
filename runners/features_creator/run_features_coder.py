# ==========================================================
#  QUANTREO FEATURE CODER RUNNER
# ==========================================================
from langchain_groq import ChatGroq
from agents.feature_creator.coder import FeatureCoderAgent
from core.utils.io import ensure_dir
from pathlib import Path
from dotenv import load_dotenv
import yaml

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()

# ==========================================================
#  2. Define paths
# ==========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT_DIR / "outputs" / "tests" / "features" / "ideator" / "volume_imbalance.yaml"
OUTPUT_DIR = ROOT_DIR / "outputs" / "tests" / "features" / "coder"
ensure_dir(OUTPUT_DIR)

# ==========================================================
#  3. Load feature YAML
# ==========================================================
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    feature_yaml = yaml.safe_load(f)

print(f"Loaded feature spec: {INPUT_FILE.name}")
print(f"Idea: {feature_yaml.get('idea')}")
print(f"Family: {feature_yaml.get('family')}")
print(f"Parameters: {feature_yaml.get('parameters')}")

# ==========================================================
#  4. Initialize model and agent
# ==========================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2
)
agent = FeatureCoderAgent(llm)

# ==========================================================
#  5. Generate Python implementation
# ==========================================================
print("\nGenerating feature implementation...")
code = agent.generate(feature_yaml)

# ==========================================================
#  6. Validate and save
# ==========================================================
if code and agent.quick_sanity_check(code):
    filename = agent.save(code, feature_yaml, OUTPUT_DIR)
    print(f"\nFeature implementation saved to: {filename}")
else:
    print("Code generation failed or invalid.")
