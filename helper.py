from datetime import datetime
from email.utils import parsedate_to_datetime

from models import Task
from settings import log


def parse_datetime(date_string: str):
    try:
        return parsedate_to_datetime(date_string)
    except TypeError as e:
        log.error(f"{e}")


async def add_task(to_parse: int, threads: int):
    task = Task(to_parse=to_parse, threads=threads, stated=datetime.now())
    await task.save()
    return task
