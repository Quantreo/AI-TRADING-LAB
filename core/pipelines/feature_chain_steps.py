from pathlib import Path
from core.utils.io_feature_chain import save_yaml_spec, save_code, save_explanation


def next_feature_dir(base_dir: Path) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    existing = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("Feature_")]
    folder = base_dir / f"Feature_{len(existing) + 1:06d}"
    folder.mkdir(exist_ok=True)
    return folder


def generate_idea(agent, base_dir: Path):
    idea_yaml = agent.generate()
    feature_dir = next_feature_dir(base_dir)
    save_yaml_spec(idea_yaml, feature_dir)
    return {"idea_yaml": idea_yaml, "feature_dir": feature_dir}


def generate_code(agent, inputs):
    idea_yaml = inputs["idea_yaml"]
    feature_dir = inputs["feature_dir"]
    code = agent.generate(idea_yaml)
    return save_code(code, idea_yaml, feature_dir, suffix="raw")


def refine_code(agent, inputs):
    refined = agent.refine(inputs["code"])
    return save_code(refined, inputs["idea_yaml"], inputs["feature_dir"], suffix="refined")


def generate_explanation(agent, inputs):
    refined_code = inputs["code"]
    idea_yaml = inputs["idea_yaml"]
    feature_dir = inputs["feature_dir"]
    explanation = agent.explain(refined_code)
    save_explanation(explanation, idea_yaml, feature_dir)
    return explanation
