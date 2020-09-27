import os

from alaya import Web3, eth, ppos, HTTPProvider, Account
from alaya.packages.eth_utils import keccak, text_if_str, to_bytes

# url = "http://10.10.8.209:6789"
# w3 = Web3(HTTPProvider(url), chain_id=201018)
# # address = 'lax12jn6835z96ez93flwezrwu4xpv8e4zatc4kfru'
# eth = eth.Eth(w3)
# ppos = ppos.Ppos(w3)

extra_key_bytes = text_if_str(to_bytes, '')
key_bytes = keccak(os.urandom(32) + extra_key_bytes)
acct = Account.privateKeyToAccount(key_bytes)

print(acct.address, acct.privateKey)