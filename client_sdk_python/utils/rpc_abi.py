from eth_utils import (
    to_dict,
)

from client_sdk_python.utils.abi import (
    map_abi_data,
)
from client_sdk_python.utils.formatters import (
    apply_formatter_at_index,
)
from client_sdk_python.utils.toolz import (
    curry,
)

TRANSACTION_PARAMS_ABIS = {
    'data': 'bytes',
    'from': 'address',
    'gas': 'uint',
    'gasPrice': 'uint',
    'nonce': 'uint',
    'to': 'address',
    'value': 'uint',
}

FILTER_PARAMS_ABIS = {
    'to': 'address',
    'address': 'address[]',
}

TRACE_PARAMS_ABIS = {
    'to': 'address',
    'from': 'address',
}

RPC_ABIS = {
    # platon
    'platon_call': TRANSACTION_PARAMS_ABIS,
    'platon_estimateGas': TRANSACTION_PARAMS_ABIS,
    'platon_getBalance': ['address', None],
    'platon_getBlockByHash': ['bytes32', 'bool'],
    'platon_getBlockTransactionCountByHash': ['bytes32'],
    'platon_getCode': ['address', None],
    'platon_getLogs': FILTER_PARAMS_ABIS,
    'platon_getStorageAt': ['address', 'uint', None],
    'platon_getTransactionByBlockHashAndIndex': ['bytes32', 'uint'],
    'platon_getTransactionByHash': ['bytes32'],
    'platon_getTransactionCount': ['address', None],
    'platon_getTransactionReceipt': ['bytes32'],
    'platon_getUncleCountByBlockHash': ['bytes32'],
    'platon_newFilter': FILTER_PARAMS_ABIS,
    'platon_sendRawTransaction': ['bytes'],
    'platon_sendTransaction': TRANSACTION_PARAMS_ABIS,
    'platon_sign': ['address', 'bytes'],
    # personal
    'personal_sendTransaction': TRANSACTION_PARAMS_ABIS,
    'personal_lockAccount': ['address'],
    'personal_unlockAccount': ['address', None, None],
    'personal_sign': [None, 'address', None],
    'trace_call': TRACE_PARAMS_ABIS,
}


@curry
def apply_abi_formatters_to_dict(normalizers, abi_dict, data):
    fields = list(set(abi_dict.keys()) & set(data.keys()))
    formatted_values = map_abi_data(
        normalizers,
        [abi_dict[field] for field in fields],
        [data[field] for field in fields],
    )
    formatted_dict = dict(zip(fields, formatted_values))
    return dict(data, **formatted_dict)


@to_dict
def abi_request_formatters(normalizers, abis):
    for method, abi_types in abis.items():
        if isinstance(abi_types, list):
            yield method, map_abi_data(normalizers, abi_types)
        elif isinstance(abi_types, dict):
            single_dict_formatter = apply_abi_formatters_to_dict(normalizers, abi_types)
            yield method, apply_formatter_at_index(single_dict_formatter, 0)
        else:
            raise TypeError("ABI definitions must be a list or dictionary, got %r" % abi_types)
