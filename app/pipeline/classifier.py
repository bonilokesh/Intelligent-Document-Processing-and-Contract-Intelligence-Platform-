import re
from app.pipeline.models import model_registry

def run_stage_1_classification(extracted_text: str) -> dict:
    """
    Classifies the document type and extracts baseline target entities.
    """
    # 1. Load the model via our lifecycle manager
    clf_pipeline = model_registry.load_classifier()
    
    # 2. Predict the document type
    predicted_type = clf_pipeline.predict([extracted_text])[0]
    
    # 3. Rule-based entity parsing (Dates, Jurisdictions)
    detected_date = None
    date_match = re.search(r'\b\d{1,2}[-/.\s]\d{1,2}[-/.\s]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b', extracted_text, re.IGNORECASE)
    if date_match:
        detected_date = date_match.group(0)
        
    jurisdiction = "Not Found"
    jur_match = re.search(r'(governed by|jurisdiction of|laws of)\s+([A-Z][a-zA-Z\s]{2,20})', extracted_text, re.IGNORECASE)
    if jur_match:
        jurisdiction = jur_match.group(2).strip()

    # 4. Immediate eviction from RAM to free up resources for Stage 2
    model_registry.free_memory()

    return {
        "document_type": predicted_type,
        "metadata": {
            "primary_date": detected_date,
            "governing_jurisdiction": jurisdiction,
            "parties": ["Party A Extract Placeholder", "Party B Extract Placeholder"]
        }
    }