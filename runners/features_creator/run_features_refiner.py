# ==========================================================
#  QUANTREO FEATURE CODE REFINER RUNNER
# ==========================================================
from langchain_groq import ChatGroq
from agents.feature_creator.refiner import FeatureCodeRefinerAgent
from core.utils.io import ensure_dir
from pathlib import Path
from dotenv import load_dotenv

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()

# ==========================================================
#  2. Define paths
# ==========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT_DIR / "outputs" / "tests" / "features" / "coder" / "volume_imbalance.py"
OUTPUT_DIR = ROOT_DIR / "outputs" / "tests" / "features" / "refiner"
ensure_dir(OUTPUT_DIR)

# ==========================================================
#  3. Load feature code
# ==========================================================
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_code = f.read()

# ==========================================================
#  4. Initialize model and refiner agent
# ==========================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2
)
refiner = FeatureCodeRefinerAgent(llm)

# ==========================================================
#  5. Refine feature code
# ==========================================================
print("\nRefining feature code...")
refined_code = refiner.refine(raw_code)

# ==========================================================
#  6. Save refined code
# ==========================================================
if refined_code:
    output_path = refiner.save(refined_code, INPUT_FILE.stem, OUTPUT_DIR)
    print(f"\nFeature '{INPUT_FILE}' refined and saved to: {output_path}")
else:
    print("Refinement failed or returned invalid code.")
