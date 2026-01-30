import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks, chat, chatkit, notifications
from mcp_server.mcp_server import mcp 
from database import create_db_and_tables
from dotenv import load_dotenv
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from reminder_service import reminder_service
from recurring_service import recurring_task_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="Todo API on Hugging Face")

# Initialize scheduler
scheduler = AsyncIOScheduler()

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
app.include_router(notifications.router) # Notifications for push notifications

# Mount the official MCP server using SSE transport
app.mount("/mcp", mcp.sse_app())

async def check_reminders_and_recurring_tasks():
    """Periodic task to check for reminders and recurring tasks"""
    logger.info("Checking for reminders and recurring tasks...")

    # Send reminders to users
    reminder_tasks = reminder_service.send_reminders_and_get_tasks()
    for task_info in reminder_tasks:
        logger.info(f"Processed reminder for task: {task_info['message']} (sent: {task_info['notification_sent']})")

    # Check for recurring tasks that need to be created
    recurring_tasks = recurring_task_service.process_recurring_tasks()
    for task in recurring_tasks:
        logger.info(f"Created new occurrence of recurring task: {task.title}")

    logger.info("Finished checking for reminders and recurring tasks.")

@app.on_event("startup")
def startup():
    logger.info("Starting up the application...")
    try:
        create_db_and_tables()
        logger.info("Database tables created successfully")

        # Start the scheduler to check for reminders and recurring tasks every 10 minutes
        scheduler.add_job(check_reminders_and_recurring_tasks, IntervalTrigger(minutes=10))
        scheduler.start()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

@app.on_event("shutdown")
def shutdown():
    logger.info("Shutting down the application...")
    scheduler.shutdown()

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Todo API running on Hugging Face Spaces!"}

@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}

@app.post("/api/jobs/trigger")
async def trigger_reminders_and_recurring_tasks():
    """Endpoint for Dapr cron binding to trigger reminder and recurring task checks"""
    logger.info("Received trigger from Dapr cron binding for reminders and recurring tasks")

    # Call the existing function that handles both reminders and recurring tasks
    await check_reminders_and_recurring_tasks()

    return {"status": "success", "message": "Reminders and recurring tasks checked successfully"}

# For Hugging Face Spaces
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))