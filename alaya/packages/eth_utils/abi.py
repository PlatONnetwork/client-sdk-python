from typing import Any, Dict

from .crypto import keccak
from alaya.param_encode import (
    stringfnv,
    rlp_encode,
    rlp_decode,
    hexstr2bytes,
    tostring_hex,
    stringtohex,
)
from eth_hash.auto import keccak as keccak_256
from hexbytes import (
    HexBytes,
)
def collapse_if_tuple(abi: Dict[str, Any]) -> str:
    """Converts a tuple from a dict to a parenthesized list of its types.

    >>> from alaya.packages.eth_utils.abi import collapse_if_tuple
    >>> collapse_if_tuple(
    ...     {
    ...         'components': [
    ...             {'name': 'anAddress', 'type': 'address'},
    ...             {'name': 'anInt', 'type': 'uint256'},
    ...             {'name': 'someBytes', 'type': 'bytes'},
    ...         ],
    ...         'type': 'tuple',
    ...     }
    ... )
    '(address,uint256,bytes)'
    """
    typ = abi["type"]
    if not typ.startswith("tuple"):
        return typ

    delimited = ",".join(collapse_if_tuple(c) for c in abi["components"])
    # Whatever comes after "tuple" is the array dims.  The ABI spec states that
    # this will have the form "", "[]", or "[k]".
    array_dim = typ[5:]
    collapsed = "({}){}".format(delimited, array_dim)

    return collapsed


def _abi_to_signature(abi: Dict[str, Any]) -> str:
    function_signature = "{fn_name}({fn_input_types})".format(
        fn_name=abi["name"],
        fn_input_types=",".join(
            [collapse_if_tuple(abi_input) for abi_input in abi.get("inputs", [])]
        ),
    )
    return function_signature


def function_signature_to_4byte_selector(event_signature: str) -> bytes:
    return keccak(text=event_signature.replace(" ", ""))[:4]


def function_abi_to_4byte_selector(function_abi: Dict[str, Any]) -> bytes:
    function_signature = _abi_to_signature(function_abi)
    return function_signature_to_4byte_selector(function_signature)


def event_signature_to_log_topic(event_signature: str) -> bytes:
    return keccak(text=event_signature.replace(" ", ""))


def event_abi_to_log_topic(event_abi: Dict[str, Any], vmtype=None) -> bytes:
    if vmtype:
        event_signature = event_abi['name']
        temp = stringtohex(bytes(event_signature, 'utf-8'))
        if len(temp)<32:
            data1=tostring_hex(temp)
            data1=data1.rjust(64,'0')
            data=HexBytes('0x'+data1)
        elif len(temp)>32:
            data1=[]
            for i in range(len(temp)):
                data1.append(int(event_signature[i], 16))
                data=keccak_256(bytes(data1))
        else:
            data=tostring_hex(temp)
            data=HexBytes('0x'+data)
        return data

        # event_signature = rlp_encode(temp)
        # event_signature1 = []
        # for i in range(len(event_signature)):
        #     event_signature1.append(int(event_signature[i], 16))
        # keccak_256(bytes(event_signature1))
        # return keccak_256(bytes(event_signature1))
    else:
        event_signature = _abi_to_signature(event_abi)
        return event_signature_to_log_topic(event_signature)
def topic_decode(data):
    temp = []
    for i in data[0]:
        if i:
            temp.append(bytes.decode(HexBytes(i)))
    data1 = ''.join(temp)
    return [data1]