"""
Utility module for managing tasks for users.

This module provides functions to read, add, and mark tasks as done.
Tasks are stored in JSON files, with each user having a separate file
named `{userid}.json` in the `tasks/` directory.

The `Task` dataclass defines the structure of a task.
"""
import json
import os
from dataclasses import asdict, dataclass
import yaml

# Define the directory where task files will be stored
# Can be overridden by TASKS_DATA_DIR environment variable
TASKS_DIR = os.getenv("TASKS_DATA_DIR", "tasks")

@dataclass
class Task:
    """Represents a single task with a title and a completion status."""
    title: str
    isDone: bool = False


def _get_task_file_path(userid: str) -> str:
    """Constructs the file path for a user's task file."""
    # Ensure the tasks directory exists
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR)
    return os.path.join(TASKS_DIR, f"{userid}.json")


def read_tasks(userid: str) -> str:
    """
    Reads all tasks for a given user and returns them as a YAML string.

    Args:
        userid: The ID of the user whose tasks are to be read.

    Returns:
        A YAML string representing the list of tasks, or "No tasks found"
        if the user has no tasks or the task file doesn't exist.
    """
    file_path = _get_task_file_path(userid)
    if not os.path.exists(file_path):
        return "No tasks found"
    try:
        with open(file_path, "r") as file:
            tasks_data = json.load(file)
        return yaml.dump(tasks_data)
    except json.JSONDecodeError:
        return "Error reading task file: Invalid JSON format"
    except Exception as e:
        return f"Error reading tasks: {str(e)}"


def mark_task_as_done(userid: str, title: str) -> str:
    """
    Marks a specific task as done for a given user.

    Args:
        userid: The ID of the user.
        title: The title of the task to mark as done.

    Returns:
        A confirmation message string.

    Raises:
        FileNotFoundError: If the user's task file does not exist.
        ValueError: If the task with the given title is not found.
    """
    file_path = _get_task_file_path(userid)
    if not os.path.exists(file_path):
        # Or consider creating an empty list if preferred
        raise FileNotFoundError(f"Task file not found for user {userid}.")

    try:
        with open(file_path, "r") as file:
            tasks = json.load(file)
    except json.JSONDecodeError:
        # If file is corrupted, treat as empty. Consider more robust error handling for production.
        tasks = [] 

    task_found = False
    for task_item in tasks:
        if task_item.get("title") == title:
            task_item["isDone"] = True
            task_found = True
            break

    if not task_found:
        raise ValueError(f"Task with title '{title}' not found.")

    try:
        with open(file_path, "w") as file:
            json.dump(tasks, file, indent=2)
        return "Successfully updated task"
    except Exception as e:
        return f"Error writing tasks: {str(e)}"


def add_task(userid: str, title: str) -> str:
    """
    Adds a new task for a given user.

    Args:
        userid: The ID of the user.
        title: The title of the new task.

    Returns:
        A confirmation message string.

    Raises:
        ValueError: If a task with the same title already exists.
    """
    file_path = _get_task_file_path(userid)
    tasks = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                # Handle empty or corrupted file by starting with an empty list
                content = file.read()
                if content.strip(): # Check if file is not empty
                    tasks = json.loads(content)
                else:
                    tasks = [] # File is empty, treat as no tasks
        except json.JSONDecodeError:
            # File is corrupted or not valid JSON, start fresh. Consider logging or more robust error handling.
            tasks = [] # Or: raise ValueError("Task file is corrupted.")
    
    # Check for existing task with the same title
    for task_item in tasks:
        if task_item.get("title") == title:
            raise ValueError(f"Task with title '{title}' already exists.")

    new_task_obj = Task(title=title)
    tasks.append(asdict(new_task_obj))

    try:
        with open(file_path, "w") as file:
            json.dump(tasks, file, indent=2)
        return "Successfully added task"
    except Exception as e:
        return f"Error writing tasks: {str(e)}"