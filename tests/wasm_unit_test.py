import rlp
import time
import random as _
import binascii
import json
import os
from hexbytes import HexBytes
from client_sdk_python import Web3, HTTPProvider
from client_sdk_python.eth import PlatON
from client_sdk_python.utils.transactions import get_block_gas_limit

w3 = Web3(HTTPProvider("http://192.168.21.75:6789"))
platon = PlatON(w3)
from_address = 'lat1c6a7wyxedrs3pgmf5ansd3xlrkd7zyhvy94sn3'
gas = get_block_gas_limit(w3) - 1

# unlock account
# w3.personal.unlockAccount('lat1c6a7wyxedrs3pgmf5ansd3xlrkd7zyhvy94sn3', "123456", 3600*100)


class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)


def hex_json_encode(dict_):
    return json.dumps(dict(dict_), cls=HexJsonEncoder, indent=2)


def wasm_deploy(wasm_bin_path, *args, **kwargs):
    wasm_bin = os.path.join(wasm_bin_path, 'main.wasm')
    abi_path = os.path.join(wasm_bin_path, 'main.abi.json')
    with open(wasm_bin, 'rb') as f:
        contents = f.read()
        bytecode = binascii.b2a_hex(contents)
    with open(abi_path, 'r') as f:
        abi = json.load(f)
    wasm_obj = platon.wasmcontract(abi=abi, bytecode=bytecode, vmtype=1)
    tx_hash = wasm_obj.constructor(*args, **kwargs).transact(
        {
            'from': from_address,
            'gas': gas,
            "gasPrice": 1000000000,
            "chainId": 100
        }
    )

    tx_receipt = platon.waitForTransactionReceipt(tx_hash)
    print(f'tx_receipt:{hex_json_encode(tx_receipt)}')
    contract_address = tx_receipt['contractAddress']
    print(f'contract_address is:{contract_address}')
    print(f'abi is:{abi}')
    return contract_address, abi


def contract_transfer_call_add(contract_address, abi):
    wasm_contract_obj = platon.wasmcontract(address=contract_address, abi=abi, vmtype=1)
    tx_events_hash = wasm_contract_obj.functions.calcAdd(0, 1).transact({'from': from_address, 'gas': gas})
    tx_events_receipt = platon.waitForTransactionReceipt(tx_events_hash)
    print(tx_events_receipt)

    topic_param = wasm_contract_obj.events.Add().processReceipt(tx_events_receipt)
    print(topic_param)


def contract_transfer_put_element(contract_address, abi):
    wasm_contract_obj = platon.wasmcontract(address=contract_address, abi=abi, vmtype=1)
    for i in [11, 12, 13]:
        tx_hash = wasm_contract_obj.functions.putElement(i).transact({'from': from_address, 'gas': gas})
        tx_events_receipt = platon.waitForTransactionReceipt(tx_hash)
        # print(f'contract_transfer_put_element receipt:{hex_json_encode(tx_events_receipt)}')
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
    tx_hash = wasm_contract_obj.functions.clearElement().transact({'from': from_address, 'gas': gas})
    tx_receipt = platon.waitForTransactionReceipt(tx_hash)
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

        self.functions = platon.wasmcontract(address=contract_address, abi=abi, vmtype=1).functions
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
        return getattr(self.functions, f'set{method_name_suffix}'), getattr(self.functions, f'get{method_name_suffix}')

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
                    tx_hash = set_uint(num).transact({'from': from_address, 'gas': gas})
                    info = f'get_and_set_{int_},bit:{bit_},set num:{num}'
                    self.tx_receipt_status(tx_hash, info)
                    time.sleep(2)
                    print(f"get_and_set_{int_},bit is:{bit_},set num:{num},get result:{get_uint().call()}")

    def get_and_set_bool(self):
        for bool_ in [True, False, True]:
            set_bool, get_bool = self.get_method_boj('Bool')
            tx_hash = set_bool(bool_).transact({'from': from_address, 'gas': gas})
            self.tx_receipt_status(tx_hash, f'get_and_set_bool,test value:{bool_}')
            time.sleep(2)
            result = get_bool().call()
            print(result)

    def other_type(self, type_, param):
        set_value, get_value = self.get_method_boj(type_)
        tx_hash = set_value(param).transact({'from': from_address, 'gas': gas})
        self.tx_receipt_status(tx_hash, f'get_and_set_other_type,type is {self.type_},test param:{param}')
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
# con_address, abi_info = wasm_deploy('./wasm/example1')
# abi_info = [{'anonymous': False, 'input': [{'name': 'topic1', 'type': 'string'}, {'name': 'topic2', 'type': 'int32'}], 'name': 'Add', 'topic': 2, 'type': 'Event'}, {'constant': False, 'input': [], 'name': 'init', 'output': 'void', 'type': 'Action'}, {'constant': False, 'input': [], 'name': 'makeNumber', 'output': 'void', 'type': 'Action'}, {'constant': False, 'input': [], 'name': 'deleteNumber', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'get_Numbers', 'output': 'list<int32>', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'a', 'type': 'int32'}, {'name': 'b', 'type': 'int32'}], 'name': 'calcAdd', 'output': 'int32', 'type': 'Action'}]
# con_address='lat1zt5rmejmzww5nglluq459r2ffsld5zamda7xk7'
# contract_transfer_call_add(con_address, abi_info)
# endregion

