from client_sdk_python.packages.eth_utils import (
    keccak,
)
from client_sdk_python.packages.platon_keys.utils.bech32 import encode, decode, bech32_decode

DEFAULTHRP = "lat"
BASE_ADDRESS = {'sta': '0x1000000000000000000000000000000000000002',
                'pip': '0x1000000000000000000000000000000000000005',
                'res': '0x1000000000000000000000000000000000000001',
                'del': '0x1000000000000000000000000000000000000006',
                'pen': '0x1000000000000000000000000000000000000004'
                }


def public_key_bytes_to_address(public_key_bytes: bytes) -> bytes:
    return keccak(public_key_bytes)[-20:]


def address_bytes_to_address(address_bytes: bytes) -> str:
    witprog = list(address_bytes)
    return encode(DEFAULTHRP, witprog)


def address_bytes_to_bech32_address(address_bytes: bytes, hrp=DEFAULTHRP) -> str:
    witprog = list(address_bytes)
    return encode(hrp, witprog)


def bech32_address_to_address_bytes(address_bytes: bytes, hrp=DEFAULTHRP) -> str:
    _, data = decode(hrp, address_bytes)
    return bytes(data).hex()
