#!/usr/bin/env python
# coding:utf-8
""":mod:`mbChange` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2017, Mikros Image"

def renameRenderManagerLayer(prefix = 'midBlur_',shutterMode = True,renameMode = True, shutterOpen = -0.25, shutterClose = 0.0,replaceMode = False,replacePrefix = 'BlurReplace_',resolution = 'Captain Stereo Double'):
    replaceMode = not renameMode
    #make sure the prefix end with '_'
    if prefix[len(prefix)-1] != '_':
        prefix += '_'
    if replaceMode:
        if replacePrefix[len(replacePrefix)-1] != '_':
            replacePrefix += '_'
    nodeSelected = NodegraphAPI.GetAllSelectedNodes()
    renderManagerNode = None
    for node in nodeSelected:
        if node.getType() != 'RenderManager':
            nodeSelected.remove(node)
    if len(nodeSelected) > 1:
        raise NameError('Select only 1 RenderManager node')
    elif len(nodeSelected) == 0:
        nodeRender = NodegraphAPI.GetAllNodesByType('RenderManager', includeDeleted=False)
        if len(nodeRender) == 0:
            raise NameError("there is no RenderManager in the scene, create one")
        elif len(nodeRender) > 1:
            raise NameError('Select  1 RenderManager node')
        else:
            renderManagerNode = nodeRender[0]
    else:
        renderManagerNode = nodeSelected[0]

    for item in renderManagerNode.getRenderLayers():
        if renameMode:
            newName = prefix + item.getName()
            item.setName(newName)
        if replaceMode:
            itemName = item.getName()
            newName = itemName.replace(prefix,replacePrefix)
            print 'changing Renderlayer Name :' + itemName + ' to :' + newName
            item.setName(newName)
        if shutterMode:
            if newName.find('_Tech') > 0:
                continue
                #print "no change in mb for: "+ item.getName()
            else:
                groupNode = item.getGroupNode()
                changeMotionBlur(groupNode,shutterOpen = shutterOpen, shutterClose = shutterClose,resolution =resolution)

    print "Motion Blur is set to:\n shutter Open: "+ str(shutterOpen) + '\n shutter Close: ' +str(shutterClose)


def getAllNodeChild(inputNode = NodegraphAPI.GetAllNodesByType('RenderManager', includeDeleted=False), listNode = []):
    for item in inputNode:
        listNode.append(item)
        try:
            item.getChildren()
        except:
            continue
        else:
            getAllNodeChild(inputNode=item.getChildren(),listNode=listNode)

def changeMotionBlur(node = NodegraphAPI.GetAllSelectedNodes(), shutterOpen = -0.25, shutterClose = 0.0,resolution = 'Captain Stereo Double'):
    nodeRender = [node]
    listNode = []
    listPOD=[]
    getAllNodeChild(nodeRender,listNode)
    for item in listNode:
        if item.getType() == 'RenderSettings':
            listPOD.append(item)
    for item in sorted(listPOD):
        item.getParameter('args.renderSettings.shutterOpen.enable').setValue(True,0)
        item.getName(),item.getParameter('args.renderSettings.shutterOpen.value').setValue(shutterOpen,0)
        item.getParameter('args.renderSettings.shutterClose.enable').setValue(True,0)
        item.getName(),item.getParameter('args.renderSettings.shutterClose.value').setValue(shutterClose,0)
        item.getParameter('args.renderSettings.resolution.enable').setValue(True,0)
        item.getParameter('args.renderSettings.resolution.value').setValue(resolution,0)

print "renameRenderManagerLayer(prefix = 'midBlur_',shutterMode = True,renameMode = True, shutterOpen = -0.25, shutterClose = 0.0,replaceMode = False,replacePrefix = 'BlurReplace_',resolution = 'Captain Stereo Double')"