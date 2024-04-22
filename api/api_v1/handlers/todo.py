from typing import Annotated, List, cast
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from deps.user_deps import get_current_active_user
from models.todo_model import Todo
from models.user_model import User
from schemas.todo_schema import TodoCreate, TodoOut, TodoUpdate
from pymongo.errors import OperationFailure
from services.todo_services import TodoService


todo_router = APIRouter()

@todo_router.get("/", summary="", response_model=List[Todo])
async def get_todo_list(current_user: Annotated[User, Depends(get_current_active_user)])-> List[TodoOut]:
    def sorter(todo): 
        return todo.updated_at
    todos = await TodoService.list_todos(current_user)
    # todos = sorted(todos, key=sorter, reverse=True)
    # todos.sort(key=sorter)
    return todos

@todo_router.get("/{todo_id}", summary="Get a specific todo", response_model=TodoOut)
async def get_todo(todo_id: UUID ,current_user: Annotated[User, Depends(get_current_active_user)]):
    todo = await TodoService.retrieve_todo(current_user, todo_id)
    return todo


@todo_router.post('/create', summary="Create Todo", response_model=Todo)
async def create_todo(data: TodoCreate, current_user: User = Depends(get_current_active_user)):
    return await TodoService.create_todo(current_user, data)



@todo_router.put('/{todo_id}', summary="Update todo by todo_id", response_model=TodoOut)
async def update(todo_id: UUID, data: TodoUpdate, current_user: User = Depends(get_current_active_user)):
    try:
        return await TodoService.update_todo(current_user, todo_id, data)
    except OperationFailure:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="update failed"
        )
        


@todo_router.delete('/{todo_id}', summary="Delete todo by todo_id")
async def delete(todo_id: UUID, current_user: User = Depends(get_current_active_user)):
    try:
        print(todo_id)
        await TodoService.delete_todo(current_user, todo_id)
    except OperationFailure:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete, failed!"
        )
        
    return None
