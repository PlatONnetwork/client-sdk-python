from client_sdk_python import Web3,HTTPProvider
from client_sdk_python.eth import PlatON
from client_sdk_python.contract import ConciseContract

# Solidity source code
# contract_source_code = '''
# pragma solidity ^0.4.21;
#
# contract Greeter {
#     string public greeting;
#
#     function Greeter() public {
#         greeting = 'Hello';
#     }
#
#     function setGreeting(string _greeting) public {
#         greeting = _greeting;
#     }
#
#     function greet() view public returns (string) {
#         return greeting;
#     }
# }
# '''

true = True
false = False

w3 = Web3(HTTPProvider("http://10.1.1.5:6789"))
platon = PlatON(w3)
print(w3.isConnected())

from_address = "lax1l0sm6ath520sa8tsq499ya8a5j9qkzh2zxgddm"
print(from_address)

send_privatekey = "16e80ad4079462cc7f9748af2f9cf03e8f7384bed597c086db4f11a98c3b08f0"

bytecode = '608060405234801561001057600080fd5b506040518060400160405280600581526020017f48656c6c6f0000000000000000000000000000000000000000000000000000008152506000908051906020019061005c929190610062565b50610107565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106100a357805160ff19168380011785556100d1565b828001600101855582156100d1579182015b828111156100d05782518255916020019190600101906100b5565b5b5090506100de91906100e2565b5090565b61010491905b808211156101005760008160009055506001016100e8565b5090565b90565b610465806101166000396000f3fe608060405234801561001057600080fd5b50600436106100415760003560e01c8063a413686214610046578063cfae321714610101578063ef690cc014610184575b600080fd5b6100ff6004803603602081101561005c57600080fd5b810190808035906020019064010000000081111561007957600080fd5b82018360208201111561008b57600080fd5b803590602001918460018302840111640100000000831117156100ad57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610207565b005b610109610221565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561014957808201518184015260208101905061012e565b50505050905090810190601f1680156101765780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b61018c6102c3565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156101cc5780820151818401526020810190506101b1565b50505050905090810190601f1680156101f95780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b806000908051906020019061021d929190610361565b5050565b606060008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102b95780601f1061028e576101008083540402835291602001916102b9565b820191906000526020600020905b81548152906001019060200180831161029c57829003601f168201915b5050505050905090565b60008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156103595780601f1061032e57610100808354040283529160200191610359565b820191906000526020600020905b81548152906001019060200180831161033c57829003601f168201915b505050505081565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106103a257805160ff19168380011785556103d0565b828001600101855582156103d0579182015b828111156103cf5782518255916020019190600101906103b4565b5b5090506103dd91906103e1565b5090565b61040391905b808211156103ff5760008160009055506001016103e7565b5090565b9056fea265627a7a7231582049d7f8a29a0126f071821d6483cb3a246925e56555044971726b41b649dd7e6864736f6c63782c302e352e31332d646576656c6f702e323032302e352e31382b636f6d6d69742e33616239633638642e6d6f64005c'

# abi = [{"constant":false,"inputs":[],"name":"doWhileControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"doWhileControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"forBreakControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"forBreakControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"forContinueControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"forContinueControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"forControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"forControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"forReturnControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"forReturnControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"int256","name":"age","type":"int256"}],"name":"forThreeControlControl","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"forThreeControlControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getForBreakControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getForContinueControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getForControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getForReturnControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getForThreeControlControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getIfControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getdoWhileResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"age","type":"uint256"}],"name":"ifControl","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"ifControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]
abi = [{'inputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'constructor'}, {'constant': True, 'inputs': [], 'name': 'greet', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'greeting', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'internalType': 'string', 'name': '_greeting', 'type': 'string'}], 'name': 'setGreeting', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}]
# platon.defaultAccount = platon.accounts[0]
# Instantiate and deploy contract
Greeter = platon.contract(abi=abi, bytecode=bytecode)
print(Greeter)
# Submit the transaction that deploys the contract
tx_hash = Greeter.constructor().transact(
    {
        'from':from_address,
        'gas':1500000,
    }
)

# Wait for the transaction to be mined, and get the transaction receipt
tx_receipt = platon.waitForTransactionReceipt(tx_hash)

# Create the contract instance with the newly-deployed address
greeter = platon.contract(address=tx_receipt.contractAddress, abi=abi)

# Display the default greeting from the contract
print('Default contract greeting: {}'.format(
    greeter.functions.greet().call()
))

print('Setting the greeting to Nihao...')
tx_hash = greeter.functions.setGreeting('Nihao').transact(
    {
        'from': from_address,
        'gas': 1500000,
    }
)

# Wait for transaction to be mined...
platon.waitForTransactionReceipt(tx_hash)

# Display the new greeting value
print('Updated contract greeting: {}'.format(
    greeter.functions.greet().call()
))

# # When issuing a lot of reads, try this more concise reader:
# reader = ConciseContract(greeter)
# assert reader.greet() == "Nihao"