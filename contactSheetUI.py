#!/usr/bin/env python
# coding:utf-8
""":mod: contactSheetUI --- Module Title
=================================

   2018.06
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
import nuke
from nukeCore.nodes import sequenceGroup
from sgtkLib import tkutil, tkm
from PyQt4.QtGui import *
from PyQt4.QtCore import *

_USER_ = os.environ['USER']
_OUTIMAGEPATH_ = '/s/prodanim/asterix2/_sandbox/'+_USER_
tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

def findAllSequence(all = False):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
    ]
    res = {}
    seqShots =[]
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','code','description']):
        seq = v['code']
        if all:
            if not seq in res:
                res[seq] = {}
            res[seq]['description'] = v['description']
        else:
            if int(seq[seq.find('s')+1:]) <9000:
                if not seq in res:
                    res[seq] = {}
                if v['description'] != None:
                    res[seq]['description'] = v['description']
                else:
                    res[seq]['description'] = 'None'
            else:
                print 'donuts for: ' + seq
    return res

def main():
    print findAllSequence()

if __name__ == '__main__':
    main()