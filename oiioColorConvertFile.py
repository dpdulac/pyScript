#!/usr/bin/env python
# coding:utf-8
""":mod: oiioColorConvertFile --- Module Title
=================================

   2019.02
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""

import OpenImageIO as oiio
import PyOpenColorIO as OCIO
from array import *
import os, sys, shutil


def convertImageOIIO(filename = '',fileOutName = '',format='tif'):
    inFile = oiio.ImageBuf(filename)
    if not inFile.has_error :
        oiio.ImageBufAlgo.colorconvert(inFile,inFile,"srgb8","acescg")
        # if format != 'tif':
        #     inFile.set_write_format(oiio.UINT16)
        # else:
        #     inFile.set_write_format(oiio.UINT8)
        inFile.write(fileOutName)
        print 'done'
    if inFile.has_error :
        print "Error writing ",fileOutName, ": ", inFile.geterror()

def convertImage(filename = '',fileOutName = '',format='tif'):
    # open the file
    inputFile = oiio.ImageInput.open(filename)
    # check if the input file is valid
    if not inputFile:
        print 'Could not open: "' + filename + '"'
        print '\tError: "', oiio.geterror()
        return
    # get the spec of the input file
    spec = inputFile.spec()
    nchans = spec.nchannels
    # read the image and return the pixels as array type
    pixels = inputFile.read_image(oiio.FLOAT)
    # check that the pixels are ok
    if not pixels:
        print 'Could not read:', inputFile.geterror()
        return
    inputFile.close() #we're done with the file at this point
    # open the OCIO config
    config = OCIO.GetCurrentConfig()
    #"""
    transform = OCIO.ColorSpaceTransform()
    transform.setSrc('srgb8')
    transform.setDst('acescg')
    #transform.setDirection(OCIO.Constants.TRANSFORM_DIR_INVERSE)
    processor = config.getProcessor(transform)
    #"""
    """
    # get the processor to transform from srgb8 to acescg space
    processor = config.getProcessor('srgb8','acescg')
    #processor = config.getProcessor('linear','srgb8')

    """
    # apply the transform
    buf = processor.applyRGBA(pixels)
    # convert the list to an array type
    imgTrans = array('f',[0,0,0,0])
    imgTrans.fromlist(buf)
    # create an output image
    output = oiio.ImageOutput.create(fileOutName)
    # if tif format output as 16bit otherwise 8bit
    # if format != 'tif':
    #     spec.set_format(oiio.UINT8)
    # else:
    #     spec.set_format(oiio.UINT16)
    spec.set_format(oiio.HALF)
    # open and write the data transformed
    output.open(fileOutName,spec,oiio.Create)
    output.write_image(imgTrans)
    output.close()
    print 'done'

def convertWithOiioTool(fileInName = '',fileOutName = '', colorSpaceIn = 'srgb8', colorSpaceOut = 'acescg'):
    command = 'oiiotool '+ fileInName + ' --colorconvert ' + colorSpaceIn + ' ' + colorSpaceOut + ' -o ' + fileOutName
    os.system(command)
    print fileInName[fileInName.rfind('/')+1:] + ' is converted from ' + '\x1b[0;31;40m'+colorSpaceIn +'\x1b[0m'+ ' to ' + '\x1b[0;31;40m'+colorSpaceOut +'\x1b[0m'


def main():
    fileIn = '/s/prodanim/m3/assets/Character/maya/surface_texturing/surface_texturing/work/textures/armor_scales-v012/maya-armor_scales-base-BaseColor.tif'
    fileOut = '/s/prodanim/m3/assets/Character/maya/surface_texturing/surface_texturing/work/textures/armor_scales-v012/testExr.exr'
    #convertImageOIIO(fileIn,fileOut)
    # convertImage(fileIn, fileOut)
    # convertWithOiioTool(fileIn, fileOut)
    rootDir = '/s/prodanim/m3/assets/Character/maya/surface_texturing/surface_texturing/work/textures'
    destDir = '/s/prodanim/m3/assets/Character/maya/surface_texturing/surface_texturing/work/texturesAcescg'
    if not os.path.isdir(destDir):
        os.makedirs(destDir)
    for subdir, dirs, files in os.walk(rootDir):
        for file in files:
            if file.find('.tif') > 0:
                newDir = subdir.replace(rootDir, destDir)
                if not os.path.isdir(newDir):
                    os.makedirs(newDir)
                srcFile = os.path.join(subdir, file)
                destFile = os.path.join(newDir, file)
                if file.find('Color') > 0:
                    destFile = destFile.replace('.tif', '.exr')
                    convertWithOiioTool(srcFile, destFile)
                else:
                    shutil.copy(srcFile,destFile)
                    #print srcFile + '\n' + destFile + '\n'

if __name__ == '__main__':
    main()