#!/usr/bin/env python
# coding:utf-8
""":mod:`fullMovie` -- dummy module
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

import os

seqOrder =['s0200', 's0300', 's0350', 's0750', 's0800', 's1000', 's1250', 's1260', 's1280', 's1300', 's1400', 's1500', 's1600', 's1850', 's1950', 's2050', 's0700', 's2150', 's2400', 's2410', 's2450', 's4000', 's4025', 's4050', 's4350', 's4365', 's4375', 's4400', 's4450', 's4550', 's4650', 's4850', 's5050', 's5100', 's5400']


def doMovie(seqMax = 's5400',create = False):
    if create:
        fileName = '/s/prods/captain/_sandbox/duda/misc/fullMovie.tx'
        fileTx = open(fileName,"w")
        for seq in seqOrder:
            pathSeqMovie = "file '" +'/s/prods/captain/sequences/' +seq+'/masters/mov/left/' + seq+"_Movie.mov'"
            fileTx.write(pathSeqMovie+'\n')
            if seq == seqMax:
                break
        fileTx.close()
        #commandLine = "ffmpeg -loglevel error -f concat -safe 0 -r '24' -i " + fileName + ' /s/prods/captain/_sandbox/duda/misc/outMovie.mp4'
        commandLine = "ffmpeg -f concat -safe 0 -r '24' -i " + fileName + ' -c:a libfdk_aac -b:a 384k -vbr 3 -strict -2 -y /s/prods/captain/_sandbox/duda/misc/outMovie.mp4'
    else:
        rvArg = ''
        for seq in seqOrder:
            rvArg += ' '+'/s/prods/captain/sequences/' +seq+'/masters/mov/left/' + seq+"_Movie.mov"
            if seq == seqMax:
                break
        commandLine = 'rv ' + rvArg
    os.system(commandLine)
def main():
    doMovie('s5400')

if __name__ == main():
    main()
