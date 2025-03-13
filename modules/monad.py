import asyncio
import random
from loguru import logger
from twocaptcha import TwoCaptcha
import config
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
            'content-type': 'application/json',
            'origin': 'https://testnet.monad.xyz',
            'priority': 'u=1, i',
            'referer': 'https://testnet.monad.xyz/',
            'sec-ch-ua': f'"Not(A:Brand";v="99", "Google Chrome";v="{self.version}", "Chromium";v="{self.version}"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.user_agent
        }

    async def faucet_mon(self):
        logger.info(
            f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Решаю капчу....')

        result = TwoCaptcha(config.API_KEY)
        captcha = result.turnstile(sitekey='0x4AAAAAAA-3X4Nd7hf3mNGx',
                                   url='https://testnet.monad.xyz/'
                                   )

        json_data = {
            'address': utils.get_account_address(private_key=self.client.private_key),
            'visitorId': utils.visitor_id(),
            'cloudFlareResponseToken': f'{captcha["code"]}'
        }
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=200)) as session:
                async with session.post(
                        url='https://testnet.monad.xyz/api/claim',
                        headers=self.headers,
                        json=json_data,
                        proxy=self.client.proxy
                ) as response:
                    response_captcha = await response.json()
                    print(f'Profile: {self.client.profile} {response_captcha}')
                    await asyncio.sleep(random.randint(1, 15))
        except aiohttp.ClientError as e:
            print(f"Профиль {self.client.profile} Ошибка клиента: {e}")
        except aiohttp.ClientOSError as e:
            print(f"Профиль {self.client.profile} Ошибка соединения: {e}")
        except Exception as e:
            print(f"Профиль {self.client.profile} Произошла ошибка: {e}")

    async def balik(self):
        balance = await self.client.w3.eth.get_balance(self.client.account.address)
        await self.client.w3.provider.disconnect()
        print(self.client.profile, self.client.account.address, self.client.w3.from_wei(balance, 'ether'))
