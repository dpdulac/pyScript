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

""" class convertImages: convert input image(s)/mov format to output format using pyoiio library
    take 3 arguments: 
    inputImages ---> image with path (i.e /s/prodanim/ta/_sandbox/duda/render/granMaHouseInt/hallwayAB/left.0001.exr)
    outputDir ---> output directory as a path
    outputImage ---> name of the output image
    function:
    setInputImages(self, inputImages='') ---> to set an input image
    setOutputDir(self, outputDir='') ---> set output directory
    setOutputImage(self, outputImage='') ---> set output image name
    setColorSpaceInput(self, colorSpaceInput='acescg') ---> set color space in
    setColorSpaceOutput(self, colorSpaceOutput='srgb8') ---> set color space out
    setUseColorSpace(self, state=True) ---> set if we want a color space conversion
    setUseRange(self, state=True) ---> set if we want to convert a range of frame
    setListFrames(self, listFrames=[]) ---> list of frame to convert separated by comma/dash in form '1,2,5,10-15' 
    setPadNb(self, padNb='') ---> number of padding number for output
    setUseColorSpaceName(self, state=True) ---> add the color space out to the outputImage name (useful for rv)
    setInputIsMovie(self, state=True) ---> set if the inputImages is a movie (i.e: .mov or .qt)
    setInFormat(self, inFormat='exr') ---> input format of image
    setOutFormat(self, outFormat='jpg') ---> output format
    setBitFormat(self, bitFormat=oiio.UINT8) ---> bit format (i.e: 8bit, 16bit, halt, float)
    splitFrame(self) ---> convert the lisFrame into a list of int
    process(self) ---> do the convertion
"""


class convertImages:
    def __init__(self, inputImages='', outputDir='', outputImage=''):
        self.inputImages = inputImages
        self.outputDir = outputDir
        self.outPutImage = outputImage
        self.outFile = ''
        self.colorSpaceInput = 'acescg'
        self.colorSpaceOutput = 'srgb8'
        self.useColorSpace = True
        self.useRange = True
        self.listFrames = ''
        self.padNb = '4'
        self.usePadNb = True
        self.useColorSpaceName = True
        self.inputIsMovie = False
        self.inFormat = 'exr'
        self.outFormat = 'jpg'
        self.bitFormat = oiio.HALF

    def setInputImages(self, inputImages=''):
        self.inputImages = inputImages

    def setOutputDir(self, outputDir=''):
        self.outputDir = outputDir

    def setOutputImage(self, outputImage=''):
        self.outPutImage = outputImage

    def setColorSpaceInput(self, colorSpaceInput='acescg'):
        self.colorSpaceInput = colorSpaceInput

    def setColorSpaceOutput(self, colorSpaceOutput='srgb8'):
        self.colorSpaceOutput = colorSpaceOutput

    def setUseColorSpace(self, state=True):
        self.useColorSpace = state

    def setUseRange(self, state=True):
        self.useRange = state

    def setListFrames(self, listFrames=[]):
        self.listFrames = listFrames

    def setPadNb(self, padNb=''):
        self.padNb = padNb

    def setUseColorSpaceName(self, state=True):
        self.useColorSpaceName = state

    def setInputIsMovie(self, state=True):
        self.setInputIsMovie(state)

    def setInFormat(self, inFormat='exr'):
        self.inFormat = inFormat

    def setOutFormat(self, outFormat='jpg'):
        self.outFormat = outFormat

    def setBitFormat(self, bitFormat=oiio.UINT8):
        self.bitFormat = bitFormat

    def splitFrame(self):
        # split the input in function of ','
        listFrame = self.listFrames.split(',')
        listFrameOut = []
        # take care of the item with '-' and add the range to the list
        for elem in range(len(listFrame)):
            # if there is a '-' in the elem
            if listFrame[elem].find('-') >= 0:
                group = listFrame[elem]
                # separate the right and left part
                start = group[:group.find('-')]
                end = group[group.find('-') + 1:]
                for sep in range(int(start), int(end) + 1):
                    # add all the frame to listFrameOut
                    listFrameOut.append(sep)
            else:
                # add the frame to the list
                listFrameOut.append(elem)
        # sort the list
        listFrameOut.sort()
        # get rid of duplicate
        listFrameOut = list(dict.fromkeys(listFrameOut))
        return listFrameOut

    def process(self):
        # check if the file is a movie file
        if self.inputImages.endswith('.mov') or self.inputImages.endswith('.qt'):
            self.inputIsMovie = True

        # if the format is other than .exr or .tif force to be 8bit
        if self.outFormat != 'exr' or self.outFormat != 'tif':
            self.bitFormat = oiio.UINT8

        # reformat padNb
        if self.usePadNb:
            if int(self.padNb) <= 1 or self.padNb == '':  # if no need of pad number
                self.padNb = 0
            else:
                self.padNb = int(self.padNb)

        # put the name of output space color in the name
        if self.useColorSpaceName and self.useColorSpace:
            self.outFile = self.outputDir + '/' + self.colorSpaceOutput + '_' + self.outPutImage
        else:
            self.outFile = self.outputDir + '/' + self.outPutImage

        # used for single frame or movie type
        buf = oiio.ImageBuf(self.inputImages)

        # if there is multiple frame to output
        if self.useRange:
            self.listFrames = self.splitFrame()
            for frameNumber in self.listFrames:
                # if the inputImage is a movie
                if self.inputIsMovie:
                    # put the frame number in the buffer
                    buf.read(frameNumber)
                else:
                    # extract the path
                    inImagePath = self.inputImages[:self.inputImages.rfind('/') + 1]
                    # extract the name of the image
                    inImageName = self.inputImages[self.inputImages.rfind('/') + 1:self.inputImages.find('.')]
                    # reconstruct the image path with padding
                    inImage = inImagePath + inImageName + '.' + str(frameNumber).zfill(self.padNb) + '.' + self.inFormat
                    # load the image in a buffer
                    buf = oiio.ImageBuf(inImage)
                # if color convertion is wanted
                if self.useColorSpace:
                    oiio.ImageBufAlgo.colorconvert(buf, buf, self.colorSpaceInput, self.colorSpaceOutput)
                # reconstruct the endfile path with padding
                endFile = self.outFile + '.' + str(frameNumber).zfill(self.padNb) + '.' + self.outFormat
                # set the bit format
                buf.set_write_format(self.bitFormat)
                # write the file
                buf.write(endFile)
                print('converting to : ' + endFile)
        # just a single frame to convert
        else:
            # if color convertion is wanted
            if self.useColorSpace:
                oiio.ImageBufAlgo.colorconvert(buf, buf, self.colorSpaceInput, self.colorSpaceOutput)
            # construct the outfile path
            self.outFile += '.' + self.outFormat
            # set the bit format
            buf.set_write_format(self.bitFormat)
            # write the file
            print('converting to : ' + self.outFile)
            buf.write(self.outFile, str(self.bitFormat))

        buf.clear()


