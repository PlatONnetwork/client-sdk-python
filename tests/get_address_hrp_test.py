from client_sdk_python import Web3, HTTPProvider
from client_sdk_python.eth import PlatON


def unit_test_address(url):
    w3 = Web3(HTTPProvider(url))
    platon = PlatON(w3)
    w3.net_type = platon.getAddressHrp
    w3.init_contract_address()
    print('net_type is:{}'.format(w3.net_type))
    print('stakingAddress is:{}'.format(w3.stakingAddress))
    print('penaltyAddress is:{}'.format(w3.penaltyAddress))
    print('delegateRewardAddress is:{}'.format(w3.delegateRewardAddress))
    print('restrictingAddress is:{}'.format(w3.restrictingAddress))
    print('pipAddress is:{}'.format(w3.pipAddress))


if __name__ == '__main__':
    test_url = "http://127.0.0.1:6789"
    unit_test_address(test_url)
