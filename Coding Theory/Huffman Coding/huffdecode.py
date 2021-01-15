#!/usr/bin/env python
# coding: utf-8

import sys

if len(sys.argv) < 2:
    print("Format: python huffdecode.py binaryfile")
    sys.exit(1)


# Decoding: Read the binary file
with open(sys.argv[1], 'rb') as fbin:
    encoded_bytes = fbin.read()


if len(encoded_bytes) < 1:
	print('Empty file. Exiting!')
	sys.exit(0)

# Decoding: first byte is the code_block_offset
code_block_offset = encoded_bytes[0]
# The code block is stored from index 1 to code_block_offset
code_block = encoded_bytes[1: code_block_offset+1].decode('utf-8')
# print(code_block)

#  Decoding: Remember the next byte is the offset value of the last byte
# We split the encoded_bytes to get just the code sequence alone
code_bytes = encoded_bytes[code_block_offset+1:]
offset = code_bytes[0]

encoded_text = ''
# Read from the next byte till the second last byte
for ebyte in code_bytes[1:len(code_bytes)-1]:
    b = format(ebyte, '08b')
    encoded_text += b
    
# The last byte may not have used full 8 bits; remove un-necessary zeros with the offset value
last_byte = code_bytes[len(code_bytes)-1]
formatter = '0' + str(offset) + 'b'
encoded_text += format(last_byte, formatter)

## Get back the code_map from the code_block (Actually reverse code_map)
code_map = {}
for code in code_block.split('\n'):
    if (len(code)>1):
        character = code.split(':')[0]
        huffcode = code.split(':')[1]
        code_map[huffcode] = character

# Decoding: Now decode the retireved binary sequence with the reverse code_map
# This is a greedy algorithm
def decoding(content, _lookup):
    while content:
        options = [i for i in _lookup if content.startswith(i) and (any(content[len(i):].startswith(b) for b in _lookup) or not content[len(i):])]
        if not options:
            raise Exception("Decoding error")
        yield _lookup[options[0]]
        content = content[len(options[0]):]

print('The original encoded text is: ')

print(''.join(decoding(encoded_text, code_map)))


