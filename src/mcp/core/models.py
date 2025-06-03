"""
Database models for MCP Agent PoC.

This module defines the SQLAlchemy models used throughout the application.
Each model represents a different type of data that can be stored and
manipulated by the agents.

Example:
    >>> from core.models import Task
    >>> task = Task(title="Example", description="A sample task")
    >>> session.add(task)
    >>> session.commit()
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tasks = relationship("Task", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    crawler_data = relationship("CrawlerData", back_populates="user")


class Task(Base):
    """Task model for storing task-related information.
    
    Attributes:
        id: Unique identifier for the task.
        title: Title of the task.
        description: Detailed description of the task.
        status: Current status of the task (e.g., 'pending', 'completed').
        priority: Priority level of the task (e.g., 'low', 'medium', 'high').
        due_date: Optional deadline for the task.
        created_at: Timestamp when the task was created.
        updated_at: Timestamp when the task was last updated.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")
    priority = Column(String(50), default="medium")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tasks")


class Memory(Base):
    """Memory model for storing agent memories.
    
    Attributes:
        id: Unique identifier for the memory.
        content: The content of the memory.
        meta_data: Additional metadata about the memory.
        created_at: Timestamp when the memory was created.
    """
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class CalendarEvent(Base):
    """Calendar event model for storing scheduled events.
    
    Attributes:
        id: Unique identifier for the event.
        title: Title of the event.
        description: Detailed description of the event.
        start_time: When the event starts.
        end_time: When the event ends.
        location: Optional location of the event.
        created_at: Timestamp when the event was created.
    """
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="calendar_events")


class CrawlerData(Base):
    """Crawler data model for storing web scraping results.
    
    Attributes:
        id: Unique identifier for the crawled data.
        url: The URL that was crawled.
        content: The content extracted from the URL.
        meta_data: Additional metadata about the crawl.
        created_at: Timestamp when the data was crawled.
    """
    __tablename__ = "crawler_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    url = Column(String(2048), nullable=False)
    content = Column(Text)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="crawler_data")


# Export all models
__all__ = ["Base", "User", "Task", "Memory", "CalendarEvent", "CrawlerData"]
