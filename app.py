import asyncio
from time import time
import aiohttp
import uvicorn
from datetime import datetime

from aiohttp import ClientResponseError, ClientConnectorError, ServerDisconnectedError
from fastapi import FastAPI

from models import database, Domain

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


def parse_datetime(date_string: str):
    if 'GMT' in date_string:
        return datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S GMT')
    else:
        pass


async def request(session):
    pk, url = await queue.get()
    domain = Domain.objects.filter(pk=pk)
    try:
        async with session.get(url) as response:
            text = await response.text()
            last_modified = response.headers.get('Last-Modified')
            if last_modified:
                last_modified = parse_datetime(last_modified)
            await domain.update(status_code=response.status,
                                www=True if 'www' in response.real_url.host else False,
                                ssl=True if response.real_url.scheme == 'https' else False,
                                server=response.headers.get('server'),
                                content_type=response.content_type,
                                content_length=response.content_length,
                                encoding=response.charset,
                                last_modified=last_modified,
                                text=text)
    except ClientResponseError as e:
        print(url + e.message)
        await domain.update(status_code=e.status)

    except ClientConnectorError as e:
        print(url + e.strerror)
        await domain.update(status_code=419)

    except ServerDisconnectedError as e:
        print(url + e.message)
        await domain.update(status_code=420)



async def task():
    async with aiohttp.ClientSession() as session:
        tasks = [request(session) for _ in range(queue.qsize())]
        result = await asyncio.gather(*tasks)


@app.get('/')
async def f():
    domains = await Domain.objects.filter(status_code=None).all()
    for domain in domains:
        url = f"http://{domain.domain_name}.{domain.zone.name}"
        await queue.put((domain.pk, url))
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
