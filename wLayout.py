#!/usr/bin/env python
# coding:utf-8
""":mod:`wLayout` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2016, Mikros Image"

import os, time
from pprint import pprint as pp
import argparse
from sgtkLib import tkutil, tkm
tk, sgw, project = tkutil.getTk(fast=True, scriptName='duda')


#get the arg from user
def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "output a comp movie for anim")
    #shot argument
    parser.add_argument('--sq','-sq', type=str, help='seq number')
    parser.add_argument('--p','-p', type=str, help='shot number')
    args = parser.parse_args()
    shotNumber = args.p
    seqNumber = args.sq
    return shotNumber, seqNumber


#find the last png file published (code largely inspire by Simon)
def lastMoviePublished(seq='s0800', shot='p90021', task='confo_layout',type="Main"):
    project = {'type': 'Project', 'id': 70}

    #Get entity SG
    sg_filter = [['project', 'is', project],
                 ['code', 'is', '%s_%s' % (seq, shot)]]
    entity = sgw.sg_find_one('Shot', sg_filter, ['code'])
    if not entity:
        print 'No Shot %s_%s exists !' % (seq, shot)
        return 0

    #Get task SG
    sg_filter = [['project', 'is', project],
                 ['content', 'is', task],
                 ['entity', 'is', entity]]
    taskSG = sgw.sg_find_one('Task', sg_filter, ['content'])
    if not taskSG:
        print 'No task %s exists in Shot %s !' % (task, entity['code'])
        return 0

    #Get Published File SG
    if type == 'Main':
        sg_filter = [['project', 'is', project],
                    ['task', 'is', taskSG],
                    ['code','contains', '_default-base-confo_layout-'],
                    ['published_file_type', 'is', {'type':'PublishedFileType', 'id':19}],
                    ['entity', 'is', entity]]
    else:
        sg_filter = [['project', 'is', project],
                    ['task', 'is', taskSG],
                    ['code','contains', 'ambientOcc-mono'],
                    ['published_file_type', 'is', {'type':'PublishedFileType', 'id':23}],
                    ['entity', 'is', entity]]
    pub = sgw.sg_find_one('PublishedFile', sg_filter, ['path'], order=[{'field_name':'version_number','direction':'desc'}])

    if not pub:
        print 'No version found for %s %s' % (entity['code'], taskSG['content'])
        return 0
    #print 'Last movie found : "%s"' % last_movie
    return pub['path']['local_path']

def main():
    shotNumber, seqNumber = get_args()

    seqNumber=seqNumber.zfill(4)
    seqNumber = "s"+seqNumber

    shotNumber=shotNumber.zfill(5)
    shotNumber = "p"+ shotNumber

    animFile = lastMoviePublished(seq=seqNumber, shot=shotNumber, task='confo_layout')
    occFile = lastMoviePublished(seq=seqNumber, shot=shotNumber, task='confo_layout', type="Occ")
    command = "rv -wipe " + occFile + " " + animFile
    print command
    os.system(command)


main()
#print lastMoviePublished(seq='s0300', shot='p00040', task='confo_layout',type="Occ")