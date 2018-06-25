#!/usr/bin/env python
# coding:utf-8
""":mod: createContactSheet --- Module Title
=================================

   2018.06
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""

import nuke
from nukeCore.nodes import sequenceGroup
import sys, pprint,ast,os


input = sys.argv[1]

res = ast.literal_eval(input)
allWriteNode = []
for key in res.keys():
    if not os.path.isdir(res[key]['outDir']):
        os.makedirs(res[key]['outDir'])
    seq = res[key]['seq']
    task = res[key]['task']
    outFile = res[key]['fileOut']
    format = res[key]['fileType']
    showTask = res[key]['showTask']
    status = res[key]['status']
    name = res[key]['name']
    label= res[key]['showLabel']
    version = res[key]['version']
    cutOrder = res[key]['cutOrder']
    artist = res[key]['artist']
    outDir = res[key]['outDir']
    nbShots = res[key]['nbShots']

    intNb = nbShots/5
    floatNb = nbShots/5.0
    if floatNb-intNb > 0:
        intNb += 1
    sequenceGroupNode = sequenceGroup.create()
    sequenceGroupNode['sequence'].setValue(seq)
    sequenceGroupNode['task'].setValue(task)
    sequenceGroupNode['outputMode'].setValue('contactSheet')
    sequenceGroupNode['Rebuild'].execute()
    sequenceGroupNode['RowCol'].setValue([intNb, 5])
    sequenceGroupNode['Resolution'].setValue([5*2048,intNb*858])
    sequenceGroupNode['showName'].setValue(name)
    sequenceGroupNode['showStatus'].setValue(status)
    sequenceGroupNode['showTask'].setValue(showTask)
    sequenceGroupNode['showLabel'].setValue(label)
    sequenceGroupNode['showVersion'].setValue(version)
    sequenceGroupNode['showArtist'].setValue(artist)
    sequenceGroupNode['showCutOrder'].setValue(cutOrder)

    colorConvertNode = nuke.nodes.OCIOColorSpace(in_colorspace="Linear", out_colorspace="Lut")
    colorConvertNode.setInput(0,sequenceGroupNode)

    if format == 'jpg':
        writeNode = nuke.nodes.Write(name=seq + "WriteLutBurn", colorspace="linear", file_type="jpeg",_jpeg_sub_sampling="4:2:2", file=outFile)
        writeNode['_jpeg_quality'].setValue(0.75)
    elif format == 'tif':
        writeNode = nuke.nodes.Write(name = seq + "WriteLutBurn", colorspace = "linear", file_type = "tiff",file =outFile)
        writeNode['datatype'].setValue('16 bit')
    else:
        writeNode = nuke.nodes.Write(name=seq + "WriteLutBurn", colorspace="linear", file_type="exr", file=outFile)
    writeNode['use_limit'].setValue(1)
    if format is not 'exr':
        writeNode.setInput(0,colorConvertNode)
    else:
        writeNode.setInput(0, sequenceGroupNode)
    allWriteNode.append(writeNode)
    nuke.scriptSave(outDir + seq + '_contactSheet.nk')

masterNukeFile = '/tmp/tmpContactSheet.nk'
nuke.scriptSave(masterNukeFile)
fRange = nuke.FrameRanges('1-1')
nuke.executeMultiple(tuple(allWriteNode), fRange, ['left'])
os.remove(masterNukeFile)



