from requests.exceptions import (
    ConnectionError,
    HTTPError,
    Timeout,
    TooManyRedirects,
)

whitelist = [
    'admin',
    'shh',
    'miner',
    'net',
    'txpool'
    'testing',
    'evm',
    'platon_protocolVersion',
    'platon_syncing',
    'platon_coinbase',
    'platon_mining',
    'platon_hashrate',
    'platon_gasPrice',
    'platon_accounts',
    'platon_blockNumber',
    'platon_getBalance',
    'platon_getStorageAt',
    'platon_getCode',
    'platon_getBlockByNumber',
    'platon_getBlockByHash',
    'platon_getBlockTransactionCountByNumber',
    'platon_getBlockTransactionCountByHash',
    'platon_getUncleCountByBlockNumber',
    'platon_getUncleCountByBlockHash',
    'platon_getTransactionByHash',
    'platon_getTransactionByBlockHashAndIndex',
    'platon_getTransactionByBlockNumberAndIndex',
    'platon_getTransactionReceipt',
    'platon_getTransactionCount',
    'platon_call',
    'platon_estimateGas',
    'platon_newBlockFilter',
    'platon_newPendingTransactionFilter',
    'platon_newFilter',
    'platon_getFilterChanges',
    'platon_getFilterLogs',
    'platon_getLogs',
    'platon_uninstallFilter',
    'platon_getCompilers',
    'platon_getWork',
    'platon_sign',
    'platon_sendRawTransaction',
    'personal_importRawKey',
    'personal_newAccount',
    'personal_listAccounts',
    'personal_lockAccount',
    'personal_unlockAccount',
    'personal_ecRecover',
    'personal_sign'
]


def check_if_retry_on_failure(method):
    root = method.split('_')[0]
    if root in whitelist:
        return True
    elif method in whitelist:
        return True
    else:
        return False


def exception_retry_middleware(make_request, web3, errors, retries=5):
    '''
    Creates middleware that retries failed HTTP requests. Is a default
    middleware for HTTPProvider.
    '''
    def middleware(method, params):
        if check_if_retry_on_failure(method):
            for i in range(retries):
                try:
                    return make_request(method, params)
                except errors:
                    if i < retries - 1:
                        continue
                    else:
                        raise
        else:
            return make_request(method, params)
    return middleware


def http_retry_request_middleware(make_request, web3):
    return exception_retry_middleware(
        make_request,
        web3,
        (ConnectionError, HTTPError, Timeout, TooManyRedirects)
    )
