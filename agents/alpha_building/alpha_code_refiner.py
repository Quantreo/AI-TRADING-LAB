from langchain_core.prompts import ChatPromptTemplate
from typing import Any, Optional
import re

class AlphaCodeRefinerAgent:
    """
    Post-processing agent for Quantreo alpha code.

    Goals
    -----
    - Keep logic identical, but enforce Quantreo conventions.
    - ONE function returning Tuple[pd.Series, pd.Series] = (alpha, condition).
    - NumPy-style docstring is REQUIRED.
    - Helpers must be SERIES-based (ema(x,n), sma(x,n)).
    - Remove unused imports/helpers/parameters.
    - No 'future_' tokens (strip prefix deterministically).
    - No look-ahead (rolling/ewm = past/current only).
    - Output only valid Python code (imports + function), no markdown.
    """

    def __init__(self, llm: Any):
        self.llm = llm
        self.prompt = self._build_prompt()

    # ------------------------------------------------------
    def _build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system",
             "You are a senior quantitative software engineer refining Python code for the Quantreo framework.\n"
             "Refactor WITHOUT changing the algorithmic logic, and output ONLY valid Python code (imports + ONE function).\n\n"
             "Hard rules:\n"
             "1) Function signature must be minimal: df: pd.DataFrame first, then ONLY used parameters.\n"
             "   Prefer: window_ema: int = 20, window_sma: int = 50, eps: float = 1e-12 (if they are used).\n"
             "2) Return EXACTLY Tuple[pd.Series, pd.Series]: (alpha, condition).\n"
             "3) NumPy-style docstring REQUIRED with Parameters / Returns / Notes.\n"
             "4) Helpers MUST be SERIES-based:\n"
             "   - ema(x, n) = x.ewm(span=n, adjust=False).mean()\n"
             "   - sma(x, n) = x.rolling(window=n).mean()\n"
             "   Define ONLY helpers that are actually used by the function.\n"
             "5) Replace any string math passed to helpers (e.g., ema(df,'a*b',n)) with real pandas expressions using Series variables.\n"
             "6) Validate required columns:\n"
             "   required = {{<columns referenced like df['col']>}};\n"
             "   missing = required - set(df.columns); if missing: raise ValueError(...)\n"
             "7) Protect divisions with epsilon: denom.abs().clip(lower=eps)\n"
             "8) No look-ahead: use only rolling/ewm past/current; leave NaNs as-is.\n"
             "9) Imports: keep ONLY what is used. Always `import pandas as pd`; add `from typing import Tuple` if type hints use Tuple; add `import numpy as np` only if np.* is used.\n"
             "10) Remove any 'future_' tokens everywhere (strip the prefix deterministically).\n"
             "11) Remove unused imports, helpers and function parameters.\n"
             "12) Do not add any comments or text outside the code."),
            ("user",
             "Here is the code to clean and standardize:\n\n{code}\n\n"
             "Return only the cleaned Python code (imports + one function).")
        ])

    # ------------------------------------------------------
    def refine(self, code: str) -> Optional[str]:
        # Pre-sanitize obvious leakage tokens deterministically
        code = code.replace("future_", "")

        msgs = self.prompt.format_messages(code=code)
        resp = self.llm.invoke(msgs)
        cleaned = resp.content.strip()

        # Strip ``` fences if present
        m = re.search(r"```(?:python)?\n(.*?)```", cleaned, re.DOTALL)
        out = m.group(1).strip() if m else cleaned

        # Deterministic hygiene pass (small but useful)
        out = self._deterministic_hygiene(out)

        if "def " not in out or "pd.DataFrame" not in out:
            print("❌ No valid function after refinement.")
            return None
        return out

    # ------------------------------------------------------
    def _deterministic_hygiene(self, code: str) -> str:
        """Small deterministic cleanups after LLM refinement."""
        # Ensure pandas import
        if "import pandas as pd" not in code:
            code = "import pandas as pd\n" + code

        # Drop numpy import if unused
        if "import numpy as np" in code and "np." not in code:
            code = code.replace("import numpy as np\n", "")
            code = code.replace("import numpy as np\r\n", "")

        # Ensure typing Tuple import if used
        if ("Tuple[" in code or "-> Tuple[" in code) and "from typing import Tuple" not in code:
            code = "from typing import Tuple\n" + code

        # Remove typing Tuple import if not used
        if "from typing import Tuple" in code and "Tuple[" not in code and "-> Tuple[" not in code:
            code = code.replace("from typing import Tuple\n", "")

        # Remove completely unused helpers std/rank/zscore if they remain
        for helper in ["std", "rank", "zscore"]:
            code = self._drop_helper_if_unused(code, helper)

        # Collapse excessive blank lines
        code = re.sub(r"\n{3,}", "\n\n", code)

        # Final guard: strip any residual 'future_' (if LLM reintroduced it)
        code = code.replace("future_", "")

        return code

    def _drop_helper_if_unused(self, code: str, name: str) -> str:
        # crude but effective: if helper defined and not called, drop its def block
        pat_def = rf"(\n|^)def {name}\(.*?\):\n(?:\s+.*\n)+"
        if re.search(pat_def, code, flags=re.DOTALL) and not re.search(rf"\b" + name + r"\(", code.split(f"def {name}")[1]):
            code = re.sub(pat_def, "\n", code, flags=re.DOTALL)
        return code
