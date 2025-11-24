# ==========================================================
#  QUANTREO STRATEGY BUILDING CHAIN RUNNER
# ==========================================================
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_groq import ChatGroq
from pathlib import Path
from dotenv import load_dotenv

from agents.strategy_conception.strategy_builder import StrategyBuilder
from agents.strategy_conception.strategy_explainer import StrategyReporterAgent

from core.pipelines.strategy_chain_steps import (
    load_alphas,
    build_strategy_block,
    generate_strategy_report
)

from core.utils.io import ensure_dir

# --------------------------------------------------
# 1. Environment
# --------------------------------------------------
load_dotenv()
ROOT_DIR = Path(__file__).resolve().parents[2]

ALPHAS_DIR = ROOT_DIR / "outputs" / "alphas" / "bundles"
STRATEGIES_DIR = ROOT_DIR / "outputs" / "strategies"
ensure_dir(STRATEGIES_DIR)

# --------------------------------------------------
# 2. Agents
# --------------------------------------------------
llm_block = ChatGroq(model="openai/gpt-oss-120b", temperature=0.65)
llm_report = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)

builder = StrategyBuilder(llm_block)
reporter = StrategyReporterAgent(llm_report)

# --------------------------------------------------
# 3. Pipeline
# --------------------------------------------------
strategy_chain = RunnableSequence(
    first=RunnableLambda(lambda _: load_alphas(ALPHAS_DIR)),
    middle=[
        RunnableLambda(lambda inputs: build_strategy_block(builder, inputs, STRATEGIES_DIR)),
    ],
    last=RunnableLambda(lambda inputs: generate_strategy_report(reporter, inputs)),
)

# --------------------------------------------------
# 4. Run pipeline
# --------------------------------------------------
print("\nRunning Strategy Creation Chain...")
final_output = strategy_chain.invoke({})
print("\nPipeline completed successfully.")

print("-" * 60)
print(str(final_output)[:600] + ("..." if len(str(final_output)) > 600 else ""))
