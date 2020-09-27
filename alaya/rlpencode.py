def rlp_encode(input):
    if isinstance(input,list):
        if len(input) == 1 and ord(input[0]) <= 0x7f: return input
        else:
            temp=encode_length(len(input), 0x80)
            return ([temp.replace('0x','')]+input)
    elif isinstance(input,tuple):
        output = []
        for item in input: output += rlp_encode(item)
        return encode_length(len(output), 0xc0) + output

def encode_length(L,offset):
    if L < 56:
         return hex(L + offset)
    elif L < 256**8:
         BL = to_binary(L)
         return hex(len(BL) + offset + 55) + BL
    else:
         raise Exception("input too long")

def to_binary(x):
    if x == 0:
        return ''
    else:
        return to_binary(int(x / 256)) + hex(x % 256)


# def rlp_decode(input):
#     if len(input) == 0:
#         return
#     output = ''
#     (offset, dataLen, type) = decode_length(input)
#     if type is str:
#         output = instantiate_str(substr(input, offset, dataLen))
#     elif type is list:
#         output = instantiate_list(substr(input, offset, dataLen))
#     output + rlp_decode(substr(input, offset + dataLen))
#     return output
#
# def decode_length(input):
#     length = len(input)
#     if length == 0:
#         raise Exception("input is null")
#     prefix = ord(input[0])
#     if prefix <= 0x7f:
#         return (0, 1, str)
#     elif prefix <= 0xb7 and length > prefix - 0x80:
#         strLen = prefix - 0x80
#         return (1, strLen, str)
#     elif prefix <= 0xbf and length > prefix - 0xb7 and length > prefix - 0xb7 + to_integer(substr(input, 1, prefix - 0xb7)):
#         lenOfStrLen = prefix - 0xb7
#         strLen = to_integer(substr(input, 1, lenOfStrLen))
#         return (1 + lenOfStrLen, strLen, str)
#     elif prefix <= 0xf7 and length > prefix - 0xc0:
#         listLen = prefix - 0xc0;
#         return (1, listLen, list)
#     elif prefix <= 0xff and length > prefix - 0xf7 and length > prefix - 0xf7 + to_integer(substr(input, 1, prefix - 0xf7)):
#         lenOfListLen = prefix - 0xf7
#         listLen = to_integer(substr(input, 1, lenOfListLen))
#         return (1 + lenOfListLen, listLen, list)
#     else:
#         raise Exception("input don't conform RLP encoding form")
#
# def to_integer(b):
#     length = len(b)
#     if length == 0:
#         raise Exception("input is null")
#     elif length == 1:
#         return ord(b[0])
#     else:
#         return ord(substr(b, -1)) + to_integer(substr(b, 0, -1)) * 256