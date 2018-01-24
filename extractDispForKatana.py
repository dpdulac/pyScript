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
import os,pprint,psutil,time

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
    nbA = 0
    nbB = 0
    while True:
        for proc in psutil.process_iter():
            if proc.name() == 'katanaBin':
                for item in proc.open_files():
                    if inFile == str(item.path):
                        nbA = nbA + 1

        time.sleep(5)

        for proc in psutil.process_iter():
            if proc.name() == 'katanaBin':
                for item in proc.open_files():
                    if inFile == str(item.path):
                        nbB = nbB + 1
            # for item in proc.open_files():
            #     if inFile == item.path:
            #         used = True
            #         break
            #     else:
            #         used = False
            # if used:
            #     break
        if nbA == nbB:
            break
    print nbA,nbB

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

def WalkBoundAttrLocations(producer,listPath=[]):
       if producer is not None :
           path = producer.getFullName()
           listPath.append(producer.getFullName())

           for child in producer.iterChildren():
               WalkBoundAttrLocations(child,listPath)
       else:
           print "producer or producerType not good"
       return listPath

def createKatanaNodes(fileOut = '/tmp/fileDispFromLua.txt'):
    node = NodegraphAPI.GetAllSelectedNodes()[0] # select the node
    nodePos = NodegraphAPI.GetNodePosition(node) # get the position of node
    nodeOutPort = node.getOutputPortByIndex(0) # get the output port
    nextPort = nodeOutPort.getConnectedPorts()[0] # get the first connected port from the previous node

    # create the opscript node
    root = NodegraphAPI.GetRootNode()
    opscriptFindDisp = NodegraphAPI.CreateNode('OpScript',root)
    opscriptFindDisp.setName('findDisp')
    opscriptFindDisp.getParameter('CEL').setValue('/root/world//*{hasattr("materialOverride.parameters.dsp_map")}',0)
    opscriptFindDispUserParam = opscriptFindDisp.getParameters().createChildGroup('user')
    opscriptFindDispUserParamBlocker = opscriptFindDispUserParam.createChildString('fileOut',fileOut)
    opscriptFindDisp.getParameter('script.lua').setValue("local getdispMap = require 'dispFunc'\ngetdispMap.getDispMap()",0)
    opscriptFindDispInPort = opscriptFindDisp.getInputPort('i0')
    opscriptFindDispOutPort = opscriptFindDisp.getOutputPort('out')
    nodeOutPort.connect(opscriptFindDispInPort)
    opscriptFindDispOutPort.connect(nextPort)
    NodegraphAPI.SetNodePosition(opscriptFindDisp, (nodePos[0]+50,nodePos[1]-50))

    NodegraphAPI.SetNodeViewed(opscriptFindDisp, True, exclusive=True)
    NodegraphAPI.SetNodeEdited(opscriptFindDisp, True, exclusive=True)

    sg = ScenegraphManager.getActiveScenegraph()
    node = NodegraphAPI.GetNode( 'root' )
    time = NodegraphAPI.GetCurrentTime()
    producer = Nodes3DAPI.GetGeometryProducer( node, time)
    prod = producer.getProducerByPath('/root')
    WalkBoundAttrLocations(prod)

    time.sleep(5)
    findDispHeight(fileOut)



def main():
     out = findDispHeight('/s/prodanim/asterix2/_sandbox/duda/fileDispFromLua.txt')
     pprint.pprint(out)

if __name__ == main():
    main()