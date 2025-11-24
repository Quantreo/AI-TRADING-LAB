# ==========================================================
#  QUANTREO STRATEGY REPORTER RUNNER
# ==========================================================
from langchain_groq import ChatGroq
from pathlib import Path

from agents.strategy_conception.strategy_explainer import StrategyReporterAgent
from core.utils.io import ensure_dir, load_yaml
from dotenv import load_dotenv

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()

# ==========================================================
#  2. Define paths
# ==========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT_DIR / "outputs" / "tests" / "strategies" /"strategy_yaml" / "strategy_block_20251124_135554.yaml"
OUTPUT_DIR = ROOT_DIR / "outputs" / "tests" / "strategies" / "documentation"
ensure_dir(OUTPUT_DIR)

# ==========================================================
#  3. Load strategy YAML
# ==========================================================
strategy_data = load_yaml(INPUT_FILE)
print(f"Loaded strategy YAML: {INPUT_FILE.name}")

# ==========================================================
#  4. Initialize model and reporter agent
# ==========================================================
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2
)
reporter = StrategyReporterAgent(llm)

# ==========================================================
#  5. Generate human readable strategy report
# ==========================================================
print("\nGenerating strategy Markdown report...")
report_text = reporter.explain(strategy_data)

# ==========================================================
#  6. Save explanation
# ==========================================================
if report_text:
    strategy_name = strategy_data.get("strategy", {}).get("name", INPUT_FILE.stem)
    output_path = reporter.save(report_text, strategy_name, OUTPUT_DIR)
    print(f"\nStrategy report for '{strategy_name}' saved to: {output_path}")

    print("-" * 60)
    print(report_text[:500] + ("..." if len(report_text) > 500 else ""))
    print("-" * 60)
else:
    print("Strategy report generation failed.")
