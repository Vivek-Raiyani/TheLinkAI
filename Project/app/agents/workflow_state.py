from typing import Optional, Dict, List, Union
from pydantic import BaseModel

class WorkflowState(BaseModel):
    document_id: str
    file_path: str

    document_text : str
    document_type: Optional[str] = None
    classification_confidence: Optional[float] = None

    extracted_data: Optional[Dict] = None
    extraction_confidence: Optional[float] = None

    validation_issues: List[Union[str, dict]] = []

    routing_decision: Optional[str] = None

    # control & safety
    status: str = "processing"
    error: Optional[str] = None

    classify_retries: int = 0
    extract_retries: int = 0
    validate_retries: int = 0