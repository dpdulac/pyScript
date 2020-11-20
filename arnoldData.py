#!/usr/bin/env python
# coding:utf-8
""":mod: arnoldData.py
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2020.11
   
"""
from arnold import *

def extractDictFromAss(assPath = "/s/prodanim/ta/_sandbox/duda/assFiles/tmp/fullScene.ass", nodeType = AI_NODE_LIGHT ):

    """
    output a dictionary of the node in the .ass file
    """
    pathList =[]

    AiBegin()

    AiMsgSetConsoleFlags(AI_LOG_ALL)
    AiASSLoad(assPath, AI_NODE_ALL)

    iter = AiUniverseGetNodeIterator(nodeType);
    while not AiNodeIteratorFinished(iter):
        node = AiNodeIteratorGetNext(iter)
        name = AiNodeGetStr(node, "name")
        data = AiNodeGetFlt(node, 'motion_end')
        AiMsgInfo(name)
        AiMsgInfo( data)
        pathList.append(name)

    AiNodeIteratorDestroy(iter)
    AiEnd()
    return data


print extractDictFromAss()
print 'ha'