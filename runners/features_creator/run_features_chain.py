# ==========================================================
#  QUANTREO FEATURE CREATION CHAIN RUNNER
# ==========================================================
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_groq import ChatGroq
from agents.feature_creator.ideator import FeatureIdeatorAgent
from agents.feature_creator.coder import FeatureCoderAgent
from agents.feature_creator.refiner import FeatureCodeRefinerAgent
from agents.feature_creator.explainer import FeatureExplainerAgent
from core.pipelines.feature_chain_steps import (
    generate_idea, generate_code, refine_code, generate_explanation
)
from core.utils.io import ensure_dir
from pathlib import Path
from dotenv import load_dotenv

# ==========================================================
#  1. Environment setup
# ==========================================================
load_dotenv()
ROOT_DIR = Path(__file__).resolve().parents[2]
FEATURES_DIR = ROOT_DIR / "outputs" / "features"
ensure_dir(FEATURES_DIR)

# ==========================================================
#  2. Initialize LLMs and agents
# ==========================================================
llm_creative = ChatGroq(model="llama-3.1-8b-instant", temperature=0.75)
llm_precise = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.35)
llm_refiner = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
llm_explainer = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)

ideator = FeatureIdeatorAgent(llm_creative, focus="volatility anomalies")
coder = FeatureCoderAgent(llm_precise)
refiner = FeatureCodeRefinerAgent(llm_refiner)
explainer = FeatureExplainerAgent(llm_explainer)

# ==========================================================
#  3. Build pipeline
# ==========================================================
feature_chain = RunnableSequence(
    first=RunnableLambda(lambda _: generate_idea(ideator, FEATURES_DIR)),
    middle=[
        RunnableLambda(lambda inputs: generate_code(coder, inputs)),
        RunnableLambda(lambda inputs: refine_code(refiner, inputs)),
    ],
    last=RunnableLambda(lambda inputs: generate_explanation(explainer, inputs)),
)

# ==========================================================
#  4. Run full pipeline
# ==========================================================
print("\nRunning full Feature Creation Chain...")
final_output = feature_chain.invoke({})
print("\nPipeline completed successfully.")
print("-" * 60)
print(final_output[:600] + ("..." if len(final_output) > 600 else ""))