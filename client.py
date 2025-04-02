class Client:
    private_key: str
    rpc: str
    proxy: str | None

    def __init__(self,
                 private_key: str,
                 rpc: str, proxy: str | None = None,
                 profile: str | None = None,):
        self.private_key = private_key
        self.rpc = rpc
        self.proxy = proxy
        self.profile = profile

        if self.proxy:
            if '://' not in self.proxy:
                self.proxy = f'http://{self.proxy}'
