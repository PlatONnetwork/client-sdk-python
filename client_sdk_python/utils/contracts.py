import functools
import struct
import numpy as np
from alaya.param_encode import (
    stringfnv,
    rlp_encode,
    rlp_decode,
    hexstr2bytes,
)

from alaya.packages.eth_abi import (
    encode_abi as eth_abi_encode_abi,
)
from alaya.packages.eth_abi.exceptions import (
    EncodingError,
)
from alaya.packages.eth_utils import (
    add_0x_prefix,
    encode_hex,
    function_abi_to_4byte_selector,
    is_text,
)
from hexbytes import (
    HexBytes,
)

from alaya.exceptions import (
    ValidationError,
)
from alaya.utils.abi import (
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
from alaya.utils.encoding import (
    to_hex,
    hexstr2bytes,
    tostring_hex,
    stringtohex,
    tobech32address,
)
from alaya.utils.function_identifiers import (
    FallbackFn,
)
from alaya.utils.normalizers import (
    abi_address_to_hex,
    abi_bytes_to_bytes,
    abi_ens_resolver,
    abi_string_to_text,
)
from alaya.utils.toolz import (
    pipe,
    valmap,
)

from alaya.packages.platon_keys.utils import bech32,address

from alaya.packages.eth_utils import to_checksum_address

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
            temp = []

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
            temp = stringtohex(bytes(param,'utf-8'))
            if isinstance(param, str) and len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
        elif type.startswith('uint') and not type.endswith(']'):
            temp=encodeuint(param)
            if len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
        elif type == 'bool':
            if param:
                temp = '01'
            else:
                temp = '0'
            if len(params) <= 1:
                arrlp.append(temp)
            else:
                arrlp = handlearrlp(arrlp, temp)
        elif type == 'int8':
            temp1 = np.uint8(param)
            temp = encodeuint(temp1)
            if len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
        elif type == 'int16':
            temp1 = np.uint16(param)
            temp = encodeuint(temp1)
            if len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
        elif type == 'int32':
            temp1 = np.uint32(param)
            temp = encodeuint(temp1)
            if len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
        elif type == 'int64':
            temp1 = np.uint64(param)
            temp = encodeuint(temp1)
            if len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
        elif type =='float':
            temp1 =float_to_hex(param)
            temp = hexstr2bytes(temp1)
            if len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
        elif type =='double':
            temp1 =double_to_hex(param)
            temp = hexstr2bytes(temp1)
            if len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
        elif type.endswith(']'):
            vectype = type.split('[')[0]
            temp=[]
            if vectype == 'uint8':
                for i in param:
                    if isinstance(i,list):
                        temp.append(hex(i[0]).replace('0x',''))
                    else:
                        if isinstance(i,str):
                            temp.append(hex(int(i,16)).replace('0x', ''))
                        else:
                            temp.append(hex(i).replace('0x', ''))
                if len(params) <= 1:
                    arrlp = temp
                else:
                    arrlp = handlearrlp(arrlp, temp)
            else:
                for i in param:
                    temp.append(encodeparameters([{'type':vectype,'name':''}],[i],setabi))
                if len(params) <= 1:
                    arrlp = tuple(temp) ##转化为字节数组列表模式
                else:
                    arrlp = tuplearrlp(arrlp, temp)
        elif type.startswith('list'):
            i1 = type.index('<')
            i2 = type.index('>')
            itype = type[i1+1:i2]
            temp=[]
            for j in param:
                temp.append(encodeparameters([{'type':itype,'name':''}], [j], setabi))
            if len(params) <= 1:
                arrlp = tuple(temp)  ##转化为字节数组列表模式
            else:
                arrlp = tuplearrlp(arrlp, temp)
        elif type.startswith('map'):
            i1=type.index('<')
            i2=type.index(',')
            i3=type.index('>')
            ktype=type[i1+1:i2]
            vtype=type[i2+1:i3]
            temp = []
            for j in param:
                kvalue=encodeparameters([{'type':ktype,'name':''}], [j[0]], setabi)
                vvalue=encodeparameters([{'type':vtype,'name':''}], [j[1]], setabi)
                temp1=(kvalue,vvalue)
                temp.append(temp1)
            if len(params) <= 1:
                arrlp = tuple(temp)  ##转化为字节数组列表模式
            else:
                arrlp = tuplearrlp(arrlp, temp)
        elif type.startswith('pair'):
            temp=[]
            i1=type.index('<')
            i2=type.index(',')
            i3=type.index('>')
            ktype=type[i1+1:i2]
            vtype=type[i2+1:i3]
            kvalue=encodeparameters([{'type':ktype, 'name':''}], [param[0]], setabi)
            vvalue=encodeparameters([{'type':vtype, 'name':''}], [param[1]], setabi)
            temp.append(kvalue)
            temp.append(vvalue)
            if len(params) <= 1:
                arrlp = tuple(temp)  ##转化为字节数组列表模式
            else:
                arrlp = tuplearrlp(arrlp, temp)

        elif type.startswith('set'):
            temp=[]
            i1=type.index('<')
            i2 = type.index('>')
            stype=type[i1+1:i2]
            for j in param:
                temp.append(encodeparameters([{'type':stype,'name':''}],[j], setabi))
            if len(params) <= 1:
                arrlp = tuple(temp)  ##转化为字节数组列表模式
            else:
                arrlp = tuplearrlp(arrlp, temp)
        elif type == 'struct':
            temp=[]
            structtype = [item for item in setabi if item['type'] == 'struct' and item['name'] == name]
            if not structtype:
                raise Exception('can not find struct in {} .'.format(name))
            else:
                temp.append(encodeparameters(structtype[0]['inputs'], param, setabi))
            if len(params) <= 1:
                arrlp = tuple(temp)  ##转化为字节数组列表模式
            else:
                arrlp = tuplearrlp(arrlp, temp)

        elif type=='FixedHash<20>':
            temp=[]
            if isinstance(param,str):
                p1 = param[0:3]
                p2 = param
            elif isinstance(param,tuple):
                p1 = param[0][0:3]
                p2 = param[0]
            if p1 == 'atx' or p1 == 'atp':
                hrpgot, data1 = bech32.decode(p1, p2)
                for i in data1:
                    temp1=hex(i).replace('0x', '')
                    if len(temp1)==1:
                        temp1='0'+temp1
                    temp.append(temp1)
                    del temp1
            if len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
        elif type.startswith('FixedHash'): # 不是很确定，把'FixedHash'开头的类型理解为 ['0x33','0x6a'.'0x5e']这样的字节数组
            temp=[]
            for i in param:
                if isinstance(i, list):
                    temp.append(hex(i[0]).replace('0x', ''))
                else:
                    temp.append(hex(i).replace('0x', ''))
            if len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
        else :
            structtype = [item for item in setabi if item['name'] == type]
            if not structtype:
                raise Exception('can not find struct through {} .'.format(type))
            else:
                temp=[]
                temp=encodeparameters(structtype[0]['inputs'], param, setabi)
            if len(params) <= 1:
                arrlp = temp
            else:
                arrlp = handlearrlp(arrlp, temp)
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
def wasmdecode_abi(types, data, setabi=None):
    if isinstance(data, HexBytes) or isinstance(data, bytes):
        buf = rlp_decode(hexstr2bytes(to_hex(data)))
    else:
        buf = data
    type = types['type']
    name = types['name']
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
                data1 = [0 for x in range(len(buf))]
                for j in range(len(buf)):
                    data1[j] = wasmdecode_abi({'type': type, 'name': ''}, buf[j], setabi)
        elif isinstance(buf, str):
            data1 = bytes.decode(HexBytes(buf))
        elif isinstance(buf,tuple):
            data1 = [0 for x in range(len(buf))]
            for j in range(len(buf)):
                data1[j] = wasmdecode_abi({'type': type, 'name': ''}, buf[j], setabi)

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
    elif type == 'int8':
        temp = np.uint8(decodeuint(buf))
        data1 = np.int8(temp)
    elif type == 'int16':
        temp = np.uint16(decodeuint(buf))
        data1 = np.int16(temp)
    elif type == 'int32':
        temp = np.uint32(decodeuint(buf))
        data1 = np.int32(temp)
    elif type == 'int64':
        temp = np.uint64(decodeuint(buf))
        data1 = np.int64(temp)
    elif type == 'float':
        data1 = struct.unpack('>f', HexBytes(buf))
    elif type == 'double':
        data1 = struct.unpack('>d', HexBytes(buf))
    elif type.endswith(']'):
        lasti=type.rindex('[')
        vectype=type[0:lasti]
        if isinstance(buf, tuple) and len(buf) <= 1:
            buf =buf[0]
        data1 = [0 for x in range(len(buf))]
        if vectype == 'uint8':
            for i in range(len(buf)):
                data1[i] = hex(int(buf[i],16))
        else:
            for i in range(len(buf)):
                data1[i] = wasmdecode_abi({'type':vectype,'name':''}, buf[i], setabi)

    elif type.startswith('list'):
        i1 = type.index('<')
        i2 = type.index('>')
        itype = type[i1 + 1:i2]
        if isinstance(buf, tuple) and len(buf) <= 1:
            buf =buf[0]
        data1 = [0 for x in range(len(buf))]
        for j in range(len(buf)):
            data1[j] = (wasmdecode_abi({'type': itype, 'name': ''}, buf[j], setabi))
    elif type.startswith('map'):
        i1 = type.index('<')
        i2 = type.index(',')
        i3 = type.index('>')
        ktype = type[i1 + 1:i2]
        vtype = type[i2 + 1:i3]
        data1 = [0 for x in range(len(buf))]
        for j in range(len(buf)):
            if len(buf[j])<=1 and len(buf[j][0])>=2:
                kvalue = wasmdecode_abi({'type': ktype, 'name': ''}, buf[j][0][0], setabi)
                vvalue = wasmdecode_abi({'type': vtype, 'name': ''}, buf[j][0][1], setabi)
            else:
                kvalue = wasmdecode_abi({'type': ktype, 'name': ''}, buf[j][0], setabi)
                vvalue = wasmdecode_abi({'type': vtype, 'name': ''}, buf[j][1], setabi)
            data1[j] = [kvalue,vvalue]
    elif type.startswith('pair'):
        i1=type.index('<')
        i2=type.index(',')
        i3=type.index('>')
        ktype=type[i1+1:i2]
        vtype=type[i2+1:i3]
        if isinstance(buf, tuple) and len(buf) <= 1:
            buf = buf[0]
        data1 = [0 for x in range(len(buf))]
        data1[0]=wasmdecode_abi({'type':ktype, 'name':''}, buf[0], setabi)
        data1[1]=wasmdecode_abi({'type':vtype, 'name':''}, buf[1], setabi)
    elif type.startswith('set'):
        i1=type.index('<')
        i2 = type.index('>')
        stype=type[i1+1:i2]
        if isinstance(buf, tuple) and len(buf) <= 1:
            buf = buf[0]
        data1 = [0 for x in range(len(buf))]
        for j in range(len(buf)):
            data1[j] = wasmdecode_abi({'type':stype,'name':''},buf[j], setabi)
        data1=set(data1)
    elif type == 'struct':
        structtype = [item for item in setabi if item['type'] == 'struct' and item['name'] == name]
        if not structtype:
            raise Exception('can not find struct in {} .'.format(name))
        else:
            data1 = [0 for x in range(len(structtype[0]['inputs']))]
            for i in range(len(structtype[0]['inputs'])):
                data1[i]=wasmdecode_abi(structtype[0]['inputs'][i], buf[i], setabi)

    elif type.startswith('FixedHash'):
        data1 = '0x'+tostring_hex(buf)
        if type.endswith('<20>'):
            temp=[]
            try :
                temp=tobech32address('atx',data1)
            except:
                try:
                    temp=tobech32address('atp',data1)
                except:
                    raise ('wasmdecode error ! can not match FixedHash<20> type !' )
            finally:
                data1 = temp

    else:
        structtype = [item for item in setabi if item['name'] == type]
        if not structtype:
            raise Exception('can not find struct through {} .'.format(type))
        else:
            data1 = [0 for x in range(len(structtype[0]['inputs']))]
            for i in range(len(structtype[0]['inputs'])):
                data1[i]=wasmdecode_abi(structtype[0]['inputs'][i], buf[i], setabi)

    return data1

def encode_abi(web3, abi, arguments, vmtype, data=None, setabi=None):
    if vmtype == 1:
        arrinputs=[]
        inputlength=len(abi['inputs'])
        if inputlength == len(arguments):
           if arguments:
               arrinputs=abi['inputs']
               paramABI= encodeparameters(arrinputs, arguments, setabi)
           else :
               paramABI= []
        else :
            raise Exception('The number of arguments is not matching the methods required number.'
                            'You need to pass {} arguments.'.format(inputlength))
        magicnum=['00','61','73','6d']
        paramabi=(stringfnv(abi['name']),paramABI)
        if abi['type']=='constructor':
            if data:
                data1=hexstr2bytes(to_hex(data))
                deploydata=rlp_encode((data1,rlp_encode(paramabi)))
                encodata=tostring_hex(magicnum)+tostring_hex(deploydata)
                return '0x'+encodata
            else :
                encodata=tostring_hex(rlp_encode(paramabi))
                return '0x'+encodata
        else :
            deploydata = rlp_encode(paramabi)
            encodata=tostring_hex(deploydata)
            return '0x'+encodata

    else:
        argument_types = get_abi_input_types(abi)
        for j in range(len(argument_types)):
            if argument_types[j]:
                if argument_types[j] == 'address':
                    if arguments[j][:3] == 'atx':
                        hrpgot, data1 = bech32.decode("atx", arguments[j])
                        addr = to_checksum_address(bytes(data1))
                        arguments[j] = addr  #.split(",")
                    elif arguments[j][:3] == 'atp':
                        hrpgot, data1 = bech32.decode("atp", arguments[j])
                        addr = to_checksum_address(bytes(data1))
                        arguments[j] = addr  #.split(",")
                    else:
                        raise Exception("wrong address")
                elif argument_types[j] == 'address[]':
                    for i in range(len(arguments[j])):
                        if arguments[j][i][:3] == 'atx':
                            hrpgot, data1 = bech32.decode("atx", arguments[j][i])
                            addr = to_checksum_address(bytes(data1))
                            arguments[j][i] = addr
                        elif arguments[j][i][:3] == 'atp':
                            hrpgot, data1 = bech32.decode("atp", arguments[j][i])
                            addr = to_checksum_address(bytes(data1))
                            arguments[j][i] = addr
                        else:
                            raise Exception("wrong address[]")

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

def wasmevent_decode(types, data,):
    if isinstance(data, HexBytes) or isinstance(data, bytes):
        bufs = rlp_decode(hexstr2bytes(to_hex(data)))
    else:
        bufs = data
    data1 = []
    # for i in range(len(bufs)):
    #     buf = bufs[i]
    #     type = types[i]
    if (not isinstance(bufs, tuple)) and (not isinstance(types, tuple)):
        buf = bufs
        type = types
        if type == 'string':
            tem = []
            if isinstance(buf,list):
                for i in buf:
                    tem.append(bytes.decode(HexBytes(i)))
                data1 = ''.join(tem)
            elif isinstance(buf, str):
                data1 = bytes.decode(HexBytes(buf))
            elif isinstance(buf,tuple):
                data1 = [0 for x in range(len(buf))]
                for j in range(len(buf)):
                    data1[j] = wasmevent_decode(types, buf[j])
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
        elif type == 'int8':
            temp = np.uint8(decodeuint(buf))
            data1 = np.int8(temp)
        elif type == 'int16':
            temp = np.uint16(decodeuint(buf))
            data1 = np.int16(temp)
        elif type == 'int32':
            temp = np.uint32(decodeuint(buf))
            data1 = np.int32(temp)
        elif type == 'int64':
            temp = np.uint64(decodeuint(buf))
            data1 = np.int64(temp)
        elif type == 'float':
            data1 = struct.unpack('>f', HexBytes(buf))
        elif type == 'double':
            data1 = struct.unpack('>d', HexBytes(buf))
        elif type.endswith(']'):
            lasti=type.rindex('[')
            vectype=type[0:lasti]
            data1 = [0 for x in range(len(buf))]
            if vectype == 'uint8':
                for i in range(len(buf)):
                    data1[i] = hex(int(buf[i],16))
            else:
                for i in range(len(buf)):
                    data1[i] = wasmevent_decode(types, buf[i])
        elif type.startswith('FixedHash'):
            data1 = '0x'+tostring_hex(buf)
            if type.endswith('<20>'):
                temp=[]
                try :
                    temp=tobech32address('atx',data1)
                except:
                    try:
                        temp=tobech32address('atp',data1)
                    except:
                        raise ('wasmdecode error ! can not match FixedHash<20> type !' )
                finally:
                    data1 = temp
    else:
        if len(bufs) != len(types):
            if len(bufs[0]) == len(types):
                data1 = [0 for x in range(len(types))]
                for i in range(len(bufs[0])):
                    buf = bufs[0][i]
                    type = types[i]
                    data1[i] = wasmevent_decode(type, buf)
        else:
            data1 = [0 for x in range(len(bufs))]
            for i in range(len(bufs)):
                buf = bufs[i]
                type = types[i]
                data1[i]=wasmevent_decode(type, buf)
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
