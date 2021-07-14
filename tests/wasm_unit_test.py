import time
import rlp
import random as _
import binascii
import json
import os
from hexbytes import HexBytes
from client_sdk_python import Web3, HTTPProvider
from client_sdk_python.eth import PlatON
from client_sdk_python.utils.transactions import get_block_gas_limit

w3 = Web3(HTTPProvider("http://127.0.0.1:6789"))
platon = PlatON(w3)
from_address = 'atp1vjhjpnc2mfl0v7kkvdcmer4nza2xgc6l5483xj'
gas = get_block_gas_limit(w3) - 1
private_key = "90eb5f39c32fe4c93cdc5b553dc3a4ef79a05f60877554bdba0791d30c313cc7"
deploy_model = 'signature'
chainId = 201030
gasPrice = 1000000000


class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)


def SendTxn(txn):
    signed_txn = platon.account.signTransaction(txn, private_key=private_key, net_type='atp')
    res = platon.sendRawTransaction(signed_txn.rawTransaction).hex()
    txn_receipt = platon.waitForTransactionReceipt(res)
    print("SendTxn res:", res)
    print("SendTxn txn_receipt:", txn_receipt)
    return txn_receipt


def hex_json_encode(dict_):
    return json.dumps(dict(dict_), cls=HexJsonEncoder, indent=2)


def deploy(wasm_bin_path, *args, **kwargs):
    if deploy_model == 'proxy':
        wasm_deploy_by_proxy(wasm_bin_path, *args, **kwargs)
    else:
        wasm_deploy_by_signature(wasm_bin_path, *args, **kwargs)


def read_wasm_bin_path(wasm_bin_path):
    wasm_bin = os.path.join(wasm_bin_path, 'main.wasm')
    abi_path = os.path.join(wasm_bin_path, 'main.abi.json')
    with open(wasm_bin, 'rb') as f:
        contents = f.read()
        bytecode = binascii.b2a_hex(contents)
    with open(abi_path, 'r') as f:
        abi = json.load(f)
    return abi, bytecode


def read_abi(abi_path):
    abi_path = os.path.join(abi_path, 'main.abi.json')
    with open(abi_path, 'r') as f:
        abi = json.load(f)
    return abi


def transaction_dict(data, to=None):
    return {"data": data,
            'from': from_address,
            'gas': gas,
            "chainId": chainId,
            "gasPrice": gasPrice,
            "nonce": platon.getTransactionCount(from_address),
            "to": to
            }


def wasm_deploy_by_proxy(wasm_bin_path, *args, **kwargs):
    # need unlock account and from_address wallet file in keystore dir
    abi, bytecode = read_wasm_bin_path(wasm_bin_path)
    wasm_obj = platon.wasmcontract(abi=abi, bytecode=bytecode, vmtype=1)
    tx_hash = wasm_obj.constructor(*args, **kwargs).transact(
        {
            'from': from_address,
            'gas': gas,
            "gasPrice": gasPrice,
            "chainId": chainId
        }
    )

    tx_receipt = platon.waitForTransactionReceipt(tx_hash)
    print(f'tx_receipt:{hex_json_encode(tx_receipt)}')
    contract_address = tx_receipt['contractAddress']
    print(f'contract_address is:{contract_address}')
    print(f'abi is:{abi}')
    return contract_address, abi


def wasm_deploy_by_signature(wasm_bin_path, *args, **kwargs):
    abi, bytecode = read_wasm_bin_path(wasm_bin_path)
    encode_data = platon.wasmcontract(abi=abi, bytecode=bytecode, vmtype=1)._encode_constructor_data(args, kwargs)
    SendTxn(transaction_dict(encode_data))


def contract_transfer_call_add(contract_address, abi):
    wasm_contract_obj = platon.wasmcontract(address=contract_address, abi=abi, vmtype=1)
    if deploy_model == 'proxy':
        tx_events_hash = wasm_contract_obj.functions.calcAdd(0, 1).transact({'from': from_address, 'gas': gas})
        tx_events_receipt = platon.waitForTransactionReceipt(tx_events_hash)
        print(tx_events_receipt)
    else:
        encode_data = wasm_contract_obj.encodeABI(fn_name="calcAdd", args=[0, 1])
        tx_events_receipt = SendTxn(transaction_dict(encode_data, contract_address))
    topic_param = wasm_contract_obj.events.Add().processReceipt(tx_events_receipt)
    print(topic_param)


