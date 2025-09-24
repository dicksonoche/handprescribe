from rapidfuzz import fuzz
import re
from transformers import pipeline  # For local LLM
from src.schema import PrescriptionSchema

# Load small LLM (local, GPU optional)
try:
    llm = pipeline("text-generation", model="microsoft/phi-2", device=0 if torch.cuda.is_available() else -1)
except:
    llm = None  # Fallback to rule-based

# Curated drug list (from RxNorm CSV; assume data/drugs.csv loaded)
drugs = ["aspirin", "ibuprofen"]  # Placeholder; load from CSV

def fuzzy_match(token: str, threshold=80):
    for drug in drugs:
        if fuzz.ratio(token.lower(), drug.lower()) > threshold:
            return drug
    return token

# Rule-based
def parse_rule_based(raw_text: str) -> dict:
    """Rule-based parsing with regex and fuzzy."""
    # Example regex
    drug_match = re.search(r"\b(\w+[\w\s]*?)\s*(?:[\d.]+(?:mg|g|ml)?)?", raw_text, re.I)
    drug = fuzzy_match(drug_match.group(1)) if drug_match else "unknown"
    # Similar for others...
    return {
        "drug_name": drug,
        "dosage": "unknown",  # Add regex
        "route": "unknown",
        "frequency": "unknown",
        "duration": "unknown",
        "confidence": 0.5  # Heuristic
    }

# LLM-assisted
PROMPT = """Extract from text: {text}
Output JSON: {{"drug_name": str, "dosage": str, ...}}"""

def parse_llm_assisted(raw_text: str) -> dict:
    if not llm:
        return parse_rule_based(raw_text)
    input_text = PROMPT.format(text=raw_text)
    output = llm(input_text, max_new_tokens=100)[0]['generated_text']
    # Parse JSON from output
    try:
        json_out = json.loads(output.split("{")[1].split("}")[0])  # Naive parse
    except:
        json_out = {}
    json_out["confidence"] = 0.8  # Placeholder
    return json_out