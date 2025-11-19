# ==========================================================
#  QUANTREO FEATURE DSR OBSERVER RUNNER
# ==========================================================
from langchain_groq import ChatGroq
from agents.features_info.feature_dsr_observer import FeatureDSRObserver
from pathlib import Path
from dotenv import load_dotenv
import yaml
import time

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()

# ==========================================================
#  2. Define paths
# ==========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT_DIR / "outputs" / "features_info" / "raw_info"
OUTPUT_DIR = ROOT_DIR / "outputs" / "features_info" / "dsr"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
#  3. Load normalized feature YAML files
# ==========================================================
yaml_files = list(INPUT_DIR.glob("*.yaml"))
if not yaml_files:
    raise FileNotFoundError(f"No normalized feature YAMLs found in {INPUT_DIR}")

print(f"Found {len(yaml_files)} normalized YAML files.")

# ==========================================================
#  4. Initialize model and DSR observer agent
# ==========================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2
)
observer = FeatureDSRObserver(llm)

# ==========================================================
#  5. Sequential analysis
# ==========================================================
for i, INPUT_FILE in enumerate(yaml_files[:1]):  # Limit to first 10 for testing
    print(f"\n📄 Analyzing {INPUT_FILE.name} ({i + 1}/{len(yaml_files)})...\n")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        feature_yaml = yaml.safe_load(f)

    dsr_result = observer.analyze(feature_yaml)

    if dsr_result:
        feature_name = dsr_result.get("feature", INPUT_FILE.stem)
        observer.save(dsr_result, OUTPUT_DIR, feature_name)
    else:
        print("❌ DSR observation failed.\n")

    # Add a small delay to respect API limits
    time.sleep(10)

# ==========================================================
#  6. Completion
# ==========================================================
print("\n🏁 All DSR analyses completed successfully.\n")