def contract_transfer_put_element(contract_address, abi):
    wasm_contract_obj = platon.wasmcontract(address=contract_address, abi=abi, vmtype=1)
    if deploy_model == 'proxy':
        for i in [11, 12, 13]:
            tx_hash = wasm_contract_obj.functions.putElement(i).transact({'from': from_address, 'gas': gas})
            tx_events_receipt = platon.waitForTransactionReceipt(tx_hash)
            # print(f'contract_transfer_put_element receipt:{hex_json_encode(tx_events_receipt)}')
    else:
        for i in [11, 12, 13]:
            encode_data = wasm_contract_obj.encodeABI(fn_name="putElement", args=[i])
            SendTxn(transaction_dict(encode_data, contract_address))
    result = wasm_contract_obj.functions.getParams().call()
    print(f'contract_transfer_put_element:{result}')


def contract_transfer_init_sum(contract_address, abi):
    wasm_contract_obj = platon.wasmcontract(address=contract_address, abi=abi, vmtype=1)
    element_list = wasm_contract_obj.functions.getParams().call()
    print(f'element_list:{element_list}')
    if element_list:
        result = wasm_contract_obj.functions.makeCall().call()
        print(result)
    else:
        return 0


def decode_vector_type(contract_address, abi):
    wasm_contract_obj = platon.wasmcontract(address=contract_address, abi=abi, vmtype=1)
    if deploy_model == 'proxy':
        tx_hash = wasm_contract_obj.functions.clearElement().transact({'from': from_address, 'gas': gas})
        tx_receipt = platon.waitForTransactionReceipt(tx_hash)
    else:
        encode_data = wasm_contract_obj.encodeABI(fn_name="clearElement")
        tx_receipt = SendTxn(transaction_dict(encode_data, contract_address))
    topic_param = wasm_contract_obj.events.clear().processReceipt(tx_receipt)
    print(topic_param)


class TypeTest:
    def __init__(self, contract_address, abi, type_=None, bit=None):
        type_list = ['Bool', 'String', 'Uint', 'Array', 'List', 'Map', 'Vector', 'Message', 'Bytes', 'Set',
                     'MyMessage', 'Double', 'Pair', 'Int', 'FixedHash']
        if type_ and type_ not in type_list:
            print(f'not exits {type_}')
            return
        if bit is None:
            bit = ['8']
        self.abi = abi
        self.wasm_obj = platon.wasmcontract(address=contract_address, abi=abi, vmtype=1)
        self.type_ = type_
        self.bit = bit

    def batch_test(self):
        self.get_and_set_uint()
        self.get_and_set_bool()
        self.get_and_set_other_type()

    def run(self):
        if not self.type_:
            self.batch_test()
        else:
            if self.type_ in ['Uint', 'Int']:
                self.get_and_set_uint()
            if self.type_ == 'Bool':
                self.get_and_set_bool()
            else:
                self.get_and_set_other_type()

    @staticmethod
    def tx_receipt_status(tx_hash, info):
        tx_receipt = platon.waitForTransactionReceipt(tx_hash)
        if not tx_receipt['status']:
            print(f"bit is:{info},tx status\n:{hex_json_encode(tx_receipt)}")

    def get_method_boj(self, method_name_suffix):
        return getattr(self.wasm_obj.functions, f'set{method_name_suffix}'), getattr(self.wasm_obj.functions,
                                                                                     f'get{method_name_suffix}')

    def get_and_set_uint(self):
        uint_data = {
            '8': [0, 255, _.randint(0, 255)],
            '16': [0, 65535, _.randint(0, 65535)],
            '32': [0, 4294967295, _.randint(0, 4294967295)],
            '64': [0, 18446744073709551615, _.randint(0, 9007199254740991)]
        }
        int_data = {
            '8': [-128, 127, _.randint(-128, 127)],
            '16': [-32767, 32767, _.randint(-32767, 32768)],
            '32': [-2147483648, 2147483647, _.randint(-2147483648, 2147483647)],
            '64': [-9223372036854775808, 9223372036854775807, _.randint(-9223372036854775808, 9223372036854775807)]
        }
        test_data = {'Uint': uint_data, 'Int': int_data}
        int_or_uint = [self.type_] if self.type_ else ['Uint', 'Int']
        for int_ in int_or_uint:
            for bit_ in self.bit:
                set_uint, get_uint = self.get_method_boj(f'{int_}{bit_}')
                for num in test_data[int_][bit_]:
                    if deploy_model == 'proxy':
                        tx_hash = set_uint(num).transact({'from': from_address, 'gas': gas})
                        info = f'get_and_set_{int_},bit:{bit_},set num:{num}'
                        self.tx_receipt_status(tx_hash, info)
                    else:
                        method_name = f"set{int_}{bit_}"
                        encode_data = self.wasm_obj.encodeABI(fn_name=method_name, args=[num])
                        SendTxn(transaction_dict(encode_data, con_address))
                    time.sleep(2)
                    print(f"get_and_set_{int_},bit is:{bit_},set num:{num},get result:{get_uint().call()}")

    def get_and_set_bool(self):
        for bool_ in [True, False, True]:
            set_bool, get_bool = self.get_method_boj('Bool')
            if deploy_model == 'proxy':
                tx_hash = set_bool(bool_).transact({'from': from_address, 'gas': gas})
                self.tx_receipt_status(tx_hash, f'get_and_set_bool,test value:{bool_}')
            else:
                encode_data = self.wasm_obj.encodeABI(fn_name=f"setBool", args=[bool_])
                SendTxn(transaction_dict(encode_data, con_address))
            time.sleep(2)
            result = get_bool().call()
            print(result)

    def other_type(self, type_, param):
        set_value, get_value = self.get_method_boj(type_)
        if deploy_model == 'proxy':
            tx_hash = set_value(param).transact({'from': from_address, 'gas': gas})
            self.tx_receipt_status(tx_hash, f'get_and_set_other_type,type is {self.type_},test param:{param}')
        else:
            method_name = f"set{type_}"
            encode_data = self.wasm_obj.encodeABI(fn_name=method_name, args=[param])
            SendTxn(transaction_dict(encode_data, con_address))
        result = get_value().call()
        print(f'type is:{type_},set param:{param},get result:{result}')

    def get_and_set_other_type(self):
        params = {
            'String': 'test string type',
            'Array': ['hello', 'world', 'may', 'the', 'force', 'with', 'you', 'impossible', 'dancing', 'in dark'],
            'List': ["1", "hello", "world"],
            'Map': [['hello world', 'may the force with you'], ['how are you', 'fine,thanks and you ? Oh,ok']],
            'Vector': [0, 65535, _.randint(0, 65535), _.randint(0, 65535), _.randint(0, 65535), _.randint(0, 65535)],
            'Message': ['HelloWorld'],
            'Set': ['str1', 'str2', 'str3'],
            'MyMessage': [['HelloWorld'], 'Wasm', 'Good'],  # struct
            'Pair': ['test setPair', -435716456],
            'FixedHash': 'd28c7465737420736574506169728433f102cf',
            # 'Double': 1.45,  # wasm不支持
        }
        if self.type_ in ['Uint', 'Int']:
            return
        if self.type_:
            self.other_type(self.type_, params[self.type_])
        else:
            for type_, param in params.items():
                self.other_type(type_, param)


