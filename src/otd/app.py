from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from otd import messenger, scheduler
from otd.log import LOGGER


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    LOGGER.info("Running application startup.")
    app.state.scheduler = scheduler.Scheduler()
    app.state.scheduler.add_job(messenger.dispatch_pending_messages)
    app.state.scheduler.start()

    yield

    LOGGER.info("Running application shutdown.")
    app.state.scheduler.stop()


app = FastAPI(lifespan=lifespan)


# TODO(Caleb): Add type annotations
@app.get("/")
async def index():
    return {"status": "ok"}
