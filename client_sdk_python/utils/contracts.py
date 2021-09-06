import functools
import struct
import numpy as np
import rlp
from client_sdk_python.param_encode import (
    fnv1_64,
    rlp_decode,
)

from client_sdk_python.packages.eth_abi import (
    encode_abi as eth_abi_encode_abi,
)
from client_sdk_python.packages.eth_abi.exceptions import (
    EncodingError,
)
from client_sdk_python.packages.eth_utils import (
    add_0x_prefix,
    encode_hex,
    function_abi_to_4byte_selector,
    is_text,
)
from hexbytes import (
    HexBytes,
)

from client_sdk_python.exceptions import (
    ValidationError,
)
from client_sdk_python.utils.abi import (
    abi_to_signature,
    check_if_arguments_can_be_encoded,
    filter_by_argument_count,
    filter_by_argument_name,
    filter_by_encodability,
    filter_by_name,
    filter_by_type,
    get_abi_input_types,
    get_fallback_func_abi,
    map_abi_data,
    merge_args_and_kwargs,
)
from client_sdk_python.utils.encoding import (
    to_hex,
    hexstr2bytes,
    tostring_hex,
    stringtohex,
    tobech32address,
)
from client_sdk_python.utils.function_identifiers import (
    FallbackFn,
)
from client_sdk_python.utils.normalizers import (
    abi_address_to_hex,
    abi_bytes_to_bytes,
    abi_ens_resolver,
    abi_string_to_text,
)
from client_sdk_python.utils.toolz import (
    pipe,
    valmap,
)

from client_sdk_python.packages.platon_keys.utils import bech32,address
from client_sdk_python.packages.eth_utils import to_checksum_address

def find_wasm_abi(abi, fn_identifier=None):
    for i in abi:
        if i['name'] == fn_identifier:
            return i
def find_matching_event_abi(abi, event_name=None, argument_names=None):

    filters = [
        functools.partial(filter_by_type, 'event'),
    ]

    if event_name is not None:
        filters.append(functools.partial(filter_by_name, event_name))

    if argument_names is not None:
        filters.append(
            functools.partial(filter_by_argument_name, argument_names)
        )

    event_abi_candidates = pipe(abi, *filters)

    if len(event_abi_candidates) == 1:
        return event_abi_candidates[0]
    elif not event_abi_candidates:
        raise ValueError("No matching events found")
    else:
        raise ValueError("Multiple events found")


def find_matching_fn_abi(abi, fn_identifier=None, args=None, kwargs=None):
    args = args or tuple()
    kwargs = kwargs or dict()
    filters = []
    num_arguments = len(args) + len(kwargs)

    if fn_identifier is FallbackFn:
        return get_fallback_func_abi(abi)

    if not is_text(fn_identifier):
        raise TypeError("Unsupported function identifier")

    name_filter = functools.partial(filter_by_name, fn_identifier)
    arg_count_filter = functools.partial(filter_by_argument_count, num_arguments)
    encoding_filter = functools.partial(filter_by_encodability, args, kwargs)
    filters.extend([
        name_filter,
        arg_count_filter,
        encoding_filter,
    ])
    function_candidates = pipe(abi, *filters)
    if len(function_candidates) == 1:
        return function_candidates[0]
    else:
        matching_identifiers = name_filter(abi)
        matching_function_signatures = [abi_to_signature(func) for func in matching_identifiers]
        arg_count_matches = len(arg_count_filter(matching_identifiers))
        encoding_matches = len(encoding_filter(matching_identifiers))
        if arg_count_matches == 0:
            diagnosis = "\nFunction invocation failed due to improper number of arguments."
        elif encoding_matches == 0:
            diagnosis = "\nFunction invocation failed due to no matching argument types."
        elif encoding_matches > 1:
            diagnosis = (
                "\nAmbiguous argument encoding. "
                "Provided arguments can be encoded to multiple functions matching this call."
            )
        message = (
            "\nCould not identify the intended function with name `{name}`, "
            "positional argument(s) of type `{arg_types}` and "
            "keyword argument(s) of type `{kwarg_types}`."
            "\nFound {num_candidates} function(s) with the name `{name}`: {candidates}"
            "{diagnosis}"
        ).format(
            name=fn_identifier,
            arg_types=tuple(map(type, args)),
            kwarg_types=valmap(type, kwargs),
            num_candidates=len(matching_identifiers),
            candidates=matching_function_signatures,
            diagnosis=diagnosis,
        )
        raise ValidationError(message)
