from fastapi import FastAPI

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
