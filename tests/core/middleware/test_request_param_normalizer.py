import pytest

from alaya import Web3
from alaya.middleware import (  # noqa: F401
    construct_result_generator_middleware,
    request_parameter_normalizer,
)
from alaya.providers.base import (
    BaseProvider,
)


@pytest.fixture
def w3_base():
    return Web3(providers=[BaseProvider()], middlewares=[])


@pytest.fixture
def result_generator_middleware():
    return construct_result_generator_middleware({
        'platon_getLogs': lambda _, params: params,
    })


@pytest.fixture
def w3(w3_base, result_generator_middleware):
    w3_base.middleware_stack.add(result_generator_middleware)
    w3_base.middleware_stack.add(request_parameter_normalizer)
    return w3_base


def test_eth_getLogs_param_normalization(w3):
    result = w3.eth.getLogs({
        'from': 'latest', 'address': '0x1111111111111111111111111111111111111111'})
    assert isinstance(result[0]['address'], list)
