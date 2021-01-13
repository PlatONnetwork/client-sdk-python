from alaya import Web3,HTTPProvider
from alaya.eth import PlatON


true = True
false = False

w3 = Web3(HTTPProvider("http://10.10.8.209:6789"))
platon = PlatON(w3)
print(w3.isConnected())
from_address = "atp1uqug0zq7rcxddndleq4ux2ft3tv6dqljhyq6jl"
send_privatekey = "983759fe9aac227c535b21d78792d79c2f399b1d43db46ae6d50a33875301557"


bytecode ='608060405234801561001057600080fd5b506102b7806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c806371e5ee5f1461003b578063e590cf7f146100a9575b600080fd5b6100676004803603602081101561005157600080fd5b81019080803590602001909291905050506101b6565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b61015f600480360360208110156100bf57600080fd5b81019080803590602001906401000000008111156100dc57600080fd5b8201836020820111156100ee57600080fd5b8035906020019184602083028401116401000000008311171561011057600080fd5b919080806020026020016040519081016040528093929190818152602001838360200280828437600081840152601f19601f8201169050808301925050505050505091929192905050506101f2565b6040518080602001828103825283818151815260200191508051906020019060200280838360005b838110156101a2578082015181840152602081019050610187565b505050509050019250505060405180910390f35b600081815481106101c357fe5b906000526020600020016000915054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60607324a42648378add5ba81c76b70caa84a9546279228260008151811061021657fe5b602002602001019073ffffffffffffffffffffffffffffffffffffffff16908173ffffffffffffffffffffffffffffffffffffffff168152505081905091905056fea265627a7a7231582095e2e313d166a0c2ce2537b858b388dfa0f631c0c8622519a5b282644d0682ef64736f6c63782c302e352e31332d646576656c6f702e323032302e352e31382b636f6d6d69742e33616239633638642e6d6f64005c'

abi = [{'constant': True, 'inputs': [{'internalType': 'address[]', 'name': 'arr', 'type': 'address[]'}], 'name': 'IuputArray', 'outputs': [{'internalType': 'address[]', 'name': '', 'type': 'address[]'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'name': 'arr', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}]
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
        'chainId':201018,
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
address = ["atp1uqug0zq7rcxddndleq4ux2ft3tv6dqljhyq6jl","atp1uqug0zq7rcxddndleq4ux2ft3tv6dqljhyq6jl"]

# Display the default greeting from the contract
print('Get Address : {}'.format(
    payable.functions.IuputArray(address).call()
))
# Get Address : ['atp1yjjzvjph3tw4h2quw6mse25y492xy7fzc70hra', 'atp1uqug0zq7rcxddndleq4ux2ft3tv6dqljhyq6jl']

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