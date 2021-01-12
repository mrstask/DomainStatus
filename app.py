import asyncio

import uvicorn

from fastapi import FastAPI
from starlette.background import BackgroundTasks

from helper import add_task
from models import database
from worker import parse_job

app = FastAPI()
app.state.database = database

queue = asyncio.Queue()


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.post('/')
async def create_task(threads: int, quantity: int, background_tasks: BackgroundTasks):
    task_data = add_task(quantity, threads)
    background_tasks.add_task(parse_job, task_data, quantity=quantity, threads=threads)
    return dict(task_id=task_data['pk'])



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='debug')
