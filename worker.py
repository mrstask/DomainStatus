import asyncio
from datetime import datetime
from time import time
import aiohttp

from aiohttp import ClientResponseError, ClientConnectorError, ServerDisconnectedError

from helper import parse_datetime
from models import Domain
from settings import log

queue = asyncio.Queue()


async def request(session):
    pk, url = await queue.get()
    domain = Domain.objects.filter(pk=pk)
    try:
        async with session.get(url) as response:
            try:
                text = await response.text()
            except UnicodeDecodeError as e:
                log.error(f"{url} {e.reason}")
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
            log.debug(f"{url} OK")
    except ClientResponseError as e:
        log.error(f"{url} {e.message}")
        await domain.update(status_code=e.status)

    except ClientConnectorError as e:
        log.error(f"{url} {e.strerror}")
        await domain.update(status_code=419)

    except ServerDisconnectedError as e:
        log.error(f"{url} + {e.message}")
        await domain.update(status_code=420)

    except TimeoutError as e:
        log.error(f"{url} + {e.errno}")
        await domain.update(status_code=421)


async def parse_job(task_data, threads: int, quantity: int):
    domains = await Domain.objects.filter(status_code=None).filter(locked=False).limit(quantity).all()
    for domain in domains:
        url = f"http://{domain.domain_name}.{domain.zone.name}"
        await domain.update(locked=True)
        await queue.put((domain.pk, url))
    start = time()
    await create_task(threads)
    await task_data.update(finished=datetime.now())
    log.debug("time: ", time() - start)


async def create_task(threads: int):
    async with aiohttp.ClientSession() as session:
        tasks = [request(session) for _ in range(threads)]
        await asyncio.gather(*tasks)
