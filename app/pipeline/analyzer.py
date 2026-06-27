def run_stage_3_4_analysis(extracted_fields: dict, doc_type: str) -> dict:
    """
    Stage 3: Analyzes extracted fields to spot compliance or mathematical anomalies.
    Stage 4: Processes a weighted risk metric based on the findings.
    """
    anomalies = []
    doc_type_lower = doc_type.lower()
    
    # --- STAGE 3: ANOMALY DETECTION RULES ---
    if doc_type_lower in ["contract", "nda"]:
        # Rule 1: Check for excessive payment terms
        p_term = extracted_fields.get("payment_terms", "Not Found")
        if p_term != "Not Found":
            digits = [int(s) for s in p_term.split() if s.isdigit()]
            if digits and digits[0] > 90:
                anomalies.append({
                    "severity": "critical",
                    "category": "legal",
                    "explanation": f"Payment window ({digits[0]} days) breaches standard 90-day corporate limits."
                })
        
        # Rule 2: Warn if a critical legal shield is missing
        if extracted_fields.get("liability_cap") == "Not Found":
            anomalies.append({
                "severity": "warning",
                "category": "legal",
                "explanation": "Document lacks a clearly defined Liability Cap limit."
            })

    elif doc_type_lower == "invoice":
        total = extracted_fields.get("total_amount", "Not Found")
        if total == "Not Found" or total == "0":
            anomalies.append({
                "severity": "critical",
                "category": "financial",
                "explanation": "Grand total billing sum could not be extracted or verified."
            })

    elif doc_type_lower == "rfp" or doc_type_lower == "other":
        # Let's add a generic diagnostic rule for unclassified/other documents to see it work
        anomalies.append({
            "severity": "informational",
            "category": "general",
            "explanation": "Standard unstructured document scanned without automated template matches."
        })

    # --- STAGE 4: WEIGHTED RISK SCORE ENGINE ---
    critical_count = sum(1 for a in anomalies if a["severity"] == "critical")
    warning_count = sum(1 for a in anomalies if a["severity"] == "warning")
    info_count = sum(1 for a in anomalies if a["severity"] == "informational")
    
    # Custom severity weights
    raw_score = (critical_count * 45) + (warning_count * 20) + (info_count * 5)
    final_risk_score = min(raw_score, 100)  # Ceiling limit of 100
    
    return {
        "anomalies": anomalies,
        "summary": {
            "critical": critical_count,
            "warning": warning_count,
            "informational": info_count
        },
        "risk_score": final_risk_score
    }