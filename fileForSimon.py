#!/usr/bin/env python
# coding:utf-8
""":mod:`fileForSimon` -- dummy module
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

from sgtkLib import tkutil, tkm

tk, sgw, project = tkutil.getTk(fast=True, scriptName='duda')

import os, time,argparse

#get the arg from user
def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "create a wipe compare for al sequence or selected shots")
    #shot argument
    parser.add_argument('--sq','-sq', type=str, help='seq number')
    parser.add_argument('--p','-p', nargs = '*', dest = 'shots', type=str, help='shot number')
    parser.add_argument('--t','-t', type=str, help='task')
    args = parser.parse_args()
    shotNumber = args.shots
    seqNumber = args.sq
    task = args.t
    return shotNumber, seqNumber,task


def lastMoviePublished(seqShot='s0800_p90021', task='confo_layout'):
    project = {'type': 'Project', 'id': 70}

    #Get entity SG
    sg_filter = [['project', 'is', project],
                 ['code', 'is', seqShot]]
    entity = sgw.sg_find_one('Shot', sg_filter, ['code'])
    if not entity:
        print 'No Shot %s exists !' % (seqShot)
        return 0

    #Get task SG
    sg_filter = [['project', 'is', project],
                 ['content', 'is', task],
                 ['entity', 'is', entity]]
    taskSG = sgw.sg_find_one('Task', sg_filter, ['content'])
    if not taskSG:
        print 'No task %s exists in Shot %s !' % (task, entity['code'])
        return 0

    sg_filter = [['project', 'is', project],
                    ['task', 'is', taskSG],
                    ['entity', 'is', entity]]

    if task == 'anim_main':
        sg_filter.append(['code','contains', 'default-base-anim_main'])
        sg_filter.append(['published_file_type', 'is', {'type':'PublishedFileType', 'id':19}])
    else:
        sg_filter.append(['code','contains', 'ambientOcc-mono'])
        sg_filter.append(['published_file_type', 'is', {'type':'PublishedFileType', 'id':23}])

    pub = sgw.sg_find_one('PublishedFile', sg_filter, ['path'], order=[{'field_name':'version_number','direction':'desc'}])

    if not pub:
        print 'No version found for %s %s' % (entity['code'], taskSG['content'])
        return 0
    #print 'Last movie found : "%s"' % last_movie
    return pub['path']['local_path']



def seqShotList(seq='s0300',task='anim_main'):
    shotNameList = []
    project = {'type': 'Project', 'id': 70}

    #Get entity SG
    sg_filter = [['project', 'is', project],
                 #['content','is',task],
                 ['code', 'is', seq]]
    for atom in sgw.sg_find('Sequence', sg_filter, ['shots']):
        #print atom['shots']
        if atom['shots']:
            for shot in atom['shots']:
                shotNameList.append(shot['name'])
    return shotNameList




def main():

    listShotName = []
    shotNumber, seqNumber,task = get_args()

    if not task:
        task = 'confo_anim'

    seqNumber=seqNumber.zfill(4)
    seqNumber = "s"+seqNumber
    if not shotNumber or len(shotNumber) == 0:
        listShotName = seqShotList(seqNumber)
    else:
        for i in shotNumber:
            listShotName.append(seqNumber+"_p"+ i.zfill(5))

    seqDict={}
    seqDict["shots"]={}
    seqDict["taskA"]="anim_main"
    seqDict["taskB"]=task
    for i in listShotName :
        pathAnim = lastMoviePublished(seqShot=i, task='anim_main')
        if pathAnim != 0:
            pathLayout = lastMoviePublished(seqShot=i, task=task)
            if pathLayout != 0:
                seqDict["shots"][i]={'anim_main':pathAnim,task:pathLayout}


    commandLine = "rv -pyeval \"from rv import commands;from scratch import createMode;import sys; sys.path.append(\'/s/prods/captain/_sandbox/duda/duda/_scripts/donuts/test_duda\'); createMode("+str(seqDict)+")\""

    print commandLine
    #os.system(commandLine)



main()