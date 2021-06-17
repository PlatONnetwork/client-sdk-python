import random
import time
from client_sdk_python import HTTPProvider, Web3
from client_sdk_python import eth, ppos, pip
from client_sdk_python.middleware import geth_poa_middleware
from hexbytes import HexBytes
from client_sdk_python.packages.platon_account.account import Account
from client_sdk_python.packages.platon_keys.utils.address import MIANNETHRP, TESTNETHRP


# 通用信息
node_url = 'http://192.168.120.121:6789'
chain_id = 201018
HRP = MIANNETHRP
w3 = Web3(HTTPProvider(node_url), chain_id=chain_id)
w3.middleware_stack.inject(geth_poa_middleware, layer=0)
platon = eth.PlatON(w3)
ppos = ppos.Ppos(w3)
pip = pip.Pip(w3)
pip_trans_cfg = {'gasPrice': 3000000000000000}

# 创建账户
def create_account():
    print("==== create account =====")
    account = w3.platon.account.create(net_type=HRP)
    address = account.address
    prikey = account.privateKey.hex()[2:]
    # check = platon.account.privateKeyToAccount(prikey, net_type=w3.net_type)
    # assert address == check
    print(f"create account = {address}, {prikey}")
    return address, prikey

# 转账交易
def transfer(from_privatekey, to_address, amount):
    print("==== transfer =====")
    from_address = Account.privateKeyToAccount(from_privatekey, HRP).address
    nonce = w3.platon.getTransactionCount(from_address)
    transaction_dict = {
        "to": to_address,
        "gasPrice": w3.eth.gasPrice,
        "gas": 21000,
        "nonce": nonce,
        "data": '',
        "chainId": chain_id,
        "value": amount,
    }
    signedTransactionDict = w3.platon.account.signTransaction(
        transaction_dict, from_privatekey
    )
    data = signedTransactionDict.rawTransaction
    result = HexBytes(w3.platon.sendRawTransaction(data)).hex()
    result = w3.platon.waitForTransactionReceipt(result)
    print(f"transfer staking result = {result}")

# 锁仓交易
def create_restricting_plan(from_private_key, to_address, restricting_plan):
    print("==== create restricting plan =====")
    # ppos.need_analyze = False
    result = ppos.createRestrictingPlan(to_address, restricting_plan, from_private_key)
    print(f"create restricting plan result = {result}")

# 创建质押
def create_staking(staking_private_key, staking_type, node_url, node_id, bls_pubkey, amount=10 ** 18 * 2000000, reward_per=1000):
    print("==== create staking =====")
    w3 = Web3(HTTPProvider(node_url), chain_id=chain_id)
    program_version = w3.admin.getProgramVersion()['Version']
    version_sign = w3.admin.getProgramVersion()['Sign']
    bls_proof = w3.admin.getSchnorrNIZKProve()
    benifit_address = Account.privateKeyToAccount(staking_private_key, HRP).address
    result = w3.ppos.createStaking(staking_type, benifit_address, node_id, 'external_id', 'node_name', 'website', 'details',
                                   amount, program_version, version_sign, bls_pubkey, bls_proof, staking_private_key, reward_per)
    print(f"create staking result = {result}")

# 增持质押
def increase_staking(staking_private_key, node_id, amount=10 ** 18 * 100):
    print("==== increase staking =====")
    result = w3.ppos.increaseStaking(0, node_id, amount, staking_private_key)
    print(f'incress staking result = {result}')

# 修改质押信息
def edit_staking(staking_private_key, node_id, benifit_address=None, external_id=None, node_name=None, website=None, details=None, reward_per=None):
        print("==== edit staking =====")
        result = w3.ppos.editCandidate(staking_private_key, node_id, benifit_address, external_id, node_name, website, details, reward_per)
        print(f'edit staking result = {result}')

# 解除质押
def withdrew_staking(staking_private_key, node_id):
    print("==== withdrew staking =====")
    result = w3.ppos.withdrewStaking(node_id, staking_private_key)
    print(f'withdrew staking result = {result}')

# 查询质押信息
def get_staking_info(node_id):
    print("==== get staking info =====")
    result = w3.ppos.getValidatorList()
    print(f'get validator list = {result}')
    result = w3.ppos.getVerifierList()
    print(f'get verifier list = {result}')
    result = w3.ppos.getCandidateList()
    print(f'get candidate list = {result}')
    result = w3.ppos.getCandidateInfo(node_id)
    print(f'get candidate info = {result}')

# 创建委托
def delegation(delegation_private_key, node_id, amount=10 * 10 ** 18):
    print("==== delegation =====")
    resutl = w3.ppos.delegate(0, node_id, amount, delegation_private_key)
    print(f'delegation result = {resutl}')

