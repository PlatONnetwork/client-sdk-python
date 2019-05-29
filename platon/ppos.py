'''
@Author: alex
@Date: 2019-2-21 16:30:41
@LastEditors: alex
@Description: file content
'''

import json
import os
import re

import rlp
from hexbytes import HexBytes
from client_sdk_python import Web3
from client_sdk_python.eth import Eth
from client_sdk_python.personal import Personal

from platon.event import Event


class PlatonPpos:
    def __init__(self, url, address, pwd, abi=os.path.abspath('./candidateConstract.json'),
                 vote_abi=os.path.abspath('./ticketContract.json')):
        self.web3 = Web3(Web3.HTTPProvider(url))
        if not self.web3.isConnected():
            raise Exception("节点连接失败")
        self.eth = Eth(self.web3)
        self.personal = Personal(self.web3)
        self.address = address
        if not self.personal.unlockAccount(self.address, pwd, 22222):
            raise Exception("账号解锁失败")
        self.abi = abi
        self.vote_abi = vote_abi
        self.value = 100

    def get_result(self, tx_hash, abi=None):
        result = self.eth.waitForTransactionReceipt(tx_hash)
        try:
            """查看eventData"""
            topics = result['logs'][0]['topics']
            data = result['logs'][0]['data']
            if abi == None:
                event = Event(json.load(open(self.abi)))
            else:
                event = Event(json.load(open(abi)))
            event_data = event.event_data(topics, data)
            return event_data
        except Exception as e:
            raise e

    def CandidateDeposit(self, nodeid, owner, fee, host, port, extra, value=None):
        '''
        @Description: 节点候选人申请/增加质押，质押金额为交易的value值。
        @param
            nodeId: [64]byte 节点ID(公钥)
            owner: [20]byte 质押金退款地址
            fee: uint32 出块奖励佣金比，以10000为基数(eg：5%，则fee=500)
            host: string 节点IP
            port: string 节点P2P端口号
            Extra: string 附加数据(有长度限制，限制值待定)
        @return: 
            出参（事件：CandidateDepositEvent）：
            Ret: bool 操作结果
            ErrMsg: string 错误信息
        '''
        data = HexBytes(rlp.encode([int(1001).to_bytes(8, 'big'), self.CandidateDeposit.__name__, nodeid,
                                    owner, fee, host, port, extra])).hex()
        if not value:
            value = self.value
        send_data = {
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "value": self.web3.toWei(value, "ether"),
            "data": data,
            "gas": "90000",
            "gasPrice": self.eth.gasPrice
        }
        self.value -= 1
        result = HexBytes(self.eth.sendTransaction(send_data)).hex()
        result = self.get_result(result)
        return result

    def CandidateApplyWithdraw(self, nodeid, withdraw):
        '''
        @Description: 节点质押金退回申请，申请成功后节点将被重新排序，权限校验from==owner
        @param
            nodeId: [64]byte 节点ID(公钥)
            withdraw: uint256 退款金额 (单位：ADP)
        @return:
            出参（事件：CandidateApplyWithdrawEvent）：
            Ret: bool 操作结果
            ErrMsg: string 错误信息
        '''
        # withdraw = np.uint256(withdraw)
        data = rlp.encode(
            [int(1002).to_bytes(8, 'big'), self.CandidateApplyWithdraw.__name__, nodeid, withdraw])
        send_data = {
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data,
            "gas": "9000",
            "gasPrice": self.eth.gasPrice
        }
        result = HexBytes(self.eth.sendTransaction(send_data)).hex()
        result = self.get_result(result)
        return result

    def CandidateWithdrawInfos(self, nodeid):
        '''
        @Description: 获取节点申请的退款记录列表
        @param {type} 
            nodeId: [64]byte 节点ID(公钥)
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            'Balance': uint256 退款金额 (单位：ADP)
            LockNumber: uint256 退款申请所在块高
            LockBlockCycle: uint256 退款金额锁定周期
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.CandidateWithdrawInfos.__name__, nodeid])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        return recive

    def CandidateWithdraw(self, nodeid):
        '''
        @Description: 节点质押金提取，调用成功后会提取所有已申请退回的质押金到owner账户。
        @param:
            nodeId: [64]byte 节点ID(公钥)
        @return:
            出参（事件：CandidateWithdrawEvent）：
            Ret: bool 操作结果
            ErrMsg: string 错误信息
        '''
        data = HexBytes(rlp.encode(
            [int(1003).to_bytes(8, 'big'), self.CandidateWithdraw.__name__, nodeid])).hex()
        send_data = {
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data,
            "gas": "9000",
            "gasPrice": self.eth.gasPrice
        }
        result = HexBytes(self.eth.sendTransaction(send_data)).hex()
        result = self.get_result(result)
        return result

    def SetCandidateExtra(self):
        '''
        @Description: 设置节点附加信息，供前端扩展使用
        @param:
            nodeId: [64]byte 节点ID(公钥)
            extra: string 附加信息
        @return:
            出参（事件：SetCandidateExtraEvent）：
            Ret: bool 操作结果
            ErrMsg: string 错误信息
        '''
        pass

    def CandidateDetails(self, nodeid):
        '''
        @Description: 获取候选人信息。
        @param {type} nodeId: [64]byte 节点ID(公钥)
        @return:
            Deposit: uint256 质押金额 (单位：ADP)
            BlockNumber: uint256 质押金更新的最新块高
            Owner: [20]byte 质押金退款地址
            TxIndex: uint32 所在区块交易索引
            CandidateId: [64]byte 节点Id(公钥)
            From: [20]byte 最新质押交易的发送方
            Fee: uint64 出块奖励佣金比，以10000为基数(eg：5%，则fee=500)
            Host: string 节点IP
            Port: string 节点P2P端口号
            Extra: string 附加数据(有长度限制，限制值待定)
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.CandidateDetails.__name__, nodeid])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile(r'{.*}')
            recive = re.findall(p, recive)[0]
            recive = re.sub("{{", "{", recive)
            recive = json.loads(recive)
        except Exception as e:
            raise e
        return recive

    def CandidateList(self):
        '''
        @Description: 获取所有入围节点的信息列表
        @param {type} @@@@
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            Deposit: uint256 质押金额 (单位：ADP)
            BlockNumber: uint256 质押金更新的最新块高
            Owner: [20]byte 质押金退款地址
            TxIndex: uint32 所在区块交易索引
            CandidateId: [64]byte 节点Id(公钥)
            From: [20]byte 最新质押交易的发送方
            Fee: uint64 出块奖励佣金比，以10000为基数(eg：5%，则fee=500)
            Host: string 节点IP
            Port: string 节点P2P端口号
            Extra: string 附加数据(有长度限制，限制值待定)
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.CandidateList.__name__])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile(r"{.*?}")
            recive = re.findall(p, recive)
            # recive = [json.loads(i) for i in recive]
        except Exception as e:
            raise e
        return recive

    def VerifiersList(self):
        '''
        @Description: 获取参与当前共识的验证人列表
        @param {type} @@@@
        @return:
            Ret: bool 操作结果
            ErrMsg: string 错误信息
            []:列表
            Deposit: uint256 质押金额 (单位：ADP)
            BlockNumber: uint256 质押金更新的最新块高
            Owner: [20]byte 质押金退款地址
            TxIndex: uint32 所在区块交易索引
            CandidateId: [64]byte 节点Id(公钥)
            From: [20]byte 最新质押交易的发送方
            Fee: uint64 出块奖励佣金比，以10000为基数(eg：5%，则fee=500)
            Host: string 节点IP
            Port: string 节点P2P端口号
            Extra: string 附加数据(有长度限制，限制值待定)
        '''
        data = HexBytes(rlp.encode(
            [int(10).to_bytes(8, 'big'), self.VerifiersList.__name__])).hex()
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile(r'{.*?}')
            recive = re.findall(p, recive)
            # recive = [json.loads(i) for i in recive]
        except Exception as e:
            raise e
        return recive

    def VoteTicket(self, count, price, nodeid, voter, value=None):
        '''
        购买选票，投票给候选人
        :param count: uint64 购票数量
        :param price:*big.Int 选票单价
        :param nodeid:[64]byte 候选人节点Id
        :param value: 发送交易的value为  购票数量 * 选票单价
        :return:
            出参（事件：VoteTicketEvent）：
            Ret: bool  操作结果
            Data: string  返回数据(成功选票的数量）
            ErrMsg: string  错误信息
        '''
        data = HexBytes(
            rlp.encode([int(1000).to_bytes(8, 'big'), self.VoteTicket.__name__, int(count).to_bytes(8, 'big'),
                        int(self.web3.toWei(price, 'ether')).to_bytes(8, 'big'), nodeid])).hex()
        if not value:
            value = self.value
        send_data = {
            "from": voter,
            "to": "0x1000000000000000000000000000000000000002",
            "value": self.web3.toWei(value, "ether"),
            "data": data,
            "gas": "0x6fffffff",
            "gasPrice": self.eth.gasPrice
        }
        result = HexBytes(self.eth.sendTransaction(send_data)).hex()
        result = self.get_result(result, abi=self.vote_abi)
        return result

    def GetTicketPrice(self):
        '''
        获取当前的票价
        :return:
            ret: *big.Int 当前票价
            error: string  错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetTicketPrice.__name__])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = HexBytes(recive).decode('utf-8')
            recive = re.sub('\x13', '', recive)
            recive = re.sub('\x00', '', recive)
        except Exception as e:
            raise e
        return recive

    def GetCandidateTicketIds(self, nodeid):
        '''
        获取指定候选人的选票Id的列表
        :param nodeid: [64]byte 节点Id
        :return:
            ret: []ticketId 选票的Id列表
            error: string 错误信息
        '''
        data = HexBytes(rlp.encode([int(10).to_bytes(8, 'big'),
                                    self.GetCandidateTicketIds.__name__, nodeid])).hex()
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile('\"(.+?)\"')
            recive = re.findall(p, recive)
        except Exception as e:
            raise e
        return recive

    def GetBatchCandidateTicketIds(self, node_ids):
        '''
        批量获取指定候选人的选票Id的列表
        :param node_ids: []nodeId 节点Id列表
        :return:
            ret: []ticketIds 多个节点的选票的Id列表
            error: string 错误信息
        '''
        encode_list = [int(10).to_bytes(8, 'big'), self.GetBatchCandidateTicketIds.__name__, ':'.join(node_ids)]
        data = rlp.encode(encode_list)
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile(r"{.*?}")
            recive = re.findall(p, recive)
            recive = [json.loads(i) for i in recive]
        except Exception as e:
            raise e
        return recive

    def GetTicketDetail(self, ticket_id):
        '''
        获取票详情
        :param ticket_id:[32]byte 票Id
        :return:
            ret: Ticket 选票信息
            error: string 错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetTicketDetail.__name__, ticket_id])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile(r"{.*?}")
            recive = re.findall(p, recive)
            recive = [json.loads(i) for i in recive]
        except Exception as e:
            raise e
        return recive

    def GetBatchTicketDetail(self, ticket_ids):
        '''
        批量获取票详情
        :param ticket_ids:[]ticketId 票Id列表
        :return:
            ret: []Ticket 选票信息列表
            error: string 错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetBatchTicketDetail.__name__, ':'.join(ticket_ids)])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile(r"{.*?}")
            recive = re.findall(p, recive)
            recive = [json.loads(i) for i in recive]
        except Exception as e:
            raise e
        return recive

    def GetCandidateEpoch(self, nodeid):
        '''
        获取指定候选人的票龄
        :param nodeid:[64]byte 节点Id
        :return:
            ret: uint64 票龄
            error: string 错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetCandidateEpoch.__name__, nodeid])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            recive = re.sub('\x00', '', recive)
            recive = re.sub('\x05', '', recive).split()[0]
        except Exception as e:
            raise e
        return recive

    def GetPoolRemainder(self):
        '''
        获取票池剩余票数量
        :return:
            ret: uint64 剩余票数量
            error: string 错误信息
        '''
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetPoolRemainder.__name__])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            recive = re.sub('\x00', '', recive)
            recive = re.sub('\x04', '', recive)
            recive = re.sub(' ', '', recive)
            # p = re.compile(r"{.*?}")
            # recive = re.findall(p, recive)
            # recive = [json.loads(i) for i in recive]
        except Exception as e:
            raise e
        return recive

