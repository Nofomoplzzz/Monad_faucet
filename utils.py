import uuid
from anycaptcha import Solver, Service
from eth_account import Account



def visitor_id():
    generated_uuid = uuid.uuid4()
    formatted_uuid_lower = str(generated_uuid).lower().replace('-', '')
    return formatted_uuid_lower

def get_account_address(private_key: str):
    # Создаем аккаунт из закрытого ключа
    account = Account.from_key(private_key)
    adress = account.address
    return adress


async def get_captcha_token(site_key, url, api_key):
    solver = Solver(Service.TWOCAPTCHA, api_key=api_key)
    solv_captcha = await solver.solve_hcaptcha(
        site_key=site_key,
        page_url=url,
    )
    return solv_captcha.solution


