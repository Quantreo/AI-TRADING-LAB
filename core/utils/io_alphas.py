# core/utils/alphas_io.py
from pathlib import Path
from core.utils.io import save_yaml, save_text, slugify, timestamp

def alpha_basename(name: str, with_ts: bool = True) -> str:
    base = slugify(name)
    return f"{base}_{timestamp()}" if with_ts else base

def concept_path(base_dir: Path, basename: str) -> Path:
    return base_dir / "concepts" / f"{basename}.yaml"

def formula_path(base_dir: Path, basename: str) -> Path:
    return base_dir / "formulas" / f"{basename}.yaml"

def bundle_path(base_dir: Path, basename: str) -> Path:
    return base_dir / "bundles" / f"{basename}.yaml"

def code_path(base_dir: Path, basename: str) -> Path:
    return base_dir / "code" / f"{basename}.py"

def refined_code_path(base_dir: Path, basename: str) -> Path:
    return base_dir / "code_refined" / f"{basename}.py"

def save_concept(concept: dict, base_dir: Path, basename: str) -> Path:
    p = concept_path(base_dir, basename); return save_yaml(concept, p)

def save_formula(formula: dict, base_dir: Path, basename: str) -> Path:
    p = formula_path(base_dir, basename); return save_yaml(formula, p)

def save_bundle(bundle: dict, base_dir: Path, basename: str) -> Path:
    p = bundle_path(base_dir, basename);  return save_yaml(bundle, p)

def save_alpha_code(code: str, base_dir: Path, basename: str) -> Path:
    p = code_path(base_dir, basename);    return save_text(code, p)

def save_alpha_code_refined(code: str, base_dir: Path, basename: str) -> Path:
    p = refined_code_path(base_dir, basename); return save_text(code, p)
