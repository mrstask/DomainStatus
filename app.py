import asyncio
from typing import List
import sqlalchemy
import uvicorn as uvicorn
from fastapi import FastAPI

from models import Item, Category, database, metadata
from settings import DATABASE_URL
import aiohttp


from time import time
from typing import List

from fastapi import FastAPI
from httpx import AsyncClient

client = AsyncClient()
app = FastAPI()
app.state.database = database


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


URL = "http://httpbin.org/uuid"


async def request(session):
    async with session.get(URL) as response:
        return await response.text()


async def task():
    async with aiohttp.ClientSession() as session:
        tasks = [request(session) for _ in range(100)]
        result = await asyncio.gather(*tasks)
        print(result)


@app.get('/')
async def f():
    queue = asyncio.Queue()
    start = time()
    await task()
    print("time: ", time() - start)




# @app.get("/items/", response_model=List[Item])
# async def get_items():
#     items = await Item.objects.select_related("category").all()
#     return items
#
#
# @app.post("/items/", response_model=Item)
# async def create_item(item: Item):
#     await item.save()
#     return item
#
#
# @app.post("/categories/", response_model=Category)
# async def create_category(category: Category):
#     await category.save()
#     return category
#
#
# @app.put("/items/{item_id}")
# async def get_item(item_id: int, item: Item):
#     item_db = await Item.objects.get(pk=item_id)
#     return await item_db.update(**item.dict())
#
#
# @app.delete("/items/{item_id}")
# async def delete_item(item_id: int, item: Item = None):
#     if item:
#         return {"deleted_rows": await item.delete()}
#     item_db = await Item.objects.get(pk=item_id)
#     return {"deleted_rows": await item_db.delete()}



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
