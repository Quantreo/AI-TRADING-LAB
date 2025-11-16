from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import re
import yaml


class FeatureCoderAgent:
    """
    An autonomous agent that transforms a YAML feature specification
    into a fully implemented Python function following Quantreo conventions.

    Parameters
    ----------
    llm : Any
        Any LangChain-compatible LLM object (e.g., ChatGroq, ChatOpenAI, etc.).
    """

    def __init__(self, llm: Any):
        self.llm = llm
        self.prompt_template = self._build_prompt()

    def _build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system",
             "You are a quantitative developer working inside the Quantreo research framework. "
             "You generate deterministic, vectorized Python functions implementing features from OHLCV data. "
             "Follow these conventions strictly:\n"
             "1. Always import dependencies listed in the YAML (e.g., numpy, pandas).\n"
             "2. Define functions with the following conventions:\n"
             "   - The first argument must always be the DataFrame: `df: pd.DataFrame`.\n"
             "   - Then include `window_size: int = ...` only if needed.\n"
             "   - Then include only the columns that are actually used in computation.\n"
             "     When a column is used, name it according to this rule:\n"
             "       * use `col` if the feature applies to any generic column (e.g., entropy, kurtosis)\n"
             "       * use `open_col`, `high_col`, `low_col`, `close_col`, or `volume_col` if the feature uses those specific columns.\n"
             "   - Never include columns that are not used in the calculation.\n"
             "   - Always respect this argument order: `df`, then `window_size` (if used), then the columns.\n"
             "   - Example of correct function signature:\n"
             "       def high_low_range(df: pd.DataFrame,  window_size: int = 20, high_col: str = 'high', low_col: str = 'low') -> pd.Series:\n"
             "         # Compute rolling high-low range\n"
             "         return (df[high_col] - df[low_col]).rolling(window=window_size).mean()\n"
             "   This example shows the expected style and argument ordering, "
             "but only include the parameters that are required for your feature.\n"
             "3. Always assume OHLCV columns exist in df.\n"
             "4. Always return a pd.Series.\n"
             "5. Use numpy/pandas vectorized operations — never loops.\n"
             "6. Always include a short NumPy-style docstring.\n"
             "7. Use the 'implementation_hint' field in YAML as the mathematical basis if provided.\n"
             "8. Add concise, professional in-line comments explaining each major computation step "
             "(e.g., '# Compute rolling volatility ratio').\n"
             "   Comments must be brief and technical — no emojis, no conversational text.\n"
             "9. Do not include examples, print statements, or markdown formatting.\n"
             "10. Output only clean Python code (imports, function, docstring, and minimal inline comments)."),

            ("user",
             "Implement the following feature specification as a Python function:\n\n"
             "{yaml_spec}\n\n"
             "Follow Quantreo conventions strictly. Return only the function code.\n")
        ])

    def generate(self, feature_yaml: Dict[str, Any]) -> Optional[str]:
        """
        Generate Python code implementing a given feature YAML specification.
        Returns the code as a string, or None if invalid.
        """
        # --- 1. Build prompt ---
        yaml_str = yaml.safe_dump(feature_yaml, sort_keys=False)
        messages = self.prompt_template.format_messages(yaml_spec=yaml_str)

        # --- 2. Invoke model ---
        response = self.llm.invoke(messages)
        raw_text = response.content.strip()

        # --- 3. Extract code ---
        match = re.search(r"```(?:python)?\n(.*?)```", raw_text, re.DOTALL)
        code_block = match.group(1).strip() if match else raw_text

        # --- 4. Basic validation ---
        if "def " not in code_block:
            print("❌ No function definition found in model output.")
            return None

        print("✅ Feature code successfully generated.")
        return code_block

    def quick_sanity_check(self, code_str: str) -> bool:
        """
        Try executing the generated code to ensure it defines a callable function.
        This does not run the function — only checks syntax validity.
        """
        try:
            exec(code_str, {})
            print("✅ Code syntax check passed.")
            return True
        except Exception as e:
            print(f"❌ Syntax error in generated code: {e}")
            return False

    def save(self, code_str: str, feature_yaml: Dict[str, Any], output_dir: Path):
        """
        Save the generated Python code to a file.
        The filename is based on the 'idea' field from the YAML spec.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        idea_name = feature_yaml.get("idea", "unknown_feature").lower().replace(" ", "_")
        filename = output_dir / f"{idea_name}.py"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(code_str)

        print(f"💾 Saved feature code to: {filename}")
        return filename