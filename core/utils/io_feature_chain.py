from core.utils.io import save_yaml
from pathlib import Path

def save_yaml_spec(idea_yaml, feature_dir: Path):
    name = idea_yaml.get("idea", "unknown_feature").lower().replace(" ", "_")
    path = feature_dir / f"feat_{name}.yml"
    save_yaml(idea_yaml, path)
    print(f"Saved YAML to: {path}")
    return idea_yaml

def save_code(code: str, idea_yaml: dict, feature_dir: Path, suffix: str):
    name = idea_yaml.get("idea", "unknown_feature").lower().replace(" ", "_")
    path = feature_dir / f"feat_{name}_{suffix}.py"
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Saved {suffix} code to: {path}")
    return {"code": code, "idea_yaml": idea_yaml, "feature_dir": feature_dir}

def save_explanation(text: str, idea_yaml: dict, feature_dir: Path):
    name = idea_yaml.get("idea", "unknown_feature").lower().replace(" ", "_")
    path = feature_dir / f"feat_{name}_explanation.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved explanation to: {path}")
    return text