# region test easy deploy and sum int number
# abi_bin_path = './wasm/example1'
# deploy(abi_bin_path)
# abi_info = read_abi(abi_bin_path)
# con_address = 'atp1hxshhg6cxhpyl8nm5xw7qxgppupwntr9vl9tq7'
# contract_transfer_call_add(con_address, abi_info)
# endregion

# region have init params deploy
# abi_bin_path = './wasm/example2'
# wasm_deploy_by_signature(abi_bin_path,[[1,2,3]])
# con_address = 'atp1rp6ju6cxg9a0pp80ny45eaf90v9wv33x6czqqa'
# abi_info = read_abi(abi_bin_path)
# contract_transfer_put_element(con_address,abi_info)
# contract_transfer_init_sum(con_address,abi_info)
# decode_vector_type(con_address, abi_info)
# endregion

# region comprehensive test
abi_bin_path = './wasm/example3'
# deploy(abi_bin_path)
con_address = 'atp13gut8q4lztn00e82wy5jlxcy5ya9445ncrm68q'
abi_info = read_abi(abi_bin_path)
# type_test = TypeTest(con_address, abi_info, type_='Double')
# type_test = TypeTest(con_address, abi_info, type_='Int', bit=['8', '16', '32', '64'])

# test all type
type_test = TypeTest(con_address, abi_info)
# type_test = TypeTest(con_address, abi_info, type_='Vector')
type_test.run()
# endregion


# region comprehensive test deploy by proxy
# abi_bin_path = './wasm/example3'
# # deploy(abi_bin_path)
# con_address = 'atp1jy93nnaeg804j9fdhmmq4tdvd2rxk2ntfwslqv'
# abi_info = read_abi(abi_bin_path)
# # # type_test = TypeTest(con_address, abi_info, type_='Double')
# type_test = TypeTest(con_address, abi_info, type_='Int', bit=['8'])
# #
# # # test all type
# # # type_test = TypeTest(con_address, abi_info, bit=['8', '16', '32', '64'])
# type_test.run()
# # endregion
