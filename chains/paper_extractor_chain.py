import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

load_dotenv()


def load_paper_extractor_prompt() -> PromptTemplate:
    """Load paper extractor prompt from prompts/ folder."""
    prompt_path = (
        Path(__file__).parent.parent / "prompts" / "paper_extractor.md"
    )

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found at: {prompt_path}"
        )

    template = prompt_path.read_text(encoding="utf-8")

    return PromptTemplate(
        input_variables=["paper_text"],
        template=template
    )


def build_paper_extractor_chain():
    """
    Builds and returns the paper extractor chain.

    Chain flow:
        PromptTemplate → ChatGroq → StrOutputParser

    Input:
        {"paper_text": str}  ← full text extracted from PDF

    Output:
        str  ← structured extraction with Key Findings, Methodology, Conclusions
    """
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        raise ValueError(
            "GROK_API_KEY not found. "
            "Make sure it is set in your .env file."
        )

    prompt = load_paper_extractor_prompt()

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0,
        max_tokens=800  # Reduced for concise extraction, avoid token limit errors
    )

    parser = StrOutputParser()

    chain = prompt | llm | parser
    return chain
