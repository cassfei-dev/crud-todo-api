from fastapi import FastAPI, HTTPException

tasks = [
    {"id": 1, "title": "Wash dishes", "done": True},
    {"id": 2, "title": "Clean bedroom", "done": False},
    {"id": 3, "title": "Shower", "done": False}
]

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
