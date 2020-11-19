import math

from alaya.utils.threads import (
    Timeout,
)
from alaya.utils.toolz import (
    assoc,
    curry,
    merge,
)

from hexbytes import HexBytes

from alaya.packages.platon_keys.datatypes import PrivateKey

VALID_TRANSACTION_PARAMS = [
    'from',
    'to',
    'gas',
    'gasPrice',
    'value',
    'data',
    'nonce',
    'chainId',
]

TRANSACTION_DEFAULTS = {
    'value': 0,
    'data': b'',
    'gas': lambda web3, tx: web3.eth.estimateGas(tx),
    'gasPrice': lambda web3, tx: web3.eth.generateGasPrice(tx) or web3.eth.gasPrice,
    'chainId': lambda web3, tx: web3.net.chainId,
}


def call_obj(obj, from_address, to_address, data):
    # to_address = obj.web3.toChecksumAddress(to_address)
    if from_address is None:
        return obj.web3.platon.call({"to": to_address, "data": data})
    # from_address = obj.web3.toChecksumAddress(from_address)
    return obj.web3.platon.call({"from": from_address, "to": to_address, "data": data})


def send_obj_transaction(obj, data, to_address, pri_key, transaction_cfg: dict):
    transaction_dict = {}
    if transaction_cfg is None:
        transaction_cfg = {}
    if transaction_cfg.get("gasPrice", None) is None:
        transaction_dict["gasPrice"] = obj.web3.platon.gasPrice
    else:
        transaction_dict["gasPrice"] = transaction_cfg["gasPrice"]
    if transaction_cfg.get("nonce", None) is None:
        from_address = obj.web3.pubkey_to_address(PrivateKey(bytes.fromhex(pri_key)).public_key)
        transaction_dict["nonce"] = obj.web3.platon.getTransactionCount(from_address)
    else:
        transaction_dict["nonce"] = transaction_cfg["nonce"]
    if transaction_cfg.get("gas", None) is None:
        from_address = obj.web3.pubkey_to_address(PrivateKey(bytes.fromhex(pri_key)).public_key)
        transaction_data = {"to": to_address, "data": data, "from": from_address}
        try:
            transaction_dict["gas"] = obj.web3.platon.estimateGas(transaction_data)
        except Exception as rep:
            print(rep)
            return rep
    else:
        transaction_dict["gas"] = transaction_cfg["gas"]
    transaction_dict["chainId"] = obj.web3.chainId
    transaction_dict["to"] = to_address
    transaction_dict["data"] = data
    if transaction_cfg.get("value", 0) > 0:
        transaction_dict["value"] = int(transaction_cfg.get("value", 0))
    signed_transaction_dict = obj.web3.platon.account.signTransaction(
        transaction_dict, pri_key, net_type=obj.web3.net_type
    )
    signed_data = signed_transaction_dict.rawTransaction
    tx_hash = HexBytes(obj.web3.platon.sendRawTransaction(signed_data)).hex()
    if obj.need_analyze:
        return obj.web3.platon.analyzeReceiptByHash(tx_hash)
    return tx_hash

@curry
def fill_nonce(web3, transaction):
    if 'from' in transaction and 'nonce' not in transaction:
        return assoc(
            transaction,
            'nonce',
            web3.eth.getTransactionCount(
                transaction['from'],
                block_identifier='pending'))
    else:
        return transaction


@curry
def fill_transaction_defaults(web3, transaction):
    '''
    if web3 is None, fill as much as possible while offline
    '''
    defaults = {}
    for key, default_getter in TRANSACTION_DEFAULTS.items():
        if key not in transaction:
            if callable(default_getter):
                if web3 is not None:
                    default_val = default_getter(web3, transaction)
                else:
                    raise ValueError("You must specify %s in the transaction" % key)
            else:
                default_val = default_getter
            defaults[key] = default_val
    return merge(defaults, transaction)


