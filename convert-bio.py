# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 20:42:48 2020

@author: Agung
"""


with open('train-test-v11/training.txt') as f:
    lines = f.readlines()
    newlines = []
    i = 1
    for l in lines:
        if ('/' in l):
            try:
                w = l.split('/')[3]
            except:
                print("line", i, l)
                continue
        else:
            newlines.append(l)
        i += 1