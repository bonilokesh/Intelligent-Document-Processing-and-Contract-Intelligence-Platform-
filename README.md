# Intelligent Document Processing & Contract Intelligence Platform

An automated, real-time document analysis pipeline built with **FastAPI** and **WebSockets**, designed to run completely CPU-bound within strict memory constraints.

## 🚀 Architecture Overview
- **Backend:** FastAPI (Python) handles async file chunks and active WebSocket channels.
- **Frontend:** Single-page real-time progress layout rendering streaming pipeline events instantly.
- **Data Pipeline:** Standardized text layer extraction that preserves structural layout boundaries (headings, tables, paragraphs) instead of flattening information into unorganized blobs.

## 🧠 Memory Management Strategy (Railway Free Tier Optimization)
Because this system is deployed on the **Railway Free Tier**, keeping multiple machine learning pipelines (OCR, Text Classification, Vectorizers) idling in RAM would cause instant Out-Of-Memory (OOM) crashes.

To circumvent this, the platform implements a strict **Model Lifecycle Manager**:
1. **Lazy Loading:** Models are never loaded at application startup; they remain compressed on disk.
2. **On-Demand Execution:** When a specific pipeline stage triggers, the required model is loaded into memory dynamically.
3. **Aggressive Cache Eviction:** Immediately after running inference, the model reference is deleted (`del`), background framework caches are cleared, and Python's garbage collector (`gc.collect()`) is explicitly invoked to flush memory completely before the next stage starts.

## 🛠️ Pipeline Stages
- **Stage 0 (Ingestion):** Auto-detects format extensions and routes data down specialized parsing paths.
- **Stage 1 (Classification):** Runs a low-footprint scikit-learn TF-IDF classifier to categorize the file type.
- **Stage 2 (Extraction):** Executes target regex pattern matchers to isolate contract clauses or line items.
- **Stage 3 & 4 (Analysis & Scoring):** Audits compliance anomalies and assigns a weighted risk index (0-100).
- **Stage 5 (Cross-Document Check):** Compares project files side-by-side to expose conflicting criteria.
- **Stage 6 (CRM Sync):** Generates a unique SHA-256 hash of the content to perform idempotent updates to a mock CRM workspace, strictly preventing duplicate records.