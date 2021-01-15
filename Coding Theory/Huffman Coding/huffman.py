#!/usr/bin/env python
# coding: utf-8

import sys

import collections
from queue import PriorityQueue

if len(sys.argv) < 2:
    print("Format: python huffman.py input.txt")
    sys.exit(1)

# Read the input file; filename is given as a command line argument
text = ''
with open(sys.argv[1], 'r') as file:
    text = file.read()


# Quit program if file is empty
if len(text) == 0:
    print("empty file. Stopping")
    sys.exit(0)


characters = list(text)
uniq_chars = set(characters)
# print(uniq_chars)
freq = collections.Counter(characters)

print("Frequency of Characters")
for c,f in freq.items():
    print(c, f)

# HuffNode is a node in the huffman tree.
# It has two child nodes one to the left and one to the right
# It also keep a weight which is the sum of the weights of its two children
# We also keep the huffman codes of all characters in its subtrees
class HuffNode:
    def __init__(self, character, weight, leftNode=None, rightNode=None):
        self.character = character
        self.weight = weight
        self.leftNode = leftNode
        self.rightNode = rightNode
        
        # We keep all the huffman codes of the children in self.codes
        if leftNode is None:
            # leaf node; empty code
            self.codes = [(character, '')]
        else:
            # prepend 0 to all codes in the left subtree and keep in codes
            self.codes = [(x[0], '0'+x[1]) for x in leftNode.codes]
            # prepend 1 to all codes in the right subtree and also keep in codes
            self.codes += [(x[0], '1'+x[1]) for x in rightNode.codes]
    
    def __lt__(self, other):
        return True
    

# A priority Queue is used for the huffman code algorithm
# It has two operations: put & get
# When an object is put in the Queue it will be inserted in the order of the provided weight
# e.g. if we put (2, obj3) to a Queue containng (1, bj1) & (3, obj2) the new Queue will be (1, obj1), (2, obj3), (3, obj2) 
# which is sorted according to the weight associated with each object
# Initialize a priority queue
q = PriorityQueue()

# Push each character & its frequency to the queue as HuffNodes
for c,f in freq.items():
    node = HuffNode(c, f) # A leaft Huffnode is created
    q.put((f, node)) # inserting to the priority queue
    
    
# Huffman Code generation
# Combine lowest frequency nodes iteratively
rootNode = None
while(q.empty() is False):
    # if there is only one element in the queue then stop
    if q.qsize() < 2:
        rootNode = q.get()[1] # Keep only the object which is the root HuffNode
        break
    
    # otherwise    
    # combine two lowest frequency nodes to one node; this is one step in the huffman algorithm
    node1 = q.get()[1]
    node2 = q.get()[1]
    # create a new HUffnode with the new weight being the sum of weights of its children
    node = HuffNode(character='', weight=node1.weight+node2.weight, leftNode=node1, rightNode=node2)
    # print(node.weight)    
    # insert back to the queue 
    q.put((node.weight, node))


# The rootNode will have all the huffman codes in its codes field
print("\nThe codes for each characters")
for code in rootNode.codes:
    print(code[0], code[1])

# Convert codes into a dictionary/map
code_map = dict(rootNode.codes)


# Generate the compressed text
# For each character convert it into its corresponding binary huffman code
compressed_list = [code_map.get(c) for c in characters]
compressed_text = ''.join(compressed_list)
print('\nCompressed text')
print(compressed_text)

# Define a function to convert binary bits to bytes
# input: '1011' output: \x0b (which is 00001011 in binary: a single byte/8 bits)
# Basically the function splits the sequence of bits into chunks of 8-bits
# Refer: https://stackoverflow.com/questions/51425638/how-to-write-huffman-coding-to-a-file-using-python
def _to_bytes(data):
    b = bytearray()
    for i in range(0, len(data), 8):
        b.append(int(data[i:i+8], 2))
    return bytes(b)

# Ideally number of bits in compressed_text should be a multiple of 8
# otherwise keep track of how many off bits to recover back while decoding
offset = len(compressed_text) % 8

# We have to save the characters & their corresponding huffman codes also in the binary file
# This is required for decoding
code_block = ''
for k in code_map.keys():
    code_block += k + ':' + code_map.get(k) + '\n'

# Convert the code block into bytes for saving in a binary file    
code_block_bytes = bytes(code_block, encoding='utf-8')
code_block_offset = len(code_block_bytes)

# Write the encoded bytes
outfilename = sys.argv[1].split('.')[0] + '.bin' # remove the .txt extension & add .bin extension

with open(outfilename, 'wb') as fbout:
    # First write the code_block_offset to determine how to bytes to be read
    # for retrieving the code block safely
    fbout.write(bytes([code_block_offset]))
    # Now write the code block as its ascii (utf-8 encoding): a couple of bytes
    fbout.write(code_block_bytes)
    
    # then we write the number of off bits; this is the number of bits in the last byte
    fbout.write(bytes([offset]))
    # then convert the bit sequence to a byte sequence
    compressed_bytes = _to_bytes(compressed_text)
    fbout.write(compressed_bytes)



print('\nHuffman encoded text written to the binary file ' + outfilename + ' Successfully!')


