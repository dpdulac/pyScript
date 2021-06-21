#!/usr/bin/env python
# coding:utf-8
""":mod: createSeqStereo --- Module Title
=================================

   2018.09
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *
# from PyQt5.QtWidgets import *
import sys, os, pprint, argparse, datetime
from sgtkLib import tkutil, tkm

_USER_ = os.environ['USER']
_OUTPATH_ = '/s/prodanim/ta/_sandbox/'+ _USER_+'/'
tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

""" 
    find all the sequences in the project
    @ all use all the sequence otherwise use only sequence under 9000
    
"""
# animMain images filter
layoutFilter= {
    'filter_operator': 'any',
    'filters': [
        ['published_file_type', 'name_is', 'PlayblastMovie'],
    ]
}

def findAllSequence(all=False):
    from sgtkLib import tkutil, tkm
    tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
    sg = sgw._sg

    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
    ]
    seqShots = []
    # get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence', filters, ['entity', 'code', 'description']):
        seq = v['code']
        if all:
            if not seq in seqShots:
                seqShots.append(seq)
        else:
            if int(seq[seq.find('s') + 1:]) < 9000:
                if not seq in seqShots:
                    seqShots.append(seq)
            else:
                print  seq + ' will not be included'
    seqShots = sorted(seqShots)
    return seqShots


def findShots(seq=40, task='compo_stereo'):
    seqString = str(seq).zfill(4)
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity', 'type_is', 'Shot'],
        # ['entity.Shot.code', 'is', seqShot],
        ['entity.Shot.sg_sequence', 'name_is', seqString],
        ['entity.Shot.sg_status_list', 'is_not', 'omt'],
        ['task', 'name_is', task],
        layoutFilter
    ]

    res = {}
    for v in sg.find('PublishedFile', filters,
                     ['code', 'entity', 'path', 'version_number','sg_first_frame', 'entity.Shot.sg_cut_order'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        #print v
        entityName = v['entity']['name']
        if not entityName in res:
            res[entityName] = {}
            res[entityName]['name'] = entityName
            res[entityName]['framePathCompoStereoLeft'] = v['path']['local_path']
            res[entityName]['framePathCompoStereoRight'] = res[entityName]['framePathCompoStereoLeft'].replace(
                '-left', '-right')
            res[entityName]['cutOrder'] = v['entity.Shot.sg_cut_order']
            if task == 'compo_stereo':
                res[entityName]['framePathCompoStereoRight'] = res[entityName]['framePathCompoStereoLeft'].replace(
                    '-left-', '-right-')
                tmpVersion = res[entityName]['framePathCompoStereoLeft'][
                             res[entityName]['framePathCompoStereoLeft'].find('-v') + 1:]
                res[entityName]['version comp_stereo'] = tmpVersion[:tmpVersion.find('-')]

    return res


def getOrder(res={}):
    shotNb = []
    for key in res.keys():
        shotNb.append(key)
    for j in range(len(shotNb)):
        # initially swapped is false
        swapped = False
        i = 0
        while i < len(res) - 1:
            # comparing the adjacent elements
            if res[shotNb[i]]['cutOrder'] > res[shotNb[i + 1]]['cutOrder']:
                # swapping
                shotNb[i], shotNb[i + 1] = shotNb[i + 1], shotNb[i]
                # Changing the value of swapped
                swapped = True
            i = i + 1
        # if swapped is false then the list is sorted
        # we can stop the loop
        if swapped == False:
            break
    return shotNb


def createMovie(seq='300', doStereo=True, outPath='/tmp', task='final_layout'):
    today = datetime.datetime.today()
    if doStereo:
        if outPath == 'None':
            # checking the output dir
            path = _OUTPATH_ + 'stereoMov/' + str(seq).zfill(4) + '/'
            if not os.path.isdir(path):
                os.makedirs(path)
        else:
            if outPath.endswith('/'):
                path = outPath
            else:
                path = outPath + '/'
        # create a tmp path to put left tmp movie
        leftTmpPath = '/tmp/' + str(seq) + '/left/'
        if not os.path.isdir(leftTmpPath):
            os.makedirs(leftTmpPath)
        # create a tmp path to put right tmp movie
        rightTmpPath = '/tmp/' + str(seq) + '/right/'
        if not os.path.isdir(rightTmpPath):
            os.makedirs(rightTmpPath)
        # get the shot from sequence
        res = findShots(seq, task=task)
        listShotOrdered = getOrder(res)
        leftMov = path + 'seq_' + str(seq).zfill(4) + '_' + task + '_' + str(today. year) + str(today.month).zfill(2) + str(today.day).zfill(2) + '_left' + '.mov'
        rightMov = path + 'seq_' + str(seq).zfill(4) + '_' + task + '_' + str(today. year) + str(today.month).zfill(2) + str(today.day).zfill(2) + '_right' + '.mov'
        # temp file for the tx
        fileLeftMov = '/tmp/leftMovTx.tx'
        fileRightMov = '/tmp/rightMovTx.tx'
        # open the file
        fileTx = open(fileLeftMov, "w")
        fileTy = open(fileRightMov, "w")

        nbClip = 0;
        frameConvert = "{0:.2f}".format(3 / 24.0)
        for shot in listShotOrdered:
            print 'preparing: ' + shot
            fileLeftOut = leftTmpPath + 'left.' + str(nbClip) + '.mov'
            fileRightOut = rightTmpPath + 'right' + str(nbClip) + '.mov'
            # os.system('ffmpeg -loglevel error -r 24 -ss ' + frameConvert + ' -i ' + res[shot]['framePathCompoStereoLeft'] + ' -y -c:v copy -an -map_metadata 0 ' + fileLeftOut)
            os.system('ffmpeg -loglevel error -r 24 -ss ' + frameConvert + ' -i ' + res[shot]['framePathCompoStereoLeft'] + ' -itsoffset ' + frameConvert + ' -i ' + res[shot]['framePathCompoStereoLeft'] + ' -c copy -map 0:v -map 1:a ' + fileLeftOut)
            os.system('ffmpeg -loglevel error -r 24 -ss ' + frameConvert + ' -i ' + res[shot]['framePathCompoStereoRight'] + ' -y -c:v copy -an -map_metadata 0 ' + fileRightOut)
            fileTx.write("file '" + fileLeftOut + "'\n")
            fileTy.write("file '" + fileRightOut + "'\n")
            nbClip += 1
        fileTx.close()
        fileTy.close()
        print 'outputing the movie for left and right eyes: \n' + leftMov + '\n' + rightMov
        os.system(
            "ffmpeg -loglevel error -f concat -safe 0 -r '24' -i " + fileLeftMov + ' -y -c:v copy -c:a copy -map_metadata 0 ' + leftMov)
        os.system(
            "ffmpeg -loglevel error -f concat -safe 0 -r '24' -i " + fileRightMov + ' -y -c:v copy -c:a copy -map_metadata 0 ' + rightMov)

        # remove the unnescesary files
        os.system('rm -rfd ' + leftTmpPath)
        os.system('rm -rfd ' + rightTmpPath)
        os.remove(fileLeftMov)
        os.remove(fileRightMov)
        print('done')

    else:
        res = findShots(seq, task=task)
        listShotOrdered = getOrder(res)
        fileLeftMov = '/tmp/leftMovTx.tx'
        fileTx = open(fileLeftMov, "w")
        # checking the output dir
        path = _OUTPATH_ + 'leftMov/s' + str(seq).zfill(4) + '/'
        if not os.path.isdir(path):
            os.makedirs(path)
        outdir = path + 's' + str(seq).zfill(4) + '_Mov' + '.mkv'
        for shot in listShotOrdered:
            # os.system('cp '+res[shot]['framePathCompoStereoLeft'] +' /s/prodanim/asterix2/_sandbox/duda/tmp/')
            print 'preparing: ' + shot
            fileTx.write("file '" + res[shot]['framePathCompoStereoLeft'] + "'\n")
        fileTx.close()
        print 'outputing the movie for left eye'
        os.system(
            "ffmpeg -loglevel error -f concat -safe 0 -r '24' -i " + fileLeftMov + ' -y -c copy -map_metadata 0 ' + outdir)
        os.remove(fileLeftMov)
    # pprint.pprint(findShots())


def get_args():
    # Assign description to the help doc
    parser = argparse.ArgumentParser(description="output right and left movie for sequence stereo" ,add_help=True, epilog=
                                     'Example of use:\n'
                                     'creatSeqStereo -s 300 -o /tmp')
    # shot argument
    parser.add_argument('-seq', type=str, nargs='*',
                        help='seq number(s) you can put multiple sequence separated by a space (i.e: 10 20 200 40)')
    parser.add_argument('--s', '-s', action='store_true', help=' create stereo movie')
    parser.add_argument('--o', '-o', type=str, default='None', help='output file path name default is in user _sandbox/stereoMov/')
    parser.add_argument('--task', '-task', type=str, default='final_layout',
                        help='task default is final_layout')
    args = parser.parse_args()
    seqNumber = args.seq
    # formatedSeq=[]
    # if seqNumber is not None and len(seqNumber)>0:
    #     for seq in seqNumber:
    #         if seq.find('s') < 0:
    #             seq = "s"+ seq.zfill(4)
    #             formatedSeq.append(seq)

    stereo = args.s
    outPath = args.o
    task = args.task

    return seqNumber, stereo, outPath, task


if __name__ == '__main__':
    sequences, stereo, outPath, task = get_args()
    print sequences,stereo
    for seq in sequences:
        createMovie(seq,stereo,outPath,task)
    # pprint.pprint(findShots(300, 'final_layout'))
