# core/utils/io.py
from pathlib import Path
import yaml, re, datetime

# ---------- Helpers génériques ----------
def ensure_dir(p: Path) -> None:
    Path(p).mkdir(parents=True, exist_ok=True)

def slugify(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", (name or "unnamed")).strip("_").lower()

def timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# ---------- YAML / TEXT ----------
def load_yaml(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def save_yaml(data: dict, path: Path) -> Path:
    ensure_dir(path.parent)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path

def save_text(text: str, path: Path) -> Path:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")
    return path
