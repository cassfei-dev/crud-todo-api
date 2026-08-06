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
    return {
        "name": "Task API",
        "version":"1,0",
        "endpoints": ["/tasks"]
    }

@myApp.get("/health")
def health():
    return {
        "status": "ok"
    }

@myApp.get("/tasks")
def get_tasks():
    return tasks

@myApp.get("/tasks/{taskId}")
def getTask(taskId: int):
    for task in tasks:
        if task["id"] == taskId:
            return task
    raise HTTPException(status_code=404, detail=f"Task {taskId} not found")

@myApp.post("/tasks", status_code=201)
def createTask(task: dict):
    global nextId
    title = task.get("title", "").strip()

    if not title:
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")

    newTask = {"id": nextId, "title": title, "done": False}
    tasks.append(newTask)
    nextId += 1
    return newTask

    