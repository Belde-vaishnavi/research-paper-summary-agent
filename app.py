import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from graph_builder import build_graph
from state import AgentState

app = FastAPI(title="Research Paper Summarizer Agent")
graph = build_graph()


@app.post("/summarize")
async def summarize_papers(
    file: UploadFile = File(...),                      # ZIP file of PDFs
    mode: str = Form(default="research_summarizer"),   # research summarization mode
):
    """
    Summarize research papers from a ZIP of PDFs.
    Extracts key findings, methodology, and conclusions from each paper,
    then synthesizes a unified cross-paper summary.
    """
    # Save uploaded ZIP to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        shutil.copyfileobj(file.file, tmp)
        zip_path = tmp.name

    try:
        initial_state: AgentState = {
            "zip_path":        zip_path,
            "mode":            mode,
            "pdf_files":       [],
            "papers_count":    0,
            "paper_summaries": [],
            "cleaned_context": "",
            "final_response":  {},
        }

        result = graph.invoke(initial_state)
        
        # Check for errors (e.g., too many PDFs)
        if "error" in result and result["error"]:
            return JSONResponse(
                status_code=400,
                content={"error": result["error"]}
            )
        
        # Convert final_response to TXT format
        txt_content = _convert_to_txt(result["final_response"])
        
        # Create temporary TXT file with UTF-8 encoding (supports all characters)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt", encoding='utf-8') as txt_file:
            txt_file.write(txt_content)
            txt_path = txt_file.name
        
        # Return file as download
        return FileResponse(
            path=txt_path,
            filename="research_summary.txt",
            media_type="text/plain"
        )

    finally:
        os.unlink(zip_path)   # always clean up temp file


def _convert_to_txt(final_response: dict) -> str:
    """Convert the final_response dictionary to formatted TXT content"""
    # Only return the comparison_table (RESEARCH PAPERS ANALYSIS section)
    comparison_table = final_response.get("comparison_table", "")
    return comparison_table


@app.get("/health")
def health():
    return {"status": "ok"}