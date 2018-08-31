#!/usr/bin/env python
# coding:utf-8
""":mod: compareImages --- Module Title
=================================

   2018.08
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
import OpenImageIO as oiio
import os, pprint, errno, argparse, sys
from sgtkLib import tkutil, tkm

_USER_ = os.environ['USER']
_OUTPATH_ ='/s/prodanim/asterix2/_sandbox/' + _USER_ +"/contactSheet"
_FONT_ = 'LiberationSans-Italic'

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg



def main():
    seqA = "/s/prodanim/asterix2/sequences/s0040/s0040_p0135/compo_stereo/compo_stereo/publish/images/s0040_p0135-base-compo_stereo-v006/left/s0040_p0135-base-compo_stereo-left.%04d.exr"
    seqB = "/s/prodanim/asterix2/sequences/s0040/s0040_p0135/compo_di/compo_di/publish/images/s0040_p0135-base-compo_di-v001/left/s0040_p0135-base-compo_di-left.%04d.exr"
    # imgC = "/s/prodanim/asterix2/sequences/s0040/s0040_p0135/compo/compo_comp/publish/images/s0040_p0135-base-compo_comp-v013/left/s0040_p0135-base-compo_comp-left.0101.exr"
    listBadFrame = []
    matchStatus = '\x1b[0;32;40m match\x1b[0m'
    wrongStatus = "\x1b[0;31;40m doesn't match\x1b[0m"
    # print_format_table()
    for imNb in range(101,260+1):
        imLeft = False
        imRight = False
        imLestStatus = ''
        imRightStatus =''
        frameNb = str(imNb).zfill(4)
        imgA = seqA.replace('%04d',frameNb)
        imgB= seqB.replace('%04d', frameNb)
        imgARight = imgA.replace('left','right')
        imgBRight =imgB.replace('left','right')
        imLeft = doCompare(imgA,imgB)
        imRight = doCompare(imgARight,imgBRight)
        if imLeft:
            imLestStatus = matchStatus
        else:
            imLestStatus = wrongStatus
        if imRight:
            imRightStatus = matchStatus
        else:
            imRightStatus = wrongStatus

        print('for frame nb '+frameNb+ ' the left images'+ imLestStatus+', the right images '+imRightStatus)
#     bufB = oiio.ImageBuf()
#     oiio.ImageBufAlgo.channels(bufB,oiio.ImageBuf(imgB),(0,1,2))
#
#     comp = oiio.CompareResults()
#
#     oiio.ImageBufAlgo.compare(oiio.ImageBuf(imgA), bufB,1.0/255.0,0.0,comp)
#
#     if comp.nwarn == 0 and comp.nfail == 0:
#         print imgA.replace('left','right')
#         print "good for image nb: "+frameNb
#     else:
#         listBadFrame.append(frameNb)
#
# print listBadFrame

def doCompare(imgA='',imgB=''):
    bufB = oiio.ImageBuf()
    oiio.ImageBufAlgo.channels(bufB, oiio.ImageBuf(imgB), (0, 1, 2))

    comp = oiio.CompareResults()

    oiio.ImageBufAlgo.compare(oiio.ImageBuf(imgA), bufB, 1.0 / 255.0, 0.0, comp)

    if comp.nwarn == 0 and comp.nfail == 0:
        return True
    else:
        return False

def print_format_table():
    """
    prints table of formatted text format options
    """
    for style in range(9):
        for fg in range(30,38):
            s1 = ''
            for bg in range(40,48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
            print(s1)
        print('\n')

if __name__ == '__main__':
    main()