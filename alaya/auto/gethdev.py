from alaya import (
    IPCProvider,
    Web3,
)
from alaya.middleware import (
    geth_poa_middleware,
)
from alaya.providers.ipc import (
    get_dev_ipc_path,
)

w3 = Web3(IPCProvider(get_dev_ipc_path()))
w3.middleware_stack.inject(geth_poa_middleware, layer=0)
