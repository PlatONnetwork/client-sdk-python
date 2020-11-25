import pkg_resources
import sys

if sys.version_info < (3, 5):
    raise EnvironmentError("Python 3.5 or above is required")

from alaya.packages.platon_account.account import Account  # noqa: E402
from alaya.main import Web3  # noqa: E402
from alaya.providers.rpc import (  # noqa: E402
    HTTPProvider,
)
from alaya.providers.eth_tester import (  # noqa: E402
    EthereumTesterProvider,
)
from alaya.providers.tester import (  # noqa: E402
    TestRPCProvider,
)
from alaya.providers.ipc import (  # noqa: E402
    IPCProvider,
)
from alaya.providers.websocket import (  # noqa: E402
    WebsocketProvider,
)

try:
    __version__ = pkg_resources.get_distribution("alaya").version
except:
    __version__ = '0.13.2'

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
