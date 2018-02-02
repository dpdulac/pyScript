#!/usr/bin/env python
# coding:utf-8
""":mod:`extractDisp` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2017, Mikros Animation"

import xml.etree.cElementTree as ET
import OpenImageIO as oiio
from PIL import Image
import OpenEXR
import Imath
import os,time,sys


def findMinMaxSingleChannel(filename='', output = 'both'):
    inputFile = oiio.ImageInput.open(filename)
    if not inputFile:
        print 'Could not open: "' + filename + '"'
        print '\tError: "', oiio.geterror()
        return
    spec = inputFile.spec()
    nchans = spec.nchannels
    # the read_image value 1 and 1 correspond to channel begin and channel end i.e we only read one channel
    pixels = inputFile.read_image(1,1,oiio.FLOAT)
    if not pixels:
        print 'Could not read:', inputFile.geterror()
        return
    inputFile.close() #we're done with the file at this point
    minval = pixels[0:1] #initialize to the first pixel value
    maxval = pixels[0:1]
    i = 0 #absolute index

    #loops going throught the height and width of the frame
    for y in range(spec.height):
        for x in range(spec.width):
            if output == 'both':
                if pixels[i] < minval[0]:
                    minval[0] = pixels[i]
                if pixels[i] > maxval[0]:
                    maxval[0] = pixels[i]
            elif output == 'min':
                if pixels[i] < minval[0]:
                    minval[0] = pixels[i]
            elif output == 'max':
                if pixels[i] > maxval[0]:
                    maxval[0] = pixels[i]
            else:
                print 'wrong type of ouput'
                return
            i = i + 1 #advance the index
    if output == 'min':
        return minval[0]
    elif output == 'max':
        return maxval[0]
    else:
        return minval[0],maxval[0]

def findMinMaxBuff(filename='', output = 'both'):
    imgBuff = oiio.ImageBuf(filename)
    imgBuff.read(0,0,True)
    spec = imgBuff.spec()
    maxValue = 0.0
    minValue = 10.0
    #for z in range(spec.depth):
    for y in range(spec.height):
        for x in range(spec.width):
            pixValue = imgBuff.getchannel(x,y,0,1)
            #pixValue = imgBuff.getpixel(x,y)[0]
            if output == 'both':
                if pixValue < minValue:
                    minValue = pixValue
                if pixValue > maxValue:
                    maxValue = pixValue
            elif output == 'min':
                if pixValue < minValue:
                    minValue = pixValue
            elif output == 'max':
                if pixValue > maxValue:
                    maxValue = pixValue
            else:
                print 'wrong type of ouput'
                return

    imgBuff.clear()
    if output == 'min':
        return minValue
    elif output == 'max':
        return maxValue
    else:
        return minValue,maxValue

def minMaxEXR(filename='', output = 'both'):
    file = OpenEXR.InputFile(filename)
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    dw = file.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    rgbf = Image.frombytes("F", size, file.channel("R", pt))

    extrema = rgbf.getextrema()
    if output == 'min':
        return extrema[0]
    elif output == 'max':
        return extrema[1]
    else:
        return extrema
    # darkest = min([lo for (lo,hi) in extrema])
    # lighest = max([hi for (lo,hi) in extrema])
    # scale = 255 / (lighest - darkest)

def minMaxOIIO(filename = '', output = 'both'):
    file = oiio.ImageInput.open(filename)
    pixels = file.read_image(0,0,oiio.FLOAT)
    spec = file.spec()
    size = (spec.width,spec.height)
    rgbf = Image.frombytes("F", size, pixels)
    print rgbf.getpixel((2,2))

    extrema = rgbf.getextrema()
    if output == 'min':
        return extrema[0]
    elif output == 'max':
        return extrema[1]
    else:
        return extrema

def findDispHeight(inFile = '/s/prodanim/asterix2/_sandbox/duda/testFileLua.txt'):
    filename = inFile.replace('.txt','.xml')
    res = {}
    mapList ={}
    returnDict = {}
    inputFile = open(inFile)
    # create a dictionary from the file
    for line in inputFile.readlines():
        line = line.replace('\n','')
        splitLine = line.split(',')
        res[splitLine[0]] = splitLine[1].split(':')

    #calculate the max extrema
    for key in res.keys():
        dispValue = 0.0
        for file in res[key]:
            if os.path.isfile(file):
                # if the file hasn't be calculated before do it and put it in mapList
                if file not in mapList.keys():
                    mapHeight = minMaxOIIO(file,'max')
                    print mapHeight
                    if mapHeight > dispValue:
                        dispValue = mapHeight
                    mapList[file]= dispValue
                else :
                    mapHeight = mapList[file]
                    if mapHeight > dispValue:
                        dispValue = mapHeight
        returnDict[key] = dispValue
        print key, dispValue


    root = ET.Element("attributeFile", version="0.1.0")
    for item in returnDict.keys():
        doc = ET.SubElement(root, "attributeList", location=item)
        ET.SubElement(doc, "attribute", name="dispValue", type="float",value=str(returnDict[item]))
    tree = ET.ElementTree(root)
    # if fileName.rfind('.xml') < 0:
    #       fileName += '.xml'
    tree.write(filename)
    print 'done and YouAreUnderArrest'




def oldFindDispHeight():
    res = {}
    inputFile = open('/s/prodanim/asterix2/_sandbox/duda/testFullPath.txt','r')
    xmlFileName = '/s/prodanim/asterix2/_sandbox/duda/filedisp_marketing3.xml'
    for line in inputFile.readlines():
        dispValue = 0.0
        line = line.replace('\n','') # replace the new line
        sepLine = line.split(',') # slpit the name and the file path
        filePath = sepLine[1]
        if filePath.find('<udim>') > 0: # if udim is find
            dirFilePath = filePath[:filePath.rfind('/')] # extract the directory
            fileName = filePath[:filePath.rfind('<udim>')]
            fileInDir = [os.path.join(dirFilePath,f) for f in os.listdir(dirFilePath)] # list all the file in the directory
            a = time.time()
            for item in fileInDir:
                if item.find(fileName) == 0 and item.endswith('exr'):
                    currentValue = findMinMaxSingleChannel(item, 'max')
                    if currentValue > dispValue:
                        dispValue = currentValue
            print 'time: ',time.time() - a
        else:
            dispValue = findMinMaxSingleChannel(filePath, 'max')
        res[sepLine[0]]= dispValue
        print sepLine[0],dispValue
    root = ET.Element("attributeFile", version="0.1.0")
    for item in res.keys():
        doc = ET.SubElement(root, "attributeList", location=item)
        ET.SubElement(doc, "attribute", name="dispValue", type="float",value=str(res[item]))
    tree = ET.ElementTree(root)
    if fileName.rfind('.xml') < 0:
          fileName += '.xml'
    tree.write(xmlFileName)
    print 'done'

def main():
    findDispHeight()

def timeTest():
    fileName = '/s/prodanim/asterix2/assets/Character/druid_chief/surface_tk/surface_renderPkg/publish/katana/Character-druid_chief-base-surface_renderPkg-v009/Character-druid_chief-body-dsp.1003.exr'
    a = time.time()
    print findMinMaxSingleChannel(fileName,'max')
    print 'first: ',time.time() - a
    a = time.time()
    print findMinMaxBuff(fileName,'max')
    print 'second: ',time.time() - a

def testEXR():
    fileName = '/s/prodanim/asterix2/assets/Character/druid_chief/surface_tk/surface_renderPkg/publish/katana/Character-druid_chief-base-surface_renderPkg-v009/Character-druid_chief-body-dsp.1003.exr'
    a = time.time()
    print minMaxEXR(fileName,'max')
    print 'first: ',time.time() - a

def testOIIO():
    fileName = '/s/prodanim/asterix2/assets/Character/cubix_pant/surface_tk/surface_renderPkg/publish/katana/Character-cubix_pant-base-surface_renderPkg-v010/Character-cubix_pant-eyes-mask_B.1051.tif'
    print minMaxOIIO(fileName,'max')

# if __name__ == main():
#     main()

if __name__ == testOIIO():
    testOIIO()
# if __name__ == timeTest():
#     timeTest()

# if __name__ == testEXR():
#     testEXR()