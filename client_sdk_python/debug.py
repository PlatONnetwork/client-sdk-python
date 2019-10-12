from client_sdk_python.module import (
    Module,
)


class Debug(Module):
    def economicConfig(self):
        return self.web3.manager.request_blocking("debug_economicConfig", [])

    def getBuildMsg(self):
        return self.web3.manager.request_blocking("debug_getBuildMsg", [])

    def getReceiveMsg(self):
        return self.web3.manager.request_blocking("debug_getReceiveMsg", [])