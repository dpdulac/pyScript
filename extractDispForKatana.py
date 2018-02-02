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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PIL import Image
import OpenImageIO as oiio
import os,pprint,psutil,time
from Katana import  NodegraphAPI,UI4, ScenegraphManager,Nodes3DAPI


class extractDispUI(QWidget):
    def __init__(self):
        super(extractDispUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.mainLayout =QVBoxLayout()
        self.extractButton = QPushButton('Extract Displace')
        self.mainLayout.addWidget(self.extractButton)

        self.setLayout(self.mainLayout)

        self.extractButton.clicked.connect(self.doIt)

    def doIt(self):
        node = NodegraphAPI.GetAllSelectedNodes()
        lenNode = len(node)
        if lenNode < 1 or lenNode > 1:
            self.messageBox = QMessageBox()
            self.messageBox.setIcon(QMessageBox.Warning)
            self.messageBox.setText("Please choose a single node")
            self.messageBox.setStandardButtons(QMessageBox.Ok)
            self.messageBox.exec_()
        else :
            createKatanaNodes()
            self.close()

ex =None
def buildExtractDispUI():

    global ex
    if ex is not None:
        ex.close()
    ex= extractDispUI()
    ex. setWindowFlags(Qt.WindowStaysOnTopHint)
    ex.show()



def minMaxOIIO(filename = '', output = 'both'):
    file = oiio.ImageInput.open(filename)
    pixels = file.read_image(0,0,oiio.FLOAT)
    spec = file.spec()
    size = (spec.width,spec.height)
    rgbf = Image.frombytes("F", size, pixels)

    extrema = rgbf.getextrema()
    if output == 'min':
        return extrema[0]
    elif output == 'max':
        return extrema[1]
    else:
        return extrema


def findDispHeight(inFile = '/s/prodanim/asterix2/_sandbox/duda/fileDispFromLua.txt'):
    # nbA = 0
    # nbB = 0
    # while True:
    #     for proc in psutil.process_iter():
    #         if proc.name() == 'katanaBin':
    #             for item in proc.open_files():
    #                 if inFile == str(item.path):
    #                     nbA = nbA + 1
    #
    #     time.sleep(1)
    #
    #     for proc in psutil.process_iter():
    #         if proc.name() == 'katanaBin':
    #             for item in proc.open_files():
    #                 if inFile == str(item.path):
    #                     nbB = nbB + 1
    #     if nbA == nbB:
    #         break
    # print nbA,nbB

    test = True
    while test:
        if len(open(inFile).read()) != 0:
            test = False


    res = {} # dictionary for the fileIn
    mapList ={} # dummy to check if the value for the map hasn't be already calculated
    returnDict = {} # output dictionary
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
            if os.path.isfile(file): # check if the file exist
                # if the file hasn't be calculated before do it and put it in mapList
                if file not in mapList.keys():
                    mapHeight = minMaxOIIO(file,'max')
                    if mapHeight > dispValue:
                        dispValue = mapHeight
                    mapList[file]= dispValue
                else :
                    mapHeight = mapList[file]
                    if mapHeight > dispValue:
                        dispValue = mapHeight
            else:
                print "no map: "+file
        # only value greater than 0.0 are nescessary to set the disp bounding box
        if dispValue > 0.0:
            returnDict[key] = dispValue
        # print key, dispValue
    inputFile.close()
    pprint.pprint(returnDict)
    return returnDict

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
    # check if there is a node ('Attribute_Disp') existing if yes delete it
    # existingNode = NodegraphAPI.GetNode('Attribute_Disp')
    # if existingNode :
    #     inputNodePort = existingNode.getInputPortByIndex(0)
    #     outputNodePort = existingNode.getOutputPortByIndex(0)
    #     inputNodePort.connect(outputNodePort)
    #     existingNode.delete()
    inputFile = open(fileOut,'a')
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
    opscriptFindDispUserParamFileOut = opscriptFindDispUserParam.createChildString('fileOut',fileOut)
    opscriptFindDisp.getParameter('script.lua').setValue("local getdispMap = require 'dispFunc'\ngetdispMap.getDispMap()",0)
    opscriptFindDispInPort = opscriptFindDisp.getInputPort('i0')
    opscriptFindDispOutPort = opscriptFindDisp.getOutputPort('out')
    nodeOutPort.connect(opscriptFindDispInPort)
    opscriptFindDispOutPort.connect(nextPort)
    NodegraphAPI.SetNodePosition(opscriptFindDisp, (nodePos[0]+50,nodePos[1]-50))
    opscriptFindDispPos = NodegraphAPI.GetNodePosition(opscriptFindDisp)
    # set the view and the edit on the opscript node
    NodegraphAPI.SetNodeViewed(opscriptFindDisp, True, exclusive=True)
    NodegraphAPI.SetNodeEdited(opscriptFindDisp, True, exclusive=True)

    # dummy functions to run the opscript and create the file
    sg = ScenegraphManager.getActiveScenegraph()
    node = NodegraphAPI.GetNode( 'root' )
    time = NodegraphAPI.GetCurrentTime()
    producer = Nodes3DAPI.GetGeometryProducer( node, time)
    prod = producer.getProducerByPath('/root')
    WalkBoundAttrLocations(prod)

    # extract the dip for each map
    assetWithDisp = findDispHeight(fileOut)

    # create a stack of AttributeSet to set the disp if there is element in the dict
    if len(assetWithDisp.keys()):
        stack = NodegraphAPI.CreateNode("GroupStack", NodegraphAPI.GetRootNode())
        stack.setName('Attribute_Disp')
        stack.setChildNodeType("AttributeSet")
        listWord = ['/location/','/prop/','/location/','/character/']
        for key in assetWithDisp.keys():
            path = ''
            attributSet = stack.buildChildNode()
            attributSet.getParameter('mode').setValue('CEL',0)
            attrPath = attributSet.getParameter('celSelection')
            attributSet.getParameter('attributeType').setValue('float',0)
            # replace the word from listWord by the wildcard '/*' so to work in lighting scene
            for word in listWord:
                if key.find(word) > 1:
                    path = key.replace(word,'//*/')
                    attrPath.setValue(path,0)
                    break
                else:
                    attrPath.setValue(key,0)
            attributSet.setName(key[key.rfind('/')+1:]) # set name to the _hi
            attrValue = attributSet.getParameter('numberValue.i0')
            attrValue.setValue(assetWithDisp[key],0)
            attrName = attributSet.getParameter('attributeName')
            attrName.setValue('arnoldStatements.disp_padding',0)
        NodegraphAPI.SetNodePosition(stack,opscriptFindDispPos)
        stackInPort = stack.getInputPort('in')
        stackOutPort = stack.getOutputPort('out')
        nodeOutPort.connect(stackInPort)
        stackOutPort.connect(nextPort)
        NodegraphAPI.SetNodeViewed(stack, True, exclusive=True)
        NodegraphAPI.SetNodeEdited(stack, True, exclusive=True)
    else:  # reconnect the nodes
        nodeOutPort.connect(nextPort)
        NodegraphAPI.SetNodeViewed(node, True, exclusive=True)
        NodegraphAPI.SetNodeEdited(node, True, exclusive=True)

    # delete the opscript and the file
    opscriptFindDisp.delete()
    os.remove(fileOut)
    print 'finished'



def main():
    print "all done!!!!"
     # out = findDispHeight('/s/prodanim/asterix2/_sandbox/duda/fileDispFromLua.txt')
     # pprint.pprint(out)
    # import extractDispForKatana as disp
    # reload(disp)
    # disp.createKatanaNodes()

# if __name__ == main():
#     main()