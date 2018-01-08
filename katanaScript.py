#!/usr/bin/env python
# coding:utf-8
""":mod:`katanaScript` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2016, Mikros Animation"

from Katana import NodegraphAPI, Utils, Nodes3DAPI, ScenegraphManager

def AddGlobalGraphStateVariable(name, options):
    '''
    :param name: name of the variable
    :param options: options for the variables (i.e choice)
    :return: name of the variable created
    '''
    variablesGroup = NodegraphAPI.GetRootNode().getParameter('variables')
    variableParam = variablesGroup.createChildGroup(name)
    variableParam.createChildNumber('enable', 1)
    variableParam.createChildString('value', options[0])
    optionsParam = variableParam.createChildStringArray('options', len(options))
    for optionParam, optionValue in zip(optionsParam.getChildren(), options):
        optionParam.setValue(optionValue, 0)
    return variableParam.getName()

def addCamswitchVariable():
    '''
    :return: create a camSwitch variable so user can switch from a published cam to a user cam
    '''
    AddGlobalGraphStateVariable("camSwitch",["assetCam","userCam"])

def WalkBoundAttrLocations(producer, attribute = "bound", listValue = [], producerType = "polymesh"):
    '''
    :param producer: input node
    :param attribute: attribute to get
    :param listValue: list for value to be recuparated
    :param producerType: type of producer
    :return: list of value recuparated
    '''
    #if producer is not None and producer.getType() in ("group", "component", "assembly","polymesh") : #
    if producer is not None and producerType in ("group", "component", "assembly","polymesh"):
        if producer.getType() == producerType:
            #print producer.getFullName()
            boundAttr =  producer.getAttribute(attribute)
            if boundAttr is not None :
                listValue.append(boundAttr.getNearestSample(0))

        for child in producer.iterChildren():
            WalkBoundAttrLocations(child, attribute, listValue, producerType)
        return listValue
    else:
        print "producer or producerType not good"

def boundingBox(bound):
    xmin = []
    xmax = []
    ymin = []
    ymax = []
    zmin = []
    zmax = []
    for i in range(0,len(bound)):
        xmin.append(bound[i][0])
        xmax.append(bound[i][1])
        ymin.append(bound[i][2])
        ymax.append(bound[i][3])
        zmin.append(bound[i][4])
        zmax.append(bound[i][5])
    xmin.sort()
    xmax.sort()
    ymin.sort()
    ymax.sort()
    zmin.sort()
    zmax.sort()
    return [xmin[0],xmax[-1],ymin[0],ymax[-1],zmin[0],zmax[-1]]

def getBB(outPutType = "all"):
    '''
    :param outPutType: Chosen channel of the bbox (all -x +x -y +y -z +z)
    :return: return value bb
    '''
    node = NodegraphAPI.GetAllSelectedNodes()[0]
    graphState = NodegraphAPI.GetGraphState(0)
    producer = Nodes3DAPI.GetGeometryProducer(node, graphState)
    sg = ScenegraphManager.getActiveScenegraph()
    loc = sg.getSelectedLocations()[0]
    geoProducer = producer.getProducerByPath(loc)
    listValue = []
    if geoProducer is not None :
        WalkBoundAttrLocations(geoProducer, "bound", listValue,"polymesh")
    if outPutType == "all":
        return boundingBox(listValue)
    elif outPutType == "-x":
        return boundingBox(listValue)[0]
    elif outPutType == "+x":
        return boundingBox(listValue)[1]
    elif outPutType == "-y":
        return boundingBox(listValue)[2]
    elif outPutType == "+y":
        return boundingBox(listValue)[3]
    elif outPutType == "-z":
        return boundingBox(listValue)[4]
    elif outPutType == "+z":
        return boundingBox(listValue)[5]
    else:
        return boundingBox(listValue)

def getBBExpression(outPutType = "all",nodeName="",path="/root"):
    '''
    :param outPutType: Chosen channel of the bbox (all -x +x -y +y -z +z)
    :param nodeName: name of the node
    :param path: object path from the scene graph
    :return:
    '''
    node = NodegraphAPI.GetNode(nodeName)
    graphState = NodegraphAPI.GetGraphState(0)
    producer = Nodes3DAPI.GetGeometryProducer(node, graphState)
    #sg = ScenegraphManager.getActiveScenegraph()
    #loc = sg.getSelectedLocations()[0]
    geoProducer = producer.getProducerByPath(path)
    listValue = []
    if geoProducer is not None :
        WalkBoundAttrLocations(geoProducer, "bound", listValue,"polymesh")
    if outPutType == "all":
        return boundingBox(listValue)
    elif outPutType == "-x":
        return boundingBox(listValue)[0]
    elif outPutType == "+x":
        return boundingBox(listValue)[1]
    elif outPutType == "-y":
        return boundingBox(listValue)[2]
    elif outPutType == "+y":
        return boundingBox(listValue)[3]
    elif outPutType == "-z":
        return boundingBox(listValue)[4]
    elif outPutType == "+z":
        return boundingBox(listValue)[5]
    else:
        return boundingBox(listValue)


def getSelectedNode():
    '''
    :return: return the first selected node
    '''
    try:
        NodegraphAPI.GetAllSelectedNodes()[0]
    except:
        print "no node selected"
    else:
        return NodegraphAPI.GetAllSelectedNodes()[0]

def upNode(node):
    '''
    :param node: NodeGraph node
    :return: list of connected node upstream
    '''
    ports = node.getInputPorts()
    nodesConnected = []
    for i in ports:
        portsConnected = i.getConnectedPorts()
        for j in portsConnected:
            nodesConnected.append(j.getNode().getName())
    return nodesConnected

NodegraphAPI.SetExpressionGlobalValue("upNode", upNode)