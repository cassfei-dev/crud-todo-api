from fastapi import FastAPI

myApp = FastAPI()

@myApp.get("/")
def hello():
    return{"message": "Hello World!"}