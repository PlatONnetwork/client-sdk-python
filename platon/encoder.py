# -*- coding: UTF-8 -*-
"""
@author: Alex
@time: 2018/12/6 16:59
@usage:platon encode工具
"""
import re


def encodeType(i: int):
    return encodeInt('int64', i)


def encodeInt(typ, i: int):
    """
    int类型encode
    :param typ: int类型：int64\int32\int16\int8
    :param i: int数字
    :return:HexBytes
    """
    num = int(re.sub('\D', '', typ)) // 8
    try:
        intByte = i.to_bytes(length=num, byteorder='big', signed=True)
        return intByte

    except:
        raise Exception('unsupported type')


def encodeString(abiStr: str):
    if isinstance(abiStr, str):
        byteStr = bytearray(abiStr, 'utf-8')
        return byteStr
    else:
        raise Exception('please input a str')


def encodeBoolean(boolean: bool):
    if isinstance(boolean, bool):
        boolByte = bytearray(boolean)
        return boolByte
    else:
        raise Exception('please input a bool')


if __name__ == '__main__':
    encodeInt('uint64', 20)
