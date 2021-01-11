import asyncio
from time import time

from models import Zone, Domain


async def populate_domains_to_database(file_name: str, limit: int):
    with open(file_name, 'r') as f:
        domains = f.read().split('\n')
        i = 0
        while i < limit:
            zone = '.'.join(domains[i].split('.')[1:])
            if not await Zone.objects.filter(name=zone).exists():
                zone = Zone(name=zone)
                await zone.save()

            domain_name = domains[i].split('.')[0]
            domain = Domain(name=domain_name)
            domain.zone = zone
            await domain.save()
            i += 1


if __name__ == '__main__':
    start = time()
    asyncio.run(populate_domains_to_database('ua.txt', 5))
    print("time: ", time() - start)
