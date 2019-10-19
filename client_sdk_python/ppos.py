import json
import rlp

from hexbytes import HexBytes
from client_sdk_python.module import (
    Module,
)
from client_sdk_python.eth import Eth
from client_sdk_python.utils.encoding import parse_str
from client_sdk_python.utils.transactions import send_obj_transaction


class Ppos(Module):
    plan_address = "0x1000000000000000000000000000000000000001"
    staking_address = "0x1000000000000000000000000000000000000002"
    penalty_address = "0x1000000000000000000000000000000000000004"
    gas_price = ""
    chain_id = 101
    need_analyze = True
    platon = Eth(Module)

    def createStaking(self, typ, benifit_address, node_id, external_id, node_name, website, details, amount,
                      program_version, program_version_sign, bls_pubkey, bls_proof, from_address,
                      pri_key, gas_price=None, gas=None, nonce=None):
        if benifit_address[:2] == '0x':
            benifit_address = benifit_address[2:]
        if program_version_sign[:2] == '0x':
            program_version_sign = program_version_sign[2:]
        data = HexBytes(rlp.encode([rlp.encode(int(1000)),
                                    rlp.encode(typ),
                                    rlp.encode(bytes.fromhex(benifit_address)),
                                    rlp.encode(bytes.fromhex(node_id)),
                                    rlp.encode(external_id), rlp.encode(node_name), rlp.encode(website),
                                    rlp.encode(details), rlp.encode(self.web3.toWei(amount, 'ether')),
                                    rlp.encode(program_version),
                                    rlp.encode(bytes.fromhex(program_version_sign)),
                                    rlp.encode(bytes.fromhex(bls_pubkey)),
                                    rlp.encode(bytes.fromhex(bls_proof))])).hex()

        return send_obj_transaction(self, data, from_address, self.staking_address, gas_price, gas, 0, pri_key, nonce)

    def updateStakingInfo(self, benifit_address, node_id, external_id, node_name, website, details, pri_key,
                          from_address, gas_price=None, gas=None, nonce=None):
        if benifit_address[:2] == '0x':
            benifit_address = benifit_address[2:]
        data = HexBytes(rlp.encode([rlp.encode(int(1001)),
                                    rlp.encode(bytes.fromhex(benifit_address)),
                                    rlp.encode(bytes.fromhex(node_id)),
                                    rlp.encode(external_id), rlp.encode(node_name), rlp.encode(website),
                                    rlp.encode(details)])).hex()
        return send_obj_transaction(self, data, from_address, self.staking_address, gas_price, gas, 0, pri_key, nonce)

    def addStaking(self, typ, node_id, amount, from_address, pri_key, gas_price=None, gas=None, nonce=None):

        data = HexBytes(rlp.encode([rlp.encode(int(1002)),
                                    rlp.encode(bytes.fromhex(node_id)),
                                    rlp.encode(typ),
                                    rlp.encode(self.web3.toWei(amount, 'ether'))])).hex()
        return send_obj_transaction(self, data, from_address, self.staking_address, gas_price, gas, 0, pri_key, nonce)

    def unStaking(self, node_id, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        data = rlp.encode([rlp.encode(int(1003)), rlp.encode(bytes.fromhex(node_id))])
        return send_obj_transaction(self, data, from_address, self.staking_address, gas_price, gas, 0, pri_key, nonce)

    def delegate(self, typ, node_id, amount, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        data = rlp.encode([rlp.encode(int(1004)),
                           rlp.encode(typ),
                           rlp.encode(bytes.fromhex(node_id)),
                           rlp.encode(self.web3.toWei(amount, 'ether'))])
        return send_obj_transaction(self, data, from_address, self.staking_address, gas_price, gas, 0, pri_key, nonce)

    def unDelegate(self, staking_blocknum, node_id, amount, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        data = rlp.encode([rlp.encode(int(1005)), rlp.encode(staking_blocknum),
                           rlp.encode(bytes.fromhex(node_id)), rlp.encode(self.web3.toWei(amount, 'ether'))])
        return send_obj_transaction(self, data, from_address, self.staking_address, gas_price, gas, 0, pri_key, nonce)

    def __call(self, from_address, to_address, data):
        return self.platon.call({"from": from_address, "to": to_address, "data": data})

    def getVerifierList(self, from_address):
        data = rlp.encode([rlp.encode(int(1100))])
        raw_data = self.__call(from_address, self.staking_address, data)
        parse = parse_str(raw_data)
        for i in parse['Data']:
            i["Shares"] = int(i["Shares"], 16)
        return parse

    def getValidatorList(self, from_address):
        data = rlp.encode([rlp.encode(int(1101))])
        raw_data = self.__call(from_address, self.staking_address, data)
        parse = parse_str(raw_data)
        for i in parse['Data']:
            i["Shares"] = int(i["Shares"], 16)
        return parse

    def getCandidateList(self, from_address):
        data = rlp.encode([rlp.encode(int(1102))])
        raw_data = self.__call(from_address, self.staking_address, data)
        parse = parse_str(raw_data)
        for i in parse['Data']:
            i["Shares"] = int(i["Shares"], 16)
            i["Released"] = int(i["Released"], 16)
            i["ReleasedHes"] = int(i["ReleasedHes"], 16)
            i["RestrictingPlan"] = int(i["RestrictingPlan"], 16)
            i["RestrictingPlanHes"] = int(i["RestrictingPlanHes"], 16)
        return parse

    def getDelegateListByAddr(self, addr, from_address):
        if addr[:2] == '0x':
            addr = addr[2:]
        data = rlp.encode([rlp.encode(int(1103)), rlp.encode(bytes.fromhex(addr))])
        raw_data = self.__call(from_address, self.staking_address, data)
        return parse_str(raw_data)

    def getDelegateInfo(self, staking_blocknum, del_address, node_id, from_address):
        if del_address[:2] == '0x':
            del_address = del_address[2:]
        data = rlp.encode([rlp.encode(int(1104)), rlp.encode(staking_blocknum),
                           rlp.encode(bytes.fromhex(del_address)), rlp.encode(bytes.fromhex(node_id))])
        raw_data = self.__call(from_address, self.staking_address, data)
        parse = json.loads(str(raw_data, encoding="utf8"))
        raw_data_dict = parse["Data"]
        if data != "":
            data = json.loads(raw_data_dict)
            data["Released"] = int(data["Released"], 16)
            data["ReleasedHes"] = int(data["ReleasedHes"], 16)
            data["RestrictingPlan"] = int(data["RestrictingPlan"], 16)
            data["RestrictingPlanHes"] = int(data["RestrictingPlanHes"], 16)
            data["Reduction"] = int(data["Reduction"], 16)
            parse["Data"] = data
        return parse

    def getCandidateInfo(self, node_id, from_address):

        data = rlp.encode([rlp.encode(int(1105)), rlp.encode(bytes.fromhex(node_id))])
        raw_data = self.__call(from_address, self.staking_address, data)
        parse = str(raw_data, encoding="utf8").replace('\\', '').replace('"{', '{').replace('}"', '}')
        result = json.loads(parse)
        if result["Data"] != "":
            result["Data"]["Shares"] = int(result["Data"]["Shares"], 16)
            result["Data"]["Released"] = int(result["Data"]["Released"], 16)
            result["Data"]["ReleasedHes"] = int(result["Data"]["ReleasedHes"], 16)
            result["Data"]["RestrictingPlan"] = int(result["Data"]["RestrictingPlan"], 16)
            result["Data"]["RestrictingPlanHes"] = int(result["Data"]["RestrictingPlanHes"], 16)
        return result

    def reportMultiSign(self, typ, data, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        data = rlp.encode([rlp.encode(int(3000)), rlp.encode(typ), rlp.encode(data)])
        return send_obj_transaction(self, data, from_address, self.penalty_address, gas_price, gas, 0, pri_key, nonce)

    def checkMultiSign(self, typ, check_address, block_number, from_address):
        if check_address[:2] == '0x':
            check_address = check_address[2:]

        data = rlp.encode([rlp.encode(int(3001)), rlp.encode(int(typ)),
                           rlp.encode(bytes.fromhex(check_address)), rlp.encode(block_number)])

        raw_data = self.__call(from_address, self.penalty_address, data)
        receive = str(raw_data, encoding="ISO-8859-1")
        return json.loads(receive)

    def createRestrictingPlan(self, account, plan, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        if account[:2] == '0x':
            account = account[2:]
        plan_list = []
        for dict_ in plan:
            v = [dict_[k] for k in dict_]
            plan_list.append(v)
        rlp_list = rlp.encode(plan_list)
        data = rlp.encode([rlp.encode(int(4000)),
                           rlp.encode(bytes.fromhex(account)),
                           rlp_list])
        return send_obj_transaction(self, data, from_address, self.plan_address, gas_price, gas, 0, pri_key, nonce)

    def getRestrictingInfo(self, account, from_address):
        if account[:2] == '0x':
            account = account[2:]
        data = rlp.encode([rlp.encode(int(4100)), rlp.encode(bytes.fromhex(account))])
        raw_data = self.__call(from_address, self.plan_address, data)
        receive = json.loads(str(raw_data, encoding="ISO-8859-1"))
        data = receive["Data"]
        if data != "":
            data = json.loads(data)
            data["balance"] = int(data["balance"], 16)
            data["Pledge"] = int(data["Pledge"], 16)
            data["debt"] = int(data["debt"], 16)
            if data["plans"]:
                for i in data["plans"]:
                    i["amount"] = int(i["amount"], 16)
            receive["Data"] = data
        return receive
