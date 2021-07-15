from client_sdk_python.fvnhash import fnv1_64
from hexbytes import (
    HexBytes,
)
def hexstr2bytes(address: str):
    pos = 0
    len_str = len(address)
    if len_str % 2 != 0:
       return None
    len_str = round(len_str/2)
    hexa = []
    for i in range(len_str):
       s1 = address[pos:pos+2]
       if s1 == '0x' or s1 == '0X':
          pos +=2
          continue
       sv = s1
       hexa.append(sv)
       pos += 2
    return hexa
def tostring_hex(arr:list):
    arrhex=''
    if arr:
        for i in arr:
            arrhex= arrhex+i
        return arrhex
    else:
        return ''
def stringtohex(str1:bytes):
    strhex=[]
    if str1:
        for i in str1:
            temp = hex(i).replace('0x','')
            if len(temp) == 1:
                temp = '0'+temp
            strhex=strhex+[temp]
            del temp
        return strhex
    else: return []

def stringfnv(str1:str):
    a1 = bytes(str1, 'utf-8')
    a2 = fnv1_64(a1)
    a3 = hex(a2)
    if len(a3) % 2:
        a4 = '0'+a3.replace('0x','')
        aa = hexstr2bytes(a4)
    else:
        aa = hexstr2bytes(a3)
    return aa

def rlp_encode(input):
    if isinstance(input,list):
        if len(input)==1 and input[0]=='0': return ['80']
        elif len(input) == 1 and int(input[0],16) <= 0x7f: return input
        elif len(input)==0:return []
        else:
            temp=encode_length(len(input), 0x80)
            return (hexstr2bytes(temp.replace('0x',''))+input)
    elif isinstance(input,tuple):
        output = []
        for item in input: output += rlp_encode(item)
        temp1=encode_length(len(output), 0xc0)
        return hexstr2bytes(temp1.replace('0x','')) + output

def encode_length(L,offset):
    if L < 56:
         return hex(L + offset)
    elif L < 256**8:
         BL = to_binary(L)
         return hex(int(len(BL)/2) + offset + 55) + BL
    else:
         raise Exception("input too long")

def to_binary(x):
    if x == 0:
        return ''
    else:
        tem1=(to_binary(int(x / 256))).replace('0x','')
        tem2=hex(x % 256).replace('0x','')
        if tem1:
            if len(tem1)==1:
                tem1='0'+tem1
        if tem2:
            if len(tem2)==1:
                tem2='0'+tem2
        return tem1+tem2
    # if x == 0:
    #     return ''
    # else: return hex(x)

def listcat(list1,list2):
    if list2:
        if isinstance(list1[0],list):
            if isinstance(list2[0],list):
                for i in range(len(list2)):
                   list1.append(list2[i])
                temp=list1
            else:
                temp=[list1,list2]
        else:
            temp=[list1]
            if isinstance(list2[0], list):
                for i in range(len(list2)):
                    temp.append(list2[i])
            else:
                temp.append(list2)
    else:
        temp = list1
    return temp
def tuplecat(tuple1,tuple2):
    # if isinstance(tuple1[0],tuple):
    #     if isinstance(tuple2[0],tuple):
    #         temp = (tuple1,tuple2)
    #     else:
    #         temp1 = list(tuple1)
    #         temp1.append(tuple2)
    #         temp = tuple(temp1)
    # elif tuple2:
    #     if isinstance(tuple2[0],tuple):
    #         temp1 = list(tuple2)
    #         temp1.insert(tuple1)
    #         temp = tuple(temp1)
    #     elif isinstance(tuple2,tuple):
    #         temp = (tuple1,tuple2)
    #     else:
    #         if isinstance(tuple2[0],list):
    #             temp1 = list(tuple1)
    #             for i in range(len(tuple2)):
    #                 temp1.append(tuple2[i])
    #             temp = tuple(temp1)
    #         else:
    #             temp1 = list(tuple1)
    #             temp1.append(tuple2)
    #             temp = tuple(temp1)
    if tuple2:
        if isinstance(tuple2,tuple):
           temp=(tuple1,tuple2)
        elif isinstance(tuple2,list):
            if isinstance(tuple2[0],list):
                temp=[tuple1]
                for i in range(len(tuple2)):
                    temp.append(tuple2[i])
                temp = tuple(temp)
            else:
                temp=(tuple1,tuple2)
    else:
        temp = tuple1

    return temp


def rlp_decode(input):
    if len(input) == 0:
        return []
    output = []
    (offset, dataLen, type) = decode_length(input)
    if type is list:
        output = input[offset:offset+dataLen]
        output = listcat(output,rlp_decode(input[offset + dataLen:]))
    elif type is tuple:
        output = rlp_decode(input[offset:offset+dataLen])
        if input[offset+dataLen:]:
            if isinstance(output, list):
                output = tuple([output])
            output = tuplecat(output,rlp_decode(input[offset+dataLen:]))
        else:
            if isinstance(output, list):
                output = tuple([output])
    return output

def decode_length(input):
    length = len(input)
    if length == 0:
        raise Exception("input is null")
    prefix = int(input[0],16)
    if prefix <= 0x7f:
        return (0, 1, list)
    elif prefix <= 0xb7 and length > prefix - 0x80:
        strLen = prefix - 0x80
        return (1, strLen, list)
    elif prefix <= 0xbf and length > prefix - 0xb7 and length > prefix - 0xb7 + to_integer(input[1:prefix - 0xb6]):
        lenOfStrLen = prefix - 0xb7
        strLen = to_integer(input[1:lenOfStrLen+1])
        return (1 + lenOfStrLen, strLen, list)
    elif prefix <= 0xf7 and length > prefix - 0xc0:
        listLen = prefix - 0xc0
        return (1, listLen, tuple)
    elif prefix <= 0xff and length > prefix - 0xf7 and length > prefix - 0xf7 + to_integer(input[1:prefix - 0xf6]):
        lenOfListLen = prefix - 0xf7
        listLen = to_integer(input[1:lenOfListLen+1])
        return (1 + lenOfListLen, listLen, tuple)
    else:
        raise Exception("input don't conform RLP encoding form")

def to_integer(b):
    #获得list或tuple的真实长度
    length = len(b)
    if length == 0:
        raise Exception("input is null")
    elif length == 1:
        return int(b[0],16)
    else:
        return int(b[-1:],16) + to_integer(b[0:-1]) * 256