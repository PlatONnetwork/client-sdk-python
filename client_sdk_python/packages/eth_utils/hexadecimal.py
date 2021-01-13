# String encodings and numeric representations

import binascii
import codecs
import re
import string
from typing import Any, AnyStr
import warnings

from eth_typing import HexStr

from .types import is_string, is_text

_HEX_REGEXP = re.compile("[0-9a-fA-F]*")


# Type ignored for `codecs.decode()` due to lack of mypy support for 'hex' encoding
# https://github.com/python/typeshed/issues/300
def decode_hex(value: str) -> bytes:
    if not is_text(value):
        raise TypeError("Value must be an instance of str")
    return codecs.decode(remove_0x_prefix(value), "hex")  # type: ignore #codecs.decode(remove_0x_prefix(value), "hex")


def encode_hex(value: AnyStr) -> HexStr:
    if not is_string(value):
        raise TypeError("Value must be an instance of str or unicode")
    binary_hex = codecs.encode(value, "hex")  # type: ignore
    return add_0x_prefix(HexStr(binary_hex.decode("ascii")))


def is_0x_prefixed(value: Any) -> bool:
    if not is_text(value):
        raise TypeError(
            "is_0x_prefixed requires text typed arguments. Got: {0}".format(repr(value))
        )
    return value.startswith("0x") or value.startswith("0X")


def remove_0x_prefix(value: HexStr) -> HexStr:
    if is_0x_prefixed(value):
        return HexStr(value[2:])
    return value


def add_0x_prefix(value: HexStr) -> HexStr:
    if is_0x_prefixed(value):
        return value
    return HexStr("0x" + value)


def is_hexstr(value: Any) -> bool:
    if not is_text(value):
        return False

    elif value.lower() == "0x":
        return True

    unprefixed_value = remove_0x_prefix(value)
    if len(unprefixed_value) % 2 != 0:
        value_to_decode = "0" + unprefixed_value
    else:
        value_to_decode = unprefixed_value

    if not _HEX_REGEXP.fullmatch(value_to_decode):
        return False

    try:
        value_as_bytes = codecs.decode(value_to_decode, "hex")  # type: ignore
    except binascii.Error:
        return False
    except TypeError:
        return False
    else:
        return bool(value_as_bytes)


def is_hex(value: Any) -> bool:
    if not is_text(value):
        raise TypeError(
            "is_hex requires text typed arguments. Got: {0}".format(repr(value))
        )
    elif value.lower() == "0x":
        return True

    unprefixed_value = remove_0x_prefix(value)
    if len(unprefixed_value) % 2 != 0:
        value_to_decode = "0" + unprefixed_value
    else:
        value_to_decode = unprefixed_value

    if not _HEX_REGEXP.fullmatch(value_to_decode):
        return False

    try:
        value_as_bytes = codecs.decode(value_to_decode, "hex")  # type: ignore
    except binascii.Error:
        return False
    except TypeError:
        return False
    else:
        return bool(value_as_bytes)
