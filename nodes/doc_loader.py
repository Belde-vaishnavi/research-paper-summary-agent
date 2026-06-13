import os
import zipfile
import tempfile
from PyPDF2 import PdfReader
from state import AgentState

MAX_PDFS = 50  # No token bottleneck - can process many papers efficiently

def doc_loader(state: AgentState) -> AgentState:
    """Extract PDF files from the uploaded ZIP file"""
    
    zip_path = state["zip_path"]
    pdf_files = []
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Find all PDF files
                pdf_members = [m for m in z.namelist() 
                               if m.lower().endswith('.pdf') and not m.startswith('__MACOSX')]
                
                # Enforce PDF limit
                if len(pdf_members) > MAX_PDFS:
                    state["pdf_files"] = []
                    state["papers_count"] = 0
                    state["error"] = f"Too many PDFs. Maximum {MAX_PDFS} allowed, found {len(pdf_members)}"
                    return state
                
                # Extract and process each PDF
                for pdf_member in pdf_members:
                    pdf_path = os.path.join(tmp_dir, pdf_member)
                    
                    # Create parent directories
                    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                    
                    # Extract PDF file
                    with z.open(pdf_member) as source, open(pdf_path, 'wb') as target:
                        target.write(source.read())
                    
                    # Extract text from PDF
                    try:
                        pdf_reader = PdfReader(pdf_path)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                        
                        # Use filename as paper name (without .pdf extension)
                        pdf_name = os.path.basename(pdf_member).replace('.pdf', '')
                        
                        if text.strip():  # Only add if PDF has extractable text
                            pdf_files.append({
                                "name": pdf_name,
                                "text": text
                            })
                            print(f"✓ Extracted {pdf_name}: {len(text)} characters")
                        else:
                            print(f"⚠ Warning: {pdf_name} has no extractable text")
                    except Exception as e:
                        import traceback
                        print(f"✗ Failed to extract text from {pdf_member}:")
                        print(f"  {type(e).__name__}: {str(e)}")
                        traceback.print_exc()
                        continue
            
            state["pdf_files"] = pdf_files
            state["papers_count"] = len(pdf_files)
            
        except Exception as e:
            import traceback
            print(f"✗ Failed to extract ZIP: {str(e)}")
            traceback.print_exc()
            state["pdf_files"] = []
            state["papers_count"] = 0
            state["error"] = f"Failed to extract ZIP: {str(e)}"
            return state
    
    return state