import asyncio
from time import time
import aiohttp
import uvicorn
from email.utils import parsedate_to_datetime

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
    try:
        return parsedate_to_datetime(date_string)
    except TypeError as e:
        print(f"{e}")


async def request(session):
    pk, url = await queue.get()
    domain = Domain.objects.filter(pk=pk)
    try:
        async with session.get(url) as response:
            try:
                text = await response.text()
            except UnicodeDecodeError as e:
                print(f"{url} {e.reason}")
                text = None
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
            print(f"{url} OK")
    except ClientResponseError as e:
        print(f"{url} {e.message}")
        await domain.update(status_code=e.status)

    except ClientConnectorError as e:
        print(f"{url} {e.strerror}")
        await domain.update(status_code=419)

    except ServerDisconnectedError as e:
        print(f"{url} + {e.message}")
        await domain.update(status_code=420)

    except TimeoutError as e:
        print(f"{url} + {e.errno}")
        await domain.update(status_code=421)


async def task():
    async with aiohttp.ClientSession() as session:
        tasks = [request(session) for _ in range(queue.qsize())]
        await asyncio.gather(*tasks)


@app.get('/')
async def f(threads: int):
    domains = await Domain.objects.filter(status_code=None).limit(threads).all()
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
