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

def createNukeFile(seq = 's0060',shName=True,outFile = '/tmp/tmp.tif',task = 'compo_comp'):
    nbShots = len(findShotsInSequence(seq,False))
    intNb = nbShots/5
    floatNb = nbShots/5.0
    if floatNb-intNb > 0:
        intNb += 1
    sequenceGroupNode = sequenceGroup.create()
    sequenceGroupNode['sequence'].setValue(seq)
    sequenceGroupNode['task'].setValue(task)
    sequenceGroupNode['outputMode'].setValue('contactSheet')
    sequenceGroupNode['Rebuild'].execute()
    # a.knob('Rebuild').execute()
    sequenceGroupNode['RowCol'].setValue([intNb, 5])
    sequenceGroupNode['Resolution'].setValue([5*2048,intNb*858])
    if shName:
        sequenceGroupNode['showName'].setValue(True)
    else:
        sequenceGroupNode['showName'].setValue(False)

    colorConvertNode = nuke.nodes.OCIOColorSpace(in_colorspace="linear", out_colorspace="Lut")
    colorConvertNode.setInput(0,sequenceGroupNode)

    writeNode = nuke.nodes.Write(name = seq + "WriteLutBurn", colorspace = "linear", file_type = "tiff",file =outFile)
    writeNode['datatype'].setValue('16 bit')
    writeNode['views'].setValue('left left')
    writeNode.setInput(0,colorConvertNode)
    nuke.execute(writeNode, 1, 1)

def main():
    createNukeFile(seq='s0060', shName=True, outFile='/tmp/tmp.tif', task='compo_comp')

if __name__ == '__main__':
    main()

