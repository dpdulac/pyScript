#!/usr/bin/env python
# coding:utf-8
""":mod: diMatteContactSheet --- Module Title
=================================

   2018.10
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
from sgtkLib import tkutil, tkm
import os, pprint, errno, argparse, sys, math,subprocess
import OpenImageIO as oiio

_USER_ = os.environ['USER']
_OUTPATH_ ='/s/prodanim/asterix2/_sandbox/' + _USER_ +"/contactSheet"
_FONT_ = 'LiberationSans-Italic'

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

def findShots( seq=40, shot = 135,status ='chk'):
    # format the input
    seqShot = 's'+str(seq).zfill(4)+'_p'+str(shot).zfill(4)

    # filter forcompo_comp
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.code', 'is', seqShot],
        ['sg_task', 'name_is', 'compo_di'],
        ['sg_status_list', 'is', 'cmpt'],
    ]

    res = {}
    for v in sg.find('Version', filters,
                     ['code', 'entity', 'sg_tank_version_number', 'sg_path_to_frames','entity.Shot.sg_cut_in', 'entity.Shot.sg_cut_out'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        entityName = v['entity']['name']
        if not entityName in res:
            res['name'] = entityName
            res['framePathCompoComp'] = v['sg_path_to_frames']
            res['cutIn'] = v['entity.Shot.sg_cut_in']
            res['cutOut'] = v['entity.Shot.sg_cut_out']
            tmpVersion = res['framePathCompoComp'][res['framePathCompoComp'].find('-v')+1:]
            res['version compo_comp']= tmpVersion[:tmpVersion.find('/')]

    return res

def createContact(res={}):
    framePath = res['framePathCompoComp']
    cutIn = res['cutIn']
    cutOut = res['cutOut']
    for frameNb in range(cutIn,cutOut+1):
        frameNbStr = str(frameNb).zfill(4)
        framePathNb = framePath.replace('%04d',frameNbStr)
        print framePathNb
        frameIn = oiio.ImageBuf(framePathNb)
        print frameIn.spec().nchannels
        frameOut  = oiio.ImageBuf()
        # get rid of extra channels in the di-matte image
        oiio.ImageBufAlgo.channels(frameOut , frameIn, (5, 6, 7))
        frameOut.write('/tmp/diTmp/testdi.'+frameNbStr+'.jpg')


def main():
    res = findShots(10,10)
    createContact(res)

if __name__ == '__main__':
    main()