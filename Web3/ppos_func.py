'''
@Author: alex
@Date: 2019-2-21 16:30:41
@LastEditors: alex
@Description: file content
'''

import json
import os
import re
import struct
import time

import rlp
from hexbytes import HexBytes
from web3 import Web3
from web3.eth import Eth
from web3.personal import Personal

# from delopy_ppos import delopy_ppos
from Event import Event


class PlatonPpos:
    def __init__(self, url, address, pwd, abi=os.path.abspath('./candidateConstract.json'),
                 vote_abi=os.path.abspath('./ticketContract.json')):
        self.web3 = Web3(Web3.HTTPProvider(url))
        if not self.web3.isConnected():
            raise Exception("节点连接失败")
        self.eth = Eth(self.web3)
        self.personal = Personal(self.web3)
        self.address = address
        if not self.web3.personal.unlockAccount(self.address, pwd, 22222):
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
            print("result:%s" % event_data)
            print("=============================================================")
            return event_data
        except Exception as e:
            print(result)
            print(e)

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
            print(e)
            print(recive)
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
            print(e)
            print(recive)
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
            print(e)
            print(recive)
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
            print(e)
            print(recive)
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
            print(e)
            print(recive)
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
            print(e)
            print(recive)
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
            print(e)
            print(recive)
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
            print(e)
            print(recive)
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
            print(e)
            print(recive)
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
            print(e)
            print(recive)
        return recive


