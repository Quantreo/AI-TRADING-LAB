# agents/feature_creator/refiner.py

from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from typing import Any, Optional
from pathlib import Path
import re


class FeatureCodeRefinerAgent:
    """
    A post-processing agent that reviews and refines Quantreo feature code.

    Responsibilities
    ----------------
    - Remove unused function parameters (e.g. high_col, volume_col).
    - Remove unused imports.
    - Keep NumPy-style docstrings and inline comments.
    - Preserve all used variables and logic.
    - Output clean, deterministic Python code only (no markdown or explanations).
    """

    def __init__(self, llm: Any):
        self.llm = llm
        self.prompt_template = self._build_prompt()

    # ------------------------------------------------------------------
    # Prompt template
    # ------------------------------------------------------------------
    def _build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a senior quantitative software engineer reviewing Python feature code "
                "for the Quantreo framework.\n\n"
                "Your goal is to refine and clean the code **without changing its logic**.\n"
                "Follow these rules strictly:\n"
                "1. Remove unused function parameters (e.g., high_col, low_col, volume_col) if they are never referenced.\n"
                "2. Remove unused imports.\n"
                "3. Keep valid imports (numpy, pandas, etc.) and code comments.\n"
                "4. Preserve function name, core logic.\n"
                "5. Always return valid Python code — no markdown, no text explanations.\n"
                "6. Use Quantreo conventions for arguments: df, window_size (if needed), and only used *_col params.\n"
                "7. Always include a NumPy-style docstring if missing. The docstring must follow the standard structure with short summary, Parameters section, and Returns section."
            ),
            (
                "user",
                "Here is the code to review and clean:\n\n{code}\n\n"
                "Return only the cleaned Python code."
            ),
        ])

    # ------------------------------------------------------------------
    # Core refine method
    # ------------------------------------------------------------------
    def refine(self, code_str: str) -> Optional[str]:
        """
        Ask the LLM to review and simplify the provided feature code.
        """
        messages = self.prompt_template.format_messages(code=code_str)
        response = self.llm.invoke(messages)
        cleaned = response.content.strip()

        # Extract code if fenced (the model might use ```python blocks)
        match = re.search(r"```(?:python)?\n(.*?)```", cleaned, re.DOTALL)
        cleaned_code = match.group(1).strip() if match else cleaned

        if "def " not in cleaned_code:
            print("❌ No valid function definition found after refinement.")
            return None

        print("✅ Code successfully refined by FeatureCodeRefinerAgent.")
        return cleaned_code

    # ------------------------------------------------------------------
    # Save method
    # ------------------------------------------------------------------
    def save(self, code_str: str, feature_name: str, output_dir: Path):
        """
        Save the cleaned code to file with suffix `_refined.py`.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f"{feature_name}.py"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(code_str)

        print(f"💾 Saved refined code to: {filename}")
        return filename
