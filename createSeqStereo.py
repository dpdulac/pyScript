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

def main():
    pprint.pprint(findShots())

if __name__ == '__main__':
    main()