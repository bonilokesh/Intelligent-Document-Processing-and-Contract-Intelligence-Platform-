import re

def run_stage_2_extraction(text: str, doc_type: str) -> dict:
    """
    Stage 2: Extracts targeted entities and values based on the 
    document type classified in Stage 1.
    """
    extracted_fields = {}

    # Case A: Handle legal documents
    if doc_type in ["contract", "nda"]:
        extracted_fields["payment_terms"] = extract_pattern(
            text, r'payment\s+(?:terms?|period)\s+(?:of|is)?\s*(\d+\s*(?:days|weeks|months))'
        )
        extracted_fields["liability_cap"] = extract_pattern(
            text, r'(?:liability\s+cap|limit\s+of\s+liability)[^.\n]*?(?:USD|Rs\.|\$)\s*(\d+(?:,\d+)*)'
        )
        extracted_fields["confidentiality_period"] = extract_pattern(
            text, r'(?:confidentiality|non-disclosure)\s+period\s+(?:of|is)?\s*(\d+\s*(?:years|months))'
        )

    # Case B: Handle billing documents
    elif doc_type == "invoice":
        extracted_fields["vendor_details"] = extract_pattern(
            text, r'(?:vendor|supplier|from):\s*([A-Za-z0-9\s,.]+)'
        )
        extracted_fields["total_amount"] = extract_pattern(
            text, r'(?:total|amount\s+due|grand\s+total):\s*(?:USD|Rs\.|\$)?\s*(\d+(?:\.\d{2})?)'
        )
        extracted_fields["tax_amount"] = extract_pattern(
            text, r'(?:tax|vat|gst):\s*(?:USD|Rs\.|\$)?\s*(\d+(?:\.\d{2})?)'
        )
        
        # Grab lines that look like transaction line items
        lines = text.split("\n")
        extracted_fields["line_items"] = [
            l.strip() for l in lines if any(k in l.lower() for k in ["qty", "price", "item", "total"])
        ][:3]

    # Fallback for alternative sheets or statements
    else:
        extracted_fields["note"] = "Standard structural text block captured. No specific templates applied."

    return extracted_fields

def extract_pattern(text: str, pattern: str) -> str:
    """Helper utility to cleanly parse out regular expression groups."""
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "Not Found"