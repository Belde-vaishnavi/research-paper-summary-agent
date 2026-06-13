from typing import TypedDict, Optional

class AgentState(TypedDict):
    # ── Input ──────────────────────────────
    zip_path: str
    mode: str                        # "research_summarizer"

    # ── After doc_loader ───────────────────
    pdf_files: list                  # list of {"name": str, "text": str}
    papers_count: int

    # ── After preprocessor ─────────────────
    paper_summaries: list            # list of {"name": str, "findings": str, "methodology": str, "conclusions": str}
    cleaned_context: str             # aggregated paper analyses (unused now)

    # ── After output_formatter ─────────────
    final_response: dict
