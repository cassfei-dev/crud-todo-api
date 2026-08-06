from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator



tasks = [
    {"id": 1, "title": "Wash dishes", "done": True},
    {"id": 2, "title": "Clean bedroom", "done": False},
    {"id": 3, "title": "Shower", "done": False}
]

nextId = max([t["id"] for t in tasks], default=0) + 1

myApp = FastAPI()

@myApp.get("/")
def door():
    """Show basic API info: name, version, and available endpoints."""
    return {
        "name": "Task API",
        "version":"1,0",
        "endpoints": ["/tasks"]
    }

@myApp.get("/health")
def health():
    """Check if the API is running."""
    return {
        "status": "ok"
    }

@myApp.get("/tasks")
def get_tasks():
    """List all tasks."""
    return tasks

@myApp.get("/tasks/{taskId}")
def getTask(taskId: int):
    """Get a single task by its id. Returns 404 if not found."""
    for task in tasks:
        if task["id"] == taskId:
            return task
    raise HTTPException(status_code=404, detail=f"Task {taskId} not found")

@myApp.post("/tasks", status_code=201)
def createTask(task: dict):
    """Create a new task with a title. Returns the created task with status 201. Empty or missing title returns 400."""
    global nextId
    title = task.get("title", "").strip()

    if not title:
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")

    newTask = {"id": nextId, "title": title, "done": False}
    tasks.append(newTask)
    nextId += 1
    return newTask

@myApp.put("/tasks/{taskId}")
def updateTask(taskId: int, task: dict):
    """Update an existing task by its id. Returns the updated task. Empty or missing title returns 400."""
    for existingTask in tasks:
        if existingTask["id"] == taskId:
            title = task.get("title", "").strip()
            if not title and "title" in task:
                raise HTTPException(status_code=400, detail="Title cannot be empty")
            if not title and "title" not in task and "done" not in task:
                raise HTTPException(status_code=400, detail="Provide a title and/or done value")
            if title:
                existingTask["title"] = title
            existingTask["done"] = task.get("done", existingTask["done"])
            return existingTask

    raise HTTPException(status_code=404, detail=f"Task {taskId} not found")

@myApp.delete("/tasks/{taskId}", status_code=204)
def deleteTask(taskId: int):
    """Delete a task by its id. Returns 204 if successful, 404 if not found."""
    for i, task in enumerate(tasks):
        if task["id"] == taskId:
            tasks.pop(i)
            return
        
    raise HTTPException(status_code=404, detail=f"Task {taskId} not found")