#!/usr/bin/env python
# coding: utf-8

import collections
from queue import PriorityQueue

import tkinter as tk
  
# importing askopenfile function 
# from class filedialog 
from tkinter.filedialog import askopenfile 

root = tk.Tk() 
root.geometry('600x400') 
root.title('Hufman Coding')
  
# This function will be used to open files in read mode 
# only filetypes mentioned can be opened
def open_file_encode(): 
    file = askopenfile(mode ='r', filetypes =[('Text', '*.txt')])
    if file:
        text_widget.delete('1.0', tk.END)
        # text_widget.insert(tk.END, file.name)
        file =  open(file.name, 'r')
        text = file.read()
        file.close()

        # Quit program if file is empty
        if len(text) == 0:
            text_widget.insert(tk.END, "empty file")
            return      

        characters = list(text)
        uniq_chars = set(characters)
        # print(uniq_chars)
        freq = collections.Counter(characters)

        text_widget.insert(tk.END, "Frequency of Characters\n")
        for c,f in freq.items():
            text_widget.insert(tk.END, c + ' ' +  str(f) + '\n')

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
        text_widget.insert(tk.END, "\nThe codes for each characters\n")
        for code in rootNode.codes:
            text_widget.insert(tk.END, code[0] + ': ' + code[1] + '\n')

        # Convert codes into a dictionary/map
        code_map = dict(rootNode.codes)


        # Generate the compressed text
        # For each character convert it into its corresponding binary huffman code
        compressed_list = [code_map.get(c) for c in characters]
        compressed_text = ''.join(compressed_list)
        # text_widget.insert(tk.END '\nCompressed text written to ')
        # print(compressed_text)

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

        code_block = ''
        for k in code_map.keys():
            code_block += k

        code_block += ':'    
    
        for k in code_map.keys():
            code_block += code_map.get(k) + ','
    
        # Convert the code block into bytes for saving in a binary file    
        code_block_bytes = bytes(code_block, encoding='utf-8')
        code_block_offset = len(code_block_bytes)

        # Write the encoded bytes
        outfilename = file.name.split('.')[0] + '.bin' # remove the .txt extension & add .bin extension

        with open(outfilename, 'wb') as fbout:
            # First write the code_block_offset to determine how many bytes to be read
            # for retrieving the code block safely
            # allocate 2 bytes for this
            b = format(code_block_offset, '016b') # two bytes = 16 bits
            fbout.write(_to_bytes(b))
            # Now write the code block as its ascii (utf-8 encoding): a couple of bytes
            fbout.write(code_block_bytes)
            
            # then we write the number of off bits; this is the number of bits in the last byte
            fbout.write(bytes([offset]))
            # then convert the bit sequence to a byte sequence
            compressed_bytes = _to_bytes(compressed_text)
            fbout.write(compressed_bytes)



        text_widget.insert(tk.END, '\nHuffman encoded text written to the binary file ' + outfilename + ' Successfully!')



                
def open_file_decode(): 
    file = askopenfile(mode ='r', filetypes =[('Binary', '*.bin')])
    if file:
        # print(file.name)
        # clear text area
        text_widget.delete('1.0', tk.END)
        # Decoding: Read the binary file
        fbin = open(file.name, 'rb')
        encoded_bytes = fbin.read()
        fbin.close()

        if len(encoded_bytes) < 1:
            text_widget.insert(tk.END, 'Empty file. Exiting!')
            return


        # Decoding: first two bytes gives the code_block_offset
        a1 = encoded_bytes[0]
        a2 = encoded_bytes[1]
        code_block_offset = a1 * 256 + a2
        # The code block is stored from index 2 to code_block_offset+2
        code_block = encoded_bytes[2: code_block_offset+2].decode('utf-8')
        # print(code_block)

        #  Decoding: Remember the next byte is the offset value of the last byte
        # We split the encoded_bytes to get just the code sequence alone
        code_bytes = encoded_bytes[code_block_offset+2:]
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

        ## Get back the code_map from the code_block
        code_map = {}
        keys = code_block.split(':')[0]
        codes = code_block.split(':')[1]

        i = 0
        for code in codes.split(','):
            if len(code) > 0:
                code_map[code] = keys[i]
                i += 1

        # Decoding: Now decode the retireved binary sequence with the reverse code_map
        # This is a greedy algorithm
        def decoding(content, _lookup):
            while content:
                options = [i for i in _lookup if content.startswith(i) and (any(content[len(i):].startswith(b) for b in _lookup) or not content[len(i):])]
                if not options:
                    raise Exception("Decoding error")
                yield _lookup[options[0]]
                content = content[len(options[0]):]

        text_widget.insert(tk.END, 'The original text is: \n')

        text_widget.insert(tk.END, ''.join(decoding(encoded_text, code_map)))


button_frame = tk.Frame(root, height=100, width=600, borderwidth=1)
button_frame.pack()
btn1 = tk.Button(button_frame, text ='Encode File', command = open_file_encode) 
btn2 = tk.Button(button_frame, text ='Decode File', command = open_file_decode)

#btn1.pack(side = TOP, pady = 10) 
btn1.grid(row=0, column=0, padx=50, pady=10)
btn2.grid(row=0, column=1, padx=50, pady=10)

text_frame = tk.Frame(root, height=200, width=600, borderwidth = 2)
text_frame.pack()
text_widget = tk.Text(text_frame, height = 200, width = 600)
text_widget.pack()
text_widget.insert(tk.END, 'Welcome to Huffman Coding! Click Encode file to choose a (text) file to encode\nClick Decode file to choose a (binary) file to decode')
  
tk.mainloop() 
