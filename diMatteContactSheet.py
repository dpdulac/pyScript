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

def createContact(res={},small = True):
    framePathRight = res['framePathCompoCompRight']
    framePathLeft = res['framePathCompoCompLeft']
    cutIn = res['cutIn']
    cutOut = res['cutOut']
    shotName = res['name']

    # set the size of the master buffer
    masterWidth = 2096
    masterHeight = 860

    # if the vignette are full frame
    if not small:
        masterWidth = masterWidth * 4
        masterHeight = masterHeight * 4

    # vignette size
    vignetteWidth = masterWidth/4
    vignetteHeight = masterHeight/4


    # masterbuffer size is 2096x860
    masterBufSpec = oiio.ImageSpec(masterWidth, masterHeight, 3, oiio.HALF)

    vignetteSpec =oiio.ImageSpec(vignetteWidth,vignetteHeight,3,oiio.HALF)

    # size of each vignette
    roi = oiio.ROI(0,vignetteWidth,0,vignetteHeight)

    # dictionary for the channels
    channelDict = {'d0':(0,1,2),'d1':(4,5,6),'d2':(8,9,10),'d3':(12,13,14),'d4':(16,17,18),'d5':(20,21,22),'d6':(24,25,26)}

    # create a jpg file made of vignettes
    for frameNb in range(cutIn,cutOut+1):
        # position of the vignette in the final image
        xPos = 0
        yPos = 0
        # set the size of masterbuff
        masterBuf = oiio.ImageBuf(masterBufSpec)
        oiio.ImageBufAlgo.fill(masterBuf,(0,0,0))
        # convert int to padded str
        frameNbStr = str(frameNb).zfill(4)
        # replace the frame nb for the left and right images
        framePathNbLeft = framePathLeft.replace('%04d',frameNbStr)
        framePathNbRight = framePathRight.replace('%04d',frameNbStr)
        print 'Malaxing frame: '+str(frameNb)
        frameInLeft = oiio.ImageBuf(framePathNbLeft)
        frameInRight = oiio.ImageBuf(framePathNbRight)
        # get rid of extra channels in the di-matte image
        for key in sorted(channelDict.keys()):
            #create 2 tmp buffer for extracting the channels and scalind down the image
            frameTmp = oiio.ImageBuf(vignetteSpec)
            scaleIn = oiio.ImageBuf(vignetteSpec)
            # extract the channel from the image
            oiio.ImageBufAlgo.channels(frameTmp , frameInLeft, channelDict[key])
            # if it's the beauty pass (i.e d0) color convert so it's accurate when in jpg
            if key == 'd0':
                oiio.ImageBufAlgo.colorconvert(frameTmp, frameTmp, 'linear', 'Asterix2_Film')
            # scale down the image
            oiio.ImageBufAlgo.resample(scaleIn,frameTmp,True,roi)
            # paste the vignette onto the masterbuffer
            oiio.ImageBufAlgo.paste(masterBuf, xPos, yPos, 0, 0, scaleIn)
            # increment the pos
            xPos = xPos + vignetteWidth
            # redo the above step but for the right image
            oiio.ImageBufAlgo.channels(frameTmp, frameInRight, channelDict[key])
            if key == 'd0':
                oiio.ImageBufAlgo.colorconvert(frameTmp, frameTmp, 'linear', 'Asterix2_Film')
            oiio.ImageBufAlgo.resample(scaleIn, frameTmp, True, roi)
            oiio.ImageBufAlgo.paste(masterBuf, xPos, yPos, 0, 0, scaleIn)
            # advance xPos and yPos
            xPos = xPos + vignetteWidth
            if xPos >= masterWidth:
                yPos = yPos+vignetteHeight
                xPos = 0


        # write the image
        path = '/tmp/diTmp/'
        if not os.path.isdir(path):
            os.makedirs(path)
        masterBuf.write(path+'testdi.'+frameNbStr+'.jpg')
        # clean the masterbuffer
        masterBuf.reset(masterBufSpec)


def main():
    res = findShots(430,60)
    createContact(res,False)

if __name__ == '__main__':
    main()