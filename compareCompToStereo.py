#!/usr/bin/env python
# coding:utf-8
""":mod: compareCompToStereo --- Module Title
=================================

   2018.09
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
"""
    Compare the technical aprouved compo_comp shot to the technical aprouved compo_stereo shot (only left eye)
    
"""


import OpenImageIO as oiio
import os, pprint, errno, argparse, sys
from sgtkLib import tkutil, tkm

_USER_ = os.environ['USER']
_OUTPATH_ ='/s/prodanim/asterix2/_sandbox/' + _USER_ +"/contactSheet"
_FONT_ = 'LiberationSans-Italic'

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

def findShots( seq=40, shot = 135):
    # format the input
    seqShot = 's'+str(seq).zfill(4)+'_p'+str(shot).zfill(4)

    # filter forcompo_comp
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.code', 'is', seqShot],
        ['sg_task', 'name_is', 'compo_comp'],
        ['sg_status_list', 'is', 'cmpt'],
    ]

    res = {}
    for v in sg.find('Version', filters,
                     ['code', 'entity', 'sg_tank_version_number', 'sg_path_to_frames', 'sg_first_frame'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        entityName = v['entity']['name']
        if not entityName in res:
            res['name'] = entityName
            res['framePathCOmpoComp'] = v['sg_path_to_frames']
            tmpVersion = res['framePathCOmpoStereo'][res['framePathCOmpoStereo'].find('-v')+1:]
            res['version comp_stereo']= tmpVersion[:tmpVersion.find('/')]

    try:
        res['framePathCOmpoComp']
    except:
        print("\x1b[0;31;40m"+'no shot for ' + seqShot + ' in compo_stereo marked as cmpt as been found'+"\x1b[0m")
        exit(0)

    # filter for compo_stereo
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.code', 'is', seqShot],
        ['sg_task', 'name_is', 'compo_stereo'],
        ['sg_status_list', 'is', 'cmpt'],
    ]
    for v in sg.find('Version', filters,
                     ['code', 'entity', 'sg_tank_version_number', 'sg_path_to_frames', 'sg_first_frame'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        entityName = v['entity']['name']
        if entityName in res:
            res['framePathCOmpoStereo'] = v['sg_path_to_frames']

    try:
        res['framePathCOmpoStereo']
    except:
        print("\x1b[0;31;40m"+'no shot for ' + seqShot + ' in compo_stereo marked as cmpt as been found'+"\x1b[0m")
        exit(0)

def main():
    pprint.pprint(findShots())

if __name__ == '__main__':
    main()