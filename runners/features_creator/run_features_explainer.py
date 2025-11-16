# ==========================================================
#  QUANTREO FEATURE EXPLAINER RUNNER
# ==========================================================
from langchain_groq import ChatGroq
from agents.feature_creator.explainer import FeatureExplainerAgent
from pathlib import Path
from core.utils.io import ensure_dir
from dotenv import load_dotenv

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()

# ==========================================================
#  2. Define paths
# ==========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT_DIR / "outputs" / "tests" / "features" / "refiner" / "volume_imbalance.py"
OUTPUT_DIR = ROOT_DIR / "outputs" / "tests" / "features" / "documentation"
ensure_dir(OUTPUT_DIR)

# ==========================================================
#  3. Load feature code
# ==========================================================
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    code = f.read()

print(f"Loaded feature code: {INPUT_FILE.name}")

# ==========================================================
#  4. Initialize model and explainer agent
# ==========================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4
)
explainer = FeatureExplainerAgent(llm)

# ==========================================================
#  5. Generate human-readable explanation
# ==========================================================
print("\nGenerating human-readable explanation...")
explanation = explainer.explain(code)

# ==========================================================
#  6. Save explanation
# ==========================================================
if explanation:
    feature_name = INPUT_FILE.stem.replace("feat_", "").replace("_refined", "")
    output_path = explainer.save(explanation, feature_name, OUTPUT_DIR)
    print(f"\nExplanation for '{feature_name}' saved to: {output_path}")

    print("-" * 60)
    print(explanation[:500] + ("..." if len(explanation) > 500 else ""))
    print("-" * 60)
else:
    print("Explanation generation failed.")
