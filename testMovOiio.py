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

# def convertImages(inputImages='',
#                   outputDir='',
#                   outPutImage = '',
#                   colorSpaceInput='acescg',
#                   colorSpaceOutput='srgb8',
#                   useColorSpace=True,
#                   useRange=True,
#                   listFrames='',
#                   padNb = '',
#                   usePadNb = True,
#                   useColorSpaceName = True,
#                   inputIsMovie = False,
#                   inFormat = 'exr',
#                   outFormat = 'jpg',
#                   bitFormat = oiio.HALF):
#     outFile = ''
#
#     if inputImages.endswith('.mov') or inputImages.endswith('.qt'):
#         inputIsMovie = True
#
#     # if the format is other tah .exr or .tif force to be 8bit
#     if outFormat != 'exr' or outFormat != 'tif':
#         bitFormat = oiio.UINT8
#
#     # reformat padNb
#     if usePadNb:
#         if int(padNb) <= 1 or padNb == '': # if no need of pad number
#             padNb = 0
#         else:
#             padNb = int(padNb)
#
#     # put the name of output space color in the name
#     if useColorSpaceName:
#         outFile = outputDir + '/' + colorSpaceOutput + '_'+ outPutImage
#     else:
#         outFile = outputDir + '/'+ outPutImage
#
#     # used for single frame or movie type
#     buf = oiio.ImageBuf(inputImages)
#
#     # if there is multiple frame to output
#     if useRange:
#         listFrames = splitFrame(listFrames)
#         print(listFrames)
#         for frameNumber in listFrames:
#             if inputIsMovie:
#                 buf.read(frameNumber)
#             else:
#                 inImage = inputImages + '.' + str(frameNumber).zfill(padNb) + '.' + inFormat
#                 buf = oiio.ImageBufAlgo(inImage)
#             if useColorSpace:
#                 oiio.ImageBufAlgo.colorconvert(buf, buf, colorSpaceInput, colorSpaceOutput)
#             endFile = outFile + '.' + str(frameNumber).zfill(padNb) + '.' + outFormat
#             buf.make_writeable()
#             buf.write(endFile, str(bitFormat))
#             print('converting to : ' + endFile)
#     else:
#         outFile += '.' + outFormat
#         print('converting to : ' + outFile)
#         buf.write(outFile, str(bitFormat))

def main():

    # mov = '/s/prodanim/ta/_sandbox/duda/render/granMaHouseInt/GranMaIntHouse.mov'
    # listFrame = '151-160,4,6,10-12'
    # outDir = '/s/prodanim/ta/_sandbox/duda/tmp/crap'
    # outName = 'testoii'
    #
    # convertImages(inputImages=mov,
    #               outputDir=outDir,
    #               outPutImage =outName,
    #               colorSpaceInput='srgb8',
    #               colorSpaceOutput='acescg',
    #               useColorSpace=True,
    #               useRange=True,
    #               listFrames=listFrame,
    #               padNb='4',
    #               usePadNb=True,
    #               useColorSpaceName=True,
    #               inputIsMovie=True,
    #               inFormat='mov',
    #               outFormat='jpg',
    #               bitFormat=oiio.HALF)

    mov = '/s/prodanim/ta/_sandbox/duda/render/granMaHouseInt/GranMaIntHouse.mov'
    listFrame = '151-160,4,6,10-12'


    mylist = splitFrame(listFrame)
    print(mylist)
    listFrame = '1'

    buf = oiio.ImageBuf(mov)
    nbImages = buf.nsubimages
    mylist = splitFrame(listFrame)
    for i in mylist:
        buf.read(i)
        #oiio.ImageBufAlgo.colorconvert(buf,buf,'srgb8','acescg')
        print('/s/prodanim/ta/_sandbox/duda/acescg_testoiio.'+str(i)+'.exr')
        buf.write('/s/prodanim/ta/_sandbox/duda/acescg_testoiio.'+str(i)+'.exr',str(oiio.HALF))
if __name__ == '__main__':
    main()