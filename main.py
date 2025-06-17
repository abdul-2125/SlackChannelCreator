from fastapi import FastAPI
from app.database import Base, engine
import logging

logging.basicConfig(level=logging.INFO)
from app.routers import forms, slack

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

app.include_router(forms.router)
app.include_router(slack.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