def encodeuint(param):
    arrlp = []
    if param:
        temp1 = int(param)
        while (temp1 % 0xff) or (temp1 & 0xff) :
            temp = (hex(temp1 & 0xff)).replace('0x', '')
            if len(temp) == 1:
                temp = '0' + temp
            arrlp.append(temp)
            temp1 = temp1 >> 8
        arrlp.reverse()
    else:
        arrlp.append('00')
    return arrlp

def float_to_hex(f):
    return hex(struct.unpack('>I', struct.pack('>f', f))[0])

def double_to_hex(d):
    return hex(struct.unpack('>Q', struct.pack('>d', d))[0])
def handlearrlp(arrlp,temp):
    if isinstance(arrlp, list):
        if isinstance(temp[0],list):
            arrlp.append(tuple(temp))
        else:
            arrlp.append(temp)
    elif isinstance(arrlp, tuple):
        arrlp = list(arrlp)
        arrlp.append(temp)
        arrlp = tuple(arrlp)
    return arrlp
def tuplearrlp(arrlp,temp):
    if isinstance(arrlp, list):
        if isinstance(temp[0],list):
            temp1=tuple(temp)
            arrlp.append(temp1)
            arrlp=tuple(arrlp)
        else:
            arrlp.append(temp)
            arrlp=tuple(arrlp)
    elif isinstance(arrlp, tuple):
        arrlp = list(arrlp)
        arrlp.append(temp)
        arrlp = tuple(arrlp)
    return arrlp
def encodeparameters(types,params,setabi=None):
    arrlp = []
    if isinstance(params,set):
        params = list(params)
    for i in range(len(params)):
        param = params[i]
        type = types[i]['type']
        name = types[i]['name']
        if type == 'string':
            arrlp.append(bytes(param,'utf-8'))
        elif type.startswith('uint') and not type.endswith(']'):
            temp=encodeuint(param)
            arrlp.append(int(''.join(temp),16))
        elif type == 'bool':
           arrlp.append(1 if param else 0)
        elif type.startswith("int") and not type.endswith("]"):
            temp1 = (param << 1) ^ (param >> 63)
            temp = encodeuint(temp1)
            arrlp.append(int(''.join(temp),16))
        elif type =='float':
            temp1 =float_to_hex(param)
            temp = hexstr2bytes(temp1)
            arrlp.append(temp)
        elif type =='double':
            temp1 =double_to_hex(param)
            temp = hexstr2bytes(temp1)
            arrlp.append(temp)
        elif type.endswith(']'):
            vectype = type.split('[')[0]
            temp=[]
            vecLen = type[type.index('[') + 1:].split(']')[0]
            if vectype == 'uint8' and vecLen =="":
               arrlp.append(param)
            else:
                for i in param:
                    temp.append(encodeparameters([{'type':vectype,'name':''}],[i],setabi)[0])
                arrlp.append(temp)
        elif type.startswith('list'):
            i1 = type.index('<')
            i2 = type.index('>')
            itype = type[i1+1:i2]
            temp=[]
            for j in param:
                temp.append(encodeparameters([{'type':itype,'name':''}], [j], setabi)[0])
            arrlp.append(temp)
        elif type.startswith('map'):
            i1=type.index('<')
            i2=type.index(',')
            i3=type.index('>')
            ktype=type[i1+1:i2]
            vtype=type[i2+1:i3]
            temp = []
            for j in param:
                kvalue=encodeparameters([{'type':ktype,'name':''}], [j[0]], setabi)[0]
                vvalue=encodeparameters([{'type':vtype,'name':''}], [j[1]], setabi)[0]
                temp.append([kvalue,vvalue])
            arrlp.append(temp)
        elif type.startswith('pair'):
            i1=type.index('<')
            i2=type.index(',')
            i3=type.index('>')
            ktype=type[i1+1:i2]
            vtype=type[i2+1:i3]
            kvalue=encodeparameters([{'type':ktype, 'name':''}], [param[0]], setabi)[0]
            vvalue=encodeparameters([{'type':vtype, 'name':''}], [param[1]], setabi)[0]
            arrlp.append([kvalue,vvalue])

        elif type.startswith('set'):
            temp=[]
            i1=type.index('<')
            i2 = type.index('>')
            stype=type[i1+1:i2]
            for j in param:
                temp.append(encodeparameters([{'type':stype,'name':''}],[j], setabi)[0])
            arrlp.append(temp)
        elif type == 'struct':
            structtype = [item for item in setabi if item['type'] == 'struct' and item['name'] == name]
            if not structtype:
                raise Exception('can not find struct in {} .'.format(name))
            else:
                arrlp.append(encodeparameters(structtype[0]['inputs'], param, setabi))

        elif type=='FixedHash<20>':
            temp=[]
            if isinstance(param,str):
                p1 = param[0:3]
                p2 = param
            elif isinstance(param,tuple):
                p1 = param[0][0:3]
                p2 = param[0]
            if p1 == 'lax' or p1 == 'lat':
                hrpgot, data1 = bech32.decode(p1, p2)
                for i in data1:
                    temp1=hex(i).replace('0x', '')
                    if len(temp1)==1:
                        temp1='0'+temp1
                    temp.append(temp1)
                    del temp1
            arrlp.append(int(''.join(temp), 16))
        elif type.startswith('FixedHash'): # 不是很确定，把'FixedHash'开头的类型理解为 ['0x33','0x6a'.'0x5e']这样的字节数组
            arrlp.append(param)
        else :
            structtype = [item for item in setabi if item['name'] == type]
            if not structtype:
                raise Exception('can not find struct through {} .'.format(type))
            else:
                temp=encodeparameters(structtype[0]['inputs'], param, setabi)
            arrlp.append(temp)
    return arrlp

