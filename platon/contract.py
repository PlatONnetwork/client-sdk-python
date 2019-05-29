# -*- coding: UTF-8 -*-
"""
@author: Alex
@time: 2018/12/6 16:59
@usage:platon合约部署、合约交易
"""
import json
import rlp
from platon import encoder
import ethereum.tools.keys as keys

from hexbytes import HexBytes
from client_sdk_python import Web3
from client_sdk_python.eth import Eth

def getPrivateKey(keystorePath, password):
    """
    获取私钥
    :param keystore_path: keystore钱包json文件路径
    :param password: 钱包密码
    :return:钱包私钥
    """
    privateKey = keys.decode_keystore_json(json.load(open(keystorePath)), password)
    return privateKey


def getBytecode(binFilePath):
    with open(binFilePath, 'rb') as f:
        bytecode = bytearray(f.read())
        return bytecode


def getAbiBytes(abiPath):
    with open(abiPath, 'r') as a:
        abi = a.read()
        abi = abi.replace('\r\n', '')
        abi = abi.replace('\n', '')
        bytecode = bytearray(abi, encoding='utf-8')
    return bytecode


class PlatonContractTransaction:
    """
    合约创建参数list结构：[txType,byteCode,abi]
    合约调用参数list结构：[txType,funcName,params01,params02,...]
    """

    def __init__(self, URL):
        self.w3 = Web3(Web3.HTTPProvider(URL))
        self.eth = Eth(self.w3)
        print('if the web3 isConnected : {}'.format(self.w3.isConnected()))

    def getSigedData(self, fromAddress, toAddress, dataList, privateKey):
        myNonce = self.eth.getTransactionCount(fromAddress, 'latest')
        data = rlp.encode(dataList)
        transactionDict = {'from': fromAddress,
                           'to': toAddress,
                           'gasPrice': '0x8250de00',
                           'gas': '0x1fffff',
                           'nonce': myNonce,
                           'data': data}
        signedTransactionDict = self.eth.account.signTransaction(transactionDict, privateKey)
        signedData = signedTransactionDict.rawTransaction
        return signedData

    def contractDeploy(self, txType, bytecode, abi, fromAddress):
        """
        非签名合约部署
        :param txType:取值类型 0-主币转账交易 1-合约发布 2-合约调用 3-投票 4-权限
        :param bytecode:合约bin(wasm文件)，二进制数组
        :param abi:abi(json文件)，二进制数组
        :param fromAddress:钱包地址
        :return:合约部署transactionHash
        """
        txType = encoder.encodeType(txType)
        rlpList = [txType, bytecode, abi]
        data = rlp.encode(rlpList)
        transactionHash = self.eth.sendTransaction(
            {'from': fromAddress, 'gas': '7a1200', 'gasPrice': '218711a00', 'data': data})
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash

    def contractTransaction(self, fromAddress, contractAddress, dataList):
        """
        非签名合约交易
        :param fromAddress: 钱包地址
        :param contractAddress: 合约地址
        :param dataList: 参数list
        :return:合约交易transactionHash
        """
        data = rlp.encode(dataList)
        transactionHash = self.eth.sendTransaction(
            {'from': fromAddress, 'to': contractAddress, 'gas': '0x1fffff', 'gasPrice': '0x8250de00', 'data': data})
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash

    def contractCall(self, fromAddress, contractAddress, dataList):
        """
        合约查询交易
        :param fromAddress:钱包地址
        :param contractAddress:合约地址
        :param dataList:参数list
        :return:
        """
        data = rlp.encode(dataList)
        recive = self.eth.call({'from': fromAddress, 'to': contractAddress, 'data': data})
        recive = HexBytes(recive).decode()
        return recive

    def signedContractDeploy(self, txType, bytecode, abi, fromAddress, privateKey):
        """
        签名部署合约
        :param txType:取值类型 0-主币转账交易 1-合约发布 2-合约调用 3-投票 4-权限
        :param bytecode:bytecode，二进制数组
        :param abi:abi，二进制数组
        :param fromAddress:钱包地址
        :param privateKey:钱包私钥
        :return:transactionHash
        """
        txType = encoder.encodeType(txType)
        bytecode = bytecode
        abi = abi
        rlpList = [txType, bytecode, abi]
        signedData = self.getSigedData(fromAddress, '',rlpList, privateKey)
        transactionHash = self.eth.sendRawTransaction(signedData)
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash

    def signedContractTransaction(self, fromAddress, contractAddress, dataList, privateKey):
        """
        签名合约交易
        :param fromAddress:钱包地址
        :param contractAddress:合约地址
        :param dataList:参数list
        :param privateKey:钱包私钥
        :return:transactionHash
        """
        signedData = self.getSigedData(fromAddress, contractAddress, dataList, privateKey)
        transactionHash = self.eth.sendRawTransaction(signedData)
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash


