"""FastAPI 应用入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config, routes

app = FastAPI(title="Crypto Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

config.ensure_dirs()

app.include_router(routes.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"ok": True}
