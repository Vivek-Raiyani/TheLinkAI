from crewai import Agent
from app.config.llm import get_llm

gemini_llm = get_llm()


classifier_agent = Agent(
    role="Document Classifier",
    goal="Identify the document type and confidence",
    backstory="Expert in business documents like invoices, contracts, POs.",
    llm=gemini_llm,
    verbose=True
)

extraction_agent = Agent(
    role="Data Extraction Specialist",
    goal="Extract structured fields based on document type",
    backstory="Expert in extracting fields from noisy business documents.",
    llm=gemini_llm,
    verbose=True
)

validation_agent = Agent(
    role="Data Validator",
    goal="Detect inconsistencies, conflicts, and missing information",
    backstory="Expert in financial and legal validation.",
    llm=gemini_llm,
    verbose=True
)