# 解除委托
def undelegation(delegation_private_key, node_id, amount=1 * 10 ** 18):
    print("==== undelegation =====")
    delegation_address = Account.privateKeyToAccount(delegation_private_key, HRP).address
    result = w3.ppos.getRelatedListByDelAddr(delegation_address)
    print(f'get related list = {result}')
    block_number = result.get('Ret')[0].get('StakingBlockNum')
    assert block_number != ''
    result = w3.ppos.withdrewDelegate(block_number, node_id, amount, delegation_private_key)
    print(f'undelegation result = {result}')

# 查询委托信息
def get_delegation_list(delegation_address):
    print("==== get delegation list =====")
    result = w3.ppos.getRelatedListByDelAddr(delegation_address)
    print(f'get delegation list = {result}')

# 领取委托分红
def withdraw_delegate_reward(delegate_private_key):
    print("==== withdraw delegate reward =====")
    result = w3.ppos.withdrawDelegateReward(delegate_private_key)
    print(f'withdraw delegate result = {result}')

# 创建升级提案
def create_version_proposal(node_private_key, node_id, upgrade_version, voting_rounds):
    print("==== create version proposal =====")
    result = w3.pip.submitVersion(node_id, str(time.time()), upgrade_version, voting_rounds, node_private_key, pip_trans_cfg)
    print(f'create version proposal result = {result}')

# 查询提案id
def get_proposal_list():
    print("==== get proposal list =====")
    pip_list = w3.pip.listProposal()
    print(f"proposal list = {pip_list}")

# 提案投票
def version_proposal_vote(node_private_key, node_url, node_id, vote_type):
    print("==== version proposal vote =====")
    w3 = Web3(HTTPProvider(node_url), chain_id=chain_id)
    program_version = w3.admin.getProgramVersion()['Version']
    version_sign = w3.admin.getProgramVersion()['Sign']
    proposal_id = w3.pip.listProposal().get('Ret')[0].get('ProposalID')
    assert proposal_id != ''
    result = w3.pip.vote(node_id, proposal_id, vote_type, program_version, version_sign, node_private_key)
    print(f'version proposal vote result = {result}, {proposal_id}')

# 获取版本号
def get_version():
    print("==== get version =====")
    result = w3.pip.getActiveVersion()
    print(f'version = {result}')


def wait_block(block_number):
    print("==== wait block ====")
    current_block = platon.blockNumber
    end_block = current_block + block_number
    while current_block < end_block:
        print(f'wait block: {current_block} -> {end_block}')
        time.sleep(5)
        current_block = platon.blockNumber


