from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
import asyncio

from app.pipeline.ingestion import detect_and_extract_text
from app.pipeline.classifier import run_stage_1_classification
from app.pipeline.extractor import run_stage_2_extraction
from app.pipeline.analyzer import run_stage_3_4_analysis
from app.pipeline.contradictor import run_stage_5_contradiction_check
from app.pipeline.crm import sync_to_crm
from app.database import save_document_to_project
from app.websocket_manager import manager

app = FastAPI(title="Contract Intelligence Engine")

app.mount("/ui", StaticFiles(directory="static", html=True), name="static")

UPLOAD_DIR = "./temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/v1/upload")
async def upload_document(file: UploadFile = File(...), project_id: str = Query("default-project-1")):
    doc_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    saved_path = os.path.join(UPLOAD_DIR, f"{doc_id}{file_extension}")
    
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"document_id": doc_id, "filename": file.filename, "status": "queued", "project_id": project_id}

@app.websocket("/ws/pipeline/{document_id}")
async def websocket_pipeline_endpoint(websocket: WebSocket, document_id: str, project_id: str = "default-project-1"):
    await manager.connect(document_id, websocket)
    
    try:
        matching_files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(document_id)]
        if not matching_files:
            await manager.send_status(document_id, stage=0, status="failed", data={"error": "File missing"})
            return
            
        file_name = matching_files[0]
        file_path = os.path.join(UPLOAD_DIR, file_name)
        file_extension = os.path.splitext(file_name)[1]

        # --- STAGE 0: INGESTION ---
        await manager.send_status(document_id, stage=0, status="processing")
        extracted_payload = detect_and_extract_text(file_path, file_extension)
        
        full_text_block = ""
        if "pages" in extracted_payload:
            full_text_block = " ".join([p["text"] for p in extracted_payload["pages"]])
        elif "content" in extracted_payload:
            full_text_block = " ".join(extracted_payload["content"])
        else:
            full_text_block = str(extracted_payload)
            
        await manager.send_status(document_id, stage=0, status="completed", data={"extraction_type": extracted_payload.get("type")})
        await asyncio.sleep(1)

        # --- STAGE 1: CLASSIFICATION ---
        await manager.send_status(document_id, stage=1, status="processing")
        classification_results = run_stage_1_classification(full_text_block)
        doc_type = classification_results.get("document_type", "other")
        
        await manager.send_status(document_id, stage=1, status="completed", data=classification_results)
        await asyncio.sleep(1)

        # --- STAGE 2: ENTITY & CLAUSE EXTRACTION ---
        await manager.send_status(document_id, stage=2, status="processing")
        extraction_results = run_stage_2_extraction(full_text_block, doc_type)
        
        await manager.send_status(document_id, stage=2, status="completed", data=extraction_results)
        await asyncio.sleep(1)
        
        save_document_to_project(project_id, document_id, doc_type, extraction_results)
        
        # --- STAGE 3: ANOMALY DETECTION ---
        await manager.send_status(document_id, stage=3, status="processing")
        analysis_results = run_stage_3_4_analysis(extraction_results, doc_type)
        
        await manager.send_status(document_id, stage=3, status="completed", data={
            "anomalies": analysis_results["anomalies"],
            "summary": analysis_results["summary"]
        })
        await asyncio.sleep(1)

        # --- STAGE 4: RISK SCORING ---
        await manager.send_status(document_id, stage=4, status="processing")
        await manager.send_status(document_id, stage=4, status="completed", data={
            "risk_score": analysis_results["risk_score"]
        })
        await asyncio.sleep(1)
        
        # --- STAGE 5: CROSS-DOCUMENT CONTRADICTION DETECTION ---
        await manager.send_status(document_id, stage=5, status="processing")
        contradictions = run_stage_5_contradiction_check(project_id)
        
        await manager.send_status(document_id, stage=5, status="completed", data={
            "contradictions_found": len(contradictions),
            "details": contradictions
        })
        await asyncio.sleep(1)

        # --- STAGE 6: CRM IDEMPOTENT WORKSPACE SYNC ---
        await manager.send_status(document_id, stage=6, status="processing")
        
        packaged_analysis = {
            "risk_score": analysis_results["risk_score"],
            "summary": analysis_results["summary"]
        }
        crm_sync_log = sync_to_crm(file_name, doc_type, packaged_analysis, full_text_block)
        
        await manager.send_status(document_id, stage=6, status="completed", data=crm_sync_log)
        await asyncio.sleep(1)
        
        if os.path.exists(file_path):
            os.remove(file_path)

    except WebSocketDisconnect:
        manager.disconnect(document_id)
    except Exception as e:
        await manager.send_status(document_id, stage=0, status="failed", data={"error": str(e)})
    finally:
        manager.disconnect(document_id)