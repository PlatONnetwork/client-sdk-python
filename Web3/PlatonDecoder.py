# -*- coding: UTF-8 -*-
"""
@author: Alex
@time: 2018/12/6 16:59
@usage:platon encode工具
"""
from hexbytes import HexBytes
import re


def encodeType(i: int):
    return decodeByte('int64', i)


def decodeByte(bt):
    """
    int类型encode
    :param typ: int类型：int64\int32\int16\int8
    :param i: int数字
    :return:HexBytes
    """
    try:
        return int.from_bytes(bt, byteorder = 'big')
    except:
        raise Exception('unsupported type')


def decodeString(abiStr: str):
    if isinstance(abiStr, str):
        return abiStr.decode('utf-8')
    else:
        raise Exception('please input a str')


def decodeBoolean(boolean: bool):
    if isinstance(boolean, bool):
        return bytearray(boolean)
    else:
        raise Exception('please input a bool')


def _encodeInt_exec(i, digit):
    cover = ''
    headStr = hex(i)[:2]
    hexNum = hex(i)[2:]
    if 2 ** (digit * 4) // 2 > i >= -(2 ** (digit * 4) // 2):
        for i in range(digit - len(hexNum)):
            cover += '0'
        result = headStr + cover + hexNum
        return result
    else:
        raise Exception('The number is out of range of its own data type')


def dec2Bin(dec):
    result = ''

    if dec:
        result = dec2Bin(dec // 2)
        return result + str(dec % 2)
    else:
        return result

if __name__ == '__main__':
    pass

