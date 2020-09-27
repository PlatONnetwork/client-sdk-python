import json
import rlp

from alaya.module import (
    Module,
)
from alaya.utils.transactions import send_obj_transaction, call_obj


def parse_data(raw_data):
    data = str(raw_data, encoding="utf-8")
    if data == "":
        return ""
    return json.loads(data)


class Pip(Module):
    # If you want to get the result of the transaction, please set it to True,
    # if you only want to get the transaction hash, please set it to False
    need_analyze = True

    def submitText(self, verifier, pip_id, pri_key, transaction_cfg=None):
        """
        Submit a text proposal
        :param verifier: The certified submitting the proposal
        :param pip_id: PIPID
        :param pri_key: Private key for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        data = rlp.encode([rlp.encode(int(2000)), rlp.encode(bytes.fromhex(verifier)), rlp.encode(pip_id)])
        return send_obj_transaction(self, data, self.web3.pipAddress, pri_key, transaction_cfg)

    def submitVersion(self, verifier, pip_id, new_version, end_voting_rounds, pri_key, transaction_cfg=None):
        """
        Submit an upgrade proposal
        :param verifier:  The certified submitting the proposal
        :param pip_id:  PIPID
        :param new_version: upgraded version
        :param end_voting_rounds: The number of voting consensus rounds.
            Explanation: Assume that the transaction submitted by the proposal is rounded when the consensus round
            number of the package is packed into the block, then the proposal voting block is high,
            which is the 230th block height of the round of the round1 + endVotingRounds
            (assuming a consensus round out of block 250, ppos The list is 20 blocks high in advance,
             250, 20 are configurable), where 0 < endVotingRounds <= 4840 (about 2 weeks, the actual discussion
             can be calculated according to the configuration), and is an integer)
        :param pri_key: Private key for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        data = rlp.encode([rlp.encode(int(2001)), rlp.encode(bytes.fromhex(verifier)), rlp.encode(pip_id),
                           rlp.encode(int(new_version)), rlp.encode(int(end_voting_rounds))])
        return send_obj_transaction(self, data, self.web3.pipAddress, pri_key, transaction_cfg)

    def submitParam(self, verifier, pip_id, module, name, new_value, pri_key, transaction_cfg=None):
        """
        Submit an param proposal
        :param verifier: The certified submitting the proposal
        :param pip_id: PIPID
        :param module: parameter module
        :param name: parameter name
        :param new_value: New parameter value
        :param pri_key: Private key for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        data = rlp.encode([rlp.encode(int(2002)), rlp.encode(bytes.fromhex(verifier)), rlp.encode(pip_id), rlp.encode(module),
                           rlp.encode(name), rlp.encode(new_value)])
        return send_obj_transaction(self, data, self.web3.pipAddress, pri_key, transaction_cfg)

    def submitCancel(self, verifier, pip_id, end_voting_rounds, tobe_canceled_proposal_id, pri_key, transaction_cfg=None):
        """
        Submit cancellation proposal
        :param verifier: The certified submitting the proposal
        :param pip_id: PIPID
        :param end_voting_rounds:
           The number of voting consensus rounds. Refer to the instructions for submitting the upgrade proposal.
           At the same time, the value of this parameter in this interface
           cannot be greater than the value in the corresponding upgrade proposal.
        :param tobe_canceled_proposal_id: Upgrade proposal ID to be cancelled
        :param pri_key: Private key for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        if tobe_canceled_proposal_id[:2] == '0x':
            tobe_canceled_proposal_id = tobe_canceled_proposal_id[2:]
        data = rlp.encode([rlp.encode(int(2005)), rlp.encode(bytes.fromhex(verifier)), rlp.encode(pip_id),
                           rlp.encode(int(end_voting_rounds)), rlp.encode(bytes.fromhex(tobe_canceled_proposal_id))])

        return send_obj_transaction(self, data, self.web3.pipAddress, pri_key, transaction_cfg)

    def vote(self, verifier, proposal_id, option, program_version, version_sign, pri_key, transaction_cfg=None):
        """
        Vote for proposal
        :param verifier:  The certified submitting the proposal
        :param proposal_id: Proposal ID
        :param option: Voting option
        :param program_version: Node code version, obtained by rpc getProgramVersion interface
        :param version_sign: Code version signature, obtained by rpc getProgramVersion interface
        :param pri_key: Private key for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        if proposal_id[:2] == '0x':
            proposal_id = proposal_id[2:]
        if version_sign[:2] == '0x':
            version_sign = version_sign[2:]
        data = rlp.encode([rlp.encode(int(2003)), rlp.encode(bytes.fromhex(verifier)), rlp.encode(bytes.fromhex(proposal_id)),
                           rlp.encode(option), rlp.encode(int(program_version)), rlp.encode(bytes.fromhex(version_sign))])
        return send_obj_transaction(self, data, self.web3.pipAddress, pri_key, transaction_cfg)

    def declareVersion(self, active_node, program_version, version_sign, pri_key, transaction_cfg=None):
        """
        Version statement
        :param active_node: The declared node can only be a verifier/candidate
        :param program_version: The declared version, obtained by rpc's getProgramVersion interface
        :param version_sign: The signed version signature, obtained by rpc's getProgramVersion interface
        :param pri_key: Private key for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        if version_sign[0:2] == '0x':
            version_sign = version_sign[2:]
        data = rlp.encode([rlp.encode(int(2004)), rlp.encode(bytes.fromhex(active_node)), rlp.encode(int(program_version)),
                           rlp.encode(bytes.fromhex(version_sign))])
        return send_obj_transaction(self, data, self.web3.pipAddress, pri_key, transaction_cfg)

    def getProposal(self, proposal_id, from_address=None):
        """
        Query proposal
        :param proposal_id: proposal id
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        if proposal_id[:2] == '0x':
            proposal_id = proposal_id[2:]
        data = rlp.encode([rlp.encode(int(2100)), rlp.encode(bytes.fromhex(proposal_id))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def getTallyResult(self, proposal_id, from_address=None):
        """
        Query proposal results
        :param proposal_id: proposal id
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        if proposal_id[:2] == '0x':
            proposal_id = proposal_id[2:]
        data = rlp.encode([rlp.encode(int(2101)), rlp.encode(bytes.fromhex(proposal_id))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def getAccuVerifiersCount(self, proposal_id, block_hash, from_address=None):
        """
        Query the cumulative number of votes for the proposal
        :param proposal_id:  proposal id
        :param block_hash: block hash
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        if proposal_id[:2] == '0x':
            proposal_id = proposal_id[2:]
        if block_hash[:2] == '0x':
            block_hash = block_hash[2:]
        data = rlp.encode(
            [rlp.encode(int(2105)), rlp.encode(bytes.fromhex(proposal_id)), rlp.encode(bytes.fromhex(block_hash))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def listProposal(self, from_address=None):
        """
        Query proposal list
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        data = rlp.encode([rlp.encode(int(2102))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def getActiveVersion(self, from_address=None):
        """
        Query the chain effective version of the node
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        data = rlp.encode([rlp.encode(int(2103))])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def getGovernParamValue(self, module, name, from_address=None):
        """
        Query the current block height governance parameter value
        :param module: Parameter module
        :param name: parameter name
        :param from_address:
        :return:
        """
        data = rlp.encode([rlp.encode(int(2104)), rlp.encode(module), rlp.encode(name)])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))

    def listGovernParam(self, module=None, from_address=None):
        """
        Query governance parameter list
        :param module
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        if module is None:
            module = ""
        data = rlp.encode([rlp.encode(int(2106)), rlp.encode(module)])
        return parse_data(call_obj(self, from_address, self.web3.pipAddress, data))
