from client_sdk_python import Web3,HTTPProvider
from client_sdk_python.eth import PlatON


# Solidity source code
# contract_source_code = '''
# pragma solidity ^0.5.0;
#
# contract Payable {
#     //获取地址的余额
#     function getBalances(address addr) view public returns (uint){
#         return addr.balance;
#     }
#
#     function transfer(address payable addr) public payable{
#         addr.transfer(msg.value);
#     }
# }
# '''

true = True
false = False


w3 = Web3(HTTPProvider("http://10.10.8.209:6789"))
platon = PlatON(w3)
print(w3.isConnected())
# w3 = Web3(HTTPProvider("http://10.1.1.5:6789"))
# platon = PlatON(w3)
# print(w3.isConnected())
# from_address = "lax1uqug0zq7rcxddndleq4ux2ft3tv6dqljphydrl"
from_address = "lax1du4w3q0h5gpxh2vpdvtl7m8h2p9qj40a2krhx7"
print(from_address)
# send_privatekey = "983759fe9aac227c535b21d78792d79c2f399b1d43db46ae6d50a33875301557"
send_privatekey = "983759fe9aac227c535b21d78792d79c2f399b1d43db46ae6d50a33875301557"

# bytecode = '608060405234801561001057600080fd5b506040518060400160405280600581526020017f48656c6c6f0000000000000000000000000000000000000000000000000000008152506000908051906020019061005c929190610062565b50610107565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106100a357805160ff19168380011785556100d1565b828001600101855582156100d1579182015b828111156100d05782518255916020019190600101906100b5565b5b5090506100de91906100e2565b5090565b61010491905b808211156101005760008160009055506001016100e8565b5090565b90565b610465806101166000396000f3fe608060405234801561001057600080fd5b50600436106100415760003560e01c8063a413686214610046578063cfae321714610101578063ef690cc014610184575b600080fd5b6100ff6004803603602081101561005c57600080fd5b810190808035906020019064010000000081111561007957600080fd5b82018360208201111561008b57600080fd5b803590602001918460018302840111640100000000831117156100ad57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610207565b005b610109610221565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561014957808201518184015260208101905061012e565b50505050905090810190601f1680156101765780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b61018c6102c3565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156101cc5780820151818401526020810190506101b1565b50505050905090810190601f1680156101f95780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b806000908051906020019061021d929190610361565b5050565b606060008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102b95780601f1061028e576101008083540402835291602001916102b9565b820191906000526020600020905b81548152906001019060200180831161029c57829003601f168201915b5050505050905090565b60008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156103595780601f1061032e57610100808354040283529160200191610359565b820191906000526020600020905b81548152906001019060200180831161033c57829003601f168201915b505050505081565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106103a257805160ff19168380011785556103d0565b828001600101855582156103d0579182015b828111156103cf5782518255916020019190600101906103b4565b5b5090506103dd91906103e1565b5090565b61040391905b808211156103ff5760008160009055506001016103e7565b5090565b9056fea265627a7a7231582049d7f8a29a0126f071821d6483cb3a246925e56555044971726b41b649dd7e6864736f6c63782c302e352e31332d646576656c6f702e323032302e352e31382b636f6d6d69742e33616239633638642e6d6f64005c'
# bytecode = '608060405234801561001057600080fd5b506040516106243803806106248339818101604052602081101561003357600080fd5b810190808051604051939291908464010000000082111561005357600080fd5b8382019150602082018581111561006957600080fd5b825186600182028301116401000000008211171561008657600080fd5b8083526020830192505050908051906020019080838360005b838110156100ba57808201518184015260208101905061009f565b50505050905090810190601f1680156100e75780820380516001836020036101000a031916815260200191505b50604052505050806000908051906020019061010492919061010b565b50506101b0565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061014c57805160ff191683800117855561017a565b8280016001018555821561017a579182015b8281111561017957825182559160200191906001019061015e565b5b509050610187919061018b565b5090565b6101ad91905b808211156101a9576000816000905550600101610191565b5090565b90565b610465806101bf6000396000f3fe608060405234801561001057600080fd5b50600436106100415760003560e01c8063a413686214610046578063cfae321714610101578063ef690cc014610184575b600080fd5b6100ff6004803603602081101561005c57600080fd5b810190808035906020019064010000000081111561007957600080fd5b82018360208201111561008b57600080fd5b803590602001918460018302840111640100000000831117156100ad57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610207565b005b610109610221565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561014957808201518184015260208101905061012e565b50505050905090810190601f1680156101765780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b61018c6102c3565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156101cc5780820151818401526020810190506101b1565b50505050905090810190601f1680156101f95780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b806000908051906020019061021d929190610361565b5050565b606060008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102b95780601f1061028e576101008083540402835291602001916102b9565b820191906000526020600020905b81548152906001019060200180831161029c57829003601f168201915b5050505050905090565b60008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156103595780601f1061032e57610100808354040283529160200191610359565b820191906000526020600020905b81548152906001019060200180831161033c57829003601f168201915b505050505081565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106103a257805160ff19168380011785556103d0565b828001600101855582156103d0579182015b828111156103cf5782518255916020019190600101906103b4565b5b5090506103dd91906103e1565b5090565b61040391905b808211156103ff5760008160009055506001016103e7565b5090565b9056fea265627a7a72315820f67de41e40b8cf679e7bae0565040506f43456684b3fa204030df4e564ea476264736f6c63782c302e352e31332d646576656c6f702e323032302e352e31382b636f6d6d69742e33616239633638642e6d6f64005c'
bytecode = '608060405234801561001057600080fd5b506101a1806100206000396000f3fe6080604052600436106100295760003560e01c80631a6952301461002e578063c84aae1714610072575b600080fd5b6100706004803603602081101561004457600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506100d7565b005b34801561007e57600080fd5b506100c16004803603602081101561009557600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610121565b6040518082815260200191505060405180910390f35b8073ffffffffffffffffffffffffffffffffffffffff166108fc349081150290604051600060405180830381858888f1935050505015801561011d573d6000803e3d6000fd5b5050565b60008173ffffffffffffffffffffffffffffffffffffffff1631905091905056fea265627a7a723158205ec5e488bb1e8d852f1da0fafa9a4557d3c92d3bf9b839b176c551d75c76b51064736f6c63782c302e352e31332d646576656c6f702e323032302e352e31382b636f6d6d69742e33616239633638642e6d6f64005c'