if __name__ == '__main__':
    main_address, main_private_key = 'atx1zkrxx6rf358jcvr7nruhyvr9hxpwv9unj58er9', 'f51ca759562e1daf9e5302d121f933a8152915d34fcbc27e542baf256b5e4b74'

    # # **** 交易模块 ****
    # from_address, from_private_key = create_account()
    # to_address, to_private_key = create_account()
    # transfer(main_private_key, from_address, 100 * 10 ** 18)
    # 普通交易
    # transfer(main_private_key, 'atx1t5kdy77uycd06aezuv2lddnsus9w02tmxpdgz2', 10000 * 10 ** 18)
    # 锁仓交易
    # plan = [{'Epoch': 0, 'Amount': 80 * 10 ** 18}]
    # create_restricting_plan(main_private_key, 'atx1c85wwztzpjefcvaev6wxpsrqp2gpfjyp6lmfqd', plan)

    # # **** 经济模型模块 ****
    # node_url = 'http://192.168.120.124:6790'
    # node_id = '7038eb30c06683c97282d0d7acbf939c15bcfc390eb461983445c2d58328d88b85a3d4c79867c18a5ed9442a13062c4b5a9f9e03ea7026e000c9b13c2a1d3255'
    # bls_pubkey = 'd2f1be8a9832048f745d30095e483fd187dd37972ef7bd6491bc6cd957372ab16ca3f9d6f4c20a41b9b9d235fca51f12ab2c21029b495647692482714573bef10d444858ddc404c97d117cb7950b1b157e3bffb1be13f31623612fd057efc605'
    # staking_address, staking_private_key = 'atp1elg3q9hw5cy3hztg0vqwglhk6tjmwk6e0na9wj', '1fa6c50d48c44f8bc289536c4a607a628524adea80536767b54041499579a887'
    # staking_address, staking_private_key = create_account()
    # delegation_address, delegation_private_key = 'atx16g303js6tushq236fhv5cmr8tw272cg9279tcl', 'b854c86a25498ce21035d3fabc7dbe784b4288ad3bd9580437bd0250014
    # e40c1'
    # # 创建质押
    # plan = [{'Epoch': 2, 'Amount': 2000 * 10 ** 18},
    #         {'Epoch': 4, 'Amount': 2000 * 10 ** 18},
    #         {'Epoch': 8, 'Amount': 2000 * 10 ** 18},
    #         {'Epoch': 16, 'Amount': 2000 * 10 ** 18},
    #         {'Epoch': 32, 'Amount': 2000 * 10 ** 18},
    #         {'Epoch': 64, 'Amount': 5000 * 10 ** 18},
    #         {'Epoch': 128, 'Amount': 5000 * 10 ** 18},
    #         {'Epoch': 256, 'Amount': 5000 * 10 ** 18}]
    # create_restricting_plan(main_private_key, staking_address, plan)
    # transfer(main_private_key, staking_address, 20010 * 10 ** 18)
    # create_staking(staking_private_key, 0, node_url, node_id, bls_pubkey, 20000 * 10 ** 18, 1000)
    # # 增持质押
    # transfer(main_private_key, staking_address, 10 * 10 ** 18)
    # increase_staking(staking_private_key, node_id, 10 * 10 ** 18)
    # # 修改质押信息
    # benifit_address = Account.privateKeyToAccount(staking_private_key, HRP).address
    # edit_staking(staking_private_key, node_id, external_id='shinnng')
    # # 创建委托
    # transfer(main_private_key, delegation_address, 11 * 10 ** 18)
    # delegation(delegation_private_key, node_id, 10 * 10 ** 18)
    # # 撤销委托
    # amout = random.randint(1, 10)
    # undelegation(delegation_private_key, node_id, amout)
    # # 领取委托分红
    # withdraw_delegate_reward(delegation_private_key)
    # # 解除质押
    # wait_block(40 * 4 * 2)
    # withdrew_staking(staking_private_key, node_id)

    # # **** 治理模块 ****
    # upgrade_version = 3584
    # upgrade_voting_rounds = 30
    # # # 升级提案
    # staking_private_key = '85128e542f92384a4f8259f44bea0a70425a7f79e722ab4c0cbbd811154ec553'
    # node_id = 'bc9dabae54a13202ec765c1537c57b9f6659161596eae7c0344a606e9396c63c96a2a76aadc320100e9a56c5acdb8faddfb61733bddeff7b9f261ac54a46d775'
    # create_version_proposal(staking_private_key, node_id, upgrade_version, upgrade_voting_rounds)
    # # 提案投票
    cdf_node_list = [('http://192.168.120.121:6789', '35bb5daad814fe902030cba6fd2d3ec60906dab70ba5df4d42a19448d300ab203cfd892c325f6716965dd93d8de2a377a2806c9703b69b68287577c70f9e7c07', ''),
                    ('http://192.168.120.122:6789', '5030440865a11ce0ab1441d3977647b0606e1f34897cfea1e55ea13d91c7a7fc5575fd3d1614f005384dc7e6974e4f96193d38883507eebcdcc29ca57d19499d'),
                    ('http://192.168.120.123:6789', '4555b0d40b857f50186703c48bc342f2e15473823627d5aa817dabe992171361ccf9d8c57967077dc5500eec65b5b9beb3f56efae4ffd3ddbf2753f4499e8c2e'),
                    ('http://192.168.120.124:6789', 'e51278714f6d8218900a311b251753f4f9408295561c4a913385e7817bbe6e69056c9f3a46dd56284d311f1e080f82d1edff98502af525fd19d233dd2406ec54')]
    # node_url = 'http://192.168.120.123:6790'
    # node_id = 'bc9dabae54a13202ec765c1537c57b9f6659161596eae7c0344a606e9396c63c96a2a76aadc320100e9a56c5acdb8faddfb61733bddeff7b9f261ac54a46d775'
    private_key = '85128e542f92384a4f8259f44bea0a70425a7f79e722ab4c0cbbd811154ec553'

    for node_url, node_id in cdf_node_list:
        print(node_url, node_id)
        version_proposal_vote(private_key, node_url, node_id, 1)
    # # 查询提案
    # get_proposal_list()

    # # **** 调试信息 ****
    # print(platon.blockNumber)
    # print(platon.getBalance(main_address))
    # print(platon.gasPrice)
    # print(ppos.getRestrictingInfo('atx1c85wwztzpjefcvaev6wxpsrqp2gpfjyp6lmfqd'))
    # print(platon.getTransactionCount('atx1zkrxx6rf358jcvr7nruhyvr9hxpwv9unj58er9'))
    # print(platon.waitForTransactionReceipt('0xda81aab7e6d9f5188081fbd281fd0eaaebef1f1be03ff2c98fd1f76c36c16ec5'))
    # print(platon.getCode('atx1rdlcxzxk88e7k7mm0w93ald07g52l6pw97gzzz'))
    # print(ppos.getValidatorList())
    # print(ppos.getVerifierList())
    # print(pip.listProposal())
    # print(ppos.getCandidateList())
    # print(pip.getAccuVerifiersCount('0x8568213e8014bcdaa38132e1df05ec2f35471ebdafd737f452a8393cc105611c', '0x8c80f64bfe241494d9b3c6509bfe2ae30eb51cf9a56277d407394bbcf00071c8'))
    # print(pip.getActiveVersion())
