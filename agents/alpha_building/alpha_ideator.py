# ==========================================================
#  ALPHA IDEATOR AGENT
# ==========================================================
from langchain_core.prompts import ChatPromptTemplate
from typing import Any, Dict, List, Optional
from pathlib import Path
import yaml
import re
import datetime


class AlphaIdeatorAgent:
    """
    Agent - Alpha Ideator Agent
    ---------------------------------
    Reads one or more DSR (Definition–Stability–Robustness) YAMLs
    describing statistical relationships between features and targets,
    and generates economically justified ALPHA CONCEPTS using the PCP rule:
        - Who loses?
        - What behavioral bias sustains it?
        - Why does it persist?

    This agent does NOT generate formulas.
    It focuses on ideation: defining the hypothesis, economic rationale,
    and intended market behavior.
    """

    def __init__(self, llm: Any, focus: str):
        """
        Initialize the Alpha Ideator Agent.

        Args:
            llm: The language model used for alpha concept generation.
            focus: The specific area of interest (e.g., trend, volatility, regime, filter).
        """
        self.focus = focus or "the category of your choice"
        self.llm = llm
        self.prompt_template = self._build_prompt()

    # ------------------------------------------------------------------
    def _build_prompt(self) -> ChatPromptTemplate:
        """
        Build the LangChain prompt for generating economically justified alpha concepts.

        Returns:
            ChatPromptTemplate: The compiled LangChain prompt.
        """
        return ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a senior quantitative researcher specializing in systematic trading. "
                "You are given a set of DSR (Definition–Stability–Robustness) YAMLs describing "
                "relationships between explanatory features and predictive targets (usually prefixed with 'future_').\n\n"
                "Your task is to extract ONE alpha *concepts* that are economically meaningful and "
                "can later be transformed into tradable formulas by another agent.\n\n"
                "Each concept must include:\n"
                "- A short, descriptive name.\n"
                "- A clear hypothesis summarizing what the alpha tries to capture.\n"
                "- A behavioral/economic justification using the LBP rule:\n"
                "  1) Who loses? — which market participants are structurally on the losing side.\n"
                "  2) Behavioral bias — which human or institutional bias maintains this inefficiency.\n"
                "  3) Persistence — why it continues to exist (regulation, latency, liquidity, structure).\n"
                "- The type of alpha expected (signal, filter, regime_indicator, risk, sizing).\n"
                "- The main features involved and their expected behavior (e.g., trend, mean reversion, volatility).\n"
                "- A short operational comment that describes how this could be useful in practice.\n\n"
                f"Your current focus is **{self.focus}**.\n\n"
                "Guidelines:\n"
                "- Stay realistic: base your reasoning on the statistical evidence from the DSRs, not wishful thinking.\n"
                "- Be specific about the market mechanism or behavior implied.\n"
                "- Do NOT propose formulas, only conceptual structures.\n"
                "- Use clear YAML syntax, no markdown.\n\n"
                " Hard constraint: never reference features starting with future_. If such features appear in inputs, drop the prefix and treat them as ex-ante equivalents in related_features."
                "Output strictly valid YAML in the following format:\n\n"
                "alpha_concept:\n"
                "  name: <short descriptive name>\n"
                "  hypothesis: <economic or behavioral hypothesis>\n"
                "  expected_role: <signal | filter | regime_indicator | risk | position_sizing>\n"
                "  target_behavior: <expected market behavior: trend, mean_reversion, volatility, etc.>\n"
                "  related_features: [<list of key features>]\n"
                "  lbp:\n"
                "    who_loses: <description>\n"
                "    behavioral_bias: <description>\n"
                "    persistence_reason: <description>\n"

            ),
            (
                "user",
                "Here are the DSR YAMLs:\n\n{dsr_yamls}\n\n"
                "Analyze them collectively and generate one alpha_concept YAML blocks "
                "according to the structure above. Do not include markdown or explanations."
            )
        ])


    def ideate_alpha(self, dsr_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Generate one alpha concept from the DSR list.
        Returns a single alpha concept dict or None.
        """
        yaml_str = "\n\n---\n\n".join(
            yaml.safe_dump(f, sort_keys=False) for f in dsr_list
        )
        messages = self.prompt_template.format_messages(dsr_yamls=yaml_str)
        response = self.llm.invoke(messages)
        raw_output = response.content.strip()

        cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", raw_output)
        cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            parsed = yaml.safe_load(cleaned)

            # If model returns several blocks, take only the first
            if isinstance(parsed, list):
                parsed = parsed[0]

            if not isinstance(parsed, dict):
                raise ValueError("Alpha concept is not a valid YAML dict.")

            print("[INFO] Generated one alpha concept.")
            return parsed

        except Exception as e:
            print(f"[ERROR] Failed to parse YAML: {e}")
            debug_path = Path("debug_alpha_ideator_output.yaml")
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(raw_output)
            print(f"[DEBUG] Raw model output saved to {debug_path.resolve()}")
            return None

        # ------------------------------------------------------------------

    def save(self, alpha: Dict[str, Any], output_dir: Path):
        """
        Save the single alpha concept to one YAML file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        name = alpha.get("alpha_concept", {}).get("name", "unnamed_concept").replace(" ", "_")
        out_path = output_dir / f"{name}_{timestamp}.yaml"

        with open(out_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(alpha, f, sort_keys=False)

        print(f"[SAVE] Alpha concept saved to: {out_path}")