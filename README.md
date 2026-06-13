# Research Paper Summary Agent

An AI agent that takes a ZIP file of research paper PDFs and returns a
synthesized cross-paper summary — key findings, methodology, and conclusions
for each paper, compared side by side. Built with **LangGraph** (agent flow),
**LangChain + Groq** (LLM calls), and exposed via a **FastAPI** server.

🔗 **Live API**: https://research-paper-summary-agent.onrender.com/docs

Try It Yourself

A sample input ZIP file is included in this repository for quick testing:

sample_input/papers.zip

You can use this file to test the agent without searching for research papers yourself.

Using the Live Demo

Open the Swagger UI:

https://research-paper-summary-agent.onrender.com/docs

Expand the POST /summarize endpoint.

Click Try it out.

Upload sample_input/papers.zip.

Execute the request and download the generated summary report.

## How it works (agent flow)

The agent is a small graph of steps (`graph_builder.py`) that run in sequence:

```
doc_loader → preprocessor → output_formatter
```

1. **doc_loader** (`nodes/doc_loader.py`)
   Unzips the uploaded file and extracts all the PDF files inside it.

2. **preprocessor** (`nodes/preprocessor.py`)
   For each PDF, extracts the text, splits it into chunks, and sends each
   chunk through the **paper extractor chain** (`chains/paper_extractor_chain.py`,
   prompt in `prompts/paper_extractor.md`) — an LLM call (Groq's
   `llama-3.1-8b-instant`) that pulls out Key Findings, Methodology, and
   Conclusions for that paper.

3. **output_formatter** (`nodes/output_formatter.py`)
   Takes all the per-paper extractions and formats them into a single
   comparison table.

   *(There's also a `synthesis_chain.py` / `research_synthesizer.md` for an
   optional cross-paper synthesis step using `llm_node.py`, currently not
   wired into the graph — `graph_builder.py` goes straight from
   `preprocessor` to `output_formatter`.)*

The shared data passed between these steps is defined in `state.py`
(`AgentState`) — things like `pdf_files`, `paper_summaries`, and
`final_response`.

## Project structure

```
.
├── app.py                       # FastAPI server (entry point)
├── graph_builder.py              # Defines the agent's step-by-step flow
├── state.py                       # Shared state passed between steps
├── nodes/
│   ├── doc_loader.py              # Step 1: unzip & find PDFs
│   ├── preprocessor.py            # Step 2: extract text, chunk, run LLM per paper
│   ├── llm_node.py                 # Optional synthesis step (not in current graph)
│   └── output_formatter.py        # Step 3: build final comparison table
├── chains/
│   ├── paper_extractor_chain.py   # LLM chain: per-paper extraction
│   └── synthesis_chain.py          # LLM chain: cross-paper synthesis (optional)
├── prompts/
│   ├── paper_extractor.md          # Prompt template for extraction
│   └── research_synthesizer.md     # Prompt template for synthesis
├── requirements.txt
├── .env.example                    # Template showing required env variable(s)
├── .gitignore
└── Dockerfile
```

## Running it locally

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your environment variable
cp .env.example .env
# then open .env and paste in your real Groq API key

# 4. Start the server
uvicorn app:app --reload
```

The API will be running at `http://127.0.0.1:8000`. Open
`http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## Using the API

### `POST /summarize`
- **file**: a `.zip` file containing one or more PDF research papers
- **mode** (optional, form field): defaults to `research_summarizer`
- **Returns**: a `.txt` file (`research_summary.txt`) containing the
  comparison table of all papers' key findings, methodology, and conclusions.

### `GET /health`
- Simple health check, returns `{"status": "ok"}`.

## Required environment variable

| Variable | Description |
|---|---|
| `GROK_API_KEY` | Your Groq API key (get one free at https://console.groq.com/keys). Despite the name, this is a **Groq** key — starts with `gsk_`. Used by `chains/paper_extractor_chain.py` and `chains/synthesis_chain.py`. |
