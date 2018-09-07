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
        ]
        }
compo_stereoFilter = {
    'filter_operator': 'all',
    'filters':[
        ['sg_task', 'name_is', 'compo_stereo'],
        ['sg_status_list', 'is', 'cmpt'],
    ]
}

compo_diFilter = {
    'filter_operator': 'all',
    'filters':[
        ['sg_task', 'name_is', 'compo_di'],
        ['sg_status_list', 'is', 'chk'],
    ]
}
def findShots( seq=40, shot = 135):
    seqShot = 's'+str(seq).zfill(4)+'_p'+str(shot).zfill(4)
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.code', 'is', seqShot],
        ['sg_task', 'name_is', 'compo_stereo'],
        ['sg_status_list', 'is', 'cmpt'],
    ]

    res = {}
    for v in sg.find('Version', filters,
                     ['code', 'entity', 'sg_tank_version_number', 'sg_path_to_frames', 'sg_first_frame'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        entityName = v['entity']['name']
        if not entityName in res:
            res['name'] = entityName
            res['framePathCOmpoStereo'] = v['sg_path_to_frames']
            tmpVersion = res['framePathCOmpoStereo'][res['framePathCOmpoStereo'].find('-v')+1:]
            res['version comp_stereo']= tmpVersion[:tmpVersion.find('/')]

    try:
        res['framePathCOmpoStereo']
    except:
        print("\x1b[0;31;40m"+'no shot for ' + seqShot + ' in compo_stereo marked as cmpt as been found'+"\x1b[0m")
        exit(0)


    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['task', 'name_is', 'compo_di'],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.code', 'is', seqShot],
        ['sg_tank_eye', 'is', 'left'],
        exrFilter,
    ]

    for v in sg.find('PublishedFile', filters,
                     ['code', 'entity', 'version_number', 'path', 'published_file_type', 'entity.Shot.sg_cut_in',
                      'entity.Shot.sg_cut_out', 'task', 'entity.Shot.sg_sequence'],
                     order=[{'field_name': 'version_number', 'direction': 'asc'}]):
        entityName = v['entity']['name']
        if entityName == res['name']:
            res['cutIn']= v['entity.Shot.sg_cut_in']
            res['cutOut'] = v['entity.Shot.sg_cut_out']
            res['framePathCompoDi'] = v['path']['local_path_linux']
            res['version comp_di'] = 'v'+str(v['version_number']).zfill(3)

    try:
        res['framePathCompoDi']
    except:
        print("\x1b[0;31;40m"+'no shot for '+ res['name'] + ' in compo_di marked as check as been found'+"\x1b[0m")
        exit(0)
    return res

# def findVersion(seq=40, shot = 135):
#     seqShot = 's'+str(seq).zfill(4)+'_p'+str(shot).zfill(4)
#     print seqShot
#     filters = [
#         ['project', 'is', {'type':'Project', 'id':project.id}],
#         ['entity', 'type_is', 'Shot'],
#         ['entity.Shot.code', 'is', seqShot],
#         ['sg_task', 'name_is', 'compo_stereo'],
#         ['sg_status_list', 'is', 'cmpt'],
#         #compo_stereoFilter,
#         #exrFilter,
#     ]
#
#     res = {}
#     for v in sg.find('Version', filters, ['code', 'entity', 'sg_status_list', 'sg_path_to_frames', 'sg_first_frame', 'sg_last_frame'], order=[{'field_name':'version_number','direction':'desc'}]):
#
#         print v['sg_path_to_frames'],v['sg_first_frame'], v['sg_last_frame'], v['sg_status_list']

def compareStereo(res={}):
    seqA = res['framePathCOmpoStereo']
    seqB = res['framePathCompoDi']
    cutIn = res['cutIn']
    cutOut = res['cutOut']

    matchStatus = '\x1b[0;32;40m match\x1b[0m'
    wrongStatus = "\x1b[0;31;40m doesn't match\x1b[0m"

    print '\n\n\n\x1b[0;32;40m---Starting comparison for shot '+ res['name']+' of '+res['version comp_stereo']+ ' compo_stereo to '+res['version comp_di']+ ' compo_di for frame '+ str(cutIn)+' to frame '+str(cutOut)+'---\x1b[0m'
    # print 'comparing version: '+ res['version comp_stereo'] + ' of compo_stereo to version ' +res['version comp_di'] + ' of compo_di'
    # print 'checking from frame: '+ str(cutIn) + ' to frame: ' + str(cutOut)

    for imNb in range(cutIn,cutOut+1):
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
    # get rid of extra channels in the di-matte image
    oiio.ImageBufAlgo.channels(bufB, oiio.ImageBuf(imgB), (0, 1, 2))

    comp = oiio.CompareResults()

    oiio.ImageBufAlgo.compare(oiio.ImageBuf(imgA), bufB, 1.0 / 255.0, 0.0, comp)

    if comp.nwarn == 0 and comp.nfail == 0:
        return True
    else:
        return False

def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "create a contactSheet for sequence")
    #shot argument
    parser.add_argument('sequences', type=str,nargs='*', help='seq number follow by shot number sequence and shot need to be separated by a space (i.e: 40 130)')
    args = parser.parse_args()
    seqShotNumber = args.sequences
    try:
        a = len(seqShotNumber) >2
    except:
        print('usage checkStereoToDi seq nb shot nd (i.e: checkStereoToDi 30 50')
        exit(0)


    return seqShotNumber

# def print_format_table():
#     """
#     prints table of formatted text format options
#     """
#     for style in range(9):
#         for fg in range(30,38):
#             s1 = ''
#             for bg in range(40,48):
#                 format = ';'.join([str(style), str(fg), str(bg)])
#                 s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
#             print(s1)
#         print('\n')

def main():
    # print_format_table()
    # findVersion(30,50)
    seqShot = get_args()
    res = findShots(seqShot[0],seqShot[1])
    #pprint.pprint(res)
    compareStereo(res)

if __name__ == '__main__':
    main()