if __name__ == "__main__":
    # delopy_ppos(5)
    # url = "http://10.10.8.235:6789"
    url = "http://192.168.120.90:6789"
    # url_list = ["http://192.168.9.160:6789", "http://192.168.9.161:6789",
    #             "http://192.168.9.162:6789", "http://192.168.9.163:6789",
    #             "http://192.168.9.164:6789", "http://192.168.9.165:6789"]
    address = Web3.toChecksumAddress(
        "0x493301712671ada506ba6ca7891f436d29185821")
    nodeid_dict = {
        '97': '0x97e424be5e58bfd4533303f8f515211599fd4ffe208646f7bfdf27885e50b6dd85d957587180988e76ae77b4b6563820a27b16885419e5ba6f575f19f6cb36b0',
        '3b': '0x3b53564afbc3aef1f6e0678171811f65a7caa27a927ddd036a46f817d075ef0a5198cd7f480829b53fe62bdb063bc6a17f800d2eebf7481b091225aabac2428d',
        '85': '0x858d6f6ae871e291d3b7b2b91f7369f46deb6334e9dacb66fa8ba6746ee1f025bd4c090b17d17e0d9d5c19fdf81eb8bde3d40a383c9eecbe7ebda9ca95a3fb94',
        'b0': '0xb0971a3670e593ad7a3d5b3983b5d67db827e1fd267688dfef97e27604c1121dc6b8e5ba82a89d6dc552083296df8a7ab41466ab1e47929af69e94efd65df7b3',
        '80': '0x805b617b9d321a65d8936e758b5c60cd6e8c873b9f1e7c793ad5f887d26ce9667d0db2fe55a9aeb1cc81f9cf9a1e7c54473203473e3ebda89e63c03cbcfe5347',
        '64': '0x64ba18ce01172da6a95b0d5b0a93aee727d77e5b2f04255a532a9566edaee7808383812a860acf5e43efeca3d9321547bfcdefd89e9d0c605dcdb65ce0bbb617'
    }
    # ip_dict = {
    #     '160': '192.168.9.160',
    #     '161': '192.168.9.161',
    #     '162': '192.168.9.162',
    #     '163': '192.168.9.163',
    #     '164': '192.168.9.164',
    #     '165': '192.168.9.165'
    # }
    pwd = "88888888"
    platon_ppos = PlatonPpos(url, address, pwd)
    # print("获取候选人列表")
    platon_ppos.CandidateList()
    platon_ppos.VerifiersList()
    '''转账，用于投票'''
    # new_address = platon_ppos.personal.newAccount('88888888')
    # print('new_address:{}'.format(new_address))
    # transaction = {'from': platon_ppos.eth.accounts[0], 'to': new_address, 'gas': 21000000,
    #                'gasPrice': platon_ppos.eth.gasPrice, 'value': platon_ppos.web3.toWei(12, 'ether')}
    # trans_hex = platon_ppos.eth.sendTransaction(transaction)
    # platon_ppos.eth.waitForTransactionReceipt(trans_hex)
    # platon_ppos.personal.unlockAccount(new_address, '88888888', 999999999)
    # after_trans = platon_ppos.eth.getBalance(new_address)
    # print('转账后余额:{}'.format(after_trans))
    '''=========投票接口========='''
    x = platon_ppos.GetTicketPrice()
    # assert '1000000000000000000' == x
    # platon_ppos.VoteTicket(10, 1, nodeid_dict['97'], value=10)
    # platon_ppos.VoteTicket(10, 1, nodeid_dict['80'], value=10)
    # platon_ppos.VoteTicket(10, 1, nodeid_dict['b0'], value=10)
    # platon_ppos.VoteTicket(10, 1, nodeid_dict['85'], value=10)
    # platon_ppos.VoteTicket(10, 1, nodeid_dict['3b'], value=10)
    # platon_ppos.VoteTicket(10, 1, nodeid_dict['b0'], new_address, value=10)
    # ids = platon_ppos.GetCandidateTicketIds(nodeid_dict['b0'])
    ids = platon_ppos.GetCandidateTicketIds('64ba18ce01172da6a95b0d5b0a93aee727d77e5b2f04255a532a9566edaee7808383812a860acf5e43efeca3d9321547bfcdefd89e9d0c605dcdb65ce0bbb617')
    print(len(ids))

    # platon_ppos.GetBatchCandidateTicketIds(
    #     [nodeid_dict['80'], nodeid_dict['b0'], nodeid_dict['97'], nodeid_dict['85'], nodeid_dict['3b']])
    platon_ppos.GetBatchCandidateTicketIds(['64ba18ce01172da6a95b0d5b0a93aee727d77e5b2f04255a532a9566edaee7808383812a860acf5e43efeca3d9321547bfcdefd89e9d0c605dcdb65ce0bbb617',
                                           'd8c4b58ae052ea9480577264bc1b2c09619757015849a4c92b71a4e4c8b5ede94f35d24107b1181d0711013ed7fdc068f21e6e6084b3e96750a571669715c0b1'])
    platon_ppos.GetCandidateEpoch('64ba18ce01172da6a95b0d5b0a93aee727d77e5b2f04255a532a9566edaee7808383812a860acf5e43efeca3d9321547bfcdefd89e9d0c605dcdb65ce0bbb617')
    platon_ppos.GetTicketDetail('0xce97728c491459ecb50f78d2295eb8b89b91d4e7e212df8e642dd4555a779034')
    platon_ppos.GetBatchTicketDetail(['0xce97728c491459ecb50f78d2295eb8b89b91d4e7e212df8e642dd4555a779034','0x76f3d0f94911f1b2bad94ee8ff32d9ea499ac51d6c1ee7dacd168ef9adfdf29b'])
    platon_ppos.GetPoolRemainder()
    '''=========投票接口========='''

    # after_vote = platon_ppos.eth.getBalance(new_address)
    # print('投票后余额:{},当前块高:{}'.format(after_vote, platon_ppos.eth.blockNumber))
    # time.sleep(255 - (platon_ppos.eth.blockNumber % 250))
    # print('揭榜,当前块高:{}'.format(platon_ppos.eth.blockNumber))
    # platon_ppos.VerifiersList()
    # final = platon_ppos.eth.getBalance(new_address)
    # print('获奖后余额:{}'.format(final))
    # print('奖励所得:{}'.format(platon_ppos.web3.fromWei((final - after_vote), 'ether') - 1))

    # # 新建一个账号用于质押
    # new_account = Web3.toChecksumAddress(
    #     platon_ppos.web3.personal.newAccount("88888888"))
    # params = {
    #     "to": new_account,
    #     "from": address,
    #     "gas": '9000',
    #     "gasPrice": '1000000000',
    #     "value": 910000000000000000000,
    # }
    # platon_ppos.eth.sendTransaction(params)
    # start_block = platon_ppos.eth.blockNumber
    # print('当前块高：', start_block)
    # owner = '0x4df6d93fce768f3581ae97c981bcd4d8a3e6272e'
    # fee = int(1000).to_bytes(8, 'big')
    # port = '16788'
    # extra = "hahahah"
    # result = platon_ppos.CandidateDeposit(
    #         '805b617b9d321a65d8936e758b5c60cd6e8c873b9f1e7c793ad5f887d26ce9667d0db2fe55a9aeb1cc81f9cf9a1e7c54473203473e3ebda89e63c03cbcfe5347', owner, fee, '192.168.9.163', port, extra,value=100)
    # print(result)
    # print("获取候选人列表")
    # platon_ppos.CandidateList()
    # platon_ppos.VerifiersList()
    # for k in nodeid_dict.keys():
    #     if k == '164' or k == '165' or k == '160':
    #         continue
    #     result = platon_ppos.CandidateDeposit(
    #         nodeid_dict[k], owner, fee, ip_dict[k], port, extra)
    # platon_p = PlatonPpos(url, new_account, pwd)
    # print("获取质押前的余额")
    # print(platon_p.web3.fromWei(platon_p.eth.getBalance(new_account), 'ether'))
    # print("发起质押")
    # platon_p.CandidateDeposit(
    #     nodeid_dict['164'], new_account, fee, ip_dict['164'], port, extra, 110)
    # print("发起质押")
    # platon_p.CandidateDeposit(
    #     nodeid_dict['165'], new_account, fee, ip_dict['165'], port, extra, 150)
    # print("获取质押后的余额")
    # print(platon_p.web3.fromWei(platon_p.eth.getBalance(new_account), 'ether'))
    # print("查看候选人信息")
    # platon_ppos.CandidateDetails(nodeid_dict['179'])
    # print("获取候选人列表")
    # platon_ppos.CandidateList()
    # # print("发起质押金退回申请")
    # # platon_p.CandidateApplyWithdraw(
    # #     nodeid_dict['178_2'], 110000000000000000000)
    # # print("获取节点申请的退款记录列表")
    # # platon_ppos.CandidateWithdrawInfos(nodeid_dict['178_2'])
    # # print("获取申请后的余额")
    # # print(platon_p.web3.fromWei(platon_p.eth.getBalance(new_account), 'ether'))
    # # a = platon_p.eth.getBalance(new_account)
    # # time.sleep(2)
    # # print("节点质押金提取，调用成功后会提取所有已申请退回的质押金到owner账户")
    # # platon_p.CandidateWithdraw(nodeid_dict['178_2'])
    # # print("获取质押金提取后的余额")
    # # print(platon_p.web3.fromWei(platon_p.eth.getBalance(new_account), 'ether'))
    # # b = platon_p.eth.getBalance(new_account)
    # # print(b - a)
    # # print("退回金额:{}".format(platon_p.web3.fromWei(b - a, 'ether')))
    # # print("退回路上损失金额:{}".format(platon_p.web3.fromWei(
    # #     110000000000000000000 - b + a, 'ether')))
    # # print("获取候选人列表")
    # # platon_ppos.CandidateList()
    # for i in range(60):
    #     time.sleep(1)
    #     if platon_p.eth.blockNumber == 50:
    #         break
    #     else:
    #         continue
    # print("揭榜信息。获取验证人列表")
    # platon_ppos.VerifiersList()
    # for i in range(260):
    #     time.sleep(1)
    #     if platon_p.eth.blockNumber == 231:
    #         break
    #     else:
    #         continue
    # print("揭榜信息。获取验证人列表")
    # platon_ppos.VerifiersList()
    #
    # for i in range(51):
    #     time.sleep(1)
    #     if platon_p.eth.blockNumber == 251:
    #         break
    #     else:
    #         continue
    # print("切换到第二轮轮出块人")
    # print("获取验证人列表")
    # platon_ppos.VerifiersList()
    # print(platon_ppos.eth.blockNumber)
    # time.sleep(5)
    # print(platon_ppos.eth.blockNumber)
    # hash_tx = platon_ppos.eth.sendTransaction(params)
    # result = platon_ppos.eth.waitForTransactionReceipt(hash_tx)
    # print("第二轮获取交易哈希结果1")
    # print(result)
    # print("查看所有节点块高")
    # for url in url_list:
    #     w = Web3(Web3.HTTPProvider(url))
    #     print(url, w.eth.blockNumber)
    # tx = platon_ppos.eth.sendTransaction(params)
    # result = platon_ppos.eth.waitForTransactionReceipt(hash_tx)
    # print("第二轮获取交易哈希结果2")
    # print(result)
    # platon_ppos.CandidateDeposit(
    #     nodeid_dict['175'], new_account, fee, ip_dict['175'], port, extra, 190)
    # print("获取候选人列表")
    # platon_ppos.CandidateList()
    # print("等待切换到第三轮....")
    # time.sleep(120-platon_ppos.eth.blockNumber+3)
    # print("获取第三轮验证人列表")
    # platon_ppos.VerifiersList()
    # platon_ppos.CandidateDeposit(
    #     nodeid_dict['176'], new_account, fee, ip_dict['176'], port, extra, 110)
    # print("获取第四轮候选人列表")
    # platon_ppos.CandidateList()
    # time.sleep(180-platon_ppos.eth.blockNumber+3)
    # print("获取第四轮验证人列表")
    # platon_ppos.VerifiersList()
    # platon_ppos.CandidateDeposit(
    #     nodeid_dict['176'], new_account, fee, ip_dict['176'], port, extra, 110)
    # print("获取候选人列表")
    # platon_ppos.CandidateList()
    # time.sleep(240-platon_ppos.eth.blockNumber)
    # print("获取验证人列表")
    # platon_ppos.VerifiersList()
    # platon_ppos.CandidateDeposit(
    #     nodeid_dict['177'], new_account, fee, ip_dict['177'], port, extra, 110)
    # print("获取候选人列表")
    # platon_ppos.CandidateList()
    # hash_tx = platon_ppos.eth.sendTransaction(params)
