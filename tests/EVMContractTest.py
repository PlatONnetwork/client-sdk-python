from hexbytes import HexBytes
from alaya import Web3, HTTPProvider
from alaya.eth import PlatON
from alaya.packages.platon_keys.utils import bech32,address
from alaya.packages.eth_utils import to_checksum_address

true = True
false = False

w3 = Web3(HTTPProvider("http://10.1.1.5:6789"))
platon = PlatON(w3)
print(w3.isConnected())

from_address = "lax1yjjzvjph3tw4h2quw6mse25y492xy7fzwdtqja"
print(from_address)
if to_checksum_address(from_address):
    print(from_address)

send_privatekey = "16e80ad4079462cc7f9748af2f9cf03e8f7384bed597c086db4f11a98c3b08f0"

def contract_deploy(bytecode, fromAddress):
    bytecode = bytecode
    transactionHash = platon.sendTransaction(
        {
            "from": fromAddress,
            "gas": 1000000,
            "gasPrice": 1000000000,
            "data": bytecode,
        }
    )
    transactionHash = HexBytes(transactionHash).hex().lower()
    return transactionHash

bytecode = '608060405234801561001057600080fd5b506040518060400160405280600581526020017f48656c6c6f0000000000000000000000000000000000000000000000000000008152506000908051906020019061005c929190610062565b50610107565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106100a357805160ff19168380011785556100d1565b828001600101855582156100d1579182015b828111156100d05782518255916020019190600101906100b5565b5b5090506100de91906100e2565b5090565b61010491905b808211156101005760008160009055506001016100e8565b5090565b90565b610465806101166000396000f3fe608060405234801561001057600080fd5b50600436106100415760003560e01c8063a413686214610046578063cfae321714610101578063ef690cc014610184575b600080fd5b6100ff6004803603602081101561005c57600080fd5b810190808035906020019064010000000081111561007957600080fd5b82018360208201111561008b57600080fd5b803590602001918460018302840111640100000000831117156100ad57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610207565b005b610109610221565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561014957808201518184015260208101905061012e565b50505050905090810190601f1680156101765780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b61018c6102c3565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156101cc5780820151818401526020810190506101b1565b50505050905090810190601f1680156101f95780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b806000908051906020019061021d929190610361565b5050565b606060008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102b95780601f1061028e576101008083540402835291602001916102b9565b820191906000526020600020905b81548152906001019060200180831161029c57829003601f168201915b5050505050905090565b60008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156103595780601f1061032e57610100808354040283529160200191610359565b820191906000526020600020905b81548152906001019060200180831161033c57829003601f168201915b505050505081565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106103a257805160ff19168380011785556103d0565b828001600101855582156103d0579182015b828111156103cf5782518255916020019190600101906103b4565b5b5090506103dd91906103e1565b5090565b61040391905b808211156103ff5760008160009055506001016103e7565b5090565b9056fea265627a7a7231582049d7f8a29a0126f071821d6483cb3a246925e56555044971726b41b649dd7e6864736f6c63782c302e352e31332d646576656c6f702e323032302e352e31382b636f6d6d69742e33616239633638642e6d6f64005c'

abi = [{"constant":False,"inputs":[],"name":"doWhileControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"doWhileControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[],"name":"forBreakControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"forBreakControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[],"name":"forContinueControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"forContinueControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[],"name":"forControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"forControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[],"name":"forReturnControl","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"forReturnControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"int256","name":"age","type":"int256"}],"name":"forThreeControlControl","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"forThreeControlControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getForBreakControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getForContinueControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getForControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getForReturnControlResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getForThreeControlControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getIfControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getdoWhileResult","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"uint256","name":"age","type":"uint256"}],"name":"ifControl","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"ifControlResult","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"}]

tx = contract_deploy(bytecode, from_address)
print(tx)
tx_receipt = platon.waitForTransactionReceipt(tx)
print(tx_receipt)
contractAddress = tx_receipt.contractAddress
print(contractAddress)

# contractAddress = bech32.bech32_decode(contractAddress)
hrpgot, data = bech32.decode("lax", from_address)
address = to_checksum_address(bytes(data))
print('qqq')
print(address)

def SendTxn(txn):
    signed_txn = platon.account.signTransaction(txn,private_key=send_privatekey)
    res = platon.sendRawTransaction(signed_txn.rawTransaction).hex()
    txn_receipt = platon.waitForTransactionReceipt(res)
    print(res)
    return txn_receipt




contract_instance = platon.contract(address=contractAddress, abi=abi)

# txn = contract_instance.functions.ifControl(20).buildTransaction(
#     {
#         'chainId':200,
#         'nonce':platon.getTransactionCount(from_address),
#         'gas':1000000,
#         'value':0,
#         'gasPrice':1000000000,
#     }
# )
# print("aaaa")
# print(SendTxn(txn))
# print("bbbb")

result = contract_instance.functions.getIfControlResult().call()
print(result)