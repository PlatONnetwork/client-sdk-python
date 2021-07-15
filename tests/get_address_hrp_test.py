from client_sdk_python import Web3, HTTPProvider
from client_sdk_python.eth import PlatON
from client_sdk_python.ppos import Ppos
from client_sdk_python.pip import Pip


def unit_test_address(url):
    w3 = Web3(HTTPProvider(url))
    platon = PlatON(w3)
    print(platon.net_type)
    ppos = Ppos(w3)
    pip = Pip(w3)
    print(ppos.getPackageReward())
    print('w3 net_type is:{}'.format(platon.net_type))
    print('platon net_type is:{}'.format(platon.net_type))
    print('stakingAddress is:{}'.format(ppos.stakingAddress))
    print('penaltyAddress is:{}'.format(ppos.penaltyAddress))
    print('delegateRewardAddress is:{}'.format(ppos.delegateRewardAddress))
    print('restrictingAddress is:{}'.format(ppos.restrictingAddress))
    print('pipAddress is:{}'.format(pip.pipAddress))


if __name__ == '__main__':
    test_url = "http://127.0.0.1:6789"
    unit_test_address(test_url)
