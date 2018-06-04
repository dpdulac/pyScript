#!/usr/bin/env python
# coding:utf-8
""":mod: contactSheetTest - 2018.06
===================================

.. module:: contactSheetTest
  :platform: Unix
  :synopsis: module idea
     
.. moduleauthor:: duda 
  
"""
import nuke
from nukeCore.nodes import sequenceGroup
from sgtkLib import tkutil, tkm

_USER_ = os.environ['USER']
tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg


def findShotsInSequence(seq='s1300',dict=False):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['code','is',seq]
    ]
    res = {}
    seqShots =[]
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','shots']):
        if not 'Shots' in res:
            tmp = v['shots']
            for item in tmp:
                seqShots.append(item['name'])
            res['Shots'] = sorted(seqShots)
    if dict:
        return res
    else:
        return sorted(seqShots)

def createNukeFile(seq = 's0060'):
    sequenceGroupNode = sequenceGroup.create()
    sequenceGroupNode['sequence'].setValue('s0060')
    sequenceGroupNode['task'].setValue('ligth_precomp')
    sequenceGroupNode['outputMode'].setValue('contactSheet')
    sequenceGroupNode['Rebuild'].execute()
    # a.knob('Rebuild').execute()
    sequenceGroupNode['RowCol'].setValue([6, 5])
