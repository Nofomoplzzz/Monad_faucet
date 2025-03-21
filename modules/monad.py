import asyncio
import random
import re
from loguru import logger
from twocaptcha import TwoCaptcha
from client import Client
import aiohttp
import utils
import config
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

        self.token_headers = {
            'Host': 'testnet.monad.xyz',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': f'"Not:A-Brand";v="99", "Chromium";v="{self.version}"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Priority': 'u=0, i',
        }

    async def faucet_mon(self):
        try:
            logger.info(
                f'Profile: {self.client.profile} Решаю капчу....')

            result = TwoCaptcha(config.API_KEY)
            captcha = result.turnstile(sitekey='0x4AAAAAAA-3X4Nd7hf3mNGx', url='https://testnet.monad.xyz/')

            json_data = {
                'address': utils.get_account_address(private_key=self.client.private_key),
                'visitorId': utils.visitor_id(),
                'cloudFlareResponseToken': f'{captcha["code"]}'
            }

            logger.info(
                f'Profile: {self.client.profile}  Получаю токен верификации...')
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=200)) as session:
                async with session.get(
                        url='https://testnet.monad.xyz/',
                        headers=self.token_headers,
                        proxy=self.client.proxy
                ) as response:
                    match = re.findall(r'requestVerification.*', await response.text())
                    token = match[0][35:99]
                    timestamp = match[0][118:131]
                    self.headers['x-request-timestamp'] = timestamp
                    self.headers['x-request-verification-token'] = token

                async with session.post(
                        url='https://faucet-claim.monadinfra.com/',
                        headers=self.headers,
                        json=json_data,
                        proxy=self.client.proxy
                ) as response:
                    response_captcha = response.status
                    if response_captcha == 200:
                        logger.success(
                            f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Drip successfully {await response.json()}')
                    else:
                        logger.warning(
                            f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Not claimed {await response.json()}')
                    await asyncio.sleep(random.randint(1, 15))
        except aiohttp.ClientError as e:
            logger.error(
                f'Профиль {self.client.profile} Ошибка клиента: {e}')
        except aiohttp.ClientOSError as e:
            logger.error(
                f"Профиль {self.client.profile} Ошибка соединения: {e}")
        except Exception as e:
            logger.error(
                f"Профиль {self.client.profile} Произошла ошибка: {e}")
