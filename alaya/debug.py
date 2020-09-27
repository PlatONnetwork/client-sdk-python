from alaya.module import (
    Module,
)
import json
import rlp
from hexbytes import HexBytes
from alaya.utils.transactions import send_obj_transaction


class Debug(Module):

    need_analyze = True

    def economicConfig(self):
        return json.loads(self.web3.manager.request_blocking("debug_economicConfig", []))

    def setValidatorList(self, node_list, pri_key, transaction_cfg={"gas": 210000}):
        data_list = []
        for node_id in node_list:
            data_list.append(bytes.fromhex(node_id))
        data = HexBytes(rlp.encode([rlp.encode(int(1900)), rlp.encode(data_list)])).hex()
        return send_obj_transaction(self, data, self.web3.stakingAddress, pri_key, transaction_cfg)

    def getWaitSlashingNodeList(self):
        result = self.web3.manager.request_blocking("debug_getWaitSlashingNodeList", [])
        if not result:
            return []
        return json.loads(result)

