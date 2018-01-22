#!/usr/bin/env python
# coding:utf-8
""":mod:`extractDispForKatana` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2018, Mikros Animation"

from PIL import Image
import OpenEXR
import Imath
import os,pprint,psutil

def minMaxEXR(filename='', output = 'both'):
    file = OpenEXR.InputFile(filename)
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    dw = file.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    rgbf = Image.frombytes("F", size, file.channel("R", pt)) # only use R because the image is B&W

    extrema = rgbf.getextrema()  #find the min and max luminance
    if output == 'min':
        return extrema[0]
    elif output == 'max':
        return extrema[1]
    else:
        return extrema


def findDispHeight(inFile = '/s/prodanim/asterix2/_sandbox/duda/fileDispFromLua.txt'):
    used = True
    nb = 0
    while used:
        for proc in psutil.process_iter():
            if proc.name() == 'katanaBin':
                for item in proc.open_files():
                    print item.path
                    #print inFile
                    if inFile == str(item.path):
                        print item.path
                        nb = nb + 1
            # for item in proc.open_files():
            #     if inFile == item.path:
            #         used = True
            #         break
            #     else:
            #         used = False
            # if used:
            #     break
        used = False
    print inFile
    print nb

    # res = {} # dictionary for the fileIn
    # mapList ={} # dummy to check if the value for the map hasn't be already calculated
    # returnDict = {} # output dictionary
    # inputFile = open(inFile)
    # # create a dictionary from the file
    # for line in inputFile.readlines():
    #     line = line.replace('\n','')
    #     splitLine = line.split(',')
    #     res[splitLine[0]] = splitLine[1].split(':')
    #
    # #calculate the max extrema
    # for key in res.keys():
    #     dispValue = 0.0
    #     for file in res[key]:
    #         if os.path.isfile(file): # check if the file exist
    #             # if the file hasn't be calculated before do it and put it in mapList
    #             if file not in mapList.keys():
    #                 mapHeight = minMaxEXR(file,'max')
    #                 print mapHeight
    #                 if mapHeight > dispValue:
    #                     dispValue = mapHeight
    #                 mapList[file]= dispValue
    #             else :
    #                 mapHeight = mapList[file]
    #                 if mapHeight > dispValue:
    #                     dispValue = mapHeight
    #     # only value greater than 0.0 are nescessary to set the disp bounding box
    #     if dispValue > 0.0:
    #         returnDict[key] = dispValue
    #     # print key, dispValue
    # inputFile.close()
    # return returnDict

def main():
     out = findDispHeight('/s/prodanim/asterix2/_sandbox/duda/dispDir/testFileLua.txt')
     pprint.pprint(out)

if __name__ == main():
    main()