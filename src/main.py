from logging import warning
import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from api.v1.endpoints import router as v1_router
from api.v1.auth import router as auth_router


if not load_dotenv():
    warning('No env variables loaded')

app = FastAPI()
app.mount("/frontend",
          StaticFiles(directory="frontend"),
          name="frontend")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("frontend/index.html", "r") as f:
        return f.read()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(v1_router, prefix="/api/v1", tags=["v1"])

uvicorn.run(app, host="0.0.0.0", port=80)