# abi = [{"constant":false,"inputs":[],"name":"doWhileControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"doWhileControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"forBreakControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"forBreakControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"forContinueControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"forContinueControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"forControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"forControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"forReturnControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"forReturnControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"int256","name":"age","type":"int256"}],"name":"forThreeControlControl","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"forThreeControlControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getForBreakControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getForContinueControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getForControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getForReturnControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getForThreeControlControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getIfControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getdoWhileResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"age","type":"uint256"}],"name":"ifControl","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"ifControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]
# abi = [{'inputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'constructor'}, {'constant': True, 'inputs': [], 'name': 'greet', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'greeting', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'internalType': 'string', 'name': '_greeting', 'type': 'string'}], 'name': 'setGreeting', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}]
# abi = [{'inputs': [{'internalType': 'string', 'name': '_greeting', 'type': 'string'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'constructor'}, {'constant': True, 'inputs': [], 'name': 'greet', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'greeting', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'internalType': 'string', 'name': '_greeting', 'type': 'string'}], 'name': 'setGreeting', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}]
abi = [{'constant': True, 'inputs': [{'internalType': 'address', 'name': 'addr', 'type': 'address'}], 'name': 'getBalances', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'internalType': 'address payable', 'name': 'addr', 'type': 'address'}], 'name': 'transfer', 'outputs': [], 'payable': True, 'stateMutability': 'payable', 'type': 'function'}]

# Instantiate and deploy contract
Payable = platon.contract(abi=abi, bytecode=bytecode)

# # Submit the transaction that deploys the contract
# tx_hash = Greeter.constructor().transact()
#
# # Wait for the transaction to be mined, and get the transaction receipt
# tx_receipt = platon.waitForTransactionReceipt(tx_hash)
# print(tx_receipt)
#
# contract_instance = platon.contract(address=contractAddress, abi=abi)
def SendTxn(txn):
    signed_txn = platon.account.signTransaction(txn,private_key=send_privatekey)
    res = platon.sendRawTransaction(signed_txn.rawTransaction).hex()
    txn_receipt = platon.waitForTransactionReceipt(res)
    print(res)
    return txn_receipt

txn = Payable.constructor().buildTransaction(
    {
        'chainId':200,
        'nonce':platon.getTransactionCount(from_address),
        'gas':1500000,
        'value':0,
        'gasPrice':1000000000,
    }
)

tx_receipt = SendTxn(txn)
print(tx_receipt)

# Create the contract instance with the newly-deployed address
payable = platon.contract(address=tx_receipt.contractAddress, abi=abi)

# hrpgot, data = bech32.decode("lax", from_address)
# address = to_checksum_address(bytes(data))
# print(address)

# Display the default greeting from the contract
print('Get Address Balance: {}'.format(
    payable.functions.getBalances(from_address).call()
))

# print('Setting the greeting to Nihao...')
# tx_hash = payable.functions.setGreeting('Nihao').transact(
#     {
#         'from':from_address,
#         'gas':1500000,
#     }
# )
# print(tx_hash)
#
# # Wait for transaction to be mined...
# platon.waitForTransactionReceipt(tx_hash)
#
# # Display the new greeting value
# print('Updated contract greeting: {}'.format(
#     payable.functions.greet().call()
# ))

# # When issuing a lot of reads, try this more concise reader:
# reader = ConciseContract(greeter)
# assert reader.greet() == "Nihao"