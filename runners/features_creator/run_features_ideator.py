from agents.feature_creator.ideator import FeatureIdeatorAgent
from langchain_groq import ChatGroq
from core.utils.io import save_yaml, ensure_dir
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------
load_dotenv()

# Root and output directories
ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT_DIR / "outputs" / "tests" / "features" / "ideator"
ensure_dir(OUTPUT_DIR)

# ---------------------------------------------------------------------
# LLM initialization
# ---------------------------------------------------------------------
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.75)

# ---------------------------------------------------------------------
# Agent instantiation and feature generation
# ---------------------------------------------------------------------
agent = FeatureIdeatorAgent(llm, focus="trend indicator")
feature = agent.generate()

# ---------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------
if feature:
    agent.save(feature, OUTPUT_DIR)
else:
    print("❌ No feature generated.")