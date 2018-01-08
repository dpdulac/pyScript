#!/usr/bin/env python
# coding:utf-8
""":mod:`burnLutExr` -- dummy module
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

import nuke
import sys
import json

def burnLut(strRes=''):
    """creation of nuke node script to convert exr image in tif 16bit or jpg using the Asterix2_film lut
        @strRes sting in format of a dictionary
        strRes is converted back to a dict using the json module.
        Each elements of the dict is composed of:
            -file path source (fileIn)
            -file path output (fileOut)
            -fileType jpg or tif
    """
    writeNodeList =[]
    strFix = strRes.replace("'","\"")
    res = json.loads(strFix)
    for key in res.keys():
        fileType = res[key]['fileType']
        fileIn = res[key]['fileIn']
        fileOut = res[key]['fileOut']
        # create a read node
        readNode = nuke.nodes.Read(file = fileIn)
        # create the color node to convert from linear space to asterix2_film space
        colorConvertNode = nuke.nodes.OCIOColorSpace(in_colorspace="linear",out_colorspace="vd/asterix2_film")
        # if tif file set the output to be 16 bit
        if fileType == "tif":
            writeNode = nuke.nodes.Write(name = 'WriteBurnLutFile', colorspace = "linear", file_type = fileType, file =fileOut )
            writeNode.knob('datatype').setValue(1)
        else:
            writeNode = nuke.nodes.Write(name = 'WriteBurnLutFile', colorspace = "linear", file_type = fileType, file =fileOut )

        colorConvertNode.setInput(0,readNode)
        writeNode.setInput(0,colorConvertNode)
        # append the write node to the list
        writeNodeList.append(writeNode)
    # for each node in the list create the image
    for node in writeNodeList:
        print 'calculating : ' + node.knob('file').getValue()
        nuke.execute(node,1,1)

dictIn = sys.argv[1]

burnLut(dictIn)
quit()



