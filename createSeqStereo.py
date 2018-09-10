#!/usr/bin/env python
# coding:utf-8
""":mod: createSeqStereo --- Module Title
=================================

   2018.09
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys,os,pprint
from sgtkLib import tkutil, tkm

_USER_ = os.environ['USER']
tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

def findShots( seq='s0040'):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity', 'type_is', 'Shot'],
        #['entity.Shot.code', 'is', seqShot],
        ['entity.Shot.sg_sequence', 'name_is', seq],
        ['sg_task', 'name_is', 'compo_stereo'],
        ['sg_status_list', 'is', 'cmpt'],
    ]

    res = {}
    for v in sg.find('Version', filters,['code', 'entity', 'sg_path_to_movie', 'sg_first_frame', 'entity.Shot.sg_cut_order'],order=[{'field_name':'version_number','direction':'desc'}]):
        #print v
        entityName = v['entity']['name']
        if not entityName in res:
            res[entityName]={}
            res[entityName]['name'] = entityName
            res[entityName]['framePathCompoStereoLeft'] = v['sg_path_to_movie']
            res[entityName]['cutOrder'] = v['entity.Shot.sg_cut_order']
            res[entityName]['framePathCompoStereoRight']= res[entityName]['framePathCompoStereoLeft'].replace('-left-','-right-')
            tmpVersion = res[entityName]['framePathCompoStereoLeft'][res[entityName]['framePathCompoStereoLeft'].find('-v')+1:]
            res[entityName]['version comp_stereo']= tmpVersion[:tmpVersion.find('-')]

    return res

def getOrder(res = {}):
    shotNb = []
    for key in res.keys():
        shotNb.append(key)
    for j in range(len(shotNb)):
    #initially swapped is false
        swapped = False
        i = 0
        while i<len(res)-1:
        #comparing the adjacent elements
            if res[shotNb[i]]['cutOrder']>res[shotNb[i+1]]['cutOrder']:
                #swapping
                shotNb[i],shotNb[i+1] = shotNb[i+1],shotNb[i]
                #Changing the value of swapped
                swapped = True
            i = i+1
    #if swapped is false then the list is sorted
    #we can stop the loop
        if swapped == False:
            break
    return shotNb

def main():
    leftMov = '/tmp/outputLeft.mkv'
    rightMov = '/tmp/outputRight.mkv'
    stereoMov = '/tmp/outputStereo.mkv'
    res = findShots()
    listShotOrdered = getOrder(res)
    fileLeftMov = '/tmp/leftMovTx.tx'
    fileRightMov = '/tmp/rightMovTx.tx'
    fileTx = open(fileLeftMov, "w")
    fileTy = open(fileRightMov, "w")
    for shot in listShotOrdered:
        #os.system('cp '+res[shot]['framePathCompoStereoLeft'] +' /s/prodanim/asterix2/_sandbox/duda/tmp/')
        fileTx.write("file '" + res[shot]['framePathCompoStereoLeft'] + "'\n")
        fileTy.write("file '" + res[shot]['framePathCompoStereoRight'] + "'\n")
    fileTx.close()
    fileTy.close()
    os.system("ffmpeg -loglevel error -f concat -safe 0 -r '24' -i "+ fileLeftMov+' -y -c copy -map_metadata 0 /tmp/outputLeft.mkv')
    os.system("ffmpeg -loglevel error -f concat -safe 0 -r '24' -i " + fileRightMov + ' -y -c copy -map_metadata 0 /tmp/outputRight.mkv')
    commandLine = 'ffmpeg -loglevel error -i ' + leftMov + ' -i ' + rightMov + " -codec:v copy -codec:a copy -map 0:v -map 1:v -map 0:a -metadata stereo_mode=left_right -aspect 3.555 -y " + stereoMov
    os.system(commandLine)

    pprint.pprint(findShots())

if __name__ == '__main__':
    main()