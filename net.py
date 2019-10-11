from client_sdk_python.module import (
    Module,
)
from client_sdk_python.utils.decorators import (
    deprecated_in_v5,
)


class Net(Module):
    @property
    def listening(self):
        return self.web3.manager.request_blocking("net_listening", [])

    @property
    def peerCount(self):
        return self.web3.manager.request_blocking("net_peerCount", [])

    @property
    @deprecated_in_v5
    def chainId(self):
        return None

    @property
    def version(self):
        return self.web3.manager.request_blocking("net_version", [])
