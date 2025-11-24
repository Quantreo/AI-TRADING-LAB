# ==========================================================
#  QUANTREO — Alpha Building Steps (pure functions)
#  Ideator -> Formulator -> Combiner -> Coder -> Refiner
# ==========================================================
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import random
import yaml
import datetime

from core.utils.io import ensure_dir, load_yaml, save_yaml
from core.utils.io import slugify, timestamp
from core.utils.io_alphas import (
    save_concept, save_formula, save_bundle,
    save_alpha_code, save_alpha_code_refined,
)

# ----------------------------------------------------------
# 0) Helpers
# ----------------------------------------------------------
def _now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")

def _basename_from_concept(concept: Dict) -> str:
    name = (
        concept.get("alpha_concept", {}) or {}
    ).get("name") or "unnamed_alpha"
    return f"{slugify(name)}_{timestamp()}"

def _load_dsr_subset(dsr_dir: Path, subset_size: int = 8, tag: Optional[str] = None, seed: Optional[int] = None) -> List[Dict]:
    files = sorted(Path(dsr_dir).glob("*.yaml"))
    if not files:
        raise FileNotFoundError(f"No DSR YAMLs found in {dsr_dir}")

    # Optional filtering by tag in YAML content
    if tag is not None:
        filtered = []
        for p in files:
            data = load_yaml(p)
            if data.get("tag") == tag:
                filtered.append((p, data))
        if not filtered:
            raise ValueError(f"No DSR YAMLs matched tag '{tag}' in {dsr_dir}")
        files = [p for p, _ in filtered]

    rng = random.Random(seed)
    subset = rng.sample(files, k=min(subset_size, len(files)))
    return [load_yaml(p) for p in subset]

# ----------------------------------------------------------
# 1) Ideation
# ----------------------------------------------------------
def generate_concept(
    ideator,                   # AlphaIdeatorAgent
    dsr_dir: Path,            # e.g. ROOT/outputs/features_info/dsr
    concept_dir: Path,        # e.g. ROOT/outputs/alphas/<focus>/concepts
    focus: str,
    subset_size: int = 8,
    seed: Optional[int] = None,
) -> Dict:
    """
    Load a subset of DSR YAMLs, call Ideator to produce ONE concept,
    save it under concept_dir and return context dict for next steps.
    """
    ensure_dir(concept_dir)
    dsr_list = _load_dsr_subset(dsr_dir, subset_size=subset_size, seed=seed)

    concepts = ideator.ideate_alpha(dsr_list)
    if not concepts:
        raise RuntimeError("Ideator returned no concept.")

    concept = concepts  # on force 1 concept
    basename = _basename_from_concept(concept)
    concept_path = save_concept(concept, concept_dir.parent, basename)  # parent = base focus dir

    return {
        "focus": focus,
        "basename": basename,
        "concept": concept,
        "concept_path": concept_path,
    }

# ----------------------------------------------------------
# 2) Formulation
# ----------------------------------------------------------
def generate_formula(
    formulator,              # AlphaFormulatorAgent
    context: Dict,
    formula_dir: Path,
) -> Dict:
    """
    Build ONE alpha_formula from the concept, save it with SAME basename.
    """
    ensure_dir(formula_dir)
    concept_path: Path = context["concept_path"]
    concept = load_yaml(concept_path)

    formula_yaml = formulator.formulate_alpha(concept)
    if not formula_yaml:
        raise RuntimeError("Formulator produced no YAML.")

    # enrich meta + save
    formula_yaml.setdefault("meta", {})
    formula_yaml["meta"]["concept_file"] = concept_path.name
    formula_path = save_formula(formula_yaml, formula_dir.parent, context["basename"])

    context.update({
        "formula": formula_yaml,
        "formula_path": formula_path,
    })
    return context

# ----------------------------------------------------------
# 3) Combine (deterministic, no LLM)
# ----------------------------------------------------------
def combine_yaml(
    context: Dict,
    bundle_dir: Path,
) -> Dict:
    """
    Deterministically concatenate concept + formula into one YAML bundle.
    """
    ensure_dir(bundle_dir)
    concept = load_yaml(context["concept_path"])
    formula = load_yaml(context["formula_path"])

    bundle = {
        "alpha_concept": concept.get("alpha_concept", {}),
        "alpha_formula": formula.get("alpha_formula", {}),
        "meta": {
            "combined_at": _now_iso(),
            "concept_file": context["concept_path"].name,
            "formula_file": context["formula_path"].name,
            "focus": (formula.get("meta") or {}).get("focus")
                     or (concept.get("meta") or {}).get("focus")
                     or context.get("focus"),
            "notes": "concept + formula concatenated",
        }
    }
    bundle_path = save_bundle(bundle, bundle_dir.parent, context["basename"])

    context.update({
        "bundle": bundle,
        "bundle_path": bundle_path,
    })
    return context

# ----------------------------------------------------------
# 4) Code generation
# ----------------------------------------------------------
def generate_code(
    coder,                # AlphaCoderAgent
    context: Dict,
    code_dir: Path,
) -> Dict:
    """
    Generate Python code from the formula YAML; save as <basename>.py.
    """
    ensure_dir(code_dir)
    alpha_yaml = load_yaml(context["formula_path"])

    code_str = coder.generate(alpha_yaml)
    if not code_str or not coder.quick_sanity_check(code_str):
        raise RuntimeError("AlphaCoder failed to generate valid code.")

    code_path = save_alpha_code(code_str, code_dir.parent, context["basename"])
    context.update({
        "code_path": code_path,
    })
    return context

# ----------------------------------------------------------
# 5) Code refinement
# ----------------------------------------------------------
def refine_code(
    refiner,              # AlphaCodeRefinerAgent
    context: Dict,
    refined_dir: Path,
) -> Dict:
    """
    Refine the generated code and save as <basename>.py in code_refined/.
    """
    ensure_dir(refined_dir)
    src = Path(context["code_path"]).read_text(encoding="utf-8")

    cleaned = refiner.refine(src)
    if not cleaned:
        raise RuntimeError("AlphaCodeRefiner failed to refine code.")

    refined_path = save_alpha_code_refined(cleaned, refined_dir.parent, context["basename"])
    context.update({
        "refined_code_path": refined_path
    })
    return context