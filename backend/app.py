from fastapi import FastAPI
from backend.core.database import engine, Base
from backend.api.routes import router
from backend.core.logging_conf import logger
from backend.services.scheduler import start_scheduler, stop_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Python Beadandó – Weather API")
app.include_router(router)

@app.on_event("startup")
def on_startup():
    logger.info("App starting up…")
    start_scheduler()

@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()
    logger.info("App shutting down…")