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
    vv = ''
    AiBegin()

    AiMsgSetConsoleFlags(AI_LOG_ALL)
    AiASSLoad(assPath, AI_NODE_ALL)

    iter = AiUniverseGetNodeIterator(nodeType);
    while not AiNodeIteratorFinished(iter):
        node = AiNodeIteratorGetNext(iter)
        name = AiNodeGetStr(node, "name")
        print name
        data = AiNodeGetArray(node, 'matrix')
        entry = AiNodeGetNodeEntry(node)
        # bla =AiNodeEntryGetType(entry)
        # if bla == AI_NODE_LIGHT:
        #     vv = 'good'
        # else:
        #     vv = 'bad'
        entry = AiNodeLookUpByName('/obj/arnold_light1')
        vv = AiNodeGetName(entry)
        AiParamValueMap()
        AiMsgInfo(name)
        #AiMsgInfo( data)
        pathList.append(name)
        print '\n\n'
        # entry = AiNodeGetNodeEntry(node)
        # iterParam = AiNodeEntryGetParamIterator(entry)
        # while not AiParamIteratorFinished(iterParam):
        #     pentry = AiParamIteratorGetNext(iterParam)
        #     paramName = AiParamGetName(pentry)
        #     para = AiNodeEntryLookUpParameter(entry, paramName)
        #     print paramName, AiParamGetTypeName(AiParamGetType(para))
        #
        # AiParamIteratorDestroy(iterParam)
        iterUser = AiNodeGetUserParamIterator(node)
        while not AiUserParamIteratorFinished(iterUser):
            upentry = AiUserParamIteratorGetNext(iterUser)
            print 'bb',AiUserParamGetName(upentry)
        AiUserParamIteratorDestroy(iterUser)
        print '\n\n'

    AiNodeIteratorDestroy(iter)
    AiEnd()
    return vv


print extractDictFromAss()
print 'ha'