#针对转化为uint的float和double,解码中以float a1=1.4为例，转化为uint32后为 a2='0x3fb33333'
# 转化为hex数组后为['3f','b3','33','33'],rlp编码后发到链上
# 获得链上传回来的数据，对应float、double的是4字节和8字节的HexBytes,以a2作为代表
# a3=struct.unpack('>f', HexBytes(a2)) 或者struct.unpack('>d', HexBytes(a2))[0]
# 1.399999976158142  或  1.4
def decodeuint(param):
    digit = 0
    if len(param) <= 1:
        data1 = int(param[0], 16)
    else:
        for i in range(len(param)):
            digit += int(param[i], 16) * (256 ** (len(param) - 1 - i))  #256
        data1 = digit
    return data1


def detail_decode_data(data_list):
    detail_after = []
    for i in data_list:
        if isinstance(i, list):
            detail_after.append(detail_decode_data(i))
        else:
            if i not in detail_after:
                str_i = to_hex(i)
                if str_i[:2] == '0x':
                    str_i = str_i[2:]
                if len(str_i) == 1:
                    str_i = '0' + str_i
                detail_after.append(str_i)
    return detail_after


def wasmdecode_abi(hrp, types, data, setabi=None):
    if isinstance(data, HexBytes) or isinstance(data, bytes):
        buf = detail_decode_data(rlp.decode(data))
    else:
        buf = data
    # print(f'wasmdecode_abi:{types,buf}')
    type = types['type']
    name = types['name']
    special_treatment = ['int8', 'int16', 'int32', 'int64']
    if not any(buf):
        if (type in special_treatment) or type.startswith('uint'):
            buf = ['0']
    # data1 = buf
    # if isinstance(data,HexBytes):
    #    decode_data = hexstr2bytes(to_hex(data))
    if type == 'string':
        tem = []
        if isinstance(buf,list):
            if not isinstance(buf[0],list):
                for i in buf:
                    tem.append(bytes.decode(HexBytes(i)))
                data1 = ''.join(tem)
            else:
                data1 = [wasmdecode_abi(hrp,{'type': type, 'name': ''}, j, setabi) for j in buf]
        elif isinstance(buf, str):
            data1 = bytes.decode(HexBytes(buf))
        elif isinstance(buf,tuple):
            data1 = [wasmdecode_abi(hrp,{'type': type, 'name': ''}, j, setabi) for j in buf]

    elif type.startswith('uint') and not type.endswith(']'):
        if len(buf) <= 1:
           data1 = int(buf[0],16)
        else:
           data1 = int(''.join(buf),16)
    elif type == 'bool':
        if not buf:
            data1 = False
        elif int(buf[0],16):
            data1 = True
        else:
            data1 = False
    elif type in ['int8', 'int16', 'int32', 'int64']:
        if isinstance(buf, list):
            buf = ''.join(buf)
        temp = int(buf, 16)
        data1 = (temp >> 1) ^ (temp & 1) * (-1)
    elif type == 'float':
        data1 = struct.unpack('>f', HexBytes(buf))
    elif type == 'double':
        data1 = struct.unpack('>d', HexBytes(buf))
    elif type.endswith(']'):
        lasti=type.rindex('[')
        vectype=type[0:lasti]
        if vectype == 'uint8':
            data1 = buf
        else:
            data1 = [wasmdecode_abi(hrp,{'type':vectype,'name':''}, i, setabi) for i in buf]

    elif type.startswith('list'):
        i1 = type.index('<')
        i2 = type.index('>')
        itype = type[i1 + 1:i2]
        if isinstance(buf, tuple) and len(buf) <= 1:
            buf =buf[0]
        data1 = [wasmdecode_abi(hrp,{'type': itype, 'name': ''}, j, setabi) for j in buf]
    elif type.startswith('map'):
        i1 = type.index('<')
        i2 = type.index(',')
        i3 = type.index('>')
        ktype = type[i1 + 1:i2]
        vtype = type[i2 + 1:i3]
        data1 = []
        for j in range(len(buf)):
            if len(buf[j])<=1 and len(buf[j][0])>=2:
                kvalue = wasmdecode_abi(hrp,{'type': ktype, 'name': ''}, buf[j][0][0], setabi)
                vvalue = wasmdecode_abi(hrp,{'type': vtype, 'name': ''}, buf[j][0][1], setabi)
            else:
                kvalue = wasmdecode_abi(hrp,{'type': ktype, 'name': ''}, buf[j][0], setabi)
                vvalue = wasmdecode_abi(hrp,{'type': vtype, 'name': ''}, buf[j][1], setabi)
            data1.append([kvalue,vvalue])
    elif type.startswith('pair'):
        i1=type.index('<')
        i2=type.index(',')
        i3=type.index('>')
        ktype=type[i1+1:i2]
        vtype=type[i2+1:i3]
        data1 = [wasmdecode_abi(hrp,{'type': ktype, 'name': ''}, buf[0], setabi),
                 wasmdecode_abi(hrp,{'type': vtype, 'name': ''}, buf[1], setabi)]
    elif type.startswith('set'):
        i1=type.index('<')
        i2 = type.index('>')
        stype=type[i1+1:i2]
        if isinstance(buf, tuple) and len(buf) <= 1:
            buf = buf[0]
        data1 = [ wasmdecode_abi(hrp,{'type':stype,'name':''},j, setabi) for j in buf]
        data1=set(data1)
    elif type == 'struct':
        structtype = [item for item in setabi if item['type'] == 'struct' and item['name'] == name]
        if not structtype:
            raise Exception('can not find struct in {} .'.format(name))
        else:
            data1 = [wasmdecode_abi(hrp,structtype[0]['inputs'][i], buf[i], setabi) for i in range(len(structtype[0]['inputs']))]

    elif type.startswith('FixedHash'):
        data1 = '0x'+tostring_hex(buf)
        if type.endswith('<20>'):
            temp=[]
            try :
                temp=tobech32address(hrp,data1)
            except:
                    raise Exception('wasmdecode error ! can not match FixedHash<20> type !' )
            finally:
                data1 = temp

    else:
        structtype = [item for item in setabi if item['name'] == type]
        if not structtype:
            raise Exception('can not find struct through {} .'.format(type))
        else:
            data1 = [wasmdecode_abi(hrp, structtype[0]['inputs'][i], buf[i], setabi) for i in
                     range(len(structtype[0]['inputs']))]
    return data1

