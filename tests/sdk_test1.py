from client_sdk_python import Web3, HTTPProvider
from client_sdk_python.eth import PlatON
from hexbytes import HexBytes

# get blockNumber
w3 = Web3(HTTPProvider("http://10.1.1.2:6789"))
platon = PlatON(w3)
block_number = platon.blockNumber
print(block_number)

# get Balance
address = 'lax1uqug0zq7rcxddndleq4ux2ft3tv6dqljphydrl'
# address = '0x493301712671Ada506ba6Ca7891F436D29185821'
balance = platon.getBalance(address)
print(balance)

# # sendtransaction
# to = '0xC1f330B214668beAc2E6418Dd651B09C7rd", 60)
# # data = {59a4Bf5'
# w3.personal.unlockAccount(address, "passwo
#     "from": address,
#     "to": to,
#     "value": 0x10909,
# }
# transaction_hex = HexBytes(platon.sendTransaction(data)).hex()
# result = platon.waitForTransactionReceipt(transaction_hex)
# print(result)