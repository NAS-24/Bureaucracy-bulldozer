import shutil
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware  # 👈 1. IMPORT THIS
from fastapi.responses import FileResponse
from rich.console import Console
from rich.json import JSON

# --- IMPORTS ---
from src.ai_engine.legal_brain import analyze_contract
from src.document_processing.ingest_pdf import extract_text_from_pdf 
from src.document_processing.generate_notice import create_legal_notice

# Initialize Pretty Printer
console = Console()

app = FastAPI(title="Bureaucracy Bulldozer API")

# 👇 2. ADD THIS CORS BLOCK (The Gatekeeper)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL frontends (React, Next.js, Mobile)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Ensure temp folder exists
os.makedirs("temp_uploads", exist_ok=True)

@app.get("/")
def home():
    return {"status": "Bureaucracy Bulldozer is Online 🚜"}

@app.post("/audit-contract/")
async def audit_contract(file: UploadFile = File(...)):
    """
    1. Receives REAL PDF file.
    2. Extracts REAL text (via PDFPlumber + Gemini Vision).
    3. Sends to Gemini 3 Brain.
    4. Returns JSON Verdict.
    """
    file_location = f"temp_uploads/{file.filename}"
    
    try:
        # 1. SAVE THE FILE
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        
        console.print(f"\n[bold yellow]📂 Received file:[/bold yellow] {file.filename}")

        # 2. EXTRACT TEXT (The Real Deal)
        console.print("[cyan]⚙️ Extracting text (checking for scans)...[/cyan]")
        
        extracted_text = extract_text_from_pdf(Path(file_location))
        
        # Validation: Did we actually get text?
        if not extracted_text.strip():
            console.print("[bold red]❌ Error: No text found in document.[/bold red]")
            return {"error": "Could not read text. The file might be empty or too blurry."}

        console.print(f"[green]✅ Extraction Complete![/green] Read {len(extracted_text)} characters.")

        # 3. ANALYZE WITH AI
        console.print("[purple]🧠 Sending to AI Engine...[/purple]")
        verdict = analyze_contract(extracted_text)

        # 4. GENERATE NOTICE IF VIOLATIONS EXIST
        if verdict.get("violations"):
            console.print("[yellow]⚖️ Generating Legal Notice PDF...[/yellow]")
            
            # Create a unique filename
            notice_filename = f"Notice_{file.filename}"
            notice_path = f"temp_uploads/{notice_filename}"
            
            # Call the generator
            create_legal_notice(verdict["violations"], notice_path)
            
            # Add download link to JSON
            # TIP: We add the full URL so the frontend can just click it
            verdict["download_notice_url"] = f"http://127.0.0.1:8000/download/{notice_filename}"
            console.print(f"[bold green]✅ Notice Generated:[/bold green] {notice_filename}")

        console.print("\n[bold green]📝 VERDICT READY[/bold green]")
        return verdict

    except Exception as e:
        console.print(f"[bold red]💥 CRITICAL ERROR:[/bold red] {str(e)}")
        return {"error": f"Processing Failed: {str(e)}"}
        
    finally:
        # 5. CLEANUP
        if os.path.exists(file_location):
            os.remove(file_location)
            console.print("[dim]🧹 Temp file cleaned up.[/dim]")

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = f"temp_uploads/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    return {"error": "File not found"}