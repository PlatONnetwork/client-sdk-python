from client_sdk_python.packages.eth_utils import (
    keccak,
)
from client_sdk_python.packages.platon_keys.utils.bech32 import encode, decode, bech32_decode

DEFAULTHRP = "lat"


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


if __name__ == "__main__":
    address_bytes = bytes.fromhex('3D452519bB81D4D622840F710B54e074717780A3')
    address_bech32 = 'atx184zj2xdms82dvg5ypacsk48qw3ch0q9rhumxrm'
    print(address_bytes_to_bech32_address(address_bytes, DEFAULTHRP))
    print(bech32_address_to_address_bytes(address_bech32, DEFAULTHRP))