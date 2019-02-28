# -*- coding: UTF-8 -*-
"""
@author: Alex
@time: 2018/12/6 16:59
@usage:解析event对象data内容
"""
import re
import rlp
from web3 import Web3


def rlpDecode(data):
    if data[:2] == '0x':
        return rlp.decode(bytes.fromhex(data[2:]))
    else:
        return rlp.decode(bytes.fromhex(data))


class Event:
    """
    初始化对象需要abi的json对象
    """

    def __init__(self, abi):
        self.eventAbi = [abi[i] for i in range(len(abi)) if abi[i]['type'] == 'event']

    def _eventContainType(self, topics):
        if isinstance(topics, list):
            topics = topics[0].hex()
        for event in self.eventAbi:
            if Web3.sha3(text=event['name']).hex() == topics:
                return event['inputs'], event['name']
            else:
                continue

    def eventData(self, topics, data):
        result = []
        decodedData = rlpDecode(data)
        if self._eventContainType(topics) is None:
            raise Exception('There is no match in your abi like this event topics :{}'.format(topics))
        else:
            eventContainType, eventName = self._eventContainType(topics)
            print(eventContainType,eventName)
        for i in range(len(eventContainType)):
            if re.search('int', eventContainType[i]['type'], re.IGNORECASE):
                decoded_item = int.from_bytes(decodedData[i], byteorder='big')
                if decoded_item == '':
                    result.append(0)
                else:
                    result.append(decoded_item)
            elif re.search('string', eventContainType[i]['type'], re.IGNORECASE):
                result.append(decodedData[i].decode('utf-8'))
            elif re.search('bool', eventContainType[i]['type'], re.IGNORECASE):
                result.append(bool(ord(decodedData[i])))
            else:
                raise Exception('unsupported type {}'.format(eventContainType[i]['type']))
        return {eventName: result}
