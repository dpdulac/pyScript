#!/usr/bin/env python
# coding:utf-8
""":mod:`ocioConvertImage` -- dummy module
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

import OpenImageIO as oiio
import PyOpenColorIO as OCIO
from array import *
import os
#'/s/prodanim/asterix2/_sandbox/duda/images/catalog_export.13.id.exr'#
__FILEIN__ = '/s/prodanim/asterix2/_sandbox/duda/tmp/ocioLut/test.tif'#'/s/prodanim/asterix2/sequences/s9997/s9997_cMarketing02/confo_anim/confo_anim/work/images/s9997_cMarketing02-base-confo_anim-v014/ALL/primary/mono/s9997_cMarketing02-base-confo_anim-ALL-primary-mono.0101.exr'
__FILEOUT__  = '/s/prodanim/asterix2/_sandbox/duda/tmp/ocioLut/tmp.tif'

def convertImage(filename = __FILEIN__,fileOutName = __FILEOUT__,format='tif'):
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
    # get the processor to transform from linear to Asterix2_Film space


    newConfig = OCIO.Config()
    colorspace = OCIO.ColorSpace(name='rawInput')
    group=OCIO.GroupTransform()
    main_lut = OCIO.FileTransform('/s/prodanim/asterix2/_sandbox/duda/tmp/ocioLut/test.csp', interpolation =OCIO.Constants.INTERP_LINEAR, direction= OCIO.Constants.TRANSFORM_DIR_FORWARD)
    group.push_back(main_lut)
    colorspace.setTransform(group,OCIO.Constants.COLORSPACE_DIR_TO_REFERENCE)
    newConfig.addColorSpace(colorspace)

    colorspace = OCIO.ColorSpace(name='srgb8')
    group=OCIO.GroupTransform()
    main_lut = OCIO.FileTransform('/s/apps/packages/prods/anim/asterix2/asterix2Core/1.2.12/color/luts/lin_to_srgb_12bits.spi1d', interpolation =OCIO.Constants.INTERP_LINEAR, direction= OCIO.Constants.TRANSFORM_DIR_FORWARD)
    group.push_back(main_lut)
    colorspace.setTransform(group,OCIO.Constants.COLORSPACE_DIR_TO_REFERENCE)
    newConfig.addColorSpace(colorspace)
    colorspace = OCIO.ColorSpace(name='processedOutput')
    newConfig.addColorSpace(colorspace)
    newProccessor = newConfig.getProcessor('rawInput','srgb8',)
    # apply the transform
    buf = newProccessor.applyRGBA(pixels)

    #processor = config.getProcessor('Asterix2_Film','srgb8')
    #buf = processor.applyRGBA(pixels)
    # convert the list to an array type
    imgTrans = array('f',[0,0,0,0])
    imgTrans.fromlist(buf)
    # create an output image
    output = oiio.ImageOutput.create(__FILEOUT__)
    # if tif format output as 16bit otherwise 8bit
    if format != 'tif':
        spec.set_format(oiio.UINT8)
    else:
        spec.set_format(oiio.UINT16)
    # open and write the data transformed
    output.open(__FILEOUT__,spec,oiio.Create)
    output.write_image(imgTrans)
    output.close()




def main():
    convertImage()

if __name__ == main():
    main()