# region have init params deploy
# con_address, abi_info = wasm_deploy('./wasm/example2',[[1,2,3]])
# con_address = 'lat1a2mgy40v88lfjpzl7nhvt4fnucq2v7xp307k35'
# abi_info = [{'constant': False, 'input': [{'name': 'ele', 'type': 'int32'}], 'name': 'putElement', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'makeCall', 'output': 'int32', 'type': 'Action'}, {'constant': False, 'input': [], 'name': 'clearElement', 'output': 'void', 'type': 'Action'}, {'anonymous': False, 'input': [{'name': 'topic', 'type': 'string'}, {'name': 'arg1', 'type': 'uint32'}], 'name': 'Add', 'topic': 1, 'type': 'Event'}, {'anonymous': False, 'input': [{'name': 'topic', 'type': 'string'}, {'name': 'arg1', 'type': 'int32'}], 'name': 'call2', 'topic': 1, 'type': 'Event'}, {'anonymous': False, 'input': [{'name': 'topic', 'type': 'string'}, {'name': 'arg1', 'type': 'int32'}], 'name': 'put', 'topic': 1, 'type': 'Event'}, {'anonymous': False, 'input': [{'name': 'topic', 'type': 'string'}, {'name': 'arg1', 'type': 'uint32'}], 'name': 'clear', 'topic': 1, 'type': 'Event'}, {'baseclass': [], 'fields': [{'name': 'myParams', 'type': 'int32[]'}], 'name': 'inputParams', 'type': 'struct'}, {'constant': False, 'input': [{'name': 'ipa', 'type': 'inputParams'}], 'name': 'init', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getParams', 'output': 'int32[]', 'type': 'Action'}, {'constant': False, 'input': [], 'name': 'AddCalc', 'output': 'int32', 'type': 'Action'}, {'constant': True, 'input': [{'name': 'a', 'type': 'int32'}, {'name': 'b', 'type': 'int32'}], 'name': 'makeCall2', 'output': 'int32', 'type': 'Action'}]
# contract_transfer_put_element(con_address,abi_info)
# contract_transfer_init_sum(con_address,abi_info)
# decode_vector_type(con_address, abi_info)
# endregion

