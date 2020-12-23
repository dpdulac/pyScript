#!/usr/bin/env python
# coding:utf-8
""":mod: sgTest.py
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2020.12
   
"""
from sgtkLib import tkutil, tkm
import sys, os

_USER_ = os.environ['USER']
_OUTPATH_ ='/s/prodanim/asterix2/_sandbox/' + _USER_ +"/contactSheet"
_FONT_ = 'LiberationSans-Italic'

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

def findAllSequence(all = False):

    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
    ]
    seqShots =[]
    desc = []
    res = {}
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','code','description']):
        seq = v['code']
        des = v['description']
        if all:
            if not seq in seqShots:
                res[seq] = des
        else:
            if int(seq[seq.find('s')+1:]) <9000:
                if not seq in seqShots:
                    res[seq] = des
            else:
                print  seq + ' will not be included'
    #seqShots=sorted(seqShots)
    # res = {}
    # for i in range(len(seqShots)):
    #     res[seqShots[i]] = desc[i]
    for item in sorted(res.keys()):
        print item,res[item]

    return res

print findAllSequence()