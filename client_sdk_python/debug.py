from client_sdk_python.module import (
    Module,
)
import json


class Debug(Module):
    def economicConfig(self):
        return json.loads(self.web3.manager.request_blocking("debug_economicConfig", []))

