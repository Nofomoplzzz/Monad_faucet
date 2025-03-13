import asyncio
from client import Client
from modules.monad import Monad
import csv


async def process_row(private_key, proxy, semaphore, profile):
    await semaphore.acquire()
    monad = Monad(
        Client(
            private_key=private_key,
            rpc='https://testnet-rpc.monad.xyz',
            proxy=proxy,
            profile=profile
        )
    )

    await monad.faucet_mon()
    # await monad.balik()
    semaphore.release()


async def main():
    # Количество потоков
    max_concurrent_tasks = 1
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    tasks = []
    with open('profiles.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            private_key = row['Private_Key']
            proxy = row['Proxy']
            profile = row['Profile']

            tasks.append(process_row(private_key, proxy, semaphore, profile))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
