from alaya import Web3,HTTPProvider
from alaya.eth import PlatON


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

w3 = Web3(HTTPProvider("http://10.1.1.5:6789"))
platon = PlatON(w3)
print(w3.isConnected())

from_address = "lax1yjjzvjph3tw4h2quw6mse25y492xy7fzwdtqja"
print(from_address)

send_privatekey = "b7a7372e78160f71a1a75e03c4aa72705806a05cf14ef39c87fdee93d108588c"

bytecode = '608060405234801561001057600080fd5b506101a1806100206000396000f3fe6080604052600436106100295760003560e01c80631a6952301461002e578063c84aae1714610072575b600080fd5b6100706004803603602081101561004457600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506100d7565b005b34801561007e57600080fd5b506100c16004803603602081101561009557600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610121565b6040518082815260200191505060405180910390f35b8073ffffffffffffffffffffffffffffffffffffffff166108fc349081150290604051600060405180830381858888f1935050505015801561011d573d6000803e3d6000fd5b5050565b60008173ffffffffffffffffffffffffffffffffffffffff1631905091905056fea265627a7a723158205ec5e488bb1e8d852f1da0fafa9a4557d3c92d3bf9b839b176c551d75c76b51064736f6c63782c302e352e31332d646576656c6f702e323032302e352e31382b636f6d6d69742e33616239633638642e6d6f64005c'

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
address = "lax1yjjzvjph3tw4h2quw6mse25y492xy7fzwdtqja"
# # Display the default greeting from the contract
print('Get Address Balance: {}'.format(
    payable.functions.getBalances(from_address).call()
))
# print('Get Address Balance: {}'.format(
#     payable.functions.getBalances(from_address).call()
# ))

# print('Setting the greeting to Nihao...')
# address1='lax15r7gxd0c9xqxu0vca35wz0zch5qfyayj9ed3r2'
# tx_hash = payable.functions.transfer(address1).transact(
#     {
#         'from':from_address,
#         'gas':1500000,
#         'value':10000,
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