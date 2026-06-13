import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

load_dotenv()


def load_synthesis_prompt() -> PromptTemplate:
    """Load research synthesizer prompt from prompts/ folder."""
    prompt_path = (
        Path(__file__).parent.parent / "prompts" / "research_synthesizer.md"
    )

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found at: {prompt_path}"
        )

    template = prompt_path.read_text(encoding="utf-8")

    return PromptTemplate(
        input_variables=["all_summaries"],
        template=template
    )


def build_synthesis_chain():
    """
    Builds and returns the synthesis chain.

    Chain flow:
        PromptTemplate → ChatGroq → StrOutputParser

    Input:
        {"all_summaries": str}  ← aggregated findings/methodology/conclusions from all papers

    Output:
        str  ← unified cross-paper synthesis and analysis
    """
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        raise ValueError(
            "GROK_API_KEY not found. "
            "Make sure it is set in your .env file."
        )

    prompt = load_synthesis_prompt()

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0,
        max_tokens=2048  # Reasonable limit for cross-paper synthesis
    )

    parser = StrOutputParser()

    chain = prompt | llm | parser
    return chain
