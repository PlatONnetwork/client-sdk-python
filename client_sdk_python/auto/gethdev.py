from client_sdk_python import (
    IPCProvider,
    Web3,
)
from client_sdk_python.middleware import (
    geth_poa_middleware,
)
from client_sdk_python.providers.ipc import (
    get_dev_ipc_path,
)

w3 = Web3(IPCProvider(get_dev_ipc_path()))
w3.middleware_stack.inject(geth_poa_middleware, layer=0)
