#!/usr/bin/env python
# coding:utf-8
""":mod:`extractImage` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2017, Mikros Image"

from sgtkLib import tkutil, tkm
import os, pprint, errno, argparse, sys, math
import datetime

_USER_ = os.environ['USER']
_OUTPATH_ ="/s/prods/captain/_sandbox/" + _USER_


tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

#get the arg from user
def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "extract an image from a movie \n usage: extractimage -sh 1300 300 -f 10 34 50")
    #shot
    parser.add_argument('--sh','-sh', nargs = '*', dest = 'shot', type=str, help='sequence, shot')
    parser.add_argument('--f','-f', nargs = '*', dest = 'frames', type=str, help='frames to capture')
    #parser.add_argument('--o','-o', type=str, help='output directory, frame name')
    args = parser.parse_args()
    shotArg = args.shot
    frames = args.frames
    sequence = shotArg[0]
    shot=shotArg[1]
    return sequence,shot,frames

imageFilter = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'name_is', 'GenericMovie'],
            ['published_file_type', 'name_is', 'DwaMovie'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
            #['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }

def findSingleShot(shot = 's1300_p00300', taskname = 'compo_precomp'):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'is', shot],
        ['task', 'name_is', taskname],
        imageFilter
    ]
    res = []
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type'], order=[{'field_name':'version_number','direction':'desc'}]):
        res.append(v['path']['local_path'])
    return res

def checkDir(path = '/tmp'):
    if not os.path.exists(os.path.dirname(path)):
        print path,'donuts'
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def exportImage(sequence = '1300',shot = '300', frames = [10,20,30], task = 'compo_precomp'):
    if sequence.find('s') < 0:
        sequence = 's'+sequence.zfill(4)
    else:
        sequence = sequence.zfill(4)
    shot = sequence +'_p'+ shot.zfill(5)

    today = _OUTPATH_ + '/'+datetime.date.today().strftime("%d%m%y") + '_paintOver/'   #today date in format day,month,year(only 2 last number of the year)
    checkDir(today)
    path = findSingleShot(shot = shot,taskname=task)
    for frame in frames:
        frameConvert = "{0:.2f}".format(float(frame)/24.0)
        commandLine = 'ffmpeg -ss ' + frameConvert + ' -r 24 -i ' + path[0] + ' -vframes 1 -f image2 ' + today+'/'+shot+'_f'+frame + '.jpg'
    #commandLine = '/s/apps/lin/rv/current/bin/rvio [ '+ path[0] + ' -in ' + frame + ' -out ' + frame + ' ]'+ ' -o ' + output + '.jpg'
        os.system(commandLine)
        print commandLine

def main():
    sequence,shot, frames = get_args()
    exportImage(sequence = sequence,shot = shot, frames = frames, task = 'compo_precomp')






if __name__ == '__main__':
    main()

