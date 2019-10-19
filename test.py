from client_sdk_python import HTTPProvider, Web3
from client_sdk_python.middleware import geth_poa_middleware
from client_sdk_python.ppos import Ppos
from client_sdk_python.pip import Pip

if __name__ == "__main__":
    web3 = Web3(HTTPProvider("http://192.168.9.204:6787"), chain_id=100)
    web3.middleware_stack.inject(geth_poa_middleware, layer=0)
    pip = Pip(web3)
    ppos = Ppos(web3)
    # ppos.set_from_address("0x2B645d169998eb0447A21D0c48a1780d115251a9")
    # ppos.set_pri_key("6382b6fc972ae9c22a2d8913dace308d09e406d118efddb702a7ea9e505cc823")
    # pip.set_from_address("0x2B645d169998eb0447A21D0c48a1780d115251a9")
    # pip.set_pri_key("6382b6fc972ae9c22a2d8913dace308d09e406d118efddb702a7ea9e505cc823")

    address = "0x2B645d169998eb0447A21D0c48a1780d115251a9"
    pri_key = "6382b6fc972ae9c22a2d8913dace308d09e406d118efddb702a7ea9e505cc823"


    ben_address = "0xe3678cf1fe1619d36fb0ac2e99305bd01f8191d1"

    proof = web3.admin.getSchnorrNIZKProve()
    msg = web3.admin.getProgramVersion()
    ProgramVersionSign = msg["Sign"]
    ProgramVersion = msg["Version"]
    blspubkey = "41d15f072194e2a4e1e3d89f5017683dad10b63c4f086edb388539a6bfae0cbf4a4c1d3f60fd45fdf2b975c89f4ab2014328f02725c480826d4bd3ded29439e1378f6aa584da70b7d2325a97f7027c140bd43d8c8020e592017cfe440213c40f"
    externalId = "1111111111"
    nodeName = "platon"
    website = "https://www.test.network"
    details = "supper node"
    node_id = "740a2efa54b1ab7816c2913c826e84a03114961c2449fa52a0a09b303c537e8daed3719fea8044e064de791fd92efda12dc8b2639335bbbc29ef428b2294b2ee"
    amount = 10000000
    # result = ppos.createStaking(typ=0, benifit_address=ben_address, node_id=node_id, external_id=externalId, node_name=nodeName,
    #                    website=website, details=details, amount=amount, program_version=ProgramVersion, program_version_sign=ProgramVersionSign,
    #                    bls_pubkey=blspubkey, bls_proof=proof)
    verifier=""
    result = pip.submitText(from_address=address,pri_key=pri_key,verifier=address,pip_id="2222")
    print("submit text:",result)
    print("=======================")
    result = pip.submitVersion(from_address=address,pri_key=pri_key,verifier=address,pip_id=111,new_version="222",end_voting_rounds="222")
    print("submit version:",result)
    print("======================")

    result = pip.listProposal()
    print("get listProposal", result)
    print("========================")
    result = pip.getActiveVersion()
    print("get getActiveVersion", result)
    print("========================")
    # result = pip.getProgramVersion()
    # print("get getProgramVersion", result)
    # print("========================")
    result = pip.listParam()
    print("get listParam", result)
    print("========================")
    print("create staking: ", result)
    print("==========================================================")
    result = ppos.editCandidate(from_address=address,pri_key=pri_key, benifit_address=ben_address, node_id=node_id, external_id="22222", node_name="platon", website=website, details=details)
    print("update staking: ", result)
    print("==========================================================")
    # ppos.need_analyze = False
    result = ppos.increaseStaking(from_address=address, pri_key=pri_key, typ=0, node_id=node_id, amount=amount)
    print("add staking: ", result)
    print("==========================================================")

    result = ppos.delegate(typ=0, node_id=node_id, amount=10, pri_key="a11859ce23effc663a9460e332ca09bd812acc390497f8dc7542b6938e13f8d7",
                           from_address="0x493301712671Ada506ba6Ca7891F436D29185821")
    print("delegate:", result)
    print("===========================================================")
    msg = ppos.getCandidateInfo(node_id=node_id)
    print(msg)
    try:
        stakingBlockNum = msg["Data"]["StakingBlockNum"]
    except:
        stakingBlockNum = 100

    result = ppos.withdrewDelegate(staking_blocknum=stakingBlockNum, node_id=node_id, amount=10,
                                   pri_key="a11859ce23effc663a9460e332ca09bd812acc390497f8dc7542b6938e13f8d7",
                                    from_address="0x493301712671Ada506ba6Ca7891F436D29185821")
    print("un delegate:", result)
    print("==========================================================")
    result = ppos.getValidatorList()
    print("get validator: ",result)
    result = ppos.getVerifierList()
    print("get verifier:", result)
    print("==========================================================")
    result = ppos.getCandidateList()
    print("get candidate:", result)
    print("==========================================================")
    result = ppos.getRelatedListByDelAddr(del_addr="0x493301712671Ada506ba6Ca7891F436D29185821")
    print("get delegate list by addr:", result)
    print("===========================================================")
    result = ppos.getDelegateInfo(staking_blocknum=stakingBlockNum, del_address="0x493301712671Ada506ba6Ca7891F436D29185821", node_id=node_id)
    print("getDelegateInfo:", result)
    print("===========================================================")
    result = ppos.getCandidateInfo(node_id=node_id)
    print("getCandidateInfo:", result)
    print("===========================================================")
    result = ppos.createRestrictingPlan(from_address=address,pri_key=pri_key,account="1f8b1dff7e12958269663c482a924c931109e7f2",plan="")
    print("createRestrictingPlan:", result)
    print("===========================================================")
    result = ppos.getRestrictingInfo(account="1f8b1dff7e12958269663c482a924c931109e7f2")
    print("getRestrictingInfo:", result)
    print("===========================================================")

    result = ppos.withdrewStaking(from_address=address,pri_key=pri_key,node_id=node_id)
    print("un staking: ", result)
    print("==========================================================")
