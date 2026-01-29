"""
Recurring tasks service for handling recurring task logic.
"""
from datetime import datetime, timedelta
from sqlmodel import select
from models import Task
from database import engine
from sqlmodel import Session
from typing import List
import logging
from dateutil import parser
from dateutil.relativedelta import relativedelta
import re
import calendar

logger = logging.getLogger(__name__)

class RecurringTaskService:
    def __init__(self):
        pass

    def _parse_recurrence_pattern(self, pattern: str) -> dict:
        """
        Parse a recurrence pattern string and return a dictionary with the interval
        Supports patterns like: "daily", "weekly", "monthly", "yearly", "every 2 days", etc.
        """
        pattern_lower = pattern.lower().strip()

        # Handle simple patterns
        if pattern_lower == "daily":
            return {"days": 1}
        elif pattern_lower == "weekly":
            return {"weeks": 1}
        elif pattern_lower == "monthly":
            return {"months": 1}
        elif pattern_lower == "yearly":
            return {"years": 1}

        # Handle patterns like "every X days/weeks/months"
        match = re.match(r"every\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)", pattern_lower)
        if match:
            num = int(match.group(1))
            unit = match.group(2)

            if "day" in unit:
                return {"days": num}
            elif "week" in unit:
                return {"weeks": num}
            elif "month" in unit:
                return {"months": num}
            elif "year" in unit:
                return {"years": num}

        # Default to daily if pattern is unrecognized
        logger.warning(f"Unrecognized recurrence pattern: {pattern}. Defaulting to daily.")
        return {"days": 1}

    def _calculate_next_occurrence(self, last_occurrence: datetime, pattern: str) -> datetime:
        """
        Calculate the next occurrence based on the last occurrence and pattern
        """
        interval = self._parse_recurrence_pattern(pattern)

        # Create a new date by adding the interval
        # For simplicity, we'll use timedelta for most cases, but handle months/years specially

        # Calculate the new date based on the intervals
        days = interval.get("days", 0)
        weeks = interval.get("weeks", 0)
        months = interval.get("months", 0)
        years = interval.get("years", 0)

        # Add the basic units (days and weeks)
        result_date = last_occurrence + timedelta(days=days + (weeks * 7))

        # Handle months and years separately as they require more complex logic
        if months or years:
            month = result_date.month - 1 + months + (years * 12)
            year = result_date.year + month // 12
            month = month % 12 + 1
            day = min(result_date.day, calendar.monthrange(year, month)[1])  # Ensure day is valid

            result_date = result_date.replace(year=year, month=month, day=day)

        return result_date

    def check_for_recurring_tasks(self) -> List[Task]:
        """
        Find recurring tasks that need to be created (based on their pattern and last completion)
        """
        with Session(engine) as session:
            # Find all recurring tasks that are completed and need to be recreated
            # or recurring tasks that are not completed but past their due date
            stmt = select(Task).where(
                Task.is_recurring == True,  # Is a recurring task
                Task.recurrence_pattern.is_not(None)  # Has a recurrence pattern
            )

            recurring_tasks = session.exec(stmt).all()

            tasks_to_recur = []
            for task in recurring_tasks:
                # Check if the task is completed and needs to be recreated
                if task.completed:
                    # Calculate when the next occurrence should be
                    next_occurrence = self._calculate_next_occurrence(task.updated_at, task.recurrence_pattern)

                    # If it's time to create the next occurrence
                    if next_occurrence <= datetime.utcnow():
                        tasks_to_recur.append(task)

            return tasks_to_recur

    def create_next_occurrence(self, original_task: Task) -> Task:
        """
        Create the next occurrence of a recurring task
        """
        with Session(engine) as session:
            # Calculate the next due date based on the recurrence pattern
            next_due_date = None
            if original_task.due_date:
                next_due_date = self._calculate_next_occurrence(original_task.due_date, original_task.recurrence_pattern)

            # Create a new task with the same properties as the original
            new_task = Task(
                user_id=original_task.user_id,
                title=original_task.title,
                description=original_task.description,
                priority=original_task.priority,
                category=original_task.category,
                tags=original_task.tags,
                due_date=next_due_date,
                is_recurring=original_task.is_recurring,
                recurrence_pattern=original_task.recurrence_pattern,
                reminder_sent=False,  # New occurrence hasn't had reminder sent
                completed=False,  # New occurrence isn't completed
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(new_task)
            session.commit()
            session.refresh(new_task)

            # Mark the original task as needing a new occurrence created
            # (in a real system, you might want to keep the completed task as a record)

            logger.info(f"Created next occurrence of recurring task '{original_task.title}' with ID {new_task.id}")
            return new_task

    def process_recurring_tasks(self) -> List[Task]:
        """
        Process all recurring tasks that need to be created
        """
        tasks_to_recur = self.check_for_recurring_tasks()
        new_tasks = []

        for task in tasks_to_recur:
            try:
                new_task = self.create_next_occurrence(task)
                new_tasks.append(new_task)
            except Exception as e:
                logger.error(f"Error creating next occurrence for task {task.id}: {e}")

        return new_tasks

# Global instance
recurring_task_service = RecurringTaskService()
