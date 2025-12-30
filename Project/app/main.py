from fastapi import FastAPI
from app.config.database import engine, Base
from app.api.documents import router as document_router
from app.config.llm import get_llm

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Processing API",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    try:
        llm = get_llm()
        if llm:
            return {"status": "ready"}
    except Exception:
        pass
    return {"status": "unconfigured", "message": "LLM API Key missing or invalid"}, 503

app.include_router(document_router)



