"""
Task management utilities.

This module provides functions for managing tasks, including adding, marking as done,
and reading tasks. It uses a simple JSON file for storage.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Default tasks file path
TASKS_FILE = "tasks.json"

def _ensure_tasks_file() -> None:
    """Ensure the tasks file exists with an empty list."""
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w') as f:
            json.dump([], f)

def _read_tasks_file() -> List[Dict[str, Any]]:
    """Read tasks from the JSON file."""
    _ensure_tasks_file()
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def _write_tasks_file(tasks: List[Dict[str, Any]]) -> None:
    """Write tasks to the JSON file."""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def add_task(title: str, description: str = "", priority: str = "medium", due_date: Optional[str] = None) -> Dict[str, Any]:
    """Add a new task.
    
    Args:
        title (str): Task title
        description (str, optional): Task description
        priority (str, optional): Task priority (low, medium, high)
        due_date (str, optional): Due date in ISO format
        
    Returns:
        Dict[str, Any]: The created task
    """
    tasks = _read_tasks_file()
    task = {
        "id": len(tasks) + 1,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "due_date": due_date
    }
    tasks.append(task)
    _write_tasks_file(tasks)
    return task

def mark_task_as_done(task_id: int) -> Optional[Dict[str, Any]]:
    """Mark a task as done.
    
    Args:
        task_id (int): ID of the task to mark as done
        
    Returns:
        Optional[Dict[str, Any]]: The updated task if found, None otherwise
    """
    tasks = _read_tasks_file()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            _write_tasks_file(tasks)
            return task
    return None

def read_tasks(status: Optional[str] = None, priority: Optional[str] = None) -> List[Dict[str, Any]]:
    """Read tasks with optional filtering.
    
    Args:
        status (str, optional): Filter by status
        priority (str, optional): Filter by priority
        
    Returns:
        List[Dict[str, Any]]: List of matching tasks
    """
    tasks = _read_tasks_file()
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if priority:
        tasks = [t for t in tasks if t["priority"] == priority]
    return tasks 