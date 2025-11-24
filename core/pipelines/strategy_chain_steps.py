# ==========================================================
#  STRATEGY BUILDING CHAIN STEPS
# ==========================================================
from pathlib import Path
import yaml
import random

from core.utils.io_strategy_chain import (
    next_strategy_dir,
    save_strategy_block,
    save_strategy_report
)

# --------------------------------------------------
# 1. Load alphas (pure function, not an agent)
# --------------------------------------------------
def load_alphas(input_dir: Path, subset_size: int = 10):
    yaml_files = list(input_dir.glob("*.yaml"))
    if not yaml_files:
        raise FileNotFoundError(f"No alpha YAMLs found in {input_dir}")

    subset_size = min(subset_size, len(yaml_files))
    subset = random.sample(yaml_files, k=subset_size)

    alphas = []
    for file in subset:
        with open(file, "r", encoding="utf-8") as fp:
            alphas.append(yaml.safe_load(fp))

    print(f"Loaded {len(alphas)} alpha files.")
    return {"alphas": alphas}

# --------------------------------------------------
# 2. StrategyBuilder agent step
# --------------------------------------------------
def build_strategy_block(agent, inputs, base_dir: Path):
    alphas = inputs["alphas"]

    # Generate strategy YAML
    block_yaml = agent.build_strategy(alphas)

    # Create Strategy_X folder
    strategy_dir = next_strategy_dir(base_dir)

    # Save YAML
    save_strategy_block(block_yaml, strategy_dir)

    return {
        "block_yaml": block_yaml,
        "strategy_dir": strategy_dir
    }

# --------------------------------------------------
# 3. StrategyReporterAgent step
# --------------------------------------------------
def generate_strategy_report(agent, inputs):
    block_yaml = inputs["block_yaml"]
    strategy_dir = inputs["strategy_dir"]

    # Create markdown report
    report_text = agent.explain(block_yaml)

    # Save markdown
    save_strategy_report(report_text, block_yaml, strategy_dir)

    return {
        "report_text": report_text,
        "block_yaml": block_yaml,
        "strategy_dir": strategy_dir
    }
