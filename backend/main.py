from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import tasks
import os

app = FastAPI(title="Todo API", version="1.0.0")

# CORS middleware - allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {"message": "Todo API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}