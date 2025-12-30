from fastapi import UploadFile, HTTPException
from pathlib import Path

def validate_file(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Empty filename")

    if not file.content_type:
        raise HTTPException(status_code=400, detail="Missing content type")

    document_type = Path(file.filename).suffix.lower()
    if document_type not in [".pdf", ".txt"]:
        return HTTPException(status_code=404, detail="Document not of valid format")