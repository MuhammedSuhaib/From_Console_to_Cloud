import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks
from database import create_db_and_tables
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Todo API on Hugging Face")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://console-to-cloud.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)

@app.on_event("startup")
def startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Todo API running on Hugging Face Spaces!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# For Hugging Face Spaces
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))