def encode_abi(web3, abi, arguments, vmtype, data=None, setabi=None):
    arguments = list(arguments)
    if vmtype == 1:
        inputlength=len(abi['inputs'])
        if inputlength == len(arguments):
           if arguments:
               arrinputs=abi['inputs']
               paramabi= encodeparameters(arrinputs, arguments, setabi)
           else :
               paramabi= []
        else :
            raise Exception('The number of arguments is not matching the methods required number.'
                            'You need to pass {} arguments.'.format(inputlength))
        magicnum=['00','61','73','6d']
        paramabi.insert(0, fnv1_64(bytes(abi['name'], 'utf8')))
        # print(f'paramabi:{paramabi}')
        if abi['type']=='constructor':
            if data:
                data1 = bytes.fromhex(str(data, encoding='utf8'))
                deploydata = rlp.encode([data1, rlp.encode(paramabi)])
                encodata = ''.join(magicnum) + deploydata.hex()
                return '0x' + encodata
            else :
                return '0x' + rlp.encode(paramabi).hex()
        else :
            encodata = rlp.encode(paramabi).hex()
            # print(f'encodata:{encodata}')
            return '0x' + encodata

    else:
        argument_types = get_abi_input_types(abi)
        for j in range(len(argument_types)):
            if argument_types[j]:
                if argument_types[j] == 'address':
                    hrpgot, data1 = bech32.decode(arguments[j][:3], arguments[j])
                    addr = to_checksum_address(bytes(data1))
                    arguments[j] = addr  # .split(",")
                elif argument_types[j] == 'address[]':
                    for i in range(len(arguments[j])):
                        hrpgot, data1 = bech32.decode(arguments[j][i][:3], arguments[j][i])
                        addr = to_checksum_address(bytes(data1))
                        arguments[j][i] = addr

        if not check_if_arguments_can_be_encoded(abi, arguments, {}):
            raise TypeError(
                "One or more arguments could not be encoded to the necessary "
                "ABI type.  Expected types are: {0}".format(
                    ', '.join(argument_types),
                )
            )

        try:
            normalizers = [
                abi_ens_resolver(web3),
                abi_address_to_hex,
                abi_bytes_to_bytes,
                abi_string_to_text,
            ]
            normalized_arguments = map_abi_data(
                normalizers,
                argument_types,
                arguments,
            )
            encoded_arguments = eth_abi_encode_abi(
                argument_types,
                normalized_arguments,
            )
        except EncodingError as e:
            raise TypeError(
                "One or more arguments could not be encoded to the necessary "
                "ABI type: {0}".format(str(e))
            )

        if data:
            return to_hex(HexBytes(data) + encoded_arguments)
        else:
            return encode_hex(encoded_arguments)

