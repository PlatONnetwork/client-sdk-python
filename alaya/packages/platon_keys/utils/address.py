from alaya.packages.eth_utils import (
    keccak,
)
from alaya.packages.platon_keys.utils.bech32 import encode

MIANNETHRP = "atp"
TESTNETHRP = "atx"


def public_key_bytes_to_address(public_key_bytes: bytes) -> bytes:
    return keccak(public_key_bytes)[-20:]


def address_bytes_to_address(address_bytes: bytes) -> str:
    witprog = list(address_bytes)
    return encode(MIANNETHRP, witprog)


def address_bytes_to_test_address(address_bytes: bytes) -> str:
    witprog = list(address_bytes)
    return encode(TESTNETHRP, witprog)
