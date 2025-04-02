import asyncio
from client import Client
from modules.monad import Monad
import csv



async def main():
    with open('profiles.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            private_key = row['Private_Key']
            proxy = row['Proxy']
            profile = row['Profile']

            monad = Monad(Client(
                private_key= private_key,
                rpc='https://testnet-rpc.monad.xyz',
                proxy = proxy,
                profile = profile
            ))

            await monad.faucet_mon()

if __name__ == "__main__":
    asyncio.run(main())