def wasmevent_decode(hrp,types, data,setabi):
    if isinstance(data, HexBytes) or isinstance(data, bytes):
        bufs = detail_decode_data(rlp.decode(data))
    else:
        bufs = data
    data1 = []

    if (not isinstance(bufs, tuple)) and (not isinstance(types, tuple)):
        buf = bufs
        type = types
        special_treatment = ['int8', 'int16', 'int32', 'int64']
        if not any(buf):
            if (type in special_treatment) or type.startswith('uint'):
                buf = ['0']
        if type == 'string':
            tem = []
            if isinstance(buf, list):
                if not isinstance(buf[0], list):
                    for i in buf:
                        tem.append(bytes.decode(HexBytes(i)))
                    data1 = ''.join(tem)
                else:
                    data1 = [wasmevent_decode(hrp, type, j,setabi) for j in buf]
            elif isinstance(buf, str):
                data1 = bytes.decode(HexBytes(buf))
            elif isinstance(buf, tuple):
                data1 = [wasmevent_decode(hrp, type, j,setabi) for j in buf]
        elif type.startswith('uint') and not type.endswith(']'):
            digit = 0
            if len(buf) <= 1:
               data1 = int(buf[0],16)
            else:
               for i in range(len(buf)):
                  digit += int(buf[i],16)*(256**(len(buf)-1-i))
               data1 = digit
        elif type == 'bool':
            if not buf:
                data1 = False
            elif int(buf[0],16):
                data1 = True
            else:
                data1 = False
        elif type in ['int8', 'int16', 'int32', 'int64']:
            if isinstance(buf, list):
                buf = ''.join(buf)
            temp = int(buf, 16)
            data1 = (temp >> 1) ^ (temp & 1) * (-1)
        elif type == 'float':
            data1 = struct.unpack('>f', HexBytes(buf))
        elif type == 'double':
            data1 = struct.unpack('>d', HexBytes(buf))
        elif type.endswith(']'):
            lasti = type.rindex('[')
            vectype = type[0:lasti]
            if vectype == 'uint8':
                data1 = buf
            else:
                data1 = [wasmevent_decode(hrp, vectype, i,setabi) for i in buf]
        elif type.startswith('FixedHash'):
            data1 = '0x'+tostring_hex(buf)
            if type.endswith('<20>'):
                temp=[]
                try :
                    temp=tobech32address(hrp,data1)
                except:
                        raise ('wasmdecode error ! can not match FixedHash<20> type !' )
                finally:
                    data1 = temp
        else:
            structtype = [item for item in setabi if item['name'] == type]
            if not structtype:
                raise Exception('can not find struct through {} .'.format(type))
            else:
                data1 = [wasmevent_decode(hrp, structtype[0]['inputs'][i]['type'], buf[i], setabi) for i in
                         range(len(structtype[0]['inputs']))]
    else:
        if len(bufs) != len(types):
            if len(bufs[0]) == len(types):
                data1 = []
                for i in range(len(bufs[0])):
                    buf = bufs[0][i]
                    type = types[i]
                    data1.append(wasmevent_decode(hrp,type, buf,setabi))
        else:
            data1 = []
            for i in range(len(bufs)):
                buf = bufs[i]
                type = types[i]
                data1.append(wasmevent_decode(hrp, type, buf,setabi))
    return data1

