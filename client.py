from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress, HexStr
from fake_useragent import UserAgent
from hexbytes import HexBytes
from web3 import AsyncWeb3, Web3
from web3.exceptions import Web3Exception
from web3.middleware import ExtraDataToPOAMiddleware


class Client:
    private_key: str
    rpc: str
    proxy: str | None
    w3: AsyncWeb3
    account: LocalAccount

    def __init__(self, private_key: str, rpc: str, proxy: str | None = None, profile: str | None = None):
        self.private_key = private_key
        self.rpc = rpc
        self.proxy = proxy
        self.profile = profile

        if self.proxy:
            if '://' not in self.proxy:
                self.proxy = f'http://{self.proxy}'

        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'user-agent': UserAgent().random
        }

        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
            endpoint_uri=self.rpc,
            request_kwargs={'proxy': self.proxy, 'headers': self.headers}
        ))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.account = self.w3.eth.account.from_key(self.private_key)

    def max_priority_fee(self, block: dict | None = None):
        w3 = Web3(provider=Web3.HTTPProvider(endpoint_uri=self.rpc))
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        if not block:
            block = w3.eth.get_block('latest')

        block_number = block['number']
        latest_block_transaction_count = w3.eth.get_block_transaction_count(block_number)
        max_priority_fee_per_gas_lst = []
        for i in range(latest_block_transaction_count):
            try:
                transaction = w3.eth.get_transaction_by_block(block_number, i)
                if 'maxPriorityFeePerGas' in transaction:
                    max_priority_fee_per_gas_lst.append(transaction['maxPriorityFeePerGas'])
            except Exception as err:
                print(err)

        if not max_priority_fee_per_gas_lst:
            max_priority_fee_per_gas = 0
            return max_priority_fee_per_gas
        else:
            max_priority_fee_per_gas_lst.sort()
            max_priority_fee_per_gas = max_priority_fee_per_gas_lst[len(max_priority_fee_per_gas_lst) // 2]
            return max_priority_fee_per_gas

    async def send_transaction(
            self,
            to: str | ChecksumAddress,
            data: str | HexStr | None = None,
            from_: str | ChecksumAddress | None = None,
            increase_gas: float = 1,
            value: int | None = None,
            eip1559: bool = True,
            max_priority_fee_per_gas: int | None = None
    ) -> HexBytes | None:
        if not from_:
            from_ = self.account.address

        tx_params = {
            'chainId': await self.w3.eth.chain_id,
            'nonce': await self.w3.eth.get_transaction_count(self.account.address),
            'from': AsyncWeb3.to_checksum_address(from_),
            'to': AsyncWeb3.to_checksum_address(to),
        }

        if eip1559:
            if max_priority_fee_per_gas is None:
                max_priority_fee_per_gas = await self.w3.eth.max_priority_fee
            base_fee = (await self.w3.eth.get_block('latest'))['baseFeePerGas']
            max_fee_per_gas = base_fee + max_priority_fee_per_gas
            tx_params['maxFeePerGas'] = max_fee_per_gas  # максимальная общая комиссия
            tx_params['maxPriorityFeePerGas'] = max_priority_fee_per_gas  # приоритетная комиссия майнеру
        else:
            tx_params['gasPrice'] = await self.w3.eth.gas_price

        if data:
            tx_params['data'] = data
        if value:
            tx_params['value'] = value

        gas = await self.w3.eth.estimate_gas(dict(tx_params))
        tx_params['gas'] = int(gas * increase_gas)

        sign = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        return await self.w3.eth.send_raw_transaction(sign.raw_transaction)

    async def verif_tx(self, tx_hash: HexBytes, timeout: int = 200) -> str:
        data = await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        if data.get('status') == 1:
            return tx_hash.hex()
        raise Web3Exception(f'transaction failed {data["transactionHash"].hex()}')
