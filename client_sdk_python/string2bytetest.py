from client_sdk_python.fvnhash import fnv1_64
from client_sdk_python.param_encode import (rlp_encode, to_binary, )
from hexbytes import (
    HexBytes,
)


# from client_sdk_python.utils.encoding import (
#     str2bytes,encodeaddress,tobech32address,)

def hexstr2bytes(address: str):
    pos = 0
    len_str = len(address)
    if len_str % 2 != 0:
        return None
    len_str = round(len_str / 2)
    hexa = []
    for i in range(len_str):
        s1 = address[pos:pos + 2]
        if s1 == '0x' or s1 == '0X':
            pos += 2
            continue
        sv = s1
        hexa.append(sv)
        pos += 2
    return hexa


def tostring_hex(arr: list):
    arrhex = ''
    if arr:
        for i in arr:
            arrhex = arrhex + i
        return arrhex
    else:
        return ''


def stringtohex(str1: bytes):
    strhex = []
    if str1:
        for i in str1:
            strhex = strhex + [hex(i).replace('0x', '')]
        return strhex
    else:
        return []
