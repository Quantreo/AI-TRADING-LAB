# agents/feature_creator/explainer.py

from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
from typing import Any, Optional
import re


class FeatureExplainerAgent:
    """
    Generates a human-readable explanation of a Quantreo feature function.

    Responsibilities
    ----------------
    - Read the feature's final Python code.
    - Summarize what the feature does, in simple, human-understandable terms.
    - Explain when and why this feature might be useful in trading.
    - Mention its inputs, parameters, and intuitive interpretation.
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
                "You are a quantitative researcher and educator. "
                "Your goal is to explain complex trading features to humans in a clear, intuitive way.\n\n"
                "When analyzing the following Python function, produce a concise, professional explanation for a reader. "
                "Use this structure:\n"
                "- **Purpose:** one-sentence summary of what the feature measures.\n"
                "- **How it works:** explain the key computation steps in simple words.\n"
                "- **Inputs & Parameters:** list the required inputs and what they mean.\n"
                "- **Use case:** when or why a trader might use this feature.\n"
                "- **Interpretation:** how to read high/low values intuitively.\n\n"
                "Output only a clean Markdown text (no code fences, no explanations of your reasoning)."
            ),
            (
                "user",
                "Here is the Quantreo feature code:\n\n{code}\n\n"
                "Write the human-readable explanation as described above."
            ),
        ])

    # ------------------------------------------------------------------
    # Main generation method
    # ------------------------------------------------------------------
    def explain(self, code_str: str) -> Optional[str]:
        """
        Generate a human-readable explanation for a given feature code.
        """
        response = self.llm.invoke(self.prompt_template.format_messages(code=code_str))
        text = response.content.strip()

        # Clean up (remove any Markdown fences if present)
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL).strip()

        if len(text) < 50:
            print("❌ Explanation too short or invalid.")
            return None

        print("✅ Human-readable feature explanation generated.")
        return text

    # ------------------------------------------------------------------
    # Save method
    # ------------------------------------------------------------------
    def save(self, explanation: str, feature_name: str, output_dir: Path):
        """
        Save the explanation to a Markdown file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / f"{feature_name}.md"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(explanation)

        print(f"💾 Saved human-readable explanation to: {file_path}")
        return file_path
