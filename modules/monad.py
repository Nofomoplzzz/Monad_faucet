import asyncio
import random
from loguru import logger
from twocaptcha import TwoCaptcha
from client import Client
import aiohttp
import utils
from fake_useragent import UserAgent


class Monad:
    def __init__(self, client: Client):
        self.client = client
        self.user_agent = UserAgent(platforms='desktop', os='Windows').chrome
        self.version = self.user_agent.split('Chrome/')[1].split('.')[0]

        self.headers = {
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://testnet.monad.xyz',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://testnet.monad.xyz/',
            'sec-ch-ua': f'"Not(A:Brand";v="99", "Google Chrome";v="{self.version}", "Chromium";v="{self.version}"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': self.user_agent
        }

    async def faucet_mon(self):
        logger.info(
            f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Решаю капчу....')

        result = TwoCaptcha('7f108abc2e46b1b25a0e9841dd7eee4c')
        captcha = result.turnstile(sitekey='0x4AAAAAAA-3X4Nd7hf3mNGx', url='https://testnet.monad.xyz/')

        json_data = {
            'address': utils.get_account_address(private_key=self.client.private_key),
            'visitorId': utils.visitor_id(),
            'cloudFlareResponseToken': f'{captcha["code"]}'
        }
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=200)) as session:
                async with session.post(
                        url='https://faucet-claim.monadinfra.com/',
                        headers=self.headers,
                        json=json_data,
                        proxy=self.client.proxy
                ) as response:
                    response_captcha = response.status
                    if response_captcha == 200:
                        logger.success(
                            f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Drip successfully {response_captcha}')
                    else:
                        logger.warning(
                            f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Not claimed {response_captcha}')
                    await asyncio.sleep(random.randint(1, 15))
        except aiohttp.ClientError as e:
            logger.error(
                f'Profile: {self.client.profile} Ошибка клиента: {e}')
        except aiohttp.ClientOSError as e:
            logger.error(
                f'Profile: {self.client.profile} Ошибка соединения: {e}')
        except Exception as e:
            logger.error(
                f'Profile: {self.client.profile} Произошла ошибка: {e}')

    async def send_transaction(self):
        # balance = await client.w3.eth.get_balance(client.account.address)
        # client.w3.from_wei(balance, 'ether')
        count_value = random.uniform(0.001, 0.035)

        logger.info(f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Отправляю транзакцию...')
        tx = await self.client.send_transaction(
            to=self.client.account.address,
            from_=self.client.account.address,
            value=self.client.w3.to_wei(count_value, 'ether'),
            max_priority_fee_per_gas=self.client.max_priority_fee()
        )


        if tx:
            try:
                await self.client.verif_tx(tx_hash=tx)
                logger.success(
                    f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Transaction success!! tx_hash: {tx.hex()}')
            except Exception as err:
                logger.warning(
                    f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Transaction error!! tx_hash: {tx.hex()}; error: {err}')
                raise ValueError(f'{self.client.profile} Ошибка транзакции')
        else:
            logger.error(f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Transaction error!!!')
            raise ValueError(f'{self.client.profile} Ошибка транзакции')

    async def   balik(self):
        balance = await self.client.w3.eth.get_balance(self.client.account.address)
        await self.client.w3.provider.disconnect()
        # print(f"{self.profile} {self.client.w3.from_wei(balance, 'ether')}")
        print(self.client.profile, self.client.account.address, self.client.w3.from_wei(balance, 'ether'))
