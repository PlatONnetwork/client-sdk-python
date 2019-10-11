from client_sdk_python.utils.normalizers import (
    abi_ens_resolver,
)
from client_sdk_python.utils.rpc_abi import (
    RPC_ABIS,
    abi_request_formatters,
)

from .formatting import (
    construct_formatting_middleware,
)


def name_to_address_middleware(w3):
    normalizers = [
        abi_ens_resolver(w3),
    ]
    return construct_formatting_middleware(
        request_formatters=abi_request_formatters(normalizers, RPC_ABIS)
    )
