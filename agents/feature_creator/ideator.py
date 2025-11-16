from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import yaml
import re
from typing import Any, Dict, Optional
from pathlib import Path


class FeatureIdeatorAgent:
    """
    An autonomous agent that generates new trading feature ideas
    and returns them as structured YAML.

    Parameters
    ----------
    llm : Any
        Any LangChain-compatible LLM object (e.g. ChatGroq, ChatOpenAI, etc.).
    focus : str, optional
        Theme or domain focus for idea generation (e.g. "volume-based indicators").
    """

    REQUIRED_KEYS = {"idea", "family", "dependencies", "parameters", "description"}

    def __init__(self, llm: Any, focus: Optional[str] = None):
        self.llm = llm
        self.focus = focus or "the trading features category of your choice"
        self.prompt_template = self._build_prompt()

    def _build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a quantitative engineer specialized in feature engineering for trading. "
                "Always respond only with a valid YAML document. No markdown, no explanations, no code fences. "
                "Use the Quantreo YAML specification format described below:\n\n"
                "Required YAML fields:\n"
                "idea: <short descriptive feature name, lowercase with underscores>\n"
                "family: <broad category such as volatility, momentum, microstructure, etc.>\n"
                "dependencies: [<Python libraries required>]\n"
                "description: >\n"
                "  <brief multi-line description explaining what the feature measures and why it might be useful>\n"
                "inputs: [<list of columns required from OHLCV data>]\n"
                "parameters:\n"
                "  <parameter_name>: <default_value>\n"
                "output:\n"
                "  name: <output name of the feature>\n"
                "  type: <expected Python type, e.g. pd.Series>\n"
                "  description: <short explanation of the returned value>\n"
                "mathematical_formula: >\n"
                "  <describe the formula or computation logic in readable math notation>\n"
                "implementation_hint: |\n"
                "  1. Step-by-step algorithmic description of how to compute the feature\n"
                "  2. Use clear pseudo-code, not actual Python\n"
                "  3. Example: 'Compute returns = df[close_col].pct_change()'\n"
            ),
            (
                "user",
                "Propose one new, exploitable, and logically coherent feature based on OHLCV data.\n\n"
                f"Focus your idea on {self.focus}.\n\n"
                "Return only a single YAML document following the Quantreo format described above.\n\n"
                "Important instructions for the 'inputs' field:\n"
                "- Include **only** the OHLCV columns that are actually required for the computation, "
                "based on the operations you describe in 'implementation_hint'.\n"
                "- If a column is not explicitly used (e.g., volume, open, high, low, close), do not include it.\n"
                "- For features that can apply to any column (e.g., entropy, kurtosis), include only one generic input 'col'.\n"
                "- Always keep 'inputs' minimal and precise."
            ),
        ])

    def _validate_yaml(self, idea_yaml: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure the generated YAML contains all mandatory fields.
        Raises a ValueError if any required field is missing.
        """
        missing = self.REQUIRED_KEYS - idea_yaml.keys()
        if missing:
            raise ValueError(f"Missing YAML fields: {missing}")
        return idea_yaml

    def generate(self) -> Dict[str, Any]:
        """
        Generate a new feature idea based on the current focus.
        The feature is validated (YAML structure) and checked for logical coherence.
        If the sanity check fails, the agent retries once.
        """
        # --- 1. Generation ---
        messages = self.prompt_template.format_messages()
        response = self.llm.invoke(messages)
        raw_text = response.content.strip()

        # --- 2. Extract YAML block ---
        match = re.search(r"```(?:yml|yaml)?\n(.*?)```", raw_text, re.DOTALL)
        yaml_block = match.group(1).strip() if match else raw_text

        # --- 3. Parse and validate YAML ---
        idea_yaml = yaml.safe_load(yaml_block)
        idea_yaml = self._validate_yaml(idea_yaml)

        # --- 4. Add metadata and return ---
        idea_yaml["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        idea_yaml["focus"] = self.focus

        return idea_yaml

    def save(self, idea_yaml: Dict[str, Any], output_dir: Path) -> Path:
        """
        Save the generated feature idea as a YAML file.

        Parameters
        ----------
        idea_yaml : dict
            The feature idea generated by the agent.
        output_dir : Path
            Directory where the YAML file should be saved.

        Returns
        -------
        Path
            Path to the saved YAML file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        idea_name = idea_yaml.get("idea", "unknown_feature").lower().replace(" ", "_")
        file_path = output_dir / f"{idea_name}.yaml"

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(idea_yaml, f, sort_keys=False, allow_unicode=True)

        print(f"💾 Saved feature idea YAML to: {file_path}")
        return file_path