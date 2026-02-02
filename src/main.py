from fastapi import FastAPI, UploadFile, File
import shutil
import os
from src.ai_engine.legal_brain import analyze_contract

app = FastAPI(title="Bureaucracy Bulldozer API")

# Ensure temp folder exists
os.makedirs("temp_uploads", exist_ok=True)

@app.get("/")
def home():
    return {"status": "Bureaucracy Bulldozer is Online 🚜"}

@app.post("/audit-contract/")
async def audit_contract(file: UploadFile = File(...)):
    """
    1. Receives a PDF file.
    2. Extracts text (Mocked for now).
    3. Sends to Gemini 3 Brain.
    4. Returns JSON Verdict.
    """
    file_location = f"temp_uploads/{file.filename}"
    
    # 1. Save the uploaded file temporarily
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    print(f"📂 Received file: {file.filename}")

    # --- TRACK B: MOCKING TEAMMATE'S WORK ---
    # (Once your teammate sends you 'ingest_pdf.py', we will import it here!)
    # For now, we simulate extracting text from the file
    print("⚙️ Extracting text (Simulation)...")
    
    # TRICK: We will just use the same "Bad Contract" text we tested earlier
    # regardless of what file is uploaded, just to test the PIPELINE.
    extracted_text = """
    1. Landlord is not responsible for structural repairs.
    2. 24-hour eviction notice is allowed.
    3. Penalty interest is Rs 2000 per day.
    """
    
    # --- TRACK A: YOUR AI BRAIN ---
    print("🧠 Sending to AI Engine...")
    verdict = analyze_contract(extracted_text)
    
    # Clean up
    os.remove(file_location)
    
    return verdict

# To run this: uvicorn src.main:app --reload