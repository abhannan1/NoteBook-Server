import logging
from typing import List
from uuid import UUID
from beanie import SortDirection
from fastapi import HTTPException, status
from models.todo_model import Todo
from models.user_model import User
from schemas.todo_schema import TodoCreate, TodoUpdate

class TodoService:

    @staticmethod
    async def get_todos_by_title(todo_title: str, user: User):
        todos = await Todo.find(Todo.title.lower() == todo_title.lower(), Todo.owner.id == user.id).to_list()
        if todos is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No such todos Found"
            )
        return todos
    
    @staticmethod
    async def list_todos(user: User) -> List[Todo]:
        todos = await Todo.find(Todo.owner.id == user.id).sort(('updated_at', SortDirection.DESCENDING)).to_list()
        if todos is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No todo Found"
            )
        return todos
    
    @staticmethod
    async def create_todo(user: User, data: TodoCreate) -> Todo:
        todo = Todo(**data.model_dump(exclude_unset=True), owner=user)
        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Could not Create todo"
            )        
        return await todo.insert()
    
    @staticmethod
    async def retrieve_todo(current_user: User, todo_id: UUID):
        todo = await Todo.find_one(Todo.todo_id == todo_id, Todo.owner.id == current_user.id)
        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Such todo Found"
            )
        return todo
    
    @staticmethod
    async def update_todo(current_user: User, todo_id: UUID, data: TodoUpdate):
        logging.debug(data)
        logging.error(data)
        print(data)
        todo = await TodoService.retrieve_todo(current_user, todo_id)
        await todo.update({"$set": data.model_dump(exclude_unset=True)})
        # await todo.save_changes()
        return todo
    
    @staticmethod
    async def delete_todo(current_user: User, todo_id: UUID) -> None:
        todo = await TodoService.retrieve_todo(current_user, todo_id)
        if todo:
            await todo.delete()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Such todo Found"
            )
        return None

