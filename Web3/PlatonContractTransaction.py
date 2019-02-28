# -*- coding: UTF-8 -*-
"""
@author: Alex
@time: 2018/12/6 16:59
@usage:platon合约部署、合约交易
"""
import json
import rlp
import PlatonEncoder
import ethereum.tools.keys as keys

from hexbytes import HexBytes
from web3 import Web3
from Event import Event
from web3.eth import Eth

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
        txType = PlatonEncoder.encodeType(txType)
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
        txType = PlatonEncoder.encodeType(txType)
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


if __name__ == '__main__':
    private_key = getPrivateKey(
        'D:\\contract\\UTC--2018-11-08T08-15-13.838161646Z--a1e7f74f970352a801b0c942c7a1be0c4085569e', '123456')
    '''初始化web3'''
    wt = PlatonContractTransaction('http://192.168.9.180:6789')
    address = wt.w3.toChecksumAddress('a1e7f74f970352a801b0c942c7a1be0c4085569e')
    '''部署合约'''
    # resp = wt.contractDeploy(1, getBytecode(r'D:\contract\Fibonacci.wasm'),
    #                          getAbiBytes(r'D:\contract\Fibonacci.cpp.abi.json'),
    #                          wt.eth.coinbase)
    # result = wt.eth.waitForTransactionReceipt(resp)
    # contractAddress = result['contractAddress']
    # print(contractAddress)
    '''发送交易'''
    # contractAddress = '0x5030bb42Ec3811B6E5F28C571ab09abBaEE396E3'
    # dataList = [PlatonEncoder.encodeType(2), PlatonEncoder.encodeString('set'), PlatonEncoder.encodeInt('uint64',-1)]
    # # dataList = [2, 'set', '[B@1da2cb77']
    #             # PlatonEncoder.encodeString(wt.w3.eth.coinbase),
    #             # PlatonEncoder.encodeString('0x0b64b46a2700979c71465d5113c8005d4c0e9e45'),
    # transResp = wt.contractTransaction(wt.w3.eth.coinbase, contractAddress, dataList)
    # result = wt.w3.eth.waitForTransactionReceipt(transResp)
    # print(result)
    '''查看eventData'''
    # topics = result['logs'][0]['topics']
    # print(topics)
    # data = result['logs'][0]['data']
    # print(data)
    # topics = [HexBytes('0xb56cc38227e362e1290f786708a79390d7c42c70892212fd4457075580b6aba4')]
    # data = '0xd688ffffffffffffff9c8c73657420737563636573732e'
    # event = Event(json.load(open(r'D:\contract\Fibonacci.cpp.abi.json')))
    # eventData = event.eventData(topics, data)
    # print(eventData)
    '''call方法查询交易'''
    # contractAddress = '0x43355C787c50b647C425f594b441D4BD751951C1'
    # dataList = [PlatonEncoder.encodeType(2), PlatonEncoder.encodeString('getBalance'),
    #             PlatonEncoder.encodeString(wt.w3.eth.coinbase)]
    # wt.contractCall(wt.w3.eth.coinbase, contractAddress, dataList)
    '''部署签名合约'''
    # resp = wt.signedContractDeploy(1, getBytecode(r'D:\contract\inputtest.wasm'),getAbiBytes(r'D:\contract\inputtest.cpp.abi.json'),'0xa1e7f74F970352A801B0c942c7A1BE0C4085569e', private_key)
    # result = wt.eth.waitForTransactionReceipt(resp)
    # contractAddress = result['contractAddress']
    # print('合约地址是：', contractAddress)
    '''签名合约发送交易'''
    contractAddress = '0xAbf9da680b92C00Ea81A165b11E95b4a70246e35'
    dataList = [PlatonEncoder.encodeType(2), PlatonEncoder.encodeString('set'), PlatonEncoder.encodeInt('uint64',-100)]
    #             # PlatonEncoder.encodeString(wt.w3.eth.coinbase),
    #             # PlatonEncoder.encodeString('0x0b64b46a2700979c71465d5113c8005d4c0e9e45'),
    transResp = wt.signedContractTransaction('0xa1e7f74F970352A801B0c942c7A1BE0C4085569e', contractAddress, dataList, private_key)
    result = wt.w3.eth.waitForTransactionReceipt(transResp)
    print(result)
    topics = result['logs'][0]['topics']
    print(topics)
    data = result['logs'][0]['data']
    print(data)
    event = Event(json.load(open(r'D:\contract\Fibonacci.cpp.abi.json')))
    eventData = event.eventData(topics, data)
    print(eventData)
