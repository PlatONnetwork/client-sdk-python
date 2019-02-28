-   [概览](#概览)
-   [版本说明](#版本说明)
    -   [v0.2.0 更新说明](#v0.2.0-更新说明)
    -   [v0.3.0 更新说明](#v0.3.0-更新说明)
    -   [v0.4.0 更新说明](#v0.4.0-更新说明)
-   [快速入门](#快速入门)
    -   [安装或引入](#安装或引入)
    -   [初始化代码](#初始化代码)
-   [秘钥/钱包管理（部分语言版本无实现）](#秘钥钱包管理部分语言版本无实现)
    -   [秘钥生成](#秘钥生成)
    -   [秘钥加载](#秘钥加载)
    -   [wasm文件转换成二进制](#wasm文件转换成二进制)
    -   [int类型编码](#int类型编码)
    -   [字符串类型编码](#字符串类型编码)
    -   [布尔类型编码](#布尔类型编码)
    -   [abi文件转换成二进制](#abi文件转换成二进制)
-   [合约](#合约)
    -   [合约代码生成](#合约代码生成)
        -   [代码生成工具安装](#代码生成工具安装)
        -   [代码生成过程](#代码生成过程)
    -   [合约示例](#合约示例)
        -   [加载合约](#加载合约)
        -   [部署合约](#部署合约)
        -   [获取signedData](#获取signedData)
        -   [部署签名合约](#部署签名合约)
        -   [非签名合约交易](#非签名合约交易)
        -   [合约call调用](#合约call调用)
        -   [合约sendRawTransaction调用](#合约sendrawtransaction调用)
        -   [合约event](#合约event)
        -   [内置合约](#内置合约)
            - CandidateContract
            - TicketContract
-   [web3](#web3)
    -   [web3 eth相关 (标准JSON RPC )](#web3-eth相关-标准json-rpc)
        -   [getBalance](#getbalance)
        -   [getStorageAt](#getstorageat)

概览
----

版本说明
--------

### v0.2.0 更新说明

1.支持PlatON的智能合约

### v0.3.0 更新说明

1.实现了PlatON协议中交易类型定义

2.优化了骨架生成，增加合约部署和调用过程中gaslimit的评估方法

3.优化了默认gasLimit、gasPrice的值

4.增加内置合约CandidateContract

### v0.4.0 更新说明

1.增加内置合约TicketContract

--------

### 安装或引入

`pip install web3`

### 初始化代码

    web3 = Web3(Web3.HTTPProvider('http://192.168.9.180:6789'))

秘钥/钱包管理（部分语言版本无实现）
-----------------------------------

### 秘钥生成
> 生成私钥

**参数**

          类型           属性       含义
  --------------------- ------ -------------------------
     keystorePath        必选   keystore钱包json文件路径
     password            必选   钱包密码

**返回值 或 回调**

`private_key`

返回值为生成的私钥

**示例**

    def getPrivateKey(keystorePath, password):
        privateKey = keys.decode_keystore_json(json.load(open(keystorePath)), password)
        return privateKey

### 秘钥加载

### int类型编码
> 对传入合约交易的int类型encode

**参数**

          类型           属性       含义
  --------------------- ------ -------------------------
     typ                 必选   合约方法中定义的int类型：int64\int32\int16\int8
     i                   必选   合约方法需要传的参数值

**返回值 或 回调**

`intByte`

返回int类型的二进制数组

**示例**

    def encodeInt(typ, i: int):
        num = int(re.sub('\D', "", typ)) // 8
        intByte = i.to_bytes(length=num, byteorder='big', signed=True)
        return intByte
        
###字符串类型编码
> 对传入合约交易的字符串类型encode

**参数**

          类型           属性       含义
  --------------------- ------ -------------------------
     abiStr              必选   即将传入合约方法中定义的String类型的参数值

**返回值 或 回调**

`byteStr`

返回String类型的二进制数组

**示例**

    def encodeString(abiStr: str):
        if isinstance(abiStr, str):
            byteStr = bytearray(abiStr, 'utf-8')
            return byteStr
        else:
            raise Exception('please input a str')
            
###布尔类型编码
> 对传入合约交易的布尔类型encode

**参数**

          类型           属性       含义
  --------------------- ------ -------------------------
     boolean              必选   即将传入合约方法中定义的布尔类型的参数值

**返回值 或 回调**

`boolByte`

返回布尔类型的二进制数组

**示例**

    def encodeBoolean(boolean: bool):
        if isinstance(boolean, bool):
            boolByte = bytearray(boolean)
            return boolByte
        else:
            raise Exception('please input a bool')

###wasm文件转换成二进制
> wasm文件转换成二进制数组

**参数**

          类型           属性       含义
  --------------------- ------ -------------
     binFilePath        必选   wasm文件路径

**返回值 或 回调**

`bytecode`

返回值wasm文件二进制数组方式

**示例**

    def getBytecode(binFilePath):
        with open(binFilePath, 'rb') as f:
            bytecode = bytearray(f.read())
            return bytecode

###abi文件转换成二进制
> wasm文件转换成二进制数组

**参数**

          类型           属性       含义
  --------------------- ------ -------------------------
     binFilePath        必选   wasm文件路径

**返回值 或 回调**

`bytecode`

返回值abi文件二进制数组方式

**示例**

    def getAbiBytes(abiPath):
        with open(abiPath, 'r') as a:
            abi = a.read()
            abi = abi.replace('\r\n', '')
            abi = abi.replace('\n', '')
            bytecode = bytearray(abi, encoding='utf-8')
        return bytecode


合约
----

### 合约示例

    namespace platon {
        class SimpleContract : public Contract {
        private:
            const Address owners;
        }
        
        public:
            unit64_t getValue(const char * address) const{
            }
            setValue(const char * address,unit64_t value){
            }
    }

#### 加载合约

#### 部署合约

> 非签名合约部署

**参数**

          类型      属性       含义
  ---------------- ------ --------------
    txType          必选   取值类型 0-主币转账交易 1-合约发布 2-合约调用 3-投票 4-权限
    bytecode        必选   区块高度类型
    abi             必选   abi(json文件)，二进制数组
    param           必选   钱包地址
**返回值 或 回调**

`transactionHash`

合约部署交易产生的哈希

**示例**

    def contractDeploy(self, txType, bytecode, abi, fromAddress):
        txType = PlatonEncoder.encodeType(txType)
        gasPrice = self.w3.eth.gasPrice
        rlpList = [txType, bytecode, abi]
        data = rlp.encode(rlpList)
        transactionHash = self.eth.sendTransaction(
            {'from': fromAddress, 'gas': '7a1200', 'gasPrice': gasPrice, 'data': data})
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash


#### 获取signedData
> 非签名合约部署

**参数**

          类型      属性       含义
  ---------------- ------ --------------
    fromAddress     必选   钱包地址
    toAddress       必选   钱包地址在部署签名合约中传空字符串即可
    dataList        必选   由txType, bytecode, abi组成的列表
    privateKey      必选   生成的私钥 
**返回值 或 回调**

`transactionHash`

合约部署交易产生的哈希

**示例**

    def getSigedData(self, fromAddress, toAddress, dataList, privateKey):
        myNonce = self.eth.getTransactionCount(fromAddress, 'latest')
        data = rlp.encode(dataList)
        transactionDict = {'from': fromAddress,
                           'to': toAddress,
                           'gasPrice': '0x8250de00',
                           'gas': '0x1fffff',
                           'nonce': myNonce,
                           'data': data}
        signedTransactionDict = self.eth.account.signTransaction(transactionDict, privateKey)
        signedData = signedTransactionDict.rawTransaction
        return signedData

#### 部署签名合约
> 非签名合约部署

**参数**

          类型      属性       含义
  ---------------- ------ --------------
    txType          必选   取值类型 0-主币转账交易 1-合约发布 2-合约调用 3-投票 4-权限
    bytecode        必选   区块高度类型
    abi             必选   abi(json文件)，二进制数组
    param           必选   钱包地址
    privateKey      必选   生成的私钥 
**返回值 或 回调**

`transactionHash`

合约部署交易产生的哈希

**示例**

    def signedContractDeploy(self, txType, bytecode, abi, fromAddress, privateKey):
        txType = PlatonEncoder.encodeType(txType)
        rlpList = [txType, bytecode, abi]
        signedData = self.getSigedData(fromAddress, '',rlpList, privateKey)
        transactionHash = self.eth.sendRawTransaction(signedData)
        transactionHash = HexBytes(transactionHash).hex().lower()
        print(transactionHash)
        return transactionHash
        
####非签名合约交易
> 非签名合约交易

**参数**

          类型          属性       含义
  ---------------- ----------- --------------
    fromAddress     必选        钱包地址
    contractAddress 必选        合约地址
    dataList        必选        参数list
**返回值 或 回调**

`transactionHash`

返回交易哈希

**示例**

    def contractTransaction(self, fromAddress, contractAddress, dataList):
        data = rlp.encode(dataList)
        transactionHash = self.eth.sendTransaction(
            {'from': fromAddress, 'to': contractAddress, 'gas': '0x1fffff', 'gasPrice': '0x8250de00', 'data': data})
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash

#### 合约call调用
> 调用call方法

**参数**

          类型          属性       含义
  ---------------- ----------- --------------
    fromAddress     必选        钱包地址
    contractAddress 必选        合约地址
    dataList        必选        参数list
**返回值 或 回调**

`recive`

**示例**

    def contractCall(self, fromAddress, contractAddress, dataList):
        data = rlp.encode(dataList)
        recive = self.eth.call({'from': fromAddress, 'to': contractAddress, 'data': data})
        recive = HexBytes(recive).decode()
        return recive

#### 合约sendRawTransaction调用
> 签名合约调用方法

**参数**

          类型          属性       含义
  ---------------- ----------- --------------
    fromAddress     必选        钱包地址
    contractAddress 必选        合约地址
    dataList        必选        参数list
    privateKey      必选        钱包私钥
**返回值 或 回调**

`transactionHash`

交易哈希

**示例**

    def signedContractTransaction(self, fromAddress, contractAddress, dataList, privateKey):
        signedData = self.getSigedData(fromAddress, contractAddress, dataList, privateKey)
        transactionHash = self.eth.sendRawTransaction(signedData)
        transactionHash = HexBytes(transactionHash).hex().lower()
        return transactionHash

#### 合约event
> 解析event返回的结果

**参数**

          类型          属性       含义
  ---------------- ----------- --------------
    topics          必选        交易哈希中的topic字段
    data            必选        交易哈希中的data字段
**返回值 或 回调**

`{eventName: result}`

事件名称以及返回的结果

**示例**
    def _eventContainType(self, topics):
        if isinstance(topics, list):
            topics = topics[0].hex()
        for event in self.eventAbi:     
            if Web3.sha3(text=event['name']).hex() == topics:
                return event['inputs'], event['name']
            else:
                continue

    def eventData(self, topics, data):
        result = []
        decodedData = rlpDecode(data)
        if self._eventContainType(topics) is None:
            raise Exception('There is no match in your abi like this event topics :{}'.format(topics))
        else:
            eventContainType, eventName = self._eventContainType(topics)
            print(eventContainType,eventName)
        for i in range(len(eventContainType)):
            if re.search('int', eventContainType[i]['type'], re.IGNORECASE):
                decoded_item = int.from_bytes(decodedData[i], byteorder='big')
                if decoded_item == '':
                    result.append(0)
                else:
                    result.append(decoded_item)
            elif re.search('string', eventContainType[i]['type'], re.IGNORECASE):
                result.append(decodedData[i].decode('utf-8'))
            elif re.search('bool', eventContainType[i]['type'], re.IGNORECASE):
                result.append(bool(ord(decodedData[i])))
            else:
                raise Exception('unsupported type {}'.format(eventContainType[i]['type']))
        return {eventName: result}

#### 内置合约

CandidateContract

加载合约

#### **`CandidateDeposit`**

> 节点候选人申请/增加质押，质押金额为交易的value值

**参数**

          类型          属性       含义
  ---------------- ----------- --------------
    nodeId             必选    [64]byte 节点ID(公钥)
    owner              必选    [20]byte 质押金退款地址
    fee                必选    uint32 出块奖励佣金比，以10000为基数(eg：5%，则fee=500)
    host               必选    string 节点IP
    port               必选    string 节点P2P端口号
    extra              必选    string 附加数据(有长度限制，限制值待定)
**返回值 或 回调**

`result`

**示例**

    def CandidateDeposit(self, nodeid, owner, fee, host, port, extra, value=None):
        data = HexBytes(rlp.encode([int(1001).to_bytes(8, 'big'), self.CandidateDeposit.__name__, nodeid,
                                    owner, fee, host, port, extra])).hex()
        if not value:
            value = self.value
        send_data = {
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "value": self.web3.toWei(value, "ether"),
            "data": data,
            "gas": "90000",
            "gasPrice": self.eth.gasPrice
        }
        self.value -= 1
        result = HexBytes(self.eth.sendTransaction(send_data)).hex()
        result = self.get_result(result)
        return result

#### **`CandidateApplyWithdraw`**

> 节点候选人申请/增加质押，质押金额为交易的value值

**参数**

| **参数名** | **类型** | **参数说明** |
| ------ | ------ | ------ |
| nodeId | String  | 节点id, 16进制格式， 0x开头 |
| withdraw | int | uint256 退款金额 (单位：ADP) |

  
**返回值 或 回调**

`result`

**示例**

    def CandidateApplyWithdraw(self, nodeid, withdraw):
        # withdraw = np.uint256(withdraw)
        data = rlp.encode(
            [int(1002).to_bytes(8, 'big'), self.CandidateApplyWithdraw.__name__, nodeid, withdraw])
        send_data = {
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data,
            "gas": "9000",
            "gasPrice": self.eth.gasPrice
        }
        result = HexBytes(self.eth.sendTransaction(send_data)).hex()
        result = self.get_result(result)
        return result

#### **`CandidateWithdrawInfos`**

> 获取节点申请的退款记录列表

**参数**

| **参数名** | **类型** | **参数说明** |
| ------ | ------ | ------ |
| nodeId | String  | [64]byte 节点ID(公钥) |

  
**返回值 或 回调**

`recive`

**示例**

    def CandidateWithdrawInfos(self, nodeid):
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.CandidateWithdrawInfos.__name__, nodeid])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        return recive

#### **`GetBatchCandidateDetail`**

> 获取节点申请的退款记录列表

**参数**

| **参数名** | **类型** | **参数说明** |
| ------ | ------ | ------ |
| nodeId | String  | [64]byte 节点ID(公钥) |

  
**返回值 或 回调**

`recive`

事件名称以及返回的结果

**示例**

    def CandidateWithdrawInfos(self, nodeid):
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.CandidateWithdrawInfos.__name__, nodeid])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        return recive

#### **`CandidateList`**

> 获取所有入围节点的信息列表

**参数**

无

  
**返回值 或 回调**

`recive`

事件名称以及返回的结果

**示例**

    def CandidateList(self):
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.CandidateList.__name__])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000001",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile(r"{.*?}")
            recive = re.findall(p, recive)
        except Exception as e:
            print(e)
            print(recive)
        return recive

###  TicketContract

> PlatOn经济模型中票池相关的合约接口 [合约描述](https://note.youdao.com/)

#### **`GetTicketPrice`**

> 获取当前的票价

**参数**

无

  
**返回值 或 回调**

`recive`

事件名称以及返回的结果

**示例**

    def GetTicketPrice(self):
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetTicketPrice.__name__])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = HexBytes(recive).decode('utf-8')
            recive = re.sub('\x13', '', recive)
            recive = re.sub('\x00', '', recive)
        except Exception as e:
            print(e)
            print(recive)
        return recive

#### **`GetPoolRemainder`**

> 获取票池剩余票数量

**参数**

无

  
**返回值 或 回调**

`recive`

事件名称以及返回的结果

**示例**

    def GetPoolRemainder(self):
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetPoolRemainder.__name__])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            recive = re.sub('\x00', '', recive)
            recive = re.sub('\x04', '', recive)
            recive = re.sub(' ', '', recive)
        except Exception as e:
            print(e)
            print(recive)
        return recive

#### **`GetTicketDetail`**

> 获取票详情

**参数**

| **参数名** | **类型** | **参数说明** |
| ------ | ------ | ------ |
| ticket_id | int  | [32]byte 票Id |

  
**返回值 或 回调**

`recive`

事件名称以及返回的结果

**示例**

    def GetTicketDetail(self, ticket_id):
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetTicketDetail.__name__, ticket_id])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile(r"{.*?}")
            recive = re.findall(p, recive)
            recive = [json.loads(i) for i in recive]
        except Exception as e:
            print(e)
            print(recive)
        return recive

#### **`GetBatchTicketDetail`**

> 批量获取票详情

**参数**

| **参数名** | **类型** | **参数说明** |
| ------ | ------ | ------ |
| ticket_ids | list  | []ticketId 票Id列表 |

  
**返回值 或 回调**

`recive`

事件名称以及返回的结果

**示例**

    def GetBatchTicketDetail(self, ticket_ids):
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetBatchTicketDetail.__name__, ':'.join(ticket_ids)])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile(r"{.*?}")
            recive = re.findall(p, recive)
            recive = [json.loads(i) for i in recive]
        except Exception as e:
            print(e)
            print(recive)
        return recive

#### **`GetCandidateTicketIds`**

> 获取指定候选人的选票Id的列表

**参数**

| **参数名** | **类型** | **参数说明** |
| ------ | ------ | ------ |
| nodeid | int  | [64]byte 节点Id |

  
**返回值 或 回调**

`recive`

事件名称以及返回的结果

**示例**

    def GetCandidateTicketIds(self, nodeid):
        data = HexBytes(rlp.encode([int(10).to_bytes(8, 'big'),
                                    self.GetCandidateTicketIds.__name__, nodeid])).hex()
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile('\"(.+?)\"')
            recive = re.findall(p, recive)
        except Exception as e:
            print(e)
            print(recive)
        return recive

#### **`GetBatchCandidateTicketIds`**

> 批量获取指定候选人的选票Id的列表

**参数**

| **参数名** | **类型** | **参数说明** |
| ------ | ------ | ------ |
| node_ids | list  | []nodeId 节点Id列表 |

  
**返回值 或 回调**

`recive`

事件名称以及返回的结果

**示例**

    def GetBatchCandidateTicketIds(self, node_ids):
        encode_list = [int(10).to_bytes(8, 'big'), self.GetBatchCandidateTicketIds.__name__, ':'.join(node_ids)]
        data = rlp.encode(encode_list)
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            p = re.compile(r"{.*?}")
            recive = re.findall(p, recive)
            recive = [json.loads(i) for i in recive]
        except Exception as e:
            print(e)
            print(recive)
        return recive
        
#### **`GetCandidateEpoch`**

> 获取指定候选人的票龄

**参数**

| **参数名** | **类型** | **参数说明** |
| ------ | ------ | ------ |
| nodeid | int  | [64]byte 节点Id |

  
**返回值 或 回调**

`recive`

事件名称以及返回的结果

**示例**

    def GetCandidateEpoch(self, nodeid):
        data = rlp.encode([int(10).to_bytes(8, 'big'),
                           self.GetCandidateEpoch.__name__, nodeid])
        recive = self.eth.call({
            "from": self.address,
            "to": "0x1000000000000000000000000000000000000002",
            "data": data
        })
        try:
            recive = str(recive, encoding="ISO-8859-1")
            recive = re.sub('\x00', '', recive)
            recive = re.sub('\x05', '', recive).split()[0]
        except Exception as e:
            print(e)
            print(recive)
        return recive


web3
----

### web3 eth相关 (标准JSON RPC )

- python api的使用请参考[web3j github](https://github.com/ethereum/web3.py)