# region comprehensive test
# con_address, abi_info = wasm_deploy('./wasm/example3')
con_address = 'lat1vdtncj4m0fws6gad0pd8rxcke75yawz6qds5ax'
abi_info = [{'constant': True, 'input': [], 'name': 'getVector', 'output': 'uint16[]', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'int8'}], 'name': 'setChar', 'output': 'void', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'int8'}], 'name': 'setInt8', 'output': 'void', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'uint8'}], 'name': 'setUint8', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getPair', 'output': 'pair<string,int32>', 'type': 'Action'}, {'baseclass': [], 'fields': [{'name': 'head', 'type': 'string'}], 'name': 'message', 'type': 'struct'}, {'baseclass': ['message'], 'fields': [{'name': 'body', 'type': 'string'}, {'name': 'end', 'type': 'string'}], 'name': 'my_message', 'type': 'struct'}, {'constant': True, 'input': [], 'name': 'getMyMessage', 'output': 'my_message', 'type': 'Action'}, {'anonymous': False, 'input': [{'name': 'topic', 'type': 'string'}, {'name': 'arg1', 'type': 'string'}], 'name': 'transfer', 'topic': 1, 'type': 'Event'}, {'anonymous': False, 'input': [{'name': 'topic', 'type': 'string'}, {'name': 'arg2', 'type': 'string'}, {'name': 'arg1', 'type': 'uint16'}], 'name': 'setUint16Evt', 'topic': 1, 'type': 'Event'}, {'constant': False, 'input': [{'name': 'input', 'type': 'FixedHash<256>'}], 'name': 'setFixedHash', 'output': 'void', 'type': 'Action'}, {'anonymous': False, 'input': [{'name': 'topic1', 'type': 'string'}, {'name': 'topic2', 'type': 'uint32'}, {'name': 'arg3', 'type': 'string'}, {'name': 'arg2', 'type': 'uint32'}, {'name': 'arg1', 'type': 'uint32'}], 'name': 'setUint32Evt', 'topic': 2, 'type': 'Event'}, {'constant': False, 'input': [], 'name': 'init', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getUint8', 'output': 'uint8', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'uint16'}], 'name': 'setUint16', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getUint16', 'output': 'uint16', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'uint32'}], 'name': 'setUint32', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getUint32', 'output': 'uint32', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'uint64'}], 'name': 'setUint64', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getUint64', 'output': 'uint64', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'string'}], 'name': 'setString', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getString', 'output': 'string', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'bool'}], 'name': 'setBool', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getBool', 'output': 'bool', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getChar', 'output': 'int8', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'msg', 'type': 'message'}], 'name': 'setMessage', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getMessage', 'output': 'message', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'msg', 'type': 'my_message'}], 'name': 'setMyMessage', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getInt8', 'output': 'int8', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'int16'}], 'name': 'setInt16', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getInt16', 'output': 'int16', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'int32'}], 'name': 'setInt32', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getInt32', 'output': 'int32', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'int64'}], 'name': 'setInt64', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getInt64', 'output': 'int64', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'float'}], 'name': 'setFloat', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getFloat', 'output': 'float', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'double'}], 'name': 'setDouble', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getDouble', 'output': 'double', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'vec', 'type': 'uint16[]'}], 'name': 'setVector', 'output': 'void', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'map<string,string>'}], 'name': 'setMap', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getMap', 'output': 'map<string,string>', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'msg', 'type': 'message'}, {'name': 'input1', 'type': 'int32'}, {'name': 'input2', 'type': 'bool'}], 'name': 'testMultiParams', 'output': 'void', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'uint8[]'}], 'name': 'setBytes', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getBytes', 'output': 'uint8[]', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'string[10]'}], 'name': 'setArray', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getArray', 'output': 'string[10]', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'pair<string,int32>'}], 'name': 'setPair', 'output': 'void', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'set<string>'}], 'name': 'setSet', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getSet', 'output': 'set<string>', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getFixedHash', 'output': 'FixedHash<256>', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'input', 'type': 'list<string>'}], 'name': 'setList', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getList', 'output': 'list<string>', 'type': 'Action'}, {'constant': False, 'input': [{'name': 'addr', 'type': 'FixedHash<20>'}], 'name': 'setAddress', 'output': 'void', 'type': 'Action'}, {'constant': True, 'input': [], 'name': 'getAddress', 'output': 'FixedHash<20>', 'type': 'Action'}]
# type_test = TypeTest(con_address, abi_info, type_='Int',bit=['8', '16', '32', '64'])
# type_test = TypeTest(con_address, abi_info, type_='Double')

# test all type
type_test = TypeTest(con_address, abi_info, bit=['8', '16', '32', '64'])
type_test.run()
# endregion

