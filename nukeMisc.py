#!/usr/bin/env python
# coding:utf-8
""":mod:`nukeMisc` -- dummy module
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

def findReadNode(readNode=[],startNode = nuke.Root(),nodeType = 'Read'):
    allNodes = nuke.allNodes(group = startNode)
    for node in allNodes:
        if node.Class() == nodeType:
            readNode.append(node)
        elif node.Class() == 'Group':
            findReadNode(readNode,node,nodeType)
        else:
            continue
    return readNode

def findNodeByName(nodeByName=[],startNode = nuke.Root(), pattern = 'cu_DefocusDWATool'):
    allNodes = nuke.allNodes(group = startNode)
    for node in allNodes:
        if node.name().find(pattern) >= 0:
            nodeByName.append(node)
        elif node.Class() == 'Group':
            findNodeByName(nodeByName,node,pattern)
    return nodeByName


#node = nuke.selectedNode()
node = nuke.Root()
readNode = []
versionNumberList = 15
allReadNode = findReadNode(readNode=readNode,startNode = node,nodeType = 'Read')
for item in allReadNode:
    oldPath = item['file'].getValue()
    if oldPath.find('CHARS') > 0:
        continue
    else:
        for i in range(versionNumberList):
            ver = 'v'+str(i+1).zfill(3)
            if oldPath.find(ver) > 0:
                oldPath = oldPath.replace(ver,'v016')
        if oldPath.find('SET')> 0:
            newpath = oldPath.replace('SET','mkt_SET')
            newNumber = newpath.replace('.%04d.exr','.0113.exr')
            print oldPath + '\n' + newNumber + '\n'
            item['file'].setValue(newNumber)
            item['first'].setValue(1)
            item['last'].setValue(1)
            item['origfirst'].setValue(1)
            item['origlast'].setValue(1)

allReadNode = findReadNode(readNode=readNode,startNode = node,nodeType = 'Read')
for item in allReadNode:
    oldPath = item['file'].getValue()
    if oldPath.find('CHARS') > 0:
        continue
    else:
        if oldPath.find('Mkt_SET') > 0:
            newNumber = newpath.replace('.0113.exr','.0101.exr')
            item['file'].setValue(newNumber)

node = nuke.Root()
nodeFormat = node.format()
rootFormat = nodeFormat.name()
reformatNodes = []
allReformatNode = findReadNode(readNode=reformatNodes,startNode = node,nodeType = 'Reformat')
for item in allReformatNode:
    formatName = item['type'].setValue(0)
    item['format'].setValue(rootFormat)

rotoNodes = []
allRotoNodes = findReadNode(readNode=rotoNodes,startNode = node,nodeType = 'Roto')
for item in allRotoNodes:
    print 'adding rotoSizeConverter for: '+ item.name()
    #grab the next node
    dependentNode = item.dependent()[0]
    #if the nextnode is a radial node
    if dependentNode.Class() == 'Radial':
        #grab the node after the radial node
        nextNode = dependentNode.dependent()[0]
        #get the xpos and y pos of the radial node
        xpos = int(dependentNode['xpos'].getValue())
        ypos = int(dependentNode['ypos'].getValue())
        #import a rotosizeconvertor node
        rotoSizeNode = nuke.createNode("/s/prods/captain/assets/Library/sceneTools/tools/Gizmos/Utils/cu_rotoSizeconverter.gizmo")
        rotoSizeNode['format_1'].setValue('Captain Stereo Double')
        #set the pos of the node
        rotoSizeNode.setXYpos(xpos + 150, ypos)
        #connect the node
        rotoSizeNode.setInput(0,dependentNode)
        nextNode.setInput(0,rotoSizeNode)
        nextNode = None
    else:
        xpos = int(item['xpos'].getValue())
        ypos = int(item['ypos'].getValue())
        rotoSizeNode = nuke.createNode("/s/prods/captain/assets/Library/sceneTools/tools/Gizmos/Utils/cu_rotoSizeconverter.gizmo")
        rotoSizeNode['format_1'].setValue('Captain Stereo Double')
        rotoSizeNode.setXYpos(xpos + 150, ypos)
        rotoSizeNode.setInput(0,item)
        dependentNode.setInput(0,rotoSizeNode)

