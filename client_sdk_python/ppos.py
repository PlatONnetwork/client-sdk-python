import json
import rlp

from hexbytes import HexBytes
from client_sdk_python.module import (
    Module,
)
from client_sdk_python.utils.encoding import parse_str
from client_sdk_python.utils.transactions import send_obj_transaction, call_obj


class Ppos(Module):
    need_analyze = True

    def createStaking(self, typ, benifit_address, node_id, external_id, node_name, website, details, amount,
                      program_version, program_version_sign, bls_pubkey, bls_proof, pri_key, from_address,
                      gas_price=None, gas=None, nonce=None):
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

        return send_obj_transaction(self, data, from_address, self.web3.stakingAddress, gas_price, gas, 0, pri_key, nonce)

    def editCandidate(self, benifit_address, node_id, external_id, node_name, website, details, pri_key,
                      from_address, gas_price=None, gas=None, nonce=None):
        if benifit_address[:2] == '0x':
            benifit_address = benifit_address[2:]
        data = HexBytes(rlp.encode([rlp.encode(int(1001)),
                                    rlp.encode(bytes.fromhex(benifit_address)),
                                    rlp.encode(bytes.fromhex(node_id)),
                                    rlp.encode(external_id), rlp.encode(node_name), rlp.encode(website),
                                    rlp.encode(details)])).hex()
        return send_obj_transaction(self, data, from_address, self.web3.stakingAddress, gas_price, gas, 0, pri_key, nonce)

    def increaseStaking(self, typ, node_id, amount, pri_key, from_address, gas_price=None, gas=None, nonce=None):

        data = HexBytes(rlp.encode([rlp.encode(int(1002)),
                                    rlp.encode(bytes.fromhex(node_id)),
                                    rlp.encode(typ),
                                    rlp.encode(self.web3.toWei(amount, 'ether'))])).hex()
        return send_obj_transaction(self, data, from_address, self.web3.stakingAddress, gas_price, gas, 0, pri_key, nonce)

    def withdrewStaking(self, node_id, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        data = rlp.encode([rlp.encode(int(1003)), rlp.encode(bytes.fromhex(node_id))])
        return send_obj_transaction(self, data, from_address, self.web3.stakingAddress, gas_price, gas, 0, pri_key, nonce)

    def delegate(self, typ, node_id, amount, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        data = rlp.encode([rlp.encode(int(1004)),
                           rlp.encode(typ),
                           rlp.encode(bytes.fromhex(node_id)),
                           rlp.encode(self.web3.toWei(amount, 'ether'))])
        return send_obj_transaction(self, data, from_address, self.web3.stakingAddress, gas_price, gas, 0, pri_key, nonce)

    def withdrewDelegate(self, staking_blocknum, node_id, amount, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        data = rlp.encode([rlp.encode(int(1005)), rlp.encode(staking_blocknum),
                           rlp.encode(bytes.fromhex(node_id)), rlp.encode(self.web3.toWei(amount, 'ether'))])
        return send_obj_transaction(self, data, from_address, self.web3.stakingAddress, gas_price, gas, 0, pri_key, nonce)

    def getVerifierList(self, from_address=None):
        data = rlp.encode([rlp.encode(int(1100))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        parse = parse_str(raw_data)
        for i in parse['Data']:
            i["Shares"] = int(i["Shares"], 16)
        return parse

    def getValidatorList(self, from_address=None):
        data = rlp.encode([rlp.encode(int(1101))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        parse = parse_str(raw_data)
        for i in parse['Data']:
            i["Shares"] = int(i["Shares"], 16)
        return parse

    def getCandidateList(self, from_address=None):
        data = rlp.encode([rlp.encode(int(1102))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        parse = parse_str(raw_data)
        for i in parse['Data']:
            i["Shares"] = int(i["Shares"], 16)
            i["Released"] = int(i["Released"], 16)
            i["ReleasedHes"] = int(i["ReleasedHes"], 16)
            i["RestrictingPlan"] = int(i["RestrictingPlan"], 16)
            i["RestrictingPlanHes"] = int(i["RestrictingPlanHes"], 16)
        return parse

    def getRelatedListByDelAddr(self, del_addr, from_address=None):
        if del_addr[:2] == '0x':
            del_addr = del_addr[2:]
        data = rlp.encode([rlp.encode(int(1103)), rlp.encode(bytes.fromhex(del_addr))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        return parse_str(raw_data)

    def getDelegateInfo(self, staking_blocknum, del_address, node_id, from_address=None):
        if del_address[:2] == '0x':
            del_address = del_address[2:]
        data = rlp.encode([rlp.encode(int(1104)), rlp.encode(staking_blocknum),
                           rlp.encode(bytes.fromhex(del_address)), rlp.encode(bytes.fromhex(node_id))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        parse = json.loads(str(raw_data, encoding="utf8"))
        raw_data_dict = parse["Data"]
        if raw_data_dict != "":
            data = json.loads(raw_data_dict)
            data["Released"] = int(data["Released"], 16)
            data["ReleasedHes"] = int(data["ReleasedHes"], 16)
            data["RestrictingPlan"] = int(data["RestrictingPlan"], 16)
            data["RestrictingPlanHes"] = int(data["RestrictingPlanHes"], 16)
            data["Reduction"] = int(data["Reduction"], 16)
            parse["Data"] = data
        return parse

    def getCandidateInfo(self, node_id, from_address=None):

        data = rlp.encode([rlp.encode(int(1105)), rlp.encode(bytes.fromhex(node_id))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        parse = str(raw_data, encoding="utf8").replace('\\', '').replace('"{', '{').replace('}"', '}')
        raw_data_dict = json.loads(parse)
        if raw_data_dict["Data"] != "":
            raw_data_dict["Data"]["Shares"] = int(raw_data_dict["Data"]["Shares"], 16)
            raw_data_dict["Data"]["Released"] = int(raw_data_dict["Data"]["Released"], 16)
            raw_data_dict["Data"]["ReleasedHes"] = int(raw_data_dict["Data"]["ReleasedHes"], 16)
            raw_data_dict["Data"]["RestrictingPlan"] = int(raw_data_dict["Data"]["RestrictingPlan"], 16)
            raw_data_dict["Data"]["RestrictingPlanHes"] = int(raw_data_dict["Data"]["RestrictingPlanHes"], 16)
        return raw_data_dict

    def reportMultiSign(self, typ, data, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        data = rlp.encode([rlp.encode(int(3000)), rlp.encode(typ), rlp.encode(data)])
        return send_obj_transaction(self, data, from_address, self.web3.penaltyAddress, gas_price, gas, 0, pri_key, nonce)

    def checkMultiSign(self, typ, check_address, block_number, from_address=None):
        if check_address[:2] == '0x':
            check_address = check_address[2:]

        data = rlp.encode([rlp.encode(int(3001)), rlp.encode(int(typ)),
                           rlp.encode(bytes.fromhex(check_address)), rlp.encode(block_number)])

        raw_data = call_obj(self, from_address, self.web3.penaltyAddress, data)
        receive = str(raw_data, encoding="ISO-8859-1")
        if receive == "":
            return receive
        return json.loads(receive)

    def createRestrictingPlan(self, account, plan, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        if account[:2] == '0x':
            account = account[2:]
        plan_list = []
        for dict_ in plan:
            # v = [dict_[k] for k in dict_]
            plan_list.append(dict_.values())
        rlp_list = rlp.encode(plan_list)
        data = rlp.encode([rlp.encode(int(4000)),
                           rlp.encode(bytes.fromhex(account)),
                           rlp_list])
        return send_obj_transaction(self, data, from_address, self.web3.restrictingAddress, gas_price, gas, 0, pri_key, nonce)

    def getRestrictingInfo(self, account, from_address=None):
        if account[:2] == '0x':
            account = account[2:]
        data = rlp.encode([rlp.encode(int(4100)), rlp.encode(bytes.fromhex(account))])
        raw_data = call_obj(self, from_address, self.web3.restrictingAddress, data)
        receive = json.loads(str(raw_data, encoding="ISO-8859-1"))
        raw_data_dict = receive["Data"]
        if raw_data_dict != "":
            data = json.loads(data)
            data["balance"] = int(data["balance"], 16)
            data["Pledge"] = int(data["Pledge"], 16)
            data["debt"] = int(data["debt"], 16)
            if data["plans"]:
                for i in data["plans"]:
                    i["amount"] = int(i["amount"], 16)
            receive["Data"] = data
        return receive
