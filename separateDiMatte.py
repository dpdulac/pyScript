#!/usr/bin/env python
# coding:utf-8
""":mod: separateDiMatte --- Module Title
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

    # filter for compo_di
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
            res['framePathCompoCompLeft'] = v['sg_path_to_frames']
            res['cutIn'] = v['entity.Shot.sg_cut_in']
            res['cutOut'] = v['entity.Shot.sg_cut_out']
            tmpVersion = res['framePathCompoCompLeft'][res['framePathCompoCompLeft'].find('-v')+1:]
            res['version compo_comp']= tmpVersion[:tmpVersion.find('/')]
            res['framePathCompoCompRight'] = res['framePathCompoCompLeft'].replace('left','right')

    return res

def extractLayer(res={},path = '/tmp'):
    framePathRight = res['framePathCompoCompRight']
    framePathLeft = res['framePathCompoCompLeft']
    cutIn = res['cutIn']
    cutOut = res['cutOut']
    shotName = res['name']

    # path to output the layers
    shotPath = path + '/' + shotName
    shotPathRight = shotPath+'/right'
    shotPathLeft = shotPath+ '/left'

    # dictionary for the channels
    channelDict = {'d0': (0, 1, 2, 3), 'd1': (4, 5, 6, 7), 'd2': (8, 9, 10, 11), 'd3': (12, 13, 14, 15), 'd4': (16, 17, 18, 19),
                   'd5': (20, 21, 22, 23), 'd6': (24, 25, 26, 27)}

    for frameNb in range(cutIn, cutOut + 1):
        frameNbStr = str(frameNb).zfill(4)
        # replace the frame nb for the left and right images
        framePathNbLeft = framePathLeft.replace('%04d', frameNbStr)
        framePathNbRight = framePathRight.replace('%04d', frameNbStr)
        # open the left and right image
        frameInLeft = oiio.ImageBuf(framePathNbLeft)
        frameInRight = oiio.ImageBuf(framePathNbRight)
        writeLayers(frameInLeft,frameNb,shotPathLeft,channelDict)
        writeLayers(framePathNbRight, frameNb, shotPathRight, channelDict)

def writeLayers(img = oiio.ImageBuf(),frameNb='0101',path='/tmp',channelDict = {}):
    for key in sorted(channelDict.keys()):
        frameTmp = oiio.ImageBuf(img.spec())
        oiio.ImageBufAlgo.channels(frameTmp, img, channelDict[key])
        # create the path for the image and set it to be 8bit (suffisant for matte)
        shotPathLayer = path + '/'+key+'/'+key+'.'+frameNb+'.tif'
        frameTmp.set_write_format(oiio.UINT8)
        # if it's the primary set the path and the output to be exr half float
        if key == 'd0':
            frameTmp.set_write_format(oiio.HALF)
            shotPathLayer = path + '/primary/primary.'+frameNb+'.exr'
        # create the output path if it doesn't exist
        if not os.path.isdir(shotPathLayer):
            os.makedirs(shotPathLayer)
        print 'writing: '+ shotPathLayer
        frameTmp.write(shotPathLayer)

def main():
    res = findShots(430,60)
    extractLayer(res)

if __name__ == '__main__':
    main()