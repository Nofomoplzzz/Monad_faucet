from loguru import logger
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
        try:
            token = utils.cloudflare()
            json_data = {
                'address': utils.get_account_address(private_key=self.client.private_key),
                'visitorId': utils.visitor_id(),
                'cloudFlareResponseToken': f'{token["code"]}'
            }
            logger.info(
                f'Profile: {self.client.profile}  Отправляю запрос на клейм...')
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=200)) as session:
                async with session.post(
                        url='https://faucet-claim-2.monadinfra.com/',
                        headers=self.headers,
                        json=json_data,
                        proxy=self.client.proxy
                ) as response:
                    response_captcha = await response.json()
                    if 'Request' in response_captcha['message'] or response.status == 200:
                        logger.success(
                            f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Drip successfully {response_captcha}')
                    else:
                        logger.warning(
                            f'Profile: {self.client.profile} {utils.get_account_address(self.client.private_key)} Not claimed {response_captcha}')
        except aiohttp.ClientError as e:
            logger.error(
                f'Профиль {self.client.profile} Ошибка клиента: {e}')
        except aiohttp.ClientOSError as e:
            logger.error(
                f"Профиль {self.client.profile} Ошибка соединения: {e}")
        except Exception as e:
            logger.error(
                f"Профиль {self.client.profile} Произошла ошибка: {e}")