def prepare_transaction(
        address,
        web3,
        fn_identifier,
        contract_abi=None,
        fn_abi=None,
        vmtype=None,
        transaction=None,
        fn_args=None,
        fn_kwargs=None):
    """
    :parameter `is_function_abi` is used to distinguish  function abi from contract abi
    Returns a dictionary of the transaction that could be used to call this
    TODO: make this a public API
    TODO: add new prepare_deploy_transaction API
    """
    if fn_abi is None:
        fn_abi = find_matching_fn_abi(contract_abi, fn_identifier, fn_args, fn_kwargs)

    validate_payable(transaction, fn_abi)

    if transaction is None:
        prepared_transaction = {}
    else:
        prepared_transaction = dict(**transaction)

    if 'data' in prepared_transaction:
        raise ValueError("Transaction parameter may not contain a 'data' key")

    if address:
        prepared_transaction.setdefault('to', address)

    prepared_transaction['data'] = encode_transaction_data(
        web3,
        fn_identifier,
        contract_abi,
        fn_abi,
        vmtype,
        fn_args,
        fn_kwargs,
    )
    return prepared_transaction


def encode_transaction_data(
        web3,
        fn_identifier,
        contract_abi=None,
        fn_abi=None,
        vmtype=None,
        args=None,
        kwargs=None):
    if fn_identifier is FallbackFn:
        fn_abi, fn_selector, fn_arguments = get_fallback_function_info(contract_abi, fn_abi)
    elif is_text(fn_identifier):
        fn_abi, fn_selector, fn_arguments = get_function_info(
            fn_identifier, contract_abi, fn_abi, args, kwargs,
        )
    else:
        raise TypeError("Unsupported function identifier")

    return add_0x_prefix(encode_abi(web3, fn_abi, fn_arguments, vmtype, fn_selector, contract_abi))


def get_fallback_function_info(contract_abi=None, fn_abi=None):
    if fn_abi is None:
        fn_abi = get_fallback_func_abi(contract_abi)
    fn_selector = encode_hex(b'')
    fn_arguments = tuple()
    return fn_abi, fn_selector, fn_arguments


def get_function_info(fn_name, contract_abi=None, fn_abi=None, args=None, kwargs=None):
    if args is None:
        args = tuple()
    if kwargs is None:
        kwargs = {}

    if fn_abi is None:
        fn_abi = find_matching_fn_abi(contract_abi, fn_name, args, kwargs)

    fn_selector = encode_hex(function_abi_to_4byte_selector(fn_abi))

    fn_arguments = merge_args_and_kwargs(fn_abi, args, kwargs)

    return fn_abi, fn_selector, fn_arguments


def validate_payable(transaction, abi):
    """Raise ValidationError if non-zero ether
    is sent to a non payable function.
    """
    if 'value' in transaction:
        if transaction['value'] != 0:
            if "payable" in abi and not abi["payable"]:
                raise ValidationError(
                    "Sending non-zero ether to a contract function "
                    "with payable=False. Please ensure that "
                    "transaction's value is 0."
                )
