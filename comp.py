#!/usr/bin/env python
# coding:utf-8
""":mod:`comp` -- dummy module
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

import os
import argparse

#command line for nuke in batch mode
_NUKE_ = "nuke -x "

#main dict nbLayers: number of layers, layoutPaths: path for the published confo layout movie, animPaths: path for the published anim movie, outputPath: path for the output movie, compPath: path for the nuke file
_SHOTS_ = {'10': {'nbLayers': 2,
                  'layoutPaths': ["/s/prods/captain/sequences/s0800/s0800_p90011/confo_layout/confo_layout/publish/movie/","/s/prods/captain/sequences/s0800/s0800_p90012/confo_layout/confo_layout/publish/movie/"],
                  'animPaths': ["/s/prods/captain/sequences/s0800/s0800_p90011/anim/anim_main/publish/movie/","/s/prods/captain/sequences/s0800/s0800_p90012/anim/anim_main/publish/movie/"],
                  'outputPath': "/tmp",
                  'compFile': "/tmp/comp10.nk"},
           '20': {'nbLayers': 2,
                  'layoutPaths': ["/s/prods/captain/sequences/s0800/s0800_p90021/confo_layout/confo_layout/publish/movie/","/s/prods/captain/sequences/s0800/s0800_p90022/confo_layout/confo_layout/publish/movie/"],
                  'animPaths': ["/s/prods/captain/sequences/s0800/s0800_p90021/anim/anim_main/publish/movie/","/s/prods/captain/sequences/s0800/s0800_p90022/anim/anim_main/publish/movie/"],
                  'outputPath': "/tmp",
                  'compFile': "/tmp/comp20.nk"},
           '30': {'nbLayers': 4,
                  'layoutPaths': ["/s/prods/captain/sequences/s0800/s0800_p90031/confo_layout/confo_layout/publish/movie/","/s/prods/captain/sequences/s0800/s0800_p90032/confo_layout/confo_layout/publish/movie/"
                                ,"/s/prods/captain/sequences/s0800/s0800_p90033/confo_layout/confo_layout/publish/movie/","/s/prods/captain/sequences/s0800/s0800_p90034/confo_layout/confo_layout/publish/movie/"],
                  'animPaths': ["/s/prods/captain/sequences/s0800/s0800_p90031/anim/anim_main/publish/movie/","/s/prods/captain/sequences/s0800/s0800_p90032/anim/anim_main/publish/movie/"
                              ,"/s/prods/captain/sequences/s0800/s0800_p90033/anim/anim_main/publish/movie/","/s/prods/captain/sequences/s0800/s0800_p90034/anim/anim_main/publish/movie/"],
                  'outputPath': "/tmp",
                  'compFile': "/tmp/comp30.nk"},
           '40': {'nbLayers': 3,
                  'layoutPaths': ["/s/prods/captain/sequences/s0800/s0800_p90041/confo_layout/confo_layout/publish/movie/","/s/prods/captain/sequences/s0800/s0800_p90042/confo_layout/confo_layout/publish/movie/"
                                ,"/s/prods/captain/sequences/s0800/s0800_p90043/confo_layout/confo_layout/publish/movie/"],
                  'animPaths': ["/s/prods/captain/sequences/s0800/s0800_p90041/anim/anim_main/publish/movie/","/s/prods/captain/sequences/s0800/s0800_p90042/anim/anim_main/publish/movie/"
                              ,"/s/prods/captain/sequences/s0800/s0800_p90043/anim/anim_main/publish/movie/"],
                  'outputPath': "/tmp",
                  'compFile': "/tmp/comp30.nk"}
           }

#list of shot who need compositing
_SHOTSLIST_ = ["10","20","30","40"]


#get the arg from user
def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "output a comp movie for anim")
    #shot argument
    parser.add_argument('--sh','-sh', type=str, help='shot number')
    args = parser.parse_args()
    shotNumber = args.sh
    return shotNumber


#extract data from the dict
def dataFromDict(shotNumber="10"):
    nbLayers = _SHOTS_[shotNumber]['nbLayers']
    layoutPaths = _SHOTS_[shotNumber]['layoutPaths']
    animPaths = _SHOTS_[shotNumber]['animPaths']
    outputPath = _SHOTS_[shotNumber]['outputPath']
    compFile = _SHOTS_[shotNumber]['compFile']
    return nbLayers, layoutPaths, animPaths, outputPath, compFile

#return the last movie published path: path of the file type: pattern to find
def lastMoviePublished(path="/tmp", type = ".mov"):
    #get the data in the directory
    listDir = os.listdir(path)
    movieFile = []
    #only keep file with pattern "type"
    for i in listDir:
        if i.rfind(type) > 0:
            movieFile.append(i)
    #if no file found return 0
    if len(movieFile) == 0:
        return 0
    #else return the last movie created
    else:
        movieFile.sort(reverse = True)
        return path + "/" + movieFile[0]




def main():
    shotNumber = get_args()
    #if user input a wrong shot number exit
    if not shotNumber in _SHOTSLIST_:
        raise Exception("doh!!!! shot "+ shotNumber + " doesn't have comp associated")

    #get the data from the dict
    nbLayers, layoutPaths, animPaths, outputPath, compFile = dataFromDict(shotNumber)
    argList = []

    #check if the anim movie exist if not put the layout movie instead
    for i in range(nbLayers):
        if not os.path.isdir(animPaths[i]):
            mov = lastMoviePublished(path=layoutPaths[i], type = "-left.mov")
            argList.append(mov)
        else:
            lastMov = lastMoviePublished(path=animPaths[i])
            if lastMov == 0:
                mov = lastMoviePublished(path=layoutPaths[i], type = "-left.mov")
                argList.append(mov)
            else:
                argList.append(lastMov)

    #build of the command line
    commandLine = _NUKE_ + compFile + " "
    for i in argList:
        commandLine += i + " "
    commandLine += outputPath

    print commandLine



    #print nbLayers, layoutPaths, animPaths, outputPath, compFile

    #print shotNumber


main()
