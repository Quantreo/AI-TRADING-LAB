# ==========================================================
#  ALPHA CODER AGENT
# ==========================================================
from langchain_core.prompts import ChatPromptTemplate
from typing import Any, Dict, Optional
from pathlib import Path
import re
import yaml


class AlphaCoderAgent:
    """
    An autonomous agent that transforms an alpha YAML specification
    into a deterministic, vectorized Python function returning two
    pd.Series: (alpha, condition), with NO look-ahead.

    Parameters
    ----------
    llm : Any
        Any LangChain-compatible LLM object (e.g., ChatGroq).
    """

    def __init__(self, llm: Any):
        self.llm = llm
        self.prompt_template = self._build_prompt()

    # ------------------------------------------------------------------
    def _build_prompt(self) -> ChatPromptTemplate:
        """
        Build the prompt that turns an alpha YAML (alpha_formula + conditioning)
        into clean Python code following Quantreo conventions.
        """
        return ChatPromptTemplate.from_messages([
            ("system",
             "You are a quantitative developer inside the Quantreo framework. "
             "Output ONLY valid Python code (imports + exactly one function), nothing else.\n\n"
             "HARD CONSTRAINTS:\n"
             "1) The input `df` is a FEATURE STORE that already contains every feature column referenced by the YAML "
             "(e.g., tail_returns_200, rs_vol_200, rs_vol_120). Do NOT recompute features from raw data "
             "(no rolling quantiles/std on `returns`, no OHLCV derivations). Only read df['<feature>'] and apply light "
             "transforms explicitly required by the formula.\n"
             "2) Use ONLY columns referenced by the YAML: first prefer `alpha_formula.used_features`; "
             "if absent, derive the identifiers from `formula` and `conditioning` by excluding function names. "
             "Build a Python set named `required` with exactly these names. At runtime, if any are missing in df.columns, "
             "raise ValueError listing the sorted missing names. Do not attempt to reconstruct missing features.\n"
             "3) Return exactly TWO pd.Series: (alpha, condition). If YAML conditioning is null, return a boolean Series "
             "of True aligned to df.index.\n"
             "4) Absolutely NO look-ahead. Leave NaNs from rolling/EMA as-is (no fillna or forward-fill).\n"
             "5) Fully vectorized numpy/pandas only. Do not use loops. Do not use DataFrame.apply over rows. "
             "Do not use Rolling.apply with lambdas.\n"
             "6) Allowed transforms must be applied via small SERIES-based helpers only (define only what you use): "
             "sma(x, n) = x.rolling(window=n).mean(); ema(x, n) = x.ewm(span=n, adjust=False).mean(); "
             "std(x, n); zscore(x, n); rank(x, n); abs(x); clip(x, lo, hi); lag(x, n). "
             "Do NOT call .rolling(...) or .ewm(...) directly in the main body; only inside helpers.\n"
             "7) Function signature must be MINIMAL: df: pd.DataFrame first, then only hyperparameters actually used "
             "(e.g., ema_window, sma_window, eps=1e-12). Do NOT invent parameters mirroring feature windows "
             "(e.g., tail_returns_window); feature windows are already encoded in the column names.\n"
             "8) Imports at the top and only if used: always `import pandas as pd`; add `from typing import Tuple` if you "
             "use Tuple in type hints; add `import numpy as np` only if you call np.*. Do not import unused names.\n"
             "Always put at the top: from typing import Tuple.\n"
             "9) Never reference tokens starting with `future_`. If such tokens appear in YAML, treat them as their "
             "ex-ante equivalents (strip the prefix).\n"
             "10) NumPy-style docstring is REQUIRED. It must clearly state that the function uses precomputed feature "
             "columns from df (feature store) and does not recompute them.\n"),
            ("user",
             "Implement the following alpha specification as a Python function:\n\n"
             "{yaml_spec}\n\n"
             "Output ONLY the Python code (imports + function). No markdown.")
        ])

    # ------------------------------------------------------------------
    def generate(self, alpha_yaml: Dict[str, Any]) -> Optional[str]:
        """
        Generate Python code implementing the given alpha YAML specification.
        Returns the code as a string, or None if invalid.
        """
        # Strip any 'future_' prefixes deterministically in the input YAML text
        yaml_str = yaml.safe_dump(alpha_yaml, sort_keys=False)
        yaml_str = yaml_str.replace("future_", "")

        messages = self.prompt_template.format_messages(yaml_spec=yaml_str)
        response = self.llm.invoke(messages)
        raw_text = response.content.strip()

        # Extract code from possible fenced blocks; otherwise take the whole text
        match = re.search(r"```(?:python)?\n(.*?)```", raw_text, re.DOTALL)
        code_block = match.group(1).strip() if match else raw_text

        if "def " not in code_block:
            print("❌ No function definition found in model output.")
            return None

        print("✅ Alpha code successfully generated.")
        return code_block

    # ------------------------------------------------------------------
    def quick_sanity_check(self, code_str: str) -> bool:
        """
        Exec the generated code to ensure it defines a callable function.
        Does not run the function — only checks syntax validity.
        """
        try:
            ns: Dict[str, Any] = {}
            exec(code_str, ns)
            funcs = [k for k, v in ns.items() if callable(v) and k.startswith("alpha_")]
            if not funcs:
                # allow generic name if alpha_<slug> not used
                funcs = [k for k, v in ns.items() if callable(v)]
            assert len(funcs) >= 1
            print("✅ Code syntax check passed.")
            return True
        except Exception as e:
            print(f"❌ Syntax error in generated code: {e}")
            return False

    # ------------------------------------------------------------------
    def save(self, code_str: str, alpha_yaml: Dict[str, Any], output_dir: Path) -> Path:
        """
        Save the generated Python code to a file.
        The filename is based on the 'alpha_formula.name' field from the YAML spec.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        name = (
            alpha_yaml.get("alpha_formula", {}).get("name")
            or alpha_yaml.get("meta", {}).get("concept_name")
            or "unnamed_alpha"
        )
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", name).strip("_").lower()
        filepath = output_dir / f"{slug}.py"
        filepath.write_text(code_str, encoding="utf-8")
        print(f"💾 Saved alpha code to: {filepath}")
        return filepath
