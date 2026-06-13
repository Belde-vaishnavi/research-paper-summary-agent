import re
from chains.paper_extractor_chain import build_paper_extractor_chain


def chunk_text(text: str, chunk_size_chars: int = 6000) -> list[str]:
    """
    Split text into non-overlapping chunks to avoid exceeding token limits.
    
    Args:
        text: The full text to chunk
        chunk_size_chars: Number of characters per chunk (roughly 1500 tokens)
    
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size_chars:
        return [text]
    
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+chunk_size_chars]
        chunks.append(chunk)
        i += chunk_size_chars
    
    return chunks


def parse_extracted_sections(extracted_text: str) -> dict:
    """Parse the structured extraction output into sections."""
    sections = {
        "findings": "",
        "methodology": "",
        "conclusions": ""
    }
    
    # Extract Key Findings section
    findings_match = re.search(r"## Key Findings\n(.*?)(?=## Methodology|$)", extracted_text, re.DOTALL)
    if findings_match:
        sections["findings"] = findings_match.group(1).strip()
    
    # Extract Methodology section
    methodology_match = re.search(r"## Methodology\n(.*?)(?=## Conclusions|$)", extracted_text, re.DOTALL)
    if methodology_match:
        sections["methodology"] = methodology_match.group(1).strip()
    
    # Extract Conclusions section
    conclusions_match = re.search(r"## Conclusions\n(.*?)$", extracted_text, re.DOTALL)
    if conclusions_match:
        sections["conclusions"] = conclusions_match.group(1).strip()
    
    return sections


def preprocessor(state: dict) -> dict:
    """
    Node: Extract key information from each paper using LLM,
    then aggregate all analyses for synthesis.
    Uses document chunking to avoid exceeding token limits on large PDFs.
    """
    pdf_files = state.get("pdf_files", [])
    paper_summaries = []
    
    if not pdf_files:
        return {
            **state,
            "paper_summaries": paper_summaries,
            "cleaned_context": "",
        }
    
    # Build the paper extractor chain
    chain = build_paper_extractor_chain()
    
    # Process each paper
    for pdf_data in pdf_files:
        paper_name = pdf_data["name"]
        paper_text = pdf_data["text"]
        
        try:
            # Split large papers into manageable chunks (6000 chars ≈ 1500 tokens)
            chunks = chunk_text(paper_text, chunk_size_chars=6000)
            print(f"Processing {paper_name}: {len(chunks)} chunk(s) ({len(paper_text)} chars total)")
            
            # Process each chunk and aggregate findings
            all_findings = []
            all_methodology = []
            all_conclusions = []
            
            for i, chunk in enumerate(chunks):
                try:
                    extracted_output = chain.invoke({"paper_text": chunk})
                    sections = parse_extracted_sections(extracted_output)
                    
                    if sections["findings"]:
                        all_findings.append(sections["findings"])
                    if sections["methodology"]:
                        all_methodology.append(sections["methodology"])
                    if sections["conclusions"]:
                        all_conclusions.append(sections["conclusions"])
                        
                except Exception as chunk_error:
                    import traceback
                    print(f"Error processing chunk {i+1}/{len(chunks)} of {paper_name}:")
                    print(f"  {type(chunk_error).__name__}: {str(chunk_error)}")
                    traceback.print_exc()
                    continue
            
            # Combine findings from all chunks, removing duplicates
            combined_findings = " ".join(all_findings).strip()
            combined_methodology = " ".join(all_methodology).strip()
            combined_conclusions = " ".join(all_conclusions).strip()
            
            # Store paper summary
            paper_summary = {
                "name": paper_name,
                "findings": combined_findings or "No findings extracted",
                "methodology": combined_methodology or "No methodology extracted",
                "conclusions": combined_conclusions or "No conclusions extracted",
            }
            paper_summaries.append(paper_summary)
            
        except Exception as e:
            import traceback
            print(f"Error processing paper {paper_name}:")
            print(f"  {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            continue
    
    # Aggregate all summaries into a formatted string for synthesis
    aggregated_chunks = []
    for summary in paper_summaries:
        chunk = (
            f"{'='*60}\n"
            f"PAPER: {summary['name']}\n"
            f"{'='*60}\n"
            f"\n## Key Findings\n{summary['findings']}\n"
            f"\n## Methodology\n{summary['methodology']}\n"
            f"\n## Conclusions\n{summary['conclusions']}\n"
        )
        aggregated_chunks.append(chunk)
    
    cleaned_context = "\n\n".join(aggregated_chunks)
    
    return {
        **state,
        "paper_summaries": paper_summaries,
        "cleaned_context": cleaned_context,
    }