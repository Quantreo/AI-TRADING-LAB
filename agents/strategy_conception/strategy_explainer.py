from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
from typing import Any, Optional
import re
import yaml


class StrategyReporterAgent:
    """
    Generates a clean Markdown report for a Quantreo strategy YAML.

    Responsibilities
    ----------------
    - Read and interpret a strategy YAML block.
    - Produce a human readable report describing the logic behind each component.
    - Explain long and short entries, exit conditions, and position sizing.
    - Provide an intuitive understanding of what the strategy tries to exploit.
    - Output a clean Markdown document (no code fences, no extra explanations).
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
                "You are a senior quantitative researcher preparing a polished internal report for a portfolio manager. "
                "Your task is to transform a strategy YAML into a clear and visually structured Markdown document. "
                "The tone must be analytical, concise, and highly readable.\n\n"

                "Follow this structure exactly, with the visual format preserved:\n\n"

                "# Strategy Overview\n"
                "**Objective:** One short paragraph that states the strategy goal, the market behavior it seeks to exploit, and "
                "the core idea behind its construction.\n\n"
                "**In one sentence:** Provide a single intuitive summary of how the strategy makes money.\n\n"
                "**Core signal logic:** Present a short bullet list of the key building blocks. "
                "Use inline code for formulas.\n"
                "- Example: `trend_slope > 0` or `volatility_filter < threshold`.\n\n"
                "**Quick interpretation:** A short list that highlights what conditions activate longs, shorts, and risk controls. "
                "This allows the PM to grasp the structure instantly before reading deeper sections.\n\n"
                "---\n\n"

                "# Long Entry Logic\n"
                "**Intuition:** Explain the economic or behavioral reasoning behind the long entry.\n\n"
                "**Conditions explained:** Provide a bullet list translating each part of the expression into simple terms.\n"
                "**Mathematical form:** A clean inline version of the rule using backticks.\n\n"
                "**Why it works:** One or two sentences on why these conditions historically support trend continuation or signal reliability.\n\n"
                "---\n\n"

                "# Short Entry Logic\n"
                "Follow the same structure as the long entry. Clarify symmetry or deliberate asymmetry. "
                "Explain what market environment activates shorts and why.\n\n"
                "---\n\n"

                "# Exit Logic\n"
                "**Purpose:** Describe the rationale behind the exit framework.\n\n"
                "**Components:** Bullet points explaining time based limit, stop loss, take profit, or other exit drivers.\n\n"
                "**Mathematical rule:** Provide the combined logical expression in inline code.\n\n"
                "**Lifecycle:** Describe how these exits shape typical trade duration and risk containment.\n\n"
                "---\n\n"

                "# Position Sizing\n"
                "**Rule:** Present the sizing expression in inline code.\n\n"
                "**Intuition:** Explain how volatility scaling modulates exposure.\n\n"
                "**Practical effect:** Describe how the position size reacts in high and low volatility regimes.\n\n"
                "---\n\n"

                "# Expected Behavior and Regime Sensitivity\n"
                "**Favorable regimes:** Bullet list of market conditions where the strategy should perform well.\n"
                "**Challenging regimes:** Bullet list of conditions that degrade performance.\n"
                "**Insight:** Mention one insight on volatility clustering or entropy dynamics to show deep understanding.\n\n"
                "---\n\n"

                "# Factor Style Interpretation\n"
                "**Primary exposure:** Identify the main style factor.\n"
                "**Secondary exposures:** Mention volatility, convexity, or other implicit loadings.\n"
                "**Interpretation:** Explain in simple terms how the strategy interacts with well known risk premia.\n\n"
                "---\n\n"

                "# Expected Trade Profile\n"
                "**Holding time:** Expected duration based on rules.\n"
                "**Drawdown pattern:** Expected behavior during adverse regimes.\n"
                "**Filter activity:** How often volatility conditions are likely to block signals.\n\n"
                "---\n\n"

                "# Risk Diagnostics\n"
                "**Sensitivity:** Noise, regime shifts, slippage vulnerability.\n"
                "**Structural risks:** Market conditions that can systematically hurt the strategy.\n\n"
                "---\n\n"

                "# Assumptions and Limitations\n"
                "List the structural assumptions that support the strategy and the main limitations that must be monitored.\n\n"
                "---\n\n"

                "# Source Alphas\n"
                "Provide a concise explanation of how each alpha supports specific components of the strategy.\n\n"

                "Formatting rules:\n"
                "- Output pure Markdown.\n"
                "- No code fences.\n"
                "- Use bold headers inside sections as specified.\n"
                "- Use inline code formatting for all formulas.\n"
                "- Do not invent variables or indicators that are not present in the YAML.\n"
                "- No em dash under any circumstances.\n"
            ),
            (
                "user",
                "Here is the strategy YAML:\n\n{yaml_text}\n\n"
                "Write the complete Markdown report following the required structure and formatting."
            ),
        ])

    # ------------------------------------------------------------------
    # Main generation method
    # ------------------------------------------------------------------
    def explain(self, strategy_yaml: dict) -> Optional[str]:
        """
        Generate a clean Markdown explanation for a given strategy YAML dict.
        """
        yaml_text = yaml.safe_dump(strategy_yaml, sort_keys=False)
        response = self.llm.invoke(
            self.prompt_template.format_messages(yaml_text=yaml_text)
        )
        text = response.content.strip()

        # Remove any accidental code fences
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL).strip()

        if len(text) < 80:
            print("❌ Explanation too short or invalid.")
            return None

        print("✅ Strategy Markdown report generated.")
        return text

    # ------------------------------------------------------------------
    # Save method
    # ------------------------------------------------------------------
    def save(self, explanation: str, strategy_name: str, output_dir: Path):
        """
        Save the strategy explanation to a Markdown file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / f"{strategy_name}.md"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(explanation)

        print(f"💾 Saved strategy report to: {file_path}")
        return file_path
