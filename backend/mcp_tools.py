from sqlmodel import Session, select
from models import Task, Conversation, Message, TaskPriority
from datetime import datetime
from typing import Optional, List
from database import get_session
import sqlalchemy


def create_add_task_tool():
    """Create the add_task MCP tool for AI agent"""
    def add_task(user_id: str, title: str, description: Optional[str] = None) -> dict:
        """
        Add a new task for the user.
        
        Args:
            user_id: The ID of the user creating the task
            title: The title of the task
            description: Optional description of the task
            
        Returns:
            Dictionary with task_id, status, and title
        """
        # Get database session
        session_gen = get_session()
        session = next(session_gen)
        
        try:
            # Create new task
            new_task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=TaskPriority.medium  # Default priority
            )
            
            session.add(new_task)
            session.commit()
            session.refresh(new_task)
            
            return {
                "task_id": new_task.id,
                "status": "created",
                "title": new_task.title
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            # Return the generator to its original state for proper cleanup
            next(session_gen, None)
    
    return add_task


def create_list_tasks_tool():
    """Create the list_tasks MCP tool for AI agent"""
    def list_tasks(user_id: str, status: Optional[str] = "all") -> List[dict]:
        """
        List tasks for the user with optional filtering.
        
        Args:
            user_id: The ID of the user whose tasks to list
            status: Filter by status - "all", "pending", "completed" (default: "all")
            
        Returns:
            List of task dictionaries
        """
        # Get database session
        session_gen = get_session()
        session = next(session_gen)
        
        try:
            # Build query based on status filter
            query = select(Task).where(Task.user_id == user_id)
            
            if status == "pending":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)
            
            tasks = session.exec(query).all()
            
            # Convert to dictionary format
            result = []
            for task in tasks:
                result.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority.value,
                    "category": task.category,
                    "tags": task.tags,
                    "created_at": task.created_at.isoformat() if hasattr(task.created_at, 'isoformat') else str(task.created_at),
                    "updated_at": task.updated_at.isoformat() if hasattr(task.updated_at, 'isoformat') else str(task.updated_at)
                })
            
            return result
        except Exception as e:
            raise e
        finally:
            session.close()
            # Return the generator to its original state for proper cleanup
            next(session_gen, None)
    
    return list_tasks


def create_complete_task_tool():
    """Create the complete_task MCP tool for AI agent"""
    def complete_task(user_id: str, task_id: int) -> dict:
        """
        Mark a task as complete.
        
        Args:
            user_id: The ID of the user who owns the task
            task_id: The ID of the task to mark as complete
            
        Returns:
            Dictionary with task_id, status, and title
        """
        # Get database session
        session_gen = get_session()
        session = next(session_gen)
        
        try:
            # Get the task
            task = session.get(Task, task_id)
            
            # Verify that the task belongs to the user
            if not task or task.user_id != user_id:
                raise ValueError(f"Task {task_id} not found or doesn't belong to user {user_id}")
            
            # Mark as complete
            task.completed = True
            task.updated_at = datetime.utcnow()
            
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "task_id": task.id,
                "status": "completed",
                "title": task.title
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            # Return the generator to its original state for proper cleanup
            next(session_gen, None)
    
    return complete_task


def create_delete_task_tool():
    """Create the delete_task MCP tool for AI agent"""
    def delete_task(user_id: str, task_id: int) -> dict:
        """
        Delete a task for the user.
        
        Args:
            user_id: The ID of the user who owns the task
            task_id: The ID of the task to delete
            
        Returns:
            Dictionary with task_id, status, and title
        """
        # Get database session
        session_gen = get_session()
        session = next(session_gen)
        
        try:
            # Get the task
            task = session.get(Task, task_id)
            
            # Verify that the task belongs to the user
            if not task or task.user_id != user_id:
                raise ValueError(f"Task {task_id} not found or doesn't belong to user {user_id}")
            
            # Store task info before deletion for response
            task_title = task.title
            
            # Delete the task
            session.delete(task)
            session.commit()
            
            return {
                "task_id": task_id,
                "status": "deleted",
                "title": task_title
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            # Return the generator to its original state for proper cleanup
            next(session_gen, None)
    
    return delete_task


def create_update_task_tool():
    """Create the update_task MCP tool for AI agent"""
    def update_task(user_id: str, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> dict:
        """
        Update a task for the user.
        
        Args:
            user_id: The ID of the user who owns the task
            task_id: The ID of the task to update
            title: Optional new title for the task
            description: Optional new description for the task
            
        Returns:
            Dictionary with task_id, status, and title
        """
        # Get database session
        session_gen = get_session()
        session = next(session_gen)
        
        try:
            # Get the task
            task = session.get(Task, task_id)
            
            # Verify that the task belongs to the user
            if not task or task.user_id != user_id:
                raise ValueError(f"Task {task_id} not found or doesn't belong to user {user_id}")
            
            # Update fields if provided
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            
            task.updated_at = datetime.utcnow()
            
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            # Return the generator to its original state for proper cleanup
            next(session_gen, None)
    
    return update_task


# Initialize all tools
add_task_tool = create_add_task_tool()
list_tasks_tool = create_list_tasks_tool()
complete_task_tool = create_complete_task_tool()
delete_task_tool = create_delete_task_tool()
update_task_tool = create_update_task_tool()