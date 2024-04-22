from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4
from beanie import Document, Indexed, Insert, Link, Replace, SaveChanges, Update, before_event
from pydantic import Field
import pymongo

from models.user_model import User
from pymongo import TEXT

class Todo(Document):
    todo_id: Annotated[UUID, Field(default_factory=uuid4, unique=True)]
    status: Annotated[bool, Field(default=False)]
    title: Annotated[str , Indexed(index_type=TEXT)]
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    owner: Link[User] 


    def __repr__(self) -> str:
        return f"<Todo {self.title}>"

    def __str__(self) -> str:
        return self.title

    def __hash__(self) -> int:
        return hash(self.title)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Todo):
            return self.todo_id == other.todo_id
        return False
    
    @before_event([Replace, Update])
    def update_update_at(self):
        print("Before event hook triggered!")
        self.updated_at = lambda: datetime.now(timezone.utc)
        

    class Settings:
        name = "todos"
        indexes = [
            [
                ("title", pymongo.TEXT)
            ]
        ]
        