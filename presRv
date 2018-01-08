#!/usr/bin/env python
# coding:utf-8
""":mod:`presRv` -- dummy module
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
import subprocess

_PRESENTATIONDIR_= "/_presentation/"    # directory name for presentation
PresPath = os.environ['PROD_ROOT']+ _PRESENTATIONDIR_   #presentation general path

def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "play all the file of type ft under the directory in rv")
    parser.add_argument('--ft','-ft', type=str, help='file type')
    parser.add_argument('-d', '--d', type = str, help='directory')
    args = parser.parse_args()
    fileType = args.ft
    directory = args.d
    return fileType, directory

def main():
    fileType, directory = get_args()
    if fileType == None:
        fileType = ".mov"
    else:
        fileType = "." + fileType
    if directory == None:
        directory = '.'

    rvAllPath = "rv"
    for i in listDir(directory,fileType):
        rvAllPath += (" " + i)

    rvAllPath += " &"

    os.system(rvAllPath)




def listDir(dir = ".",fType= ".mov"):
    fileList = []
    for dirname, dirnames, filenames in os.walk(dir):
    # print path to all filenames.
        for filename in filenames:
            if filename.rfind(".mov") > 0:
                fileList.append(os.path.join(dirname, filename))
    return fileList

main()