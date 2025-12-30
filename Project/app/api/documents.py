import uuid
import shutil
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.models.document import Document
from app.config.uploads import UPLOAD_DIR
from app.utils.file_utils import validate_file

from app.agents.processing_graph import build_workflow
from app.agents.workflow_state import WorkflowState
from app.utils.pdf_extract import extract_text_from_pdf
from pathlib import Path
from app.config.llm import get_llm

router = APIRouter(prefix="/documents", tags=["Documents"])

workflow = build_workflow()

def run_workflow(document_id: str, file_path: str):
    db: Session = SessionLocal()

    try:
        llm = get_llm()
        if llm is None:
            raise RuntimeError("LLM service is unavailable. Check API keys and configuration.")
        
        document_type = Path(file_path).suffix.lower()
        document_text = ""
        if document_type == ".pdf":
            print("Extracting PDF data")
            document_text = extract_text_from_pdf(file_path)
        else:
            print("Reading text file")
            with open(file_path, "r", encoding="utf-8") as f:
                document_text = f.read().strip()

        state = WorkflowState(
            document_id=document_id,
            file_path=file_path,
            document_text= document_text
        )

        final_state_dict  = workflow.invoke(state)
        final_state = WorkflowState(**final_state_dict)

        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        doc.status = final_state.status
        doc.result = final_state.model_dump()
        doc.updated_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        print("Exception:",e)
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = "failed"
            doc.error = str(e)
            db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    validate_file(file)

    doc_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        id=doc_id,
        file_path = str(file_path),
        status="processing"
    )

    db.add(document)
    db.commit()

    background_tasks.add_task(run_workflow, doc_id, str(file_path))

    return {
        "document_id": doc_id,
        "status": "processing"
    }


@router.get("/{document_id}/status")
def check_status(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": document_id,
        "status": doc.status
    }


@router.get("/{document_id}/result")
def get_result(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != "completed":
        raise HTTPException(status_code=400, detail="Processing not completed")

    return {
        "document_id": document_id,
        "result": doc.result
    }


@router.post("/{document_id}/cancel")
def cancel_processing(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.status = "cancelled"
    doc.updated_at = datetime.utcnow()
    db.commit()

    return {
        "document_id": document_id,
        "status": "cancelled"
    }
