# A simple in-memory store tracking projects and their associated processed documents
PROJECT_DB = {
    "default-project-1": {
        "project_name": "Vendor Operations Workspace",
        "documents": {}  # Maps document_id -> its extraction data
    }
}

def save_document_to_project(project_id: str, document_id: str, doc_type: str, extraction_data: dict):
    """Saves a document's extracted fields into its project workspace."""
    if project_id not in PROJECT_DB:
        PROJECT_DB[project_id] = {"project_name": f"Project {project_id}", "documents": {}}
        
    PROJECT_DB[project_id]["documents"][document_id] = {
        "doc_type": doc_type,
        "data": extraction_data
    }

def get_project_documents(project_id: str) -> dict:
    """Retrieves all documents associated with a project workspace."""
    return PROJECT_DB.get(project_id, {}).get("documents", {})