"""
Reminder service for handling due dates and sending reminders for tasks.
"""
from datetime import datetime, timedelta
from sqlmodel import Session, select
from models import Task, PushSubscription
from database import get_session, engine
from sqlmodel import Session
from typing import List
import asyncio
import logging
import pywebpush
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ReminderService:
    def __init__(self):
        pass

    def check_for_due_reminders(self) -> List[Task]:
        """
        Find tasks that are due for reminder (due_date within 24 hours and reminder not yet sent)
        """
        with Session(engine) as session:
            # Get current time
            now = datetime.utcnow()
            # Define time window for upcoming due tasks (next 24 hours)
            tomorrow = now + timedelta(hours=24)

            # Find tasks that are due within 24 hours and haven't had a reminder sent
            stmt = select(Task).where(
                Task.due_date.is_not(None),  # Has a due date
                Task.reminder_sent == False,  # Reminder not yet sent
                Task.due_date >= now,        # Due date is in the future
                Task.due_date <= tomorrow,   # Due date is within 24 hours
                Task.completed == False      # Task is not completed
            )

            due_tasks = session.exec(stmt).all()
            return due_tasks

    def check_for_overdue_tasks(self) -> List[Task]:
        """
        Find tasks that are overdue (past due date and not completed)
        """
        with Session(engine) as session:
            now = datetime.utcnow()

            # Find tasks that are past their due date but not completed
            stmt = select(Task).where(
                Task.due_date.is_not(None),  # Has a due date
                Task.due_date < now,         # Due date is in the past
                Task.completed == False      # Task is not completed
            )

            overdue_tasks = session.exec(stmt).all()
            return overdue_tasks

    def mark_reminder_sent(self, task_id: int) -> bool:
        """
        Mark that a reminder has been sent for a task
        """
        with Session(engine) as session:
            task = session.get(Task, task_id)
            if task:
                task.reminder_sent = True
                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                return True
            return False

    def get_tasks_needing_reminders(self) -> List[dict]:
        """
        Get all tasks that need reminders with their user information
        """
        due_tasks = self.check_for_due_reminders()
        overdue_tasks = self.check_for_overdue_tasks()

        reminder_tasks = []

        # Process due tasks (coming up soon)
        for task in due_tasks:
            reminder_tasks.append({
                'task_id': task.id,
                'user_id': task.user_id,
                'title': task.title,
                'due_date': task.due_date,
                'type': 'due_soon',
                'message': f"Reminder: Your task '{task.title}' is due soon on {task.due_date.strftime('%Y-%m-%d at %H:%M')}"
            })

        # Process overdue tasks
        for task in overdue_tasks:
            reminder_tasks.append({
                'task_id': task.id,
                'user_id': task.user_id,
                'title': task.title,
                'due_date': task.due_date,
                'type': 'overdue',
                'message': f"Reminder: Your task '{task.title}' is overdue since {task.due_date.strftime('%Y-%m-%d at %H:%M')}"
            })

        return reminder_tasks

    def send_push_notification(self, user_id: str, title: str, body: str) -> bool:
        """
        Send a push notification to a user
        """
        with Session(engine) as session:
            # Get user's push subscription
            subscription = session.exec(
                select(PushSubscription).where(PushSubscription.user_id == user_id)
            ).first()

            if not subscription:
                logger.warning(f"No push subscription found for user {user_id}")
                return False

            # Get VAPID keys from environment
            vapid_private_key = os.getenv('VAPID_PRIVATE_KEY')
            vapid_public_key = os.getenv('VAPID_PUBLIC_KEY')
            vapid_claims = {
                "sub": "mailto:admin@example.com"  # Change this to your admin email
            }

            # Prepare the payload
            payload = {
                "title": title,
                "body": body
            }

            # Send the push notification
            try:
                pywebpush.send_web_push(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.p256dh,
                            "auth": subscription.auth
                        }
                    },
                    data=str(payload),
                    vapid_private_key=vapid_private_key,
                    vapid_claims=vapid_claims
                )

                logger.info(f"Push notification sent successfully to user {user_id}")
                return True
            except Exception as e:
                logger.error(f"Error sending push notification to user {user_id}: {str(e)}")
                return False

    def send_reminders_and_get_tasks(self) -> List[dict]:
        """
        Send reminders to users and return the list of tasks that needed reminders
        """
        due_tasks = self.check_for_due_reminders()
        overdue_tasks = self.check_for_overdue_tasks()

        reminder_tasks = []

        # Process due tasks (coming up soon)
        for task in due_tasks:
            title = f"Task Due Soon: {task.title}"
            body = f"Your task '{task.title}' is due soon on {task.due_date.strftime('%Y-%m-%d at %H:%M')}"

            # Send push notification
            success = self.send_push_notification(task.user_id, title, body)

            if success:
                # Mark reminder as sent
                self.mark_reminder_sent(task.id)

            reminder_tasks.append({
                'task_id': task.id,
                'user_id': task.user_id,
                'title': task.title,
                'due_date': task.due_date,
                'type': 'due_soon',
                'message': body,
                'notification_sent': success
            })

        # Process overdue tasks
        for task in overdue_tasks:
            title = f"Overdue Task: {task.title}"
            body = f"Your task '{task.title}' is overdue since {task.due_date.strftime('%Y-%m-%d at %H:%M')}"

            # Send push notification
            success = self.send_push_notification(task.user_id, title, body)

            reminder_tasks.append({
                'task_id': task.id,
                'user_id': task.user_id,
                'title': task.title,
                'due_date': task.due_date,
                'type': 'overdue',
                'message': body,
                'notification_sent': success
            })

        return reminder_tasks

# Global instance
reminder_service = ReminderService()