def wait_for_transaction_receipt(web3, txn_hash, timeout=120, poll_latency=0.1):
    with Timeout(timeout) as _timeout:
        while True:
            txn_receipt = web3.eth.getTransactionReceipt(txn_hash)
            if txn_receipt is not None:
                break
            _timeout.sleep(poll_latency)
    return txn_receipt


def get_block_gas_limit(web3, block_identifier=None):
    if block_identifier is None:
        block_identifier = web3.eth.blockNumber
    block = web3.eth.getBlock(block_identifier)
    return block['gasLimit']


def get_buffered_gas_estimate(web3, transaction, gas_buffer=100000):
    gas_estimate_transaction = dict(**transaction)

    gas_estimate = web3.eth.estimateGas(gas_estimate_transaction)

    gas_limit = get_block_gas_limit(web3)

    if gas_estimate > gas_limit:
        raise ValueError(
            "Contract does not appear to be deployable within the "
            "current network gas limits.  Estimated: {0}. Current gas "
            "limit: {1}".format(gas_estimate, gas_limit)
        )

    return min(gas_limit, gas_estimate + gas_buffer)


def get_required_transaction(web3, transaction_hash):
    current_transaction = web3.eth.getTransaction(transaction_hash)
    if not current_transaction:
        raise ValueError('Supplied transaction with hash {} does not exist'
                         .format(transaction_hash))
    return current_transaction


def extract_valid_transaction_params(transaction_params):
    extracted_params = {key: transaction_params[key]
                        for key in VALID_TRANSACTION_PARAMS if key in transaction_params}

    if extracted_params.get('data') is not None:
        if transaction_params.get('input') is not None:
            if extracted_params['data'] != transaction_params['input']:
                msg = 'failure to handle this transaction due to both "input: {}" and'
                msg += ' "data: {}" are populated. You need to resolve this conflict.'
                err_vals = (transaction_params['input'], extracted_params['data'])
                raise AttributeError(msg.format(*err_vals))
            else:
                return extracted_params
        else:
            return extracted_params
    elif extracted_params.get('data') is None:
        if transaction_params.get('input') is not None:
            return assoc(extracted_params, 'data', transaction_params['input'])
        else:
            return extracted_params
    else:
        raise Exception("Unreachable path: transaction's 'data' is either set or not set")


def assert_valid_transaction_params(transaction_params):
    for param in transaction_params:
        if param not in VALID_TRANSACTION_PARAMS:
            raise ValueError('{} is not a valid transaction parameter'.format(param))


def prepare_replacement_transaction(web3, current_transaction, new_transaction):
    if current_transaction['blockHash'] != HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000'):
        raise ValueError('Supplied transaction with hash {} has already been mined'
                         .format(current_transaction['hash']))

    if 'nonce' in new_transaction:
        if isinstance(new_transaction['nonce'], int) :
            if new_transaction['nonce'] != int(current_transaction['nonce'], 16):
                raise ValueError('Supplied nonce in new_transaction must match the pending transaction')
        else:
            if '0x' in new_transaction['nonce']:
                if int(new_transaction['nonce'], 16) != int(current_transaction['nonce'], 16):
                    raise ValueError('Supplied nonce in new_transaction must match the pending transaction')

    if 'nonce' not in new_transaction:
        new_transaction = assoc(new_transaction, 'nonce', current_transaction['nonce'])

    if 'gasPrice' in new_transaction:
        if new_transaction['gasPrice'] <= current_transaction['gasPrice']:
            raise ValueError('Supplied gas price must exceed existing transaction gas price')
    else:
        generated_gas_price = web3.eth.generateGasPrice(new_transaction)
        minimum_gas_price = int(current_transaction['gasPrice'] * 1.1)
        if generated_gas_price and generated_gas_price > minimum_gas_price:
            new_transaction = assoc(new_transaction, 'gasPrice', generated_gas_price)
        else:
            new_transaction = assoc(new_transaction, 'gasPrice', minimum_gas_price)

    return new_transaction


def replace_transaction(web3, current_transaction, new_transaction):
    new_transaction = prepare_replacement_transaction(
        web3, current_transaction, new_transaction
    )
    return web3.eth.sendTransaction(new_transaction)