"""Take a sting made of number separated by ',' or '-' and return an ordered list of number
the number separated by '-' are expended (i,e: 15-17 => 15,16,17"""


# def splitFrame(listFrame=''):
#     # split the input in function of ','
#     listFrame = listFrame.split(',')
#     listFrameOut = []
#     # take care of the item with '-' and add the range to the list
#     for elem in range(len(listFrame)):
#         if listFrame[elem].find('-') >= 0:
#             group = listFrame[elem]
#             start = group[:group.find('-')]
#             end = group[group.find('-') + 1:]
#             for sep in range(int(start), int(end) + 1):
#                 listFrameOut.append(sep)
#         else:
#             listFrameOut.append(elem)
#     listFrameOut.sort()
#     return listFrameOut
#
#
# def convertImages(inputImages='',
#                   outputDir='',
#                   outPutImage='',
#                   colorSpaceInput='acescg',
#                   colorSpaceOutput='srgb8',
#                   useColorSpace=True,
#                   useRange=True,
#                   listFrames='',
#                   padNb='',
#                   usePadNb=True,
#                   useColorSpaceName=True,
#                   inputIsMovie=False,
#                   inFormat='exr',
#                   outFormat='jpg',
#                   bitFormat=oiio.HALF):
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
#         if int(padNb) <= 1 or padNb == '':  # if no need of pad number
#             padNb = 0
#         else:
#             padNb = int(padNb)
#
#     # put the name of output space color in the name
#     if useColorSpaceName and useColorSpace:
#         outFile = outputDir + '/' + colorSpaceOutput + '_' + outPutImage
#     else:
#         outFile = outputDir + '/' + outPutImage
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
#             buf.set_write_format(bitFormat)
#             buf.write(endFile)
#             print('converting to : ' + endFile)
#     else:
#         outFile += '.' + outFormat
#         print('converting to : ' + outFile)
#         buf.write(outFile, str(bitFormat))
#
#     buf.clear()


def main():
    mov = '/s/prodanim/ta/_sandbox/duda/render/granMaHouseInt/hallwayAB/left.0001.exr'
    listFrame = '1-100'
    outDir = '/s/prodanim/ta/_sandbox/duda/tmp/crap'
    outName = 'testoii'

    # convertImages(inputImages=mov,
    #               outputDir=outDir,
    #               outPutImage=outName,
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

    myConvert = convertImages(mov, outDir, outName)
    myConvert.setColorSpaceInput('acescg')
    myConvert.setColorSpaceOutput('srgb8')
    myConvert.setListFrames(listFrame)
    myConvert.setInFormat('exr')
    myConvert.setOutFormat('jpg')
    myConvert.process()

    # mov = '/s/prodanim/ta/_sandbox/duda/render/granMaHouseInt/GranMaIntHouse.mov'
    # listFrame = '151-160,4,6,10-12'
    #
    #
    # mylist = splitFrame(listFrame)
    # print(mylist)
    # listFrame = '1'
    #
    # buf = oiio.ImageBuf(mov)
    # nbImages = buf.nsubimages
    # mylist = splitFrame(listFrame)
    # for i in mylist:
    #     buf.read(i)
    #     #oiio.ImageBufAlgo.colorconvert(buf,buf,'srgb8','acescg')
    #     print('/s/prodanim/ta/_sandbox/duda/acescg_testoiio.'+str(i)+'.exr')
    #     buf.write('/s/prodanim/ta/_sandbox/duda/acescg_testoiio.'+str(i)+'.exr',str(oiio.HALF))


if __name__ == '__main__':
    main()
