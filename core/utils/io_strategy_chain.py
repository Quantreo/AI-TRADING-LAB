# ==========================================================
#  IO HELPERS FOR STRATEGY CHAIN
# ==========================================================
from pathlib import Path
from core.utils.io import ensure_dir, save_yaml, save_text

# --------------------------------------------------
# Incremental folder creator: Strategy_000001, etc.
# --------------------------------------------------
def next_strategy_dir(base_dir: Path) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    existing = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("Strategy_")]
    folder = base_dir / f"Strategy_{len(existing) + 1:06d}"
    folder.mkdir(exist_ok=True)
    return folder

# --------------------------------------------------
# Helpers for naming
# --------------------------------------------------
def strategy_slug(block: dict) -> str:
    name = block.get("strategy", {}).get("name", "unnamed_strategy")
    return name.lower().replace(" ", "_")

# --------------------------------------------------
# Save generated block
# --------------------------------------------------
def save_strategy_block(block_yaml: dict, strategy_dir: Path):
    slug = strategy_slug(block_yaml)
    path = strategy_dir / f"{slug}.yaml"
    save_yaml(block_yaml, path)
    print(f"Saved strategy block to: {path}")
    return path

# --------------------------------------------------
# Save human readable report
# --------------------------------------------------
def save_strategy_report(report_text: str, block_yaml: dict, strategy_dir: Path):
    slug = strategy_slug(block_yaml)
    path = strategy_dir / f"{slug}_report.md"
    save_text(report_text, path)
    print(f"Saved strategy report to: {path}")
    return path
