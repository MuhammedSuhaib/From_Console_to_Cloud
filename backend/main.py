import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks, chat, chatkit # Added chatkit
from database import create_db_and_tables
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
app.include_router(chat.router)
app.include_router(chatkit.router) # Registered chatkit

@app.on_event("startup")
def startup():
    logger.info("Starting up the application...")
    try:
        create_db_and_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Todo API running on Hugging Face Spaces!"}

@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}

# For Hugging Face Spaces
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))