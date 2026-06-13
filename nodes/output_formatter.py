def output_formatter(state: dict) -> dict:
    """
    Node: shape the final JSON response that FastAPI returns.
    Generates paper-wise summaries and comparison table.
    No synthesis step - just formatting extracted data.
    """
    paper_summaries = state.get("paper_summaries", [])
    
    # Build individual summaries reference
    individual_summaries = []
    for summary in paper_summaries:
        individual_summaries.append({
            "paper": summary["name"],
            "key_findings": summary["findings"],
            "methodology": summary["methodology"],
            "conclusions": summary["conclusions"],
        })
    
    # Generate comparison table as markdown
    comparison_table = _generate_comparison_table(paper_summaries)
    
    final_response = {
        "mode": "research_summarizer",
        "papers_analyzed": state.get("papers_count", 0),
        "paper_titles": [s["name"] for s in paper_summaries],
        "individual_summaries": individual_summaries,
        "comparison_table": comparison_table,
        "status": "success",
    }

    return {
        **state,
        "final_response": final_response,
    }


def _generate_comparison_table(paper_summaries: list) -> str:
    """
    Generate a structured format with bullet points (no paragraphs).
    Only spacing between papers.
    """
    if not paper_summaries:
        return "No papers to analyze"
    
    output = []
    output.append("RESEARCH PAPERS ANALYSIS")
    output.append("=" * 80)
    
    # Process each paper
    for idx, summary in enumerate(paper_summaries, 1):
        paper_name = summary["name"]
        
        # Paper header - BOLD
        output.append("")
        output.append(f"**PAPER {idx}: {paper_name}**")
        output.append("─" * 80)
        
        # Key Findings - BOLD with bullet points
        output.append("**KEY FINDINGS:**")
        findings = summary["findings"] if summary["findings"] else "(No findings extracted)"
        for point in findings.split('\n'):
            point = point.strip()
            if point:
                output.append(f"• {point}")
        
        # Methodology - BOLD with bullet points
        output.append("**METHODOLOGY:**")
        methodology = summary["methodology"] if summary["methodology"] else "(No methodology extracted)"
        for point in methodology.split('\n'):
            point = point.strip()
            if point:
                output.append(f"• {point}")
        
        # Conclusions - BOLD with bullet points
        output.append("**CONCLUSIONS:**")
        conclusions = summary["conclusions"] if summary["conclusions"] else "(No conclusions extracted)"
        for point in conclusions.split('\n'):
            point = point.strip()
            if point:
                output.append(f"• {point}")
    
    return "\n".join(output)