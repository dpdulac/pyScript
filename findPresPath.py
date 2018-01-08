#!/usr/bin/env python
# coding:utf-8
""":mod:`findPresPath` -- dummy module
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
import datetime
import shutil
import argparse

_PRESENTATIONDIR_= "/_presentation/"    # directory name for presentation
PresPath = os.environ['PROD_ROOT']+ _PRESENTATIONDIR_   #presentation general path

def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "find the presentation directory for the day")
    parser.add_argument('--mv','-mv', type=str, help='file to move')
    parser.add_argument('-d', '--d', type = str, help='day of presentation')
    parser.add_argument('-dp', '--dp', type = str, help='department for presentation')
    parser.add_argument('-rv', '--rv', type = str, help=" start rv for all the .mov file in directory")
    #parser.add_argument('--cp','-cp', action='store_true', help='file to copy')
    parser.add_argument('--cp','-cp', type=str, help='file to copy')
    args = parser.parse_args()
    mvFile = args.mv
    day = args.d
    copy = args.cp
    department = args.dp
    rv = args.rv
    return mvFile, day, department, copy

def main():

    mvFile, day, department, copy= get_args()
    today = datetime.date.today().strftime("%d%m%y")   #today date in format day,month,year(only 2 last number of the year)

    if not day and not mvFile and not department and not copy:
        todayPresPath = presPathDay([today])
        if not os.path.isdir(todayPresPath):
            os.mkdir(todayPresPath)
        print todayPresPath

    elif department != None: #if looking for a department
        todayPresPathDp = ""
        if day != None:     #if the day is different of the current day
            todayPresPathDp = presPathDay([day,"/",department])
        elif copy != None:
            cpFile = presPathDay([today,"/",department, "/", copy])
            todayPresPathDp = "shutil.copy("+ copy +","+cpFile+")"
        else:
            todayPresPathDp = presPathDay([today,"/",department])
        print todayPresPathDp


def presPathDay(arg=["donuts"]):
    argConcatenat = ""
    for i in arg:
        argConcatenat += i

    listDir = os.listdir(PresPath ) #list all directory in the presentation path
    listDir.sort(reverse = True)  # sort from the max to min
    return PresPath + listDir[0]+'/' + argConcatenat



def listDir(dir = "."):
    for dirname, dirnames, filenames in os.walk(dir):
    # print path to all subdirectories first.
    #for subdirname in dirnames:
        #print(os.path.join(dirname, subdirname))

    # print path to all filenames.
        for filename in filenames:
            if filename.find(".mov") > 0:
                print(os.path.join(dirname, filename))

main()

