#!/usr/bin/env python
# coding:utf-8
""":mod:`checkAFX` -- dummy module
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

import os, pprint, errno, argparse, sys, math

seqPath = os.environ['PROD_ROOT']+ '/sequences/'   #presentation general path

def checkIfDir(path='/tmp'):
    direxist = os.path.exists(path)
    return direxist

def foundDir(dir = '/tmp'):
    dirPath = []
    for dirName, subdirList, fileList in os.walk(dir):
        dirPath.append(dirName)
        # for fname in fileList:
        #     print('\t%s' % fname)
    return dirPath



def checkAFX(seq = 's0750', shot = '_p00010', fileType = 'exr'):
    rvPath = 'rv'
    if seq.find('s') < 0:
        seq = 's'+seq.zfill(4)
    else:
        seq = seq.zfill(4)
    # if shot.find('_p') < 0:
    #     shot = '_p'+shot.zfill(5)
    fullShot =  seq +'_p'+ shot.zfill(5)
    seqencePath = seqPath + seq + '/'+fullShot +'/afx'
    print seqencePath
    if checkIfDir(seqencePath):
        foundpath = foundDir(seqencePath)
        del foundpath[0]
        for path in foundpath:
            rvPath += ' '+ path + '/*.'+fileType
    print rvPath

def main():
    checkAFX('4650','840','mov')

if __name__ == '__main__':
    main()




