import hashlib
import time

# Mock external CRM Database representing our Notion/Airtable workspace rows
CRM_WORKSPACE_RECORDS = {}

def compute_content_hash(text: str) -> str:
    """Generates a unique SHA-256 hash to ensure data idempotency."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def sync_to_crm(file_name: str, doc_type: str, analysis_results: dict, content_text: str) -> dict:
    """
    Section 3: Synchronizes structured document metrics to the CRM.
    Updates existing entries if content hashes match to prevent duplication.
    """
    content_hash = compute_content_hash(content_text)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    record_payload = {
        "file_name": file_name,
        "document_type": doc_type.upper(),
        "risk_score": analysis_results.get("risk_score", 0),
        "critical_anomalies": analysis_results.get("summary", {}).get("critical", 0),
        "warning_anomalies": analysis_results.get("summary", {}).get("warning", 0),
        "last_processed_timestamp": timestamp,
        "status": "Synced Successfully"
    }
    
    # Idempotency Check: Check if hash already exists
    if content_hash in CRM_WORKSPACE_RECORDS:
        action_taken = "UPDATED (Prevented Duplication)"
        CRM_WORKSPACE_RECORDS[content_hash].update(record_payload)
    else:
        action_taken = "CREATED NEW RECORD"
        CRM_WORKSPACE_RECORDS[content_hash] = record_payload
        
    return {
        "action": action_taken,
        "content_hash": content_hash,
        "record": CRM_WORKSPACE_RECORDS[content_hash]
    }