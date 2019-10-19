import json
import rlp

from client_sdk_python.module import (
    Module,
)
from client_sdk_python.utils.transactions import send_obj_transaction, call_obj


def parse_data(raw_data):
    data = str(raw_data, encoding="utf-8")
    if data == "":
        return ""
    return json.loads(data)


class Pip(Module):
    need_analyze = True

    def submitText(self, verifier, pip_id, pri_key, from_address, gas_price=None, gas=None, nonce=None):
        data = rlp.encode([rlp.encode(int(2000)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(pip_id)])
        return send_obj_transaction(self, data, from_address, self.web3.pipAddress, gas_price, gas, 0, pri_key, nonce)

    def submitVersion(self, verifier, pip_id, new_version, end_voting_rounds, pri_key,
                      from_address, gas_price=None, gas=None, nonce=None):

        data = rlp.encode([rlp.encode(int(2001)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(pip_id), rlp.encode(int(new_version)), rlp.encode(int(end_voting_rounds))])
        return send_obj_transaction(self, data, from_address, self.web3.pipAddress, gas_price, gas, 0, pri_key, nonce)

    def submitParam(self, verifier, url, end_voting_block, param_name, current_value, new_value,
                    pri_key, from_address, gas_price=None, gas=None, nonce=None):

        data = rlp.encode([rlp.encode(int(2002)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(url), rlp.encode(int(end_voting_block)),
                           rlp.encode(param_name), rlp.encode(str(current_value)), rlp.encode(str(new_value))])
        return send_obj_transaction(self, data, from_address, self.web3.pipAddress, gas_price, gas, 0, pri_key, nonce)

    def submitCancel(self, verifier, pip_id, end_voting_rounds, tobe_canceled_proposal_id, pri_key,
                     from_address, gas_price=None, gas=None, nonce=None):

        if tobe_canceled_proposal_id[:2] == '0x':
            tobe_canceled_proposal_id = tobe_canceled_proposal_id[2:]
        data = rlp.encode([rlp.encode(int(2005)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(pip_id), rlp.encode(int(end_voting_rounds)),
                           rlp.encode(bytes.fromhex(tobe_canceled_proposal_id))])

        return send_obj_transaction(self, data, from_address, self.web3.pipAddress, gas_price, gas, 0, pri_key, nonce)

    def vote(self, verifier, proposal_id, option, program_version, version_sign, pri_key, from_address,
             gas_price=None, gas=None, nonce=None):

        if proposal_id[:2] == '0x':
            proposal_id = proposal_id[2:]
        if version_sign[:2] == '0x':
            version_sign = version_sign[2:]
        data = rlp.encode([rlp.encode(int(2003)), rlp.encode(bytes.fromhex(verifier)),
                           rlp.encode(bytes.fromhex(proposal_id)), rlp.encode(option), rlp.encode(int(program_version)),
                           rlp.encode(bytes.fromhex(version_sign))])
        return send_obj_transaction(self, data, from_address, self.web3.pipAddress, gas_price, gas, 0, pri_key, nonce)

    def declareVersion(self, active_node, version, version_sign, pri_key, from_address, gas_price=None,
                       gas=None, nonce=None):

        if version_sign[0:2] == '0x':
            version_sign = version_sign[2:]
        data = rlp.encode([rlp.encode(int(2004)), rlp.encode(bytes.fromhex(active_node)),
                           rlp.encode(int(version)), rlp.encode(bytes.fromhex(version_sign))])
        return send_obj_transaction(self, data, from_address, self.web3.pipAddress, gas_price, gas, 0, pri_key, nonce)

    def getProposal(self, proposal_id, from_address=None):
        if proposal_id[:2] == '0x':
            proposal_id = proposal_id[2:]
        data = rlp.encode([rlp.encode(int(2100)), rlp.encode(bytes.fromhex(proposal_id))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def getTallyResult(self, proposal_id, from_address=None):

        if proposal_id[:2] == '0x':
            proposal_id = proposal_id[2:]
        data = rlp.encode([rlp.encode(int(2101)), rlp.encode(bytes.fromhex(proposal_id))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def getAccuVerifiersCount(self, proposal_id, block_hash, from_address=None):
        if proposal_id[:2] == '0x':
            proposal_id = proposal_id[2:]
        if block_hash[:2] == '0x':
            block_hash = block_hash[2:]
        data = rlp.encode(
            [rlp.encode(int(2105)), rlp.encode(bytes.fromhex(proposal_id)), rlp.encode(bytes.fromhex(block_hash))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def listProposal(self, from_address=None):
        data = rlp.encode([rlp.encode(int(2102))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def getActiveVersion(self, from_address=None):
        data = rlp.encode([rlp.encode(int(2103))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    # def getProgramVersion(self, from_address=None):
    #     data = rlp.encode([rlp.encode(int(2104))])
    #     return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def listParam(self, from_address=None):
        data = rlp.encode([rlp.encode(int(2105))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))
