import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as StarletteHTTPException


def init_db():
    """Initialize the SQLite database and create the tasks table if it doesn't exist."""
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", 
        [
            ("Wash dishes", 1),
            ("Clean bedroom", 0),
            ("Shower", 0)
        ])
        conn.commit()
    conn.close()

def get_db_connection():
    """Open a new connection to tasks.db with rows returned as dict-like objects."""
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

tasks = [
    {"id": 1, "title": "Wash dishes", "done": True},
    {"id": 2, "title": "Clean bedroom", "done": False},
    {"id": 3, "title": "Shower", "done": False}
]

nextId = max([t["id"] for t in tasks], default=0) + 1

myApp = FastAPI()

@myApp.exception_handler(StarletteHTTPException)
def custom_http_exception_handler(request, exc):
    """Return errors as {error:"message"} instead of FastAPI's default error message format."""
    return JSONResponse(status_code=exc.status_code,content={"error": exc.detail},)

@myApp.on_event("startup")
def startup_event():
    """Run the database initialization on startup."""
    init_db()

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
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@myApp.get("/tasks/{taskId}")
def getTask(taskId: int):
    """Get a single task by its id. Returns 404 if not found."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (taskId,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return dict(row)

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

