# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 08:56:37 2020

@author: dewandaru@gmail.com
Parser for BIO format in FSM style.

"""

class BIO:
    def reset(self):
        self.state = "^"
    def begin(self):
        #print("begin (", self.w, ")")
        self.chunk = [self.w]
        self.begin_callback()
        
    def inside(self):
        #print("inside ()")
        self.chunk.append(self.w)
        
    def complete(self):
        #print("complete (", ' '.join(self.chunk),")")
        
        self.complete_callback()
        
    def __init__(self, begin_callback, complete_callback):
        self.begin_callback = begin_callback
        self.complete_callback = complete_callback
        self.functions = {} # dictionary for callback functions based on transition as index
        self.states = "^BIO$"
        self.transitions = [('^','B'), #1
                            ('^','O'), #2
                            ('B','I'), #3
                            ('B','O'), #4
                            ('I','$'), #5
                            ('O','$'), #6
                            ('I','O'), #7
                            ('B','B'), #8
                            ('B','$'), #9
                            ('O','B'), #10
                            ('I','B'), #11
                            ('I','I'), #12
                            ]
        self.state = '^'
        self.chunk = ''
        self.w = ''
        for t in self.transitions:
            self.functions[t] = []
            
        # transition callback for complete first
        self.attach(('I','O'), self.complete)
        self.attach(('I','B'), self.complete)
        self.attach(('I','$'), self.complete)
        
        self.attach(('B','B'), self.complete)
        self.attach(('B','O'), self.complete)        
        self.attach(('B','$'), self.complete)
        
        # transition callback for inside
        self.attach(('I','I'), self.inside)
        self.attach(('B','I'), self.inside)
        
         # transition callback for begin
        self.attach(('B','B'), self.begin)
        self.attach(('^','B'), self.begin)
        self.attach(('O','B'), self.begin)
        self.attach(('I','B'), self.begin)
        
    def next(self, w, nextstate):
        if nextstate in self.states:
            for n,t in enumerate(self.transitions):
                if t[0] == self.state and t[1] == nextstate:
                    #valid
                    self.w = w
                    self.state = nextstate
                    for f in self.functions[t]:
                        f()
                    return True
        return False
    
    def attach(self, transition, f):
        ''' only allows single function callback for each wanted transition '''
        self.functions[transition].append(f)
        
        
def b():
    return
def c():
    global bio
    #print (bio.chunk)
    return

bio = BIO(b,c)
bio.next("Bandung", "B")
bio.next("Jawa", "B")
bio.next("Barat", "I")
bio.next("", "$")
bio.reset()
bio.next("Surabaya", "B")
bio.next(",", "O")
bio.next("Jawa", "B")
bio.next("Timur", "I")
bio.next(".", "O")
bio.next("", "$")

