#!/usr/bin/env python
# coding:utf-8
""":mod:`camForNuke` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2016, Mikros Image"

from sgApi.sgApi import SgApi
from sgtkLib import tkutil, tkm
import os, pprint

_USER_ = os.environ['USER']

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg
sgA = SgApi(sgw=sgw, tk=tk, project=project)



def findShotsWithMattePainting( seq='s1300', shotList=[]):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'in',shotList],
        ['entity.Shot.tag_list', 'name_contains', 'mattepainting'],
    ]

    listShot = []
    for v in sg.find('PublishedFile', filters, ['code', 'entity','tag_list'], order=[{'field_name':'created_at','direction':'desc'}]):
        entityName = v['entity']['name']
        if not entityName in listShot:
            listShot.append(entityName)
    return listShot

#get all the shot from the sequence
def findShotsInSequence(seq='1300'):
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
    return sorted(seqShots)

def findCameraPath(seq='1300',all = True):
    shotInSeq = findShotsInSequence(seq=seq)
    if all:
        shotFound=shotInSeq
    else:
        shotFound = findShotsWithMattePainting( seq=seq, shotList=shotInSeq)
    res = {}
    for shot in shotFound:
        try:
            camPath = sgA.getLastCamera(shot, taskPriority=['dwa_camera']).getPath()
        except AttributeError:
            print "no cam for: " + shot
        else:
            if not shot in res:
                res[shot] = camPath
    return res



def createCam(seq='s4650',all=True):
    import nuke
    rootNuke = nuke.root()
    rootNuke['format'].setValue( 'Captain Stereo Full' )
    rootNuke['first_frame'].setValue(101)
    rootNuke['last_frame'].setValue(500)
    Xpos, Ypos = 0,0
    input = 1
    scene = nuke.nodes.Scene(name = "Scene: "+seq)
    cams = findCameraPath(seq=seq,all=all)
    for key in sorted(cams.keys()):
        cam = nuke.nodes.Camera2(name="CAM_"+key,read_from_file=True, file = cams[key])#,display = 'off')
        cam.setXYpos(Xpos, Ypos)
        input += 1
        Xpos += 125
        scene.setInput(input,cam)
    scene.setXYpos(Xpos/2, Ypos +300)





# def main():
#
#     pprint.pprint(findMattePaintingCameraPath(seq='s0800'))
#
# if __name__ == '__main__':
#     main()