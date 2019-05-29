from eth_utils.curried import (
    apply_formatters_to_dict,
    apply_key_map,
)
from hexbytes import (
    HexBytes,
)

from client_sdk_python.middleware.formatting import (
    construct_formatting_middleware,
)
from client_sdk_python.utils.toolz import (
    compose,
)

remap_geth_poa_fields = apply_key_map({
    'extraData': 'proofOfAuthorityData',
})

pythonic_geth_poa = apply_formatters_to_dict({
    'proofOfAuthorityData': HexBytes,
})

geth_poa_cleanup = compose(pythonic_geth_poa, remap_geth_poa_fields)

geth_poa_middleware = construct_formatting_middleware(
    result_formatters={
        'platon_getBlockByHash': geth_poa_cleanup,
        'platon_getBlockByNumber': geth_poa_cleanup,
    },
)
