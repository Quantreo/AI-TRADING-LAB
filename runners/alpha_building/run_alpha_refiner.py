# ==========================================================
#  QUANTREO ALPHA CODE REFINER RUNNER
# ==========================================================
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from agents.alpha_building.alpha_code_refiner import AlphaCodeRefinerAgent

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()

# ==========================================================
#  2. Define paths and configuration
# ==========================================================
focus = "volatility_regime"
ROOT_DIR = Path(__file__).resolve().parents[2]
CODE_DIR = ROOT_DIR / "outputs" / "tests" / "alphas" / focus / "code"
OUT_DIR  = ROOT_DIR / "outputs" / "tests" / "alphas" / focus / "code_refined"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Alpha refiner focus: {focus}")
print(f"Input code directory:  {CODE_DIR}")
print(f"Output directory:      {OUT_DIR}")

# ==========================================================
#  3. Initialize model and Alpha Code Refiner Agent
# ==========================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1
)
agent = AlphaCodeRefinerAgent(llm)

# ==========================================================
#  4. Refine all Python code files
# ==========================================================
print("\nRefining alpha code files...")
for py in CODE_DIR.glob("*.py"):
    src = py.read_text(encoding="utf-8")
    refined = agent.refine(src)

    if refined:
        (OUT_DIR / py.name).write_text(refined, encoding="utf-8")
        print(f"Refined: {py.name}")
    else:
        print(f"Skipped: {py.name} refinement failed.")

print("\n------------------------------------------------------------")
print("Alpha Code Refiner Runner completed.")
print("------------------------------------------------------------\n")