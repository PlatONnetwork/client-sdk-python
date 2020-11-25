from cytoolz import (
    pipe,
)
from alaya.packages.eth_utils import (
    to_bytes,
    to_int,
)

from alaya.packages.platon_account.internal.transactions import (
    ChainAwareUnsignedTransaction,
    UnsignedTransaction,
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
    strip_signature,
)
from hexbytes import (
    HexBytes,
)
import rlp
from alaya.packages.gmssl import sm2, func ,sm3
CHAIN_ID_OFFSET = 35
V_OFFSET = 27


def sign_transaction_dict(eth_key, transaction_dict, mode='ECDSA'):
    # generate RLP-serializable transaction, with defaults filled
    unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction_dict)
    if mode=='ECDSA':
        transaction_hash = unsigned_transaction.hash()
    elif mode=='SM':
        transaction_hash=HexBytes(sm3.sm3_hash(func.bytes_to_list(rlp.encode(unsigned_transaction))))

    # detect chain
    if isinstance(unsigned_transaction, UnsignedTransaction):
        chain_id = None
    else:
        chain_id = unsigned_transaction.v

    # sign with private key
    if mode=='SM':
        SMC=sm2.CryptSM2(hex(eth_key),1)
        rand=func.random_hex(SMC.para_len)
        (r, s, v1) = SMC.sign(transaction_hash, rand)
        v = to_eth_v(v1, chain_id)
    else:
        (v, r, s) = sign_transaction_hash(eth_key, transaction_hash, chain_id)

    # serialize transaction with rlp
    encoded_transaction = encode_transaction(unsigned_transaction, vrs=(v, r, s))

    return (v, r, s, encoded_transaction)


# watch here for updates to signature format: https://github.com/awake006/EIPs/issues/191
def signature_wrapper(message, version=b'E'):
    assert isinstance(message, bytes)
    if version == b'E':
        preamble = b'\x19awake006 Signed Message:\n'
        size = str(len(message)).encode('utf-8')
        return preamble + size + message
    else:
        raise NotImplementedError("Only the 'awake006 Signed Message' preamble is supported")


def hash_of_signed_transaction(txn_obj):
    '''
    Regenerate the hash of the signed transaction object.

    1. Infer the chain ID from the signature
    2. Strip out signature from transaction
    3. Annotate the transaction with that ID, if available
    4. Take the hash of the serialized, unsigned, chain-aware transaction

    Chain ID inference and annotation is according to EIP-155
    See details at https://github.com/awake006/EIPs/blob/master/EIPS/eip-155.md

    :return: the hash of the provided transaction, to be signed
    '''
    (chain_id, _v) = extract_chain_id(txn_obj.v)
    unsigned_parts = strip_signature(txn_obj)
    if chain_id is None:
        signable_transaction = UnsignedTransaction(*unsigned_parts)
    else:
        extended_transaction = unsigned_parts + [chain_id, 0, 0]
        signable_transaction = ChainAwareUnsignedTransaction(*extended_transaction)
    return signable_transaction.hash()


def extract_chain_id(raw_v,mode='ECDSA'):
    '''
    Extracts chain ID, according to EIP-155
    @return (chain_id, v)
    '''
    above_id_offset = raw_v - CHAIN_ID_OFFSET
    if above_id_offset < 0:
        if mode == 'ECDSA':
            if raw_v in {0, 1}:
                return (None, raw_v + V_OFFSET)
            elif raw_v in {27, 28}:
                return (None, raw_v)
            else:
                raise ValueError("v %r is invalid, must be one of: 0, 1, 27, 28, 35+")
        elif mode == 'SM':
            if raw_v in {0, 1, 2, 3}:
                return (None, raw_v + V_OFFSET)
            elif raw_v in {27, 28, 29, 30}:
                return (None, raw_v)
            else:
                raise ValueError("v %r is invalid, must be one of: 0, 1, 27, 28, 35+")
    else:
        (chain_id, v_bit) = divmod(above_id_offset, 2)
        return (chain_id, v_bit + V_OFFSET)


def to_standard_signature_bytes(awake006_signature_bytes,mode='ECDSA'):
    rs = awake006_signature_bytes[:-1]
    v = to_int(awake006_signature_bytes[-1])
    standard_v = to_standard_v(v,mode)
    return rs + to_bytes(standard_v)


def to_standard_v(enhanced_v,mode='ECDSA'):
    (_chain, chain_naive_v) = extract_chain_id(enhanced_v,mode)
    v_standard = chain_naive_v - V_OFFSET
    if mode=='ECDSA':
        assert v_standard in {0, 1}
    elif mode=='SM':
        assert v_standard in {0, 1, 2, 3}
    return v_standard

def to_eth_v(v_raw, chain_id=None):
    if chain_id is None:
        v = v_raw + V_OFFSET
    else:
        v = v_raw + CHAIN_ID_OFFSET + 2 * chain_id
    return v


def sign_transaction_hash(account, transaction_hash, chain_id):
    signature = account.sign_msg_hash(transaction_hash)
    (v_raw, r, s) = signature.vrs
    v = to_eth_v(v_raw, chain_id)
    return (v, r, s)


def _pad_to_eth_word(bytes_val):
    return bytes_val.rjust(32, b'\0')


def to_bytes32(val):
    return pipe(
        val,
        to_bytes,
        _pad_to_eth_word,
    )


def sign_message_hash(key, msg_hash, mode='ECDSA'):
    if mode == 'ECDSA':
        signature = key.sign_msg_hash(msg_hash)
        (v_raw, r, s) = signature.vrs
    elif mode == 'SM':
        privatekey = key.to_bytes()
        SMC = sm2.CryptSM2(privatekey.hex(), 1)
        rand = func.random_hex(SMC.para_len)
        (r, s, v_raw) = SMC.sign(msg_hash, rand)

    v = to_eth_v(v_raw)
    eth_signature_bytes = to_bytes32(r) + to_bytes32(s) + to_bytes(v)
    return (v, r, s, eth_signature_bytes)
