from fastapi import FastAPI

from .api.routes import routers

app = FastAPI()

for router in routers:
    app.include_router(router)


@app.get("/")
def healthcheck() -> str:
    return "Hello, World!"
