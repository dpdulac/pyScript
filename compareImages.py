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

exrFilter = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'CompoImageSequence'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
        ]
        }

def findShots(taskname='compo_comp', seq=40, shot = 135):
    seqShot = 's'+str(seq).zfill(4)+'_p'+str(shot).zfill(4)
    print seqShot
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['task', 'name_is', taskname],
        ['entity.Shot.code', 'is', seqShot],
        #['entity.Shot.sg_status_artistique','is', 'cmpt'],
        #['entity.Shot.sg_status_artistique','contains','cmpt'],
        exrFilter,
    ]

    res = {}
    for v in sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_status_artistique', 'version_number', 'path', 'published_file_type', 'entity.Shot.sg_cut_in','entity.Shot.sg_cut_out','task','entity.Shot.sg_sequence'], order=[{'field_name':'version_number','direction':'desc'}]):

        entityName = v['entity']['name']
        if not entityName in res:
            res[entityName] = {}
            res[entityName]['cutIn'] = v['entity.Shot.sg_cut_in']
            res[entityName]['cutOut'] = v['entity.Shot.sg_cut_out']
            res[entityName]['framePath'] = v['path']['local_path_linux']
            res[entityName]['Task'] = v['task']['name']
            res[entityName]['version'] = v['version_number']
            res[entityName]['imgFormat'] = '.'+ v['path']['content_type'][v['path']['content_type'].find("/")+1:]
            res[entityName]['status']=v['entity.Shot.sg_status_list']

    return res

def findAprouved(taskname = 'compo_di',seq=40):
    seq = 's'+str(seq).zfill(4)
    filterTask = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['content', 'is', taskname],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.sg_sequence', 'name_is', seq],
        ['sg_status_artistique','is','cmpt']
        #['entity.Shot.code', 'in', res.keys()]
    ]
    res = {}
    for v in sg.find('Task', filterTask, ['code', 'entity', 'sg_status_artistique','entity.Shot.code','entity.Shot.version_number' 'version_name']):
        entityName = v['entity']['name']
        res[entityName] = {}
        try:
            res[entityName]['status'] = v['sg_status_artistique']
            res[entityName]['version'] = v['entity.Shot.version_name']
        except:
            res[entityName]['status'] = 'None'
           # res[entityName]['version'] = v['code']

    return res

def compareStereo(seqA = '', seqB = ''):

    matchStatus = '\x1b[0;32;40m match\x1b[0m'
    wrongStatus = "\x1b[0;31;40m doesn't match\x1b[0m"

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

def main():
    # print_format_table()
    pprint.pprint(findShots('compo_di'))
    #print findAprouved()
    seqA = "/s/prodanim/asterix2/sequences/s0040/s0040_p0135/compo_stereo/compo_stereo/publish/images/s0040_p0135-base-compo_stereo-v006/left/s0040_p0135-base-compo_stereo-left.%04d.exr"
    seqB = "/s/prodanim/asterix2/sequences/s0040/s0040_p0135/compo_di/compo_di/publish/images/s0040_p0135-base-compo_di-v001/left/s0040_p0135-base-compo_di-left.%04d.exr"
    #compareStereo(seqA,seqB)

if __name__ == '__main__':
    main()