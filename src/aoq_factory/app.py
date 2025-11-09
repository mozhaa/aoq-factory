from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def healthcheck() -> str:
    return "Hello, World!"
