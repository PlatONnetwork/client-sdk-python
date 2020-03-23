import json
import sha3
import rlp
from eth_utils.hexadecimal import remove_0x_prefix
from eth_account import (
    Account,
)
from eth_utils import (
    apply_to_return_value,
    is_checksum_address,
    is_string,
)
from hexbytes import (
    HexBytes,
)

from client_sdk_python.contract import (
    Contract,
)
from client_sdk_python.iban import (
    Iban,
)
from client_sdk_python.module import (
    Module,
)
from client_sdk_python.utils.blocks import (
    select_method_for_block_identifier,
)
from client_sdk_python.utils.decorators import (
    deprecated_for,
    deprecated_in_v5,
)
from client_sdk_python.utils.empty import (
    empty,
)
from client_sdk_python.utils.encoding import (
    to_hex,
)
from client_sdk_python.utils.filters import (
    BlockFilter,
    LogFilter,
    TransactionFilter,
)
from client_sdk_python.utils.toolz import (
    assoc,
    merge,
)
from client_sdk_python.utils.transactions import (
    assert_valid_transaction_params,
    extract_valid_transaction_params,
    get_buffered_gas_estimate,
    get_required_transaction,
    replace_transaction,
    wait_for_transaction_receipt,
)

from eth_account.internal.signing import (
    to_standard_signature_bytes,
)

class Eth(Module):
    account = Account()
    defaultAccount = empty
    defaultBlock = "latest"
    defaultContractFactory = Contract
    iban = Iban
    gasPriceStrategy = None

    @deprecated_for("doing nothing at all")
    def enable_unaudited_features(self):
        pass

    def namereg(self):
        raise NotImplementedError()

    def icapNamereg(self):
        raise NotImplementedError()

    @property
    def protocolVersion(self):
        return self.web3.manager.request_blocking("platon_protocolVersion", [])

    @property
    def syncing(self):
        return self.web3.manager.request_blocking("platon_syncing", [])

    # @property
    # def coinbase(self):
    #     return self.web3.manager.request_blocking("platon_coinbase", [])

    # @property
    # def mining(self):
    #     return self.web3.manager.request_blocking("platon_mining", [])

    # @property
    # def hashrate(self):
    #     return self.web3.manager.request_blocking("platon_hashrate", [])

    @property
    def gasPrice(self):
        return self.web3.manager.request_blocking("platon_gasPrice", [])

    @property
    def accounts(self):
        return self.web3.manager.request_blocking("platon_accounts", [])

    @property
    def blockNumber(self):
        return self.web3.manager.request_blocking("platon_blockNumber", [])

    @property
    def evidences(self):
        data = self.web3.manager.request_blocking("platon_evidences", [])
        return json.loads(data)

    @property
    def consensusStatus(self):
        return self.web3.manager.request_blocking("platon_consensusStatus", [])

    def getPrepareQC(self, block_number):
        return self.web3.manager.request_blocking("platon_getPrepareQC", [block_number])

    def getBalance(self, account, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "platon_getBalance",
            [account, block_identifier],
        )

    def getStorageAt(self, account, position, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "platon_getStorageAt",
            [account, position, block_identifier]
        )

    def getCode(self, account, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "platon_getCode",
            [account, block_identifier],
        )

    def getBlock(self, block_identifier, full_transactions=False):
        """
        `platon_getBlockByHash`
        `platon_getBlockByNumber`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='platon_getBlockByNumber',
            if_hash='platon_getBlockByHash',
            if_number='platon_getBlockByNumber',
        )

        return self.web3.manager.request_blocking(
            method,
            [block_identifier, full_transactions],
        )

    def getBlockTransactionCount(self, block_identifier):
        """
        `platon_getBlockTransactionCountByHash`
        `platon_getBlockTransactionCountByNumber`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='platon_getBlockTransactionCountByNumber',
            if_hash='platon_getBlockTransactionCountByHash',
            if_number='platon_getBlockTransactionCountByNumber',
        )
        return self.web3.manager.request_blocking(
            method,
            [block_identifier],
        )

    # def getUncleCount(self, block_identifier):
    #     """
    #     `platon_getUncleCountByBlockHash`
    #     `platon_getUncleCountByBlockNumber`
    #     """
    #     method = select_method_for_block_identifier(
    #         block_identifier,
    #         if_predefined='platon_getUncleCountByBlockNumber',
    #         if_hash='platon_getUncleCountByBlockHash',
    #         if_number='platon_getUncleCountByBlockNumber',
    #     )
    #     return self.web3.manager.request_blocking(
    #         method,
    #         [block_identifier],
    #     )

    # def getUncleByBlock(self, block_identifier, uncle_index):
    #     """
    #     `platon_getUncleByBlockHashAndIndex`
    #     `platon_getUncleByBlockNumberAndIndex`
    #     """
    #     method = select_method_for_block_identifier(
    #         block_identifier,
    #         if_predefined='platon_getUncleByBlockNumberAndIndex',
    #         if_hash='platon_getUncleByBlockHashAndIndex',
    #         if_number='platon_getUncleByBlockNumberAndIndex',
    #     )
    #     return self.web3.manager.request_blocking(
    #         method,
    #         [block_identifier, uncle_index],
    #     )

    def getTransaction(self, transaction_hash):
        return self.web3.manager.request_blocking(
            "platon_getTransactionByHash",
            [transaction_hash],
        )

    def getRawTransaction(self, transaction_hash):
        return self.web3.manager.request_blocking(
            "platon_getRawTransactionByHash",
            [transaction_hash],
        )

    @deprecated_for("w3.eth.getTransactionByBlock")
    def getTransactionFromBlock(self, block_identifier, transaction_index):
        """
        Alias for the method getTransactionByBlock
        Depreceated to maintain naming consistency with the json-rpc API
        """
        return self.getTransactionByBlock(block_identifier, transaction_index)

    def getTransactionByBlock(self, block_identifier, transaction_index):
        """
        `platon_getTransactionByBlockHashAndIndex`
        `platon_getTransactionByBlockNumberAndIndex`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='platon_getTransactionByBlockNumberAndIndex',
            if_hash='platon_getTransactionByBlockHashAndIndex',
            if_number='platon_getTransactionByBlockNumberAndIndex',
        )
        return self.web3.manager.request_blocking(
            method,
            [block_identifier, transaction_index],
        )

    def waitForTransactionReceipt(self, transaction_hash, timeout=120):
        return wait_for_transaction_receipt(self.web3, transaction_hash, timeout)

    def getTransactionReceipt(self, transaction_hash):
        return self.web3.manager.request_blocking(
            "platon_getTransactionReceipt",
            [transaction_hash],
        )

    def getTransactionCount(self, account, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "platon_getTransactionCount",
            [
                account,
                block_identifier,
            ],
        )

    def replaceTransaction(self, transaction_hash, new_transaction):
        current_transaction = get_required_transaction(self.web3, transaction_hash)
        return replace_transaction(self.web3, current_transaction, new_transaction)

    def modifyTransaction(self, transaction_hash, **transaction_params):
        assert_valid_transaction_params(transaction_params)
        current_transaction = get_required_transaction(self.web3, transaction_hash)
        current_transaction_params = extract_valid_transaction_params(current_transaction)
        new_transaction = merge(current_transaction_params, transaction_params)
        return replace_transaction(self.web3, current_transaction, new_transaction)

    def sendTransaction(self, transaction):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        # TODO: move gas estimation in middleware
        if 'gas' not in transaction:
            transaction = assoc(
                transaction,
                'gas',
                get_buffered_gas_estimate(self.web3, transaction),
            )

        return self.web3.manager.request_blocking(
            "platon_sendTransaction",
            [transaction],
        )

    def sendRawTransaction(self, raw_transaction):
        return self.web3.manager.request_blocking(
            "platon_sendRawTransaction",
            [raw_transaction],
        )

    def sign(self, account, data=None, hexstr=None, text=None):
        message_hex = to_hex(data, hexstr=hexstr, text=text)
        return self.web3.manager.request_blocking(
            "platon_sign", [account, message_hex],
        )

    @apply_to_return_value(HexBytes)
    def call(self, transaction, block_identifier=None):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        # TODO: move to middleware
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "platon_call",
            [transaction, block_identifier],
        )

    def estimateGas(self, transaction):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        return self.web3.manager.request_blocking(
            "platon_estimateGas",
            [transaction],
        )

    def filter(self, filter_params=None, filter_id=None):
        if filter_id and filter_params:
            raise TypeError(
                "Ambiguous invocation: provide either a `filter_params` or a `filter_id` argument. "
                "Both were supplied."
            )
        if is_string(filter_params):
            if filter_params == "latest":
                filter_id = self.web3.manager.request_blocking(
                    "platon_newBlockFilter", [],
                )
                return BlockFilter(self.web3, filter_id)
            elif filter_params == "pending":
                filter_id = self.web3.manager.request_blocking(
                    "platon_newPendingTransactionFilter", [],
                )
                return TransactionFilter(self.web3, filter_id)
            else:
                raise ValueError(
                    "The filter API only accepts the values of `pending` or "
                    "`latest` for string based filters"
                )
        elif isinstance(filter_params, dict):
            _filter_id = self.web3.manager.request_blocking(
                "platon_newFilter",
                [filter_params],
            )
            return LogFilter(self.web3, _filter_id)
        elif filter_id and not filter_params:
            return LogFilter(self.web3, filter_id)
        else:
            raise TypeError("Must provide either filter_params as a string or "
                            "a valid filter object, or a filter_id as a string "
                            "or hex.")

    def getFilterChanges(self, filter_id):
        return self.web3.manager.request_blocking(
            "platon_getFilterChanges", [filter_id],
        )

    def getFilterLogs(self, filter_id):
        return self.web3.manager.request_blocking(
            "platon_getFilterLogs", [filter_id],
        )

    def getLogs(self, filter_params):
        return self.web3.manager.request_blocking(
            "platon_getLogs", [filter_params],
        )

    def uninstallFilter(self, filter_id):
        return self.web3.manager.request_blocking(
            "platon_uninstallFilter", [filter_id],
        )

    def contract(self,
                 address=None,
                 **kwargs):
        ContractFactoryClass = kwargs.pop('ContractFactoryClass', self.defaultContractFactory)

        ContractFactory = ContractFactoryClass.factory(self.web3, **kwargs)

        if address:
            return ContractFactory(address)
        else:
            return ContractFactory

    def setContractFactory(self, contractFactory):
        self.defaultContractFactory = contractFactory

    # @deprecated_in_v5
    # def getCompilers(self):
    #     return self.web3.manager.request_blocking("platon_getCompilers", [])

    # def getWork(self):
    #     return self.web3.manager.request_blocking("platon_getWork", [])

    def generateGasPrice(self, transaction_params=None):
        if self.gasPriceStrategy:
            return self.gasPriceStrategy(self.web3, transaction_params)

    def setGasPriceStrategy(self, gas_price_strategy):
        self.gasPriceStrategy = gas_price_strategy

    # add to platon
    def analyzeReceiptByHash(self, tx_hash):
        receipt = self.waitForTransactionReceipt(tx_hash)
        return self.analyzeReceipt(receipt)

    def analyzeReceipt(self, transaction_receipt):
        return self.web3.analyzeReceipt(transaction_receipt)

    def ecrecover(self, block_identifier):
        block = self.getBlock(block_identifier)
        extra = block.proofOfAuthorityData[0:32]
        sign = block.proofOfAuthorityData[32:]
        raw_data = [bytes.fromhex(remove_0x_prefix(block.parentHash.hex())),
                    bytes.fromhex(remove_0x_prefix(block.miner)),
                    bytes.fromhex(remove_0x_prefix(block.stateRoot.hex())),
                    bytes.fromhex(remove_0x_prefix(block.transactionsRoot.hex())),
                    bytes.fromhex(remove_0x_prefix(block.receiptsRoot.hex())),
                    bytes.fromhex(remove_0x_prefix(block.logsBloom.hex())),
                    block.number,
                    block.gasLimit,
                    block.gasUsed,
                    block.timestamp,
                    extra,
                    bytes.fromhex(remove_0x_prefix(block.nonce))
                    ]
        message_hash = sha3.keccak_256(rlp.encode(raw_data)).digest()
        hash_bytes = HexBytes(message_hash)
        signature_bytes = HexBytes(sign)
        signature_bytes_standard = to_standard_signature_bytes(signature_bytes)
        signature_obj = self.account._keys.Signature(signature_bytes=signature_bytes_standard)
        return remove_0x_prefix(signature_obj.recover_public_key_from_msg_hash(hash_bytes).to_hex())


class PlatON(Eth):
    pass

