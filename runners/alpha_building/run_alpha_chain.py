# ==========================================================
#  QUANTREO FULL ALPHA BUILDING CHAIN RUNNER
# ==========================================================
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_groq import ChatGroq
import argparse

from core.utils.io import ensure_dir
from core.pipelines.alpha_building_steps import (
    generate_concept,
    generate_formula,
    combine_yaml,
    generate_code,
    refine_code,
)

from agents.alpha_building.alpha_ideator import AlphaIdeatorAgent
from agents.alpha_building.alpha_formulator import AlphaFormulatorAgent
from agents.alpha_building.alpha_coder import AlphaCoderAgent
from agents.alpha_building.alpha_code_refiner import AlphaCodeRefinerAgent

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()

# ==========================================================
#  2. CLI arguments and configuration
# ==========================================================
parser = argparse.ArgumentParser()
parser.add_argument(
    "--focus", "-f",
    default="trend",
    choices=[
        "trend",
        "volatility",
        "volume"
    ]
)

FOCUS = parser.parse_known_args()[0].focus
ROOT_DIR = Path(__file__).resolve().parents[2]

DSR_DIR = ROOT_DIR / "outputs" / "features_info" / "dsr"

BASE_DIR          = ROOT_DIR / "outputs" / "alphas"
CONCEPT_DIR       = BASE_DIR / "concepts"
FORMULA_DIR       = BASE_DIR / "formulas"
BUNDLE_DIR        = BASE_DIR / "bundles"
CODE_DIR          = BASE_DIR / "code"
CODE_REFINED_DIR  = BASE_DIR / "code_refined"

for d in [CONCEPT_DIR, FORMULA_DIR, BUNDLE_DIR, CODE_DIR, CODE_REFINED_DIR]:
    ensure_dir(d)

print(f"Alpha building chain focus: {FOCUS}")
print(f"DSR directory:          {DSR_DIR}")
print(f"Concepts directory:     {CONCEPT_DIR}")
print(f"Formulas directory:     {FORMULA_DIR}")
print(f"Bundles directory:      {BUNDLE_DIR}")
print(f"Code directory:         {CODE_DIR}")
print(f"Refined code directory: {CODE_REFINED_DIR}")

# ==========================================================
#  3. Initialize LLMs and Agents
# ==========================================================
llm_creative = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.65
)
llm_precise = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.30
)
llm_coder = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.15
)
llm_refiner = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.10
)

ideator    = AlphaIdeatorAgent(llm_creative, focus=FOCUS)
formulator = AlphaFormulatorAgent(llm_precise)
coder      = AlphaCoderAgent(llm_coder)
refiner    = AlphaCodeRefinerAgent(llm_refiner)

# ==========================================================
#  4. Build full Alpha Building Chain
# ==========================================================
alpha_chain = RunnableSequence(
    first=RunnableLambda(lambda _: generate_concept(
        ideator=ideator,
        dsr_dir=DSR_DIR,
        concept_dir=CONCEPT_DIR,
        focus=FOCUS,
        subset_size=8
    )),
    middle=[
        RunnableLambda(lambda ctx: generate_formula(formulator, ctx, FORMULA_DIR)),
        RunnableLambda(lambda ctx: combine_yaml(ctx, BUNDLE_DIR)),
        RunnableLambda(lambda ctx: generate_code(coder, ctx, CODE_DIR)),
        RunnableLambda(lambda ctx: refine_code(refiner, ctx, CODE_REFINED_DIR)),
    ],
    last=RunnableLambda(lambda ctx: {
        "concept": str(ctx["concept_path"]),
        "formula": str(ctx["formula_path"]),
        "bundle":  str(ctx["bundle_path"]),
        "code":    str(ctx["code_path"]),
        "refined": str(ctx["refined_code_path"]),
    }),
)

# ==========================================================
#  5. Entry point
# ==========================================================
if __name__ == "__main__":
    print("\nRunning full Alpha Building Chain...")
    result = alpha_chain.invoke({})
    print(result)
    print("\n------------------------------------------------------------")
    print("Alpha Building Chain completed.")
    print("------------------------------------------------------------\n")
