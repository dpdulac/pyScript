#!/usr/bin/env python
# coding:utf-8
""":mod:`OpenImageIOtest` -- dummy module
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

def find_min_max(filename, output = 'both'):
    inputFile = oiio.ImageInput.open(filename)
    if not inputFile:
        print 'Could not open: "' + filename + '"'
        print '\tError: "', oiio.geterror()
        return
    spec = inputFile.spec()
    nchans = spec.nchannels
    pixels = inputFile.read_image(oiio.FLOAT)
    if not pixels:
        print 'Could not read:', inputFile.geterror()
        return
    inputFile.close() #we're done with the file at this point
    minval = pixels[0:nchans] #initialize to the first pixel value
    maxval = pixels[0:nchans]
    i = 0 #absolute index
    for z in range(spec.depth):
        for y in range(spec.height):
            for x in range(spec.width):
                for c in range(nchans):
                    if pixels[i+c] < minval[c]:
                        minval[c] = pixels[i+c]
                    if pixels[i+c] > maxval[c]:
                        maxval[c] = pixels[i+c]
                i = i + nchans #advance the index
    if output == 'min':
        return minval
    elif output == 'max':
        return maxval
    else:
        return minval,maxval

def findMinMaxSingleChannel(filename, output = 'both'):
    inputFile = oiio.ImageInput.open(filename)
    if not inputFile:
        print 'Could not open: "' + filename + '"'
        print '\tError: "', oiio.geterror()
        return
    spec = inputFile.spec()
    nchans = spec.nchannels
    pixels = inputFile.read_image(oiio.FLOAT)
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
            i = i + nchans #advance the index
    if output == 'min':
        return minval[0]
    elif output == 'max':
        return maxval[0]
    else:
        return minval[0],maxval[0]


