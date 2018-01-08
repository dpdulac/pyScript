#!/usr/bin/env python
# coding:utf-8
""":mod:`compB` -- dummy module
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

'''create comp images for layered shots using the latest anim rendered png. If there is no anim it will use the latest png from confo Layout. The command line on shell should be: comp -sh (shot number) -d (if user want to look at the result in rv)
the nuke syntax to start in shell mode is nuke -x [argv0] [argv 1] ...[argv x], the arguments called [argv 0]...[argv X] in the nuke file are the input (also named [argv 0]....[argv x] in the field namefile) on the read nodes and write node
'''

import os, time
from pprint import pprint as pp
import argparse
from sgtkLib import tkutil, tkm

tk, sgw, project = tkutil.getTk(fast=True, scriptName='duda')

_SEQ_ = 's0800'

#file format
_FILEFORMAT_ = ".%04d.png"

#command line for nuke in batch mode
_NUKE_ = "nuke -x "

#main dict nbLayers: number of layers, seq: sequence nb, shots: shot number of the layer, task: task to use, outputPath: path for the output movie, compPath: path for the nuke file
_SHOTS_ = {'10': {'nbLayers': 2,
                  'seq': _SEQ_,
                  'shots': ["p90011","p90012"],
                  'task':['anim_main','confo_layout'],
                  'outputPath': "/s/prods/captain/sequences/s0800/s0800_p00010/anim/anim_main/publish/images/",
                  'compFile': "/s/prods/captain/sequences/s0800/s0800_p00010/anim/anim_main/work/nuke/s0010NukeScript.nk",
                  'startEnd': ['101', '395']},
           '20': {'nbLayers': 2,
                  'seq': _SEQ_,
                  'shots': ["p90021","p90022"],
                  'task':['anim_main','confo_layout'],
                  'outputPath': "/s/prods/captain/sequences/s0800/s0800_p00020/anim/anim_main/publish/images",
                  'compFile': "/s/prods/captain/sequences/s0800/s0800_p00020/anim/anim_main/work/nuke/s0020NukeScript.nk",
                  'startEnd': ['1', '101']},
           '30': {'nbLayers': 4,
                  'seq': _SEQ_,
                  'shots': ["p90031","p90032","p90033","p90034"],
                  'task':['anim_main','confo_layout'],
                  'outputPath': "/s/prods/captain/sequences/s0800/s0800_p00030/anim/anim_main/publish/images",
                  'compFile': "/s/prods/captain/sequences/s0800/s0800_p00030/anim/anim_main/work/nuke/s0030NukeScript.nk",
                  'startEnd': ['1', '101']},
           '40': {'nbLayers': 3,
                  'seq': _SEQ_,
                  'shots': ["p90041","p90042","p90043"],
                  'task':['anim_main','confo_layout'],
                  'outputPath': "/s/prods/captain/sequences/s0800/s0800_p00040/anim/anim_main/publish/images",
                  'compFile': "/s/prods/captain/sequences/s0800/s0800_p00040/anim/anim_main/work/nuke/s0040NukeScript.nk",
                  'startEnd': ['1', '101']}
           }

#list of shot who need compositing
_SHOTSLIST_ = ["10","20","30","40"]


#get the arg from user
def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "output a comp movie for anim")
    #shot argument
    parser.add_argument('--sh','-sh', type=str, help='shot number')
    parser.add_argument('--d','-d', action='store_true', help='display in rv')
    args = parser.parse_args()
    shotNumber = args.sh
    display = args.d
    return shotNumber, display


#extract data from the dict
def dataFromDict(shotNumber="10"):
    nbLayers = _SHOTS_[shotNumber]['nbLayers']
    seq = _SHOTS_[shotNumber]['seq']
    shots = _SHOTS_[shotNumber]['shots']
    task = _SHOTS_[shotNumber]['task']
    outputPath = _SHOTS_[shotNumber]['outputPath']
    compFile = _SHOTS_[shotNumber]['compFile']
    startEnd = _SHOTS_[shotNumber]['startEnd']
    return nbLayers, seq, shots,task, outputPath, compFile, startEnd


#find the last png file published (code largely inspire by Simon)
def lastMoviePublished(seq='s0800', shot='p90021', task='confo_layout'):
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
    sg_filter = [['project', 'is', project],
                 ['task', 'is', taskSG],
                 ['published_file_type', 'is', {'type':'PublishedFileType', 'id':21}],
                 ['entity', 'is', entity]]
    pub = sgw.sg_find_one('PublishedFile', sg_filter, ['path'], order=[{'field_name':'version_number','direction':'desc'}])

    if not pub:
        print 'No version found for %s %s' % (entity['code'], taskSG['content'])
        return 0
    #print 'Last movie found : "%s"' % last_movie
    return pub['path']['local_path']

#create a new version for the output directory "crude programming......."
def outDir(path = "/tmp",shot="10"):
    #put the shot in good format
    shotFormat = "p"+shot.zfill(4)
    #list the dir
    listDir = os.listdir(path)
    dirWithVersion = []
    #put only directory with the letter V in the list
    for i in listDir:
        if os.path.isdir(path +i) and i.find("V") == 0:
            dirWithVersion.append(i)
    #if there is no directory create the version V001
    if not dirWithVersion:
        outputDir = path+'V001'
        os.mkdir(outputDir)
        return outputDir+ "/"+_SEQ_+shotFormat+_FILEFORMAT_
    #return a path with incremented version
    else:
        #sort from hight to lowest
        dirWithVersion.sort(reverse = True)
        #extract the nember from the latest version
        latest = dirWithVersion[0][1:]
        #increment the version
        newVersion = str(int(latest)+1).zfill(len(latest))
        #output the directory
        outputDir = path + "V"+newVersion
        os.mkdir(outputDir)
        return outputDir + "/"+ _SEQ_+ shotFormat+ _FILEFORMAT_






def main():
    shotNumber, display = get_args()
    #if user input a wrong shot number exit
    if not shotNumber in _SHOTSLIST_:
        raise Exception("doh!!!! shot "+ shotNumber + " doesn't have comp associated")

    #get the data from the dict
    nbLayers, seq, shots,task, outputPath, compFile, startEnd = dataFromDict(shotNumber)
    argList = []

    #check if the anim movie exist if not put the layout movie instead
    for i in range(nbLayers):
        lastMov = lastMoviePublished(seq, shots[i],task[0])
        if not lastMov:
            lastMov = lastMoviePublished(seq, shots[i],task[1])
            argList.append(lastMov)
        else:
            argList.append(lastMov)

    #build of the command line
    commandLine = _NUKE_ + compFile + " "
    #extract the input file path
    for i in argList:
        commandLine += i + " "
    #get the output file path
    outputDir = outDir(outputPath,shotNumber)
    #if the user want to play in rv the result
    if display:
        commandLine += outputDir + " " + startEnd[0] + "-" + startEnd[1] + ";rv " + outputDir
    else:
        commandLine += outputDir + " " + startEnd[0] + "-" + startEnd[1]

    print commandLine

    os.system(commandLine)



main()



