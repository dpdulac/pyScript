#!/usr/bin/env python
# coding:utf-8
""":mod: testMovOiio
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2021.01
   
"""
import PyOpenColorIO as ocio
import OpenImageIO as oiio

"""Take a sting made of number separated by ',' or '-' and return an ordered list of number
the number separated by '-' are expended (i,e: 15-17 => 15,16,17"""
def splitFrame(listFrame = ''):
    # split the input in function of ','
    listFrame = listFrame.split(',')
    listFrameOut = []
    # take care of the item with '-' and add the range to the list
    for elem in range(len(listFrame)):
        if listFrame[elem].find('-') >= 0:
            group = listFrame[elem]
            start = group[:group.find('-')]
            end = group[group.find('-') + 1:]
            for sep in range(int(start), int(end) + 1):
                listFrameOut.append(sep)
        else:
            listFrameOut.append(elem)
    listFrameOut.sort()
    return listFrameOut

def convertImages(inputImages='',
                  outputDir='',
                  outPutImage = '',
                  colorSpaceInput='acescg',
                  colorSpaceOutput='srgb8',
                  useColorSpace=True,
                  useRange=True,
                  listFrames='',
                  padNb = '',
                  usePadNb = True,
                  useColorSpaceName = True,
                  outFormat = 'exr',
                  bitFormat = oiio.HALF):
    outFile = ''
    # reformat padNb
    if usePadNb:
        if int(padNb) <= 1 or padNb == '': # if no need of pad number
            padNb = 0
        else:
            padNb = int(padNb)

    # put the name of output space color in the name
    if useColorSpaceName:
        outFile = outputDir + '/' + colorSpaceOutput + '_'+ outPutImage
    else:
        outFile = outputDir + '/'+ outPutImage
    buf = oiio.ImageBuf(inputImages)
    if useRange:
        for frameNumber in listFrames:
            buf.read(frameNumber)
            if useColorSpace:
                oiio.ImageBufAlgo.colorconvert(buf, buf, colorSpaceInput, colorSpaceOutput)
            outFile += '.' + str(frameNumber).zfill(padNb) + '.' + outFormat
            print('converting to : ' + outFile)
            buf.write(outFile, str(bitFormat))
    else:
        outFile += '.' + outFormat
        buf.write(outFile, str(bitFormat))

def main():

    mov = '/s/prodanim/ta/_sandbox/duda/render/granMaHouseInt/GranMaIntHouse.mov'
    listFrame = '151-160,4,6,10-12'

    buf = oiio.ImageBuf(mov)
    nbImages = buf.nsubimages
    mylist = splitFrame(listFrame)
    for i in mylist:
        buf.read(i)
        oiio.ImageBufAlgo.colorconvert(buf,buf,'srgb8','acescg')
        print('/s/prodanim/ta/_sandbox/duda/acescg_testoiio.'+str(i)+'.exr')
        buf.write('/s/prodanim/ta/_sandbox/duda/acescg_testoiio.'+str(i)+'.exr',str(oiio.HALF))


if __name__ == '__main__':
    main()