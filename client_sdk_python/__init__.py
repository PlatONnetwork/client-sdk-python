import pkg_resources
import sys

if sys.version_info < (3, 5):
    raise EnvironmentError("Python 3.5 or above is required")

from eth_account import Account  # noqa: E402
from client_sdk_python.main import Web3  # noqa: E402
from client_sdk_python.providers.rpc import (  # noqa: E402
    HTTPProvider,
)
from client_sdk_python.providers.eth_tester import (  # noqa: E402
    EthereumTesterProvider,
)
from client_sdk_python.providers.tester import (  # noqa: E402
    TestRPCProvider,
)
from client_sdk_python.providers.ipc import (  # noqa: E402
    IPCProvider,
)
from client_sdk_python.providers.websocket import (  # noqa: E402
    WebsocketProvider,
)

__version__ = pkg_resources.get_distribution("client_sdk_python").version

__all__ = [
    "__version__",
    "Web3",
    "HTTPProvider",
    "IPCProvider",
    "WebsocketProvider",
    "TestRPCProvider",
    "EthereumTesterProvider",
    "Account",
]
