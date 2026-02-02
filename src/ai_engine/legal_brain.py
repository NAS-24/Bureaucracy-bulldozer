import os
import json
from google import genai
from dotenv import load_dotenv

# 1. Setup & Load Keys
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ API Key not found! Check your .env file.")

client = genai.Client(api_key=api_key)

# ✅ USING THE HACKATHON MODEL
MODEL_ID = "gemini-3-flash-preview"

def analyze_contract(contract_text, law_type="RENT"):
    """
    Takes raw contract text, compares it against the Rent Act, 
    and returns a strict JSON verdict with a LIST of violations.
    """
    print(f"🧠 Bureaucracy Bulldozer is auditing using {MODEL_ID}...")

    # 2. Context Switcher
    law_filename = "maharashtra_rent_control_act.txt" 
    
    try:
        # Load the "Truth" (The Law Text)
        law_path = os.path.join("Data", law_filename)
        with open(law_path, "r", encoding="utf-8") as f:
            law_text = f.read()
    except FileNotFoundError:
        return {"error": f"Law file '{law_filename}' not found in data/ folder."}

    # 3. The "Ruthless Auditor" Prompt
    prompt = f"""
    ROLE:
    You are a strict Legal Auditor for Indian Rental Agreements. 
    Your job is to identify ILLEGAL clauses based ONLY on the provided Context (The Law).

    CONTEXT (THE LAW):
    {law_text}

    USER CONTRACT (THE SUSPECT):
    {contract_text}

    INSTRUCTIONS:
    1. Analyze the "USER CONTRACT" clause by clause.
    2. Compare it against "THE LAW".
    3. Identify **ALL** clauses that violate the law.
    4. Specifically look for:
       - Structural repair costs shifted to tenant (Section 14).
       - Excessive security deposits (Section 18).
       - Unlawful eviction notices (Section 16).
       - Exorbitant penalty interest (Usury/Unfair practice).

    OUTPUT FORMAT (STRICT JSON ONLY):
    Output a single JSON object with this exact structure:
    {{
      "is_compliant": boolean,
      "summary_verdict": "One sentence summary.",
      "violations": [
        {{
          "violated_clause_text": "Text of the bad clause from contract",
          "relevant_law_section": "Section X",
          "explanation": "Why it is illegal.",
          "suggested_remedy": "What to change it to."
        }}
      ]
    }}
    """

    # 4. Call Gemini
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config={
                'response_mime_type': 'application/json' # 👈 Force strict JSON
            }
        )
        
        # 5. Parse and Return
        return json.loads(response.text)
        
    except Exception as e:
        return {"error": f"AI Brain Malfunction: {str(e)}"}

# --- 🧪 TEST ZONE (Runs only when you execute this file) ---
if __name__ == "__main__":
    
    # ✅ REAL DATA from your 'illegal_contract_test.pdf'
    # I have pasted the actual clauses you uploaded:
    # 1. Clause 9 (Repairs)
    # 2. Clause 15 (24-hour Eviction)
    # 3. Clause 2 (Penalty Interest)
    
    real_test_data = """
    2. In the event of any delay in payment beyond the 7th day, the Tenant shall be 
    liable to pay a penalty interest calculated at the rate of Rs. 2,000 per day 
    (approx 8% per day) until the full amount is cleared.
    
    9. That the Tenant shall bear the sole cost and responsibility for all repairs 
    required in the demised premises, including but not limited to structural repairs, 
    roof leakage, seepage, plumbing overhauls, and major civil works.
    
    15. That the Owner reserves the absolute and unfettered right to terminate this 
    agreement and evict the Tenant at any time, without assigning any reason, 
    by serving a notice of 24 (Twenty-Four) hours.
    """
    
    print("\n--- 🧪 STRESS TEST: Checking Your PDF Clauses ---")
    
    result = analyze_contract(real_test_data)
    
    # Pretty print the JSON result
    print("\n📝 AI VERDICT:")
    print(json.dumps(result, indent=2))