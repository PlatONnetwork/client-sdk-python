import json
import rlp

from hexbytes import HexBytes
from client_sdk_python.module import (
    Module,
)
from client_sdk_python.utils.encoding import parse_str
from client_sdk_python.utils.transactions import send_obj_transaction
from client_sdk_python.eth import Eth


class Pip(Module):
    pip_address = "0x1000000000000000000000000000000000000005"
    gas_price = ""
    chain_id = 101
    need_analyze = True
    platon = Eth(Module)

    def submitText(self, verifier, pip_id, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        data = rlp.encode([rlp.encode(int(2000)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(pip_id)])
        return send_obj_transaction(self, data, from_address, self.pip_address, gas_price, gas, 0, pri_key, nonce)

    def submitVersion(self, verifier, pip_id, new_version, end_voting_rounds, pri_key,
                      from_address, gas_price=None, gas=None, nonce=None):

        data = rlp.encode([rlp.encode(int(2001)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(pip_id), rlp.encode(int(new_version)), rlp.encode(int(end_voting_rounds))])
        return send_obj_transaction(self, data, from_address, self.pip_address, gas_price, gas, 0, pri_key, nonce)

    def submitParam(self, verifier, url, end_voting_block, param_name, current_value, new_value,
                    privatekey=None, from_address=None, gasPrice=None, gas=None):
        '''
        提交参数提案
        :param verifier: 64bytes
        :param githubID: string
        :param topic: string
        :param desc: string
        :param url: string
        :param end_voting_block: uint64
        :param param_name:string
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        to_address = "0x1000000000000000000000000000000000000005"
        data = rlp.encode([rlp.encode(int(2002)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(url), rlp.encode(int(end_voting_block)),
                           rlp.encode(param_name), rlp.encode(str(currentValue)), rlp.encode(str(new_value))])
        return send_obj_transaction(self, data, from_address, self.pip_address, gas_price, gas, 0, pri_key, nonce)

    def vote(self, verifier, proposalID, option, programVersion, versionSign, from_address=None, gasPrice=None,
             gas=None, privatekey=None):
        '''
        给提案投票
        :param verifier: 64bytes
        :param proposalID: common.Hash
        :param option: VoteOption
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        if proposalID[:2] == '0x':
            proposalID = proposalID[2:]
        if versionSign[:2] == '0x':
            versionSign = versionSign[2:]
        data = rlp.encode([rlp.encode(int(2003)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(bytes.fromhex(proposalID)), rlp.encode(option), rlp.encode(int(programVersion)),
                           rlp.encode(bytes.fromhex(versionSign))])
        return send_obj_transaction(self, data, from_address, self.pip_address, gas_price, gas, 0, pri_key, nonce)

    def declareVersion(self, activeNode, version, versionSign, privatekey=None, from_address=None, gasPrice=None,
                       gas=None):
        '''
        版本声明
        :param activeNode: 64bytes
        :param version: uint
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        to_address = "0x1000000000000000000000000000000000000005"
        if versionSign[0:2] == '0x':
            versionSign = versionSign[2:]
        data = rlp.encode([rlp.encode(int(2004)), rlp.encode(bytes.fromhex(activeNode)),
                           rlp.encode(int(version)), rlp.encode(bytes.fromhex(versionSign))])
        return send_obj_transaction(self, data, from_address, self.pip_address, gas_price, gas, 0, pri_key, nonce)

    def getProposal(self, proposalID):
        '''
        查询提案
        :param proposalID: common.Hash
        :return:
        '''
        if proposalID[:2] == '0x':
            proposalID = proposalID[2:]
        to_address = "0x1000000000000000000000000000000000000005"
        data = rlp.encode([rlp.encode(int(2100)), rlp.encode(bytes.fromhex(proposalID))])
        recive = self.platon.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        recive = json.loads(recive)
        return recive

    def getTallyResult(self, proposalID):
        '''
        查询提案结果
        :param proposalID: common.Hash
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        if proposalID[:2] == '0x':
            proposalID = proposalID[2:]
        data = rlp.encode([rlp.encode(int(2101)), rlp.encode(bytes.fromhex(proposalID))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.platon.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        recive = json.loads(recive)
        return recive

    def getAccuVerifiersCount(self, proposalID, blockHash):
        '''
        查询提案的累积可投票人数
        :param proposalID: common.Hash
        :param from_address:
        :param gasPrice:
        :param gas:
        :return:
        '''
        if proposalID[:2] == '0x':
            proposalID = proposalID[2:]
        if blockHash[:2] == '0x':
            blockHash = blockHash[2:]
        data = rlp.encode(
            [rlp.encode(int(2105)), rlp.encode(bytes.fromhex(proposalID)), rlp.encode(bytes.fromhex(blockHash))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.platon.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        recive = json.loads(recive)
        return recive

    def listProposal(self):
        '''
        查询提案列表
        :return:
        '''
        data = rlp.encode([rlp.encode(int(2102))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.platon.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        recive = json.loads(recive)
        return recive

    def getActiveVersion(self):
        """
        查询节点的链生效版本
        """
        data = rlp.encode([rlp.encode(int(2103))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.platon.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        recive = json.loads(recive)
        # print(recive)
        return recive

    def getProgramVersion(self):
        """
        查询节点代码版本
        """
        data = rlp.encode([rlp.encode(int(2104))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.platon.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        recive = json.loads(recive)
        # print(recive)
        return recive

    def listParam(self):
        """
        查询可治理参数列表
        """
        data = rlp.encode([rlp.encode(int(2105))])
        to_address = "0x1000000000000000000000000000000000000005"
        recive = self.platon.call({
            "from": self.address,
            "to": to_address,
            "data": data
        })
        recive = str(recive, encoding="utf8")
        recive = json.loads(recive)
        # print(recive)
        return recive

    def submitCancel(self, verifier, pIDID, endVotingRounds, tobeCanceledProposalID, pri_key=None,
                     from_address=None, gas_price=None, gas=None):

        if tobeCanceledProposalID[:2] == '0x':
            tobeCanceledProposalID = tobeCanceledProposalID[2:]
        to_address = "0x1000000000000000000000000000000000000005"
        print(pIDID, endVotingRounds, tobeCanceledProposalID)
        data = rlp.encode([rlp.encode(int(2005)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(pIDID), rlp.encode(int(endVotingRounds)),
                           rlp.encode(bytes.fromhex(tobeCanceledProposalID))])

        return send_obj_transaction(self, data, from_address, self.pip_address, gas_price, gas, 0, pri_key, nonce)