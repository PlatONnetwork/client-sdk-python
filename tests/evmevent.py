from alaya import Web3,HTTPProvider
from alaya.eth import PlatON

true = True
false = False

w3 = Web3(HTTPProvider("http://10.1.1.2:6789"))
platon = PlatON(w3)
print(w3.isConnected())

from_address = "lax1uqug0zq7rcxddndleq4ux2ft3tv6dqljphydrl"
print(from_address)

send_privatekey = "983759fe9aac227c535b21d78792d79c2f399b1d43db46ae6d50a33875301557"

bytecode = '608060405234801561001057600080fd5b50610169806100206000396000f3fe608060405234801561001057600080fd5b50600436106100415760003560e01c806301ad4d8714610046578063477a5c981461006a578063edd89c081461008e575b600080fd5b61004e6100bf565b604051808260ff1660ff16815260200191505060405180910390f35b6100726100d1565b604051808260ff1660ff16815260200191505060405180910390f35b6100bd600480360360208110156100a457600080fd5b81019080803560ff1690602001909291905050506100e7565b005b6000809054906101000a900460ff1681565b60008060009054906101000a900460ff16905090565b806000806101000a81548160ff021916908360ff1602179055508060ff167f6c2b4666ba8da5a95717621d879a77de725f3d816709b9cbe9f059b8f875e28460405160405180910390a25056fea265627a7a7231582090ef2e55c9c3e1fc6cc130590605b1904b7c91f07bf401c7463c6dcebe70a96e64736f6c634300050c0032'

abi = [{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"_var","type":"uint256"}],"name":"MyEvent","type":"event"},{"constant":true,"inputs":[],"name":"_myVar","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint8","name":"_var","type":"uint8"}],"name":"setVar","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getVar","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"}]

Payable = platon.contract(abi=abi, bytecode=bytecode)

tx_hash = Payable.constructor().transact(
    {
        'from':from_address,
        'gas':1500000,
    }
)

# Wait for the transaction to be mined, and get the transaction receipt
tx_receipt = platon.waitForTransactionReceipt(tx_hash)

# Create the contract instance with the newly-deployed address
greeter = platon.contract(address=tx_receipt.contractAddress, abi=abi)

tx_hash = greeter.functions.setVar(100).transact(
    {
        'from':from_address,
        'gas':1500000,
    }
)

tx_receipt = platon.waitForTransactionReceipt(tx_hash)
print(tx_receipt)

topic_param = greeter.events.MyEvent().processReceipt(tx_receipt)
print(topic_param)