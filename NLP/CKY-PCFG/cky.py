#!/usr/bin/env python
# coding: utf-8
import sys
if len(sys.argv) < 3:
    print("Correct Format: python cky.py grammar.txt test.txt")
    sys.exit(1)

# Read grammar file
with open(sys.argv[1]) as f:
    rules = f.read()

rules = rules.split('\n')

# split into A->BC and B->b parts
rules1 = []
rules2 = []
for rule in rules:
    a,b = rule.split("->") # A->B C prob
    k = b.strip().split(" ")
    if len(k) == 3:
        rules1.append(rule)
    else:
        rules2.append(rule)


NT = [] # Non Terminals
for rule in rules1:
    a,b = rule.split("->") # a->c d
    a = a.strip() # remove extra spaces
    b = b.strip() # remove extra spaces
    c,d,p = b.split(" ")
    c = c.strip() # remove extra spaces
    d = d.strip() # remove extra spaces
    p = float(p.strip()) # probability of the rule
    # print(a,c,d)
    if a not in NT:
        NT.append(a)
    if c not in NT:
        NT.append(c)
    if d not in NT:
        NT.append(d)
    
# NT = ["S", "NP", "VP", "D", "N", "PP", "V"]

# Create a mapping from Non Terminals to index as well
NT_dict = {}
for i, a in enumerate(NT):
    NT_dict[a] = i

# Grammar G has three columns: S -> NP VP 
G1 = []
for rule in rules1:
    a,b = rule.split("->") # a->c d
    a = a.strip() # remove extra spaces
    b = b.strip() # remove extra spaces
    c,d,p = b.split(" ")
    c = c.strip() # remove extra spaces
    d = d.strip() # remove extra spaces
    p = float(p.strip()) # probability value 
    G1.append([NT_dict.get(a), NT_dict.get(c), NT_dict.get(d), p])


T = [] # Terminals
for rule in rules2:
    a,b = rule.split("->") # a->c d
    a = a.strip() # remove extra spaces
    b = b.strip() # remove extra spaces
    t,p = b.split(" ")
    t = t.strip() # remove extra spaces
    p = float(p.strip()) # probability of the rule

    if t not in T:
        T.append(t)
    
# Create a mapping from Terminals (strings) to index as well
T_dict = {}
for i, t in enumerate(T):
    T_dict[t] = i

# Grammar G2 has two columns in RHS: N -> car 0.8 
G2 = []
for rule in rules2:
    a,b = rule.split("->") # a->c d
    a = a.strip() # remove extra spaces
    b = b.strip() # remove extra spaces
    t,p = b.split(" ")
    t = t.strip() # remove extra spaces
    p = float(p.strip()) # probability value 
    G2.append([NT_dict.get(a), T_dict.get(t), p])


# function to print final tree
def tree(begin, end, nt, depth):
    # get the rule from back-trace
    b = back[begin][end][nt]
    if len(b) == 1:
        # reached a terminal symbol
        print(T[b[0]] + ")")
        return True
    
    A = NT[b[1]]
    B = NT[b[2]]
    print("(" + A + " ", end='')
    r = tree(begin, b[0], b[1], depth+1)
    if r:
        print(' '*depth, end='')
    
    print("(" + B + " ", end='')
    r = tree(b[0], end, b[2], depth+1)
    if r:
        print(' '*depth, end='')
    return False


# Open Test file
with open(sys.argv[2]) as f:
    sentences = f.read()

sentences = sentences.split("\n")

for sentence in sentences:
    print(sentence)
    # sentence = "this flight serves a cake with the airport"
    words = sentence.split(" ")
    n_words = len(words)
    n_words


    # Initialize score matrix and back pointer matrix
    score = [[[0 for k in range(len(NT))] for j in range(n_words+1)] for i in range(n_words+1)]
    back = [[[0 for k in range(len(NT))] for j in range(n_words+1)] for i in range(n_words+1)]


    # lexicon (terminal) part of CKY algorithm
    i = 0
    for word in words:
        w = T_dict.get(word)
        for g in G2:
            if g[1] == w:
                score[i][i+1][g[0]] = g[2]
                back[i][i+1][g[0]] = (w,)
        i += 1


    # Non Terminal part of CKY algorithm
    for span in range(2, n_words+1):
        for begin in range(n_words-span+1):
            end = begin + span
            for split in range(begin+1, end):
                for g in G1:
                    prob = score[begin][split][g[1]] * score[split][end][g[2]] * g[3]
                    if prob > score[begin][end][g[0]]:
                        score[begin][end][g[0]] = prob
                        back[begin][end][g[0]] = (split, g[1], g[2])
            


    # Check validity of the input string
    if score[0][n_words][0] > 0:
        print("The input string is valid according to the grammar")
        # print the maximum probable tree
        tree(0, n_words, 0, 0)
        print("\nMaximum probability value = " + str(score[0][n_words][0]) + "\n\n")
    else:
        print("The input string is NOT valid according to the grammar\n\n")



