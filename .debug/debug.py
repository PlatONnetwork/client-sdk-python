import os

from alaya import Account
from alaya.packages.eth_utils import keccak, text_if_str, to_bytes


acc = Account()
a = acc.create()
print(a.address)

# extra_key_bytes = text_if_str(to_bytes, '')
# key_bytes = keccak(os.urandom(32) + extra_key_bytes)
# acct = Account.privateKeyToAccount(key_bytes)
#
# print(acct.address, acct.privateKey)
