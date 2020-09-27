from client_sdk_python import Web3, eth, ppos, HTTPProvider

url = "http://192.168.16.11:6789"
w3 = Web3(HTTPProvider(url), chain_id=298)
# address = 'lax12jn6835z96ez93flwezrwu4xpv8e4zatc4kfru'
eth = eth.Eth(w3)
ppos = ppos.Ppos(w3)


eth.blockNumber
eth.getBlock()

# print(ppos.getCandidateList())
from_address = "lax1pd5pfmq8apq5wnfjmgg7nf6crfpff8wwgvnzat"
# accounts = "lax1pd5pfmq8apq5wnfjmgg7nf6crfpff8wwgvnzat;lax1yrfd8dc5jjzkvjaygv5sfqs6aa29hht3pyzv6l"
accounts = "0x3D452519bB81D4D622840F710B54e074717780A3;0xBE0af016941Acaf08Bf5f4ad185155Df6B7388ce"
result = ppos.getRestrictingBalance(from_address, accounts)
print(f"result == {result}")


# # privatekey to bech32
# from platon_keys.datatypes import PrivateKey
# pk = bytes.fromhex('91751513fa39f02ada9a7110bef0a20e03375e9b05d78036e84e91366276e5d8')
# prikey = PrivateKey(pk)
# print(prikey.public_key.to_bech32_test_address())

# 0x_address to bech32
# from platon_keys.utils import address
# add = bytes.fromhex('BE0af016941Acaf08Bf5f4ad185155Df6B7388ce')
# print(address.address_bytes_to_test_address(add))
#
# 0x_address to bech32
from platon_keys.utils import address
add = bytes.fromhex('0000000000000000000000000000000000000000')
print(address.address_bytes_to_test_address(add))


from platon_keys.utils import address
lax = 'lax1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqmscn5j'
addr = address.test_address_to_address_bytes(lax)
print(addr)
# bytes.fromhex(addr)
