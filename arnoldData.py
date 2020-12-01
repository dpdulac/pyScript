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

def extractDictFromAss(assPath = "/s/prodanim/ta/_sandbox/duda/assFiles/tmp/light.ass", nodeType = AI_NODE_LIGHT ):

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
        # entry = AiNodeLookUpByName('/obj/arnold_light1')
        # vv = AiNodeGetName(entry)
        # AiParamValueMap()
        # AiMsgInfo(name)
        #AiMsgInfo( data)
        pathList.append(name)
        print '\n\n'

        # iterParam = AiNodeGetUserParamIterator(node)
        # print AiUserParamIteratorFinished(iterParam)
        # while not AiUserParamIteratorFinished(iterParam):
        #     pentry = AiUserParamIteratorGetNext(iterParam)
        #     print 'haha', AiUserParamGetName(pentry)
        # AiUserParamIteratorDestroy(iterParam)

        entry = AiNodeGetNodeEntry(node)
        iterParam = AiNodeEntryGetParamIterator(entry)
        while not AiParamIteratorFinished(iterParam):
            pentry = AiParamIteratorGetNext(iterParam)
            paramName = AiParamGetName(pentry)
            if AiParamGetTypeName(AiParamGetType(pentry)) == 'ARRAY':
                array = AiNodeGetArray(node,paramName )
                type = AiArrayGetType(array)
                atom =''
                if type == AI_TYPE_MATRIX:
                    myMtx ='\n'
                    for i in range(4):
                        for j in range(4):
                            myMtx += str((AiArrayGetMtx(array,0)[i][j]))
                            if j <= 2:
                                myMtx += ' '
                            else:
                                myMtx += '\n'
                    atom = myMtx
                    print AiParamGetDefault(pentry)
                elif type == AI_TYPE_NODE:
                    atom = AiArrayGetNumElements(array)

            #print paramName, AiNodeGetArray(node,paramName )
            # para = AiNodeEntryLookUpParameter(entry, paramName)
                print paramName, atom

        AiParamIteratorDestroy(iterParam)

        print '\n\n'

    AiNodeIteratorDestroy(iter)
    AiEnd()
    return vv


print extractDictFromAss()
print 'ha'