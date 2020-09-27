import json
import rlp

from hexbytes import HexBytes
from client_sdk_python.module import (
    Module,
)
from eth_utils.hexadecimal import remove_0x_prefix
from client_sdk_python.utils.encoding import parse_str
from client_sdk_python.utils.transactions import send_obj_transaction, call_obj
from client_sdk_python.packages.platon_account.internal.transactions import bech32_address_bytes


class Ppos(Module):
    # If you want to get the result of the transaction, please set it to True,
    # if you only want to get the transaction hash, please set it to False
    need_analyze = True

    def createStaking(self, typ, benifit_address, node_id, external_id, node_name, website, details, amount,
                      program_version, program_version_sign, bls_pubkey, bls_proof, pri_key, reward_per, transaction_cfg=None):
        """
        Initiate Staking
        :param typ: Indicates whether the account free amount or the account's lock amount is used for staking, 0: free amount; 1: lock amount
        :param benifit_address: Income account for accepting block rewards and staking rewards
        :param node_id: The idled node Id (also called the candidate's node Id)
        :param external_id: External Id (with length limit, Id for the third party to pull the node description)
        :param node_name: The name of the staking node (with a length limit indicating the name of the node)
        :param website: The third-party home page of the node (with a length limit indicating the home page of the node)
        :param details: Description of the node (with a length limit indicating the description of the node)
        :param amount: staking von (unit:von, 1LAT = 10**18 von)
        :param program_version: The real version of the program, admin_getProgramVersion
        :param program_version_sign: The real version of the program is signed, admin_getProgramVersion
        :param bls_pubkey: Bls public key
        :param bls_proof: Proof of bls, obtained by pulling the proof interface, admin_getSchnorrNIZKProve
        :param pri_key: Private key for transaction
        :param reward_per: Proportion of the reward share obtained from the commission, using BasePoint 1BP = 0.01%
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
        benifit_address = bech32_address_bytes(benifit_address)
        if program_version_sign[:2] == '0x':
            program_version_sign = program_version_sign[2:]
        data = HexBytes(rlp.encode([rlp.encode(int(1000)), rlp.encode(typ), rlp.encode(benifit_address),
                                    rlp.encode(bytes.fromhex(node_id)), rlp.encode(external_id), rlp.encode(node_name),
                                    rlp.encode(website), rlp.encode(details),
                                    rlp.encode(amount), rlp.encode(reward_per), rlp.encode(program_version),
                                    rlp.encode(bytes.fromhex(program_version_sign)), rlp.encode(bytes.fromhex(bls_pubkey)),
                                    rlp.encode(bytes.fromhex(bls_proof))])).hex()
        return send_obj_transaction(self, data, self.web3.stakingAddress, pri_key, transaction_cfg)

    def editCandidate(self, benifit_address, node_id, external_id, node_name, website, details, pri_key, reward_per, transaction_cfg=None):
        """
        Modify staking information
        :param benifit_address: Income account for accepting block rewards and staking rewards
        :param node_id: The idled node Id (also called the candidate's node Id)
        :param external_id: External Id (with length limit, Id for the third party to pull the node description)
        :param node_name: The name of the staking node (with a length limit indicating the name of the node)
        :param website: The third-party home page of the node (with a length limit indicating the home page of the node)
        :param details: Description of the node (with a length limit indicating the description of the node)
        :param pri_key: Private key for transaction
        :param reward_per: Proportion of the reward share obtained from the commission, using BasePoint 1BP = 0.01%
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
        # if benifit_address[:2] == '0x':
        #     benifit_address = benifit_address[2:]
        benifit_address = bech32_address_bytes(benifit_address)
        data = HexBytes(rlp.encode([rlp.encode(int(1001)), rlp.encode(benifit_address), rlp.encode(bytes.fromhex(node_id)),
                                    rlp.encode(reward_per),
                                    rlp.encode(external_id), rlp.encode(node_name), rlp.encode(website), rlp.encode(details)])).hex()
        return send_obj_transaction(self, data, self.web3.stakingAddress, pri_key, transaction_cfg)

    def increaseStaking(self, typ, node_id, amount, pri_key, transaction_cfg=None):
        """
        Increase staking
        :param typ: Indicates whether the account free amount or the account's lock amount is used for staking, 0: free amount; 1: lock amount
        :param node_id: The idled node Id (also called the candidate's node Id)
        :param amount: staking von (unit:von, 1LAT = 10**18 von)
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
        data = HexBytes(rlp.encode([rlp.encode(int(1002)), rlp.encode(bytes.fromhex(node_id)), rlp.encode(typ), rlp.encode(amount)])).hex()
        return send_obj_transaction(self, data, self.web3.stakingAddress, pri_key, transaction_cfg)

    def withdrewStaking(self, node_id, pri_key, transaction_cfg=None):
        """
        Withdrawal of staking (one-time initiation of all cancellations, multiple arrivals)
        :param node_id: The idled node Id (also called the candidate's node Id)
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
        data = rlp.encode([rlp.encode(int(1003)), rlp.encode(bytes.fromhex(node_id))])
        return send_obj_transaction(self, data, self.web3.stakingAddress, pri_key, transaction_cfg)

    def delegate(self, typ, node_id, amount, pri_key, transaction_cfg=None):
        """
        Initiate delegate
        :param typ: Indicates whether the account free amount or the account's lock amount is used for delegate, 0: free amount; 1: lock amount
        :param node_id: The idled node Id (also called the candidate's node Id)
        :param amount: Amount of delegate (unit:von, 1LAT = 10**18 von)
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
        data = rlp.encode([rlp.encode(int(1004)), rlp.encode(typ), rlp.encode(bytes.fromhex(node_id)), rlp.encode(amount)])
        return send_obj_transaction(self, data, self.web3.stakingAddress, pri_key, transaction_cfg)

    def withdrewDelegate(self, staking_blocknum, node_id, amount, pri_key, transaction_cfg=None):
        """
        Reduction/revocation of entrustment (all reductions are revoked)
        :param staking_blocknum: A unique indication of a pledge of a node
        :param node_id: The idled node Id (also called the candidate's node Id)
        :param amount: The amount of the entrusted reduction (unit:von, 1LAT = 10**18 von)
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
        data = rlp.encode([rlp.encode(int(1005)), rlp.encode(staking_blocknum), rlp.encode(bytes.fromhex(node_id)), rlp.encode(amount)])
        return send_obj_transaction(self, data, self.web3.stakingAddress, pri_key, transaction_cfg)

    def getVerifierList(self, from_address=None):
        """
        Query the certified queue for the current billing cycle
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        data = rlp.encode([rlp.encode(int(1100))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        parse = parse_str(raw_data)
        try:
            raw_data = parse["Ret"]
            for i in raw_data:
                i["Shares"] = int(i["Shares"], 16)
        except:...
        return parse

    def getValidatorList(self, from_address=None):
        """
        Query the list of certified for the current consensus cycle
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        data = rlp.encode([rlp.encode(int(1101))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        parse = parse_str(raw_data)
        try:
            raw_data = parse["Ret"]
            for i in raw_data:
                i["Shares"] = int(i["Shares"], 16)
        except:...
        return parse

    def getCandidateList(self, from_address=None):
        """
        Query all real-time candidate lists
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        data = rlp.encode([rlp.encode(int(1102))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        parse = parse_str(raw_data)
        try:
            raw_data = parse["Ret"]
            for i in raw_data:
                i["Shares"] = int(i["Shares"], 16)
                i["Released"] = int(i["Released"], 16)
                i["ReleasedHes"] = int(i["ReleasedHes"], 16)
                i["RestrictingPlan"] = int(i["RestrictingPlan"], 16)
                i["RestrictingPlanHes"] = int(i["RestrictingPlanHes"], 16)
        except:...
        return parse

    def getRelatedListByDelAddr(self, del_addr, from_address=None):
        """
        Query the NodeID and pledge ID of the node entrusted by the current account address
        :param del_addr: Client's account address
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        del_addr = bech32_address_bytes(del_addr)
        data = rlp.encode([rlp.encode(int(1103)), rlp.encode(del_addr)])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        return parse_str(raw_data)

    def getDelegateInfo(self, staking_blocknum, del_address, node_id, from_address=None):
        """
        Query current single delegation information
        :param staking_blocknum: Block height at the time of staking
        :param del_address: Client's account address
        :param node_id: Verifier's node ID
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        del_address = bech32_address_bytes(del_address)
        data = rlp.encode([rlp.encode(int(1104)), rlp.encode(staking_blocknum), rlp.encode(del_address), rlp.encode(bytes.fromhex(node_id))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        receive = json.loads(str(raw_data, encoding="utf8"))
        try:
            raw_data_dict = receive["Ret"]
            raw_data_dict["Released"] = int(raw_data_dict["Released"], 16)
            raw_data_dict["ReleasedHes"] = int(raw_data_dict["ReleasedHes"], 16)
            raw_data_dict["RestrictingPlan"] = int(raw_data_dict["RestrictingPlan"], 16)
            raw_data_dict["RestrictingPlanHes"] = int(raw_data_dict["RestrictingPlanHes"], 16)
            raw_data_dict["CumulativeIncome"] = int(raw_data_dict["CumulativeIncome"], 16)
            # raw_data_dict["Reduction"] = int(raw_data_dict["Reduction"], 16)
            receive["Ret"] = raw_data_dict
        except:...
        return receive

    def getCandidateInfo(self, node_id, from_address=None):
        """
        Query the staking information of the current node
        :param node_id: Verifier's node ID
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        data = rlp.encode([rlp.encode(int(1105)), rlp.encode(bytes.fromhex(node_id))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        parse = str(raw_data, encoding="utf8").replace('\\', '').replace('"{', '{').replace('}"', '}')
        receive = json.loads(parse)
        try:
            raw_data_dict = receive["Ret"]
            raw_data_dict["Shares"] = int(raw_data_dict["Shares"], 16)
            raw_data_dict["Released"] = int(raw_data_dict["Released"], 16)
            raw_data_dict["ReleasedHes"] = int(raw_data_dict["ReleasedHes"], 16)
            raw_data_dict["RestrictingPlan"] = int(raw_data_dict["RestrictingPlan"], 16)
            raw_data_dict["RestrictingPlanHes"] = int(raw_data_dict["RestrictingPlanHes"], 16)
            raw_data_dict["DelegateRewardTotal"] = int(raw_data_dict["DelegateRewardTotal"], 16)
            raw_data_dict["DelegateTotal"] = int(raw_data_dict["DelegateTotal"], 16)
            raw_data_dict["DelegateTotalHes"] = int(raw_data_dict["DelegateTotalHes"], 16)
            receive["Ret"] = raw_data_dict
        except:...
        return receive

    def reportDuplicateSign(self, typ, data, pri_key, transaction_cfg=None):
        """
        Report duplicate sign
        :param typ: Represents duplicate sign type, 1:prepareBlock, 2: prepareVote, 3:viewChange
        :param data: Json value of single evidence, format reference RPC interface Evidences
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
        data = rlp.encode([rlp.encode(int(3000)), rlp.encode(typ), rlp.encode(data)])
        return send_obj_transaction(self, data, self.web3.penaltyAddress, pri_key, transaction_cfg)

    def checkDuplicateSign(self, typ, node_id, block_number, from_address=None):
        """
        Check if the node has been reported too much
        :param typ: Represents double sign type, 1:prepareBlock, 2: prepareVote, 3:viewChange
        :param check_address: Reported node address
        :param block_number: Duplicate-signed block height
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        data = rlp.encode([rlp.encode(int(3001)), rlp.encode(int(typ)), rlp.encode(bytes.fromhex(node_id)), rlp.encode(block_number)])
        raw_data = call_obj(self, from_address, self.web3.penaltyAddress, data)
        receive = str(raw_data, encoding="ISO-8859-1")
        if receive == "":
            return receive
        return json.loads(receive)

    def createRestrictingPlan(self, account, plan, pri_key, transaction_cfg=None):
        """
        Create a lockout plan
        :param account: Locked account release account
        :param plan:
        An is a list of RestrictingPlan types (array), and RestrictingPlan is defined as follows:
        type RestrictingPlan struct {
            Epoch uint64
            Amount *big.Int
            }
         where Epoch: represents a multiple of the billing period.
         The product of the number of blocks per billing cycle indicates that the locked fund
         s are released at the target block height. Epoch * The number of blocks per cycle is
         at least greater than the maximum irreversible block height.
         Amount: indicates the amount to be released on the target block.
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
        # if account[:2] == '0x':
        #     account = account[2:]
        account = bech32_address_bytes(account)
        plan_list = []
        for dict_ in plan:
            v = [dict_[k] for k in dict_]
            plan_list.append(v)
        rlp_list = rlp.encode(plan_list)
        data = rlp.encode([rlp.encode(int(4000)), rlp.encode(account), rlp_list])
        return send_obj_transaction(self, data, self.web3.restrictingAddress, pri_key, transaction_cfg)

    def getRestrictingInfo(self, account, from_address=None):
        """
        Get the lock position information.
        :param account: Locked account release account
        :param from_address: Used to call the rpc call method
        :return:
        todo fill
        """
        # if account[:2] == '0x':
        #     account = account[2:]
        account = bech32_address_bytes(account)
        data = rlp.encode([rlp.encode(int(4100)), rlp.encode(account)])
        raw_data = call_obj(self, from_address, self.web3.restrictingAddress, data)
        receive = json.loads(str(raw_data, encoding="ISO-8859-1"))
        try:
            raw_data_dict = receive["Ret"]
            raw_data_dict["balance"] = int(raw_data_dict["balance"], 16)
            raw_data_dict["Pledge"] = int(raw_data_dict["Pledge"], 16)
            raw_data_dict["debt"] = int(raw_data_dict["debt"], 16)
            if raw_data_dict["plans"]:
                for i in raw_data_dict["plans"]:
                    i["amount"] = int(i["amount"], 16)
            receive["Ret"] = raw_data_dict
        except:...
        return receive

    def getPackageReward(self, from_address=None):
        data = rlp.encode([rlp.encode(int(1200))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        receive = json.loads(str(raw_data, encoding="ISO-8859-1"))
        ret = receive["Ret"]
        receive["Ret"] = int(str(ret), 16)
        return receive

    def getStakingReward(self, from_address=None):
        data = rlp.encode([rlp.encode(int(1201))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        receive = json.loads(str(raw_data, encoding="ISO-8859-1"))
        ret = receive["Ret"]
        receive["Ret"] = int(str(ret), 16)
        return receive

    def getAvgPackTime(self, from_address=None):
        data = rlp.encode([rlp.encode(int(1202))])
        raw_data = call_obj(self, from_address, self.web3.stakingAddress, data)
        receive = json.loads(str(raw_data, encoding="ISO-8859-1"))
        return receive

    def getDelegateReward(self, from_address, node_ids=[]):
        node_id_bytes = [bytes.fromhex(node_id) for node_id in node_ids]
        tmp_from_address = bech32_address_bytes(from_address)
        data = [rlp.encode(int(5100)), rlp.encode(tmp_from_address), rlp.encode(node_id_bytes)]
        data = rlp.encode(data)
        raw_data = call_obj(self, from_address, self.web3.delegateRewardAddress, data)
        receive = json.loads(str(raw_data, encoding="ISO-8859-1"))
        try:
            raw_data_dict = receive["Ret"]
            result = []
            for d in raw_data_dict:
                d["reward"] = int(d["reward"], 16)
                result.append(d)
            receive["Ret"] = result
        except:...
        return receive

    def withdrawDelegateReward(self, pri_key, transaction_cfg=None):
        data = rlp.encode([rlp.encode(int(5000))])
        return send_obj_transaction(self, data, self.web3.delegateRewardAddress, pri_key, transaction_cfg)