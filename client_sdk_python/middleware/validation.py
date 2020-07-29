from client_sdk_python.packages.eth_utils.curried import (
    apply_formatter_at_index,
    apply_formatter_if,
    apply_formatters_to_dict,
    is_null,
)
from hexbytes import (
    HexBytes,
)

from client_sdk_python.exceptions import (
    ValidationError,
)
from client_sdk_python.middleware.formatting import (
    construct_web3_formatting_middleware,
)
from client_sdk_python.utils.toolz import (
    complement,
    compose,
    curry,
    dissoc,
)

MAX_EXTRADATA_LENGTH = 32 #32


is_not_null = complement(is_null)


@curry
def validate_chain_id(web3, chain_id):
    if chain_id == web3.net.chainId:
        return chain_id
    else:
        raise ValidationError(
            "The transaction declared chain ID %r, "
            "but the connected node is on %r" % (
                chain_id,
                "UNKNOWN",
            )
        )


def check_extradata_length(val: object) -> object:
    if not isinstance(val, (str, int, bytes)):
        return val
    result = HexBytes(val)
    if len(result) > MAX_EXTRADATA_LENGTH:
        raise ValidationError(
            "The field extraData is %d bytes, but should be %d. "
            "It is quite likely that you are connected to a POA chain. "
            "Refer "
            "http://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority "
            "for more details. The full extraData is: %r" % (
                len(result), MAX_EXTRADATA_LENGTH, result
            )
        )
    return val


def transaction_normalizer(transaction):
    return dissoc(transaction, 'chainId')


def transaction_param_validator(web3):
    transactions_params_validators = {
        'chainId': apply_formatter_if(
            # Bypass `validate_chain_id` if chainId can't be determined
            lambda _: is_not_null(web3.net.chainId),
            validate_chain_id(web3)
        ),
    }
    return apply_formatter_at_index(
        apply_formatters_to_dict(transactions_params_validators),
        0
    )


BLOCK_VALIDATORS = {
    'extraData': check_extradata_length,
}


block_validator = apply_formatter_if(
    is_not_null,
    apply_formatters_to_dict(BLOCK_VALIDATORS)
)


@curry
def chain_id_validator(web3):
    return compose(
        apply_formatter_at_index(transaction_normalizer, 0),
        transaction_param_validator(web3)
    )


def build_validators_with_web3(w3):
    return dict(
        request_formatters={
            'platon_sendTransaction': chain_id_validator(w3),
            'platon_estimateGas': chain_id_validator(w3),
            'platon_call': chain_id_validator(w3),
        },
        result_formatters={
            'platon_getBlockByHash': block_validator,
            'platon_getBlockByNumber': block_validator,
        },
    )


validation_middleware = construct_web3_formatting_middleware(build_validators_with_web3)
