#!/usr/bin/env python
# coding:utf-8
""":mod:`renameFile` -- dummy module
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

def renameFile(pattern='atom',replace='donuts',dir =''):
    searchDir =''
    if dir == '':
        searchDir = '.'
    else:
        searchDir = dir
    fileInDir = os.listdir(searchDir)
    for item in fileInDir:
        os.chdir(searchDir)
        filepath = item
        if os.path.isfile(filepath) and filepath.find(pattern)>0:
            atom = filepath.replace(pattern,replace)
            os.rename(filepath,atom)

def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "replace a section of a named file")
    #shot argument
    parser.add_argument('--p','-p', type=str, help='pattern to replace')
    parser.add_argument('--r','-r',type=str, help='pattern to replace with')
    parser.add_argument('--d','-d',type=str, help='directory of the file')
    args = parser.parse_args()
    pattern = args.p
    replace = args.r
    dir = args.d
    return pattern,replace,dir

def main():
    pattern,replace,dir = get_args()
    if dir is None:
        dir = '.'
    renameFile(pattern,replace,dir)

if __name__ == '__main__':
    main()



