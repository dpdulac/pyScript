#!/usr/bin/env python
# coding:utf-8
""":mod: focusNode.py --- Module Title
=================================

   2019.05
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""

import os, pprint, errno, argparse, sys, math, operator
from Katana import  NodegraphAPI,UI4

opNodeScript = "--plane shape"\
    "\npoints ={-0.5,-0.5,0,"\
    "\n\t0.5,-0.5,0," \
    "\n\t-0.5,0.5,0," \
    "\n\t0.5,0.5,0}"\
    "\nvertexList = {2,3,1,0}"\
    "\nstartIndex = {0,4}"\
    "\n\n-- Set the location's type to 'polymesh'"\
    "\nInterface.SetAttr('type', StringAttribute('polymesh'))"\
    "\n\n-- Create the 'geometry' group attribute"\
    "\nlocal gb = GroupBuilder()"\
    "\n--point builder"\
    "\nlocal gbPoint  = GroupBuilder()"\
    "\ngbPoint:set('P', FloatAttribute(points, 3))"\
    "\ngb:set('point', gbPoint:build())"\
    "\n\n--poly builder"\
    "\nlocal gbPoly  = GroupBuilder()"\
    "\ngbPoly:set('vertexList', IntAttribute(vertexList))"\
    "\ngbPoly:set('startIndex', IntAttribute(startIndex))"\
    "\ngb:set('poly', gbPoly:build())--build the geoetry Attr"\
    "\nInterface.SetAttr('geometry', gb:build())"\
    "\nlocal nodeName =Interface.GetOpArg('user.nodeName'):getValue()"\
    "\nInterface.SetAttr('attributeEditor.xform.exclusiveTo',StringAttribute{nodeName})"\
    "\n\n--set the bounds"\
    "\nlocal scale = Interface.GetOpArg('user.scale'):getValue()"\
    "\nlocal bounds = {-.5*scale, .5*scale, -.5*scale, .5*scale, -.5*scale,.5*scale }"\
    "\nInterface.SetAttr('bound', DoubleAttribute( bounds))"\
    "\n\n-- set the color of the primitive "\
    "\nlocal color = Interface.GetOpArg('user.displayColor'):getNearestSample(0.0)"\
    "\nInterface.SetAttr('viewer.default.drawOptions.color', FloatAttribute(color))"\
    "\nInterface.SetAttr('viewer.default.drawOptions.fill',StringAttribute('wireframe'))"\
    "\n\n--set the visibility to 0"\
    "\nInterface.SetAttr('visible',IntAttribute(0))"\
    "\nlocal message = Interface.GetOpArg('user.displayName'):getValue()"\
    "\nInterface.SetAttr('viewer.default.annotation.text', StringAttribute(message))"\
    "\nInterface.SetAttr('viewer.default.annotation.color', FloatAttribute(color))"\
    "\n\n-- set the xform"\
    "\nlocal gbXform = GroupBuilder()"\
    "\ngbXform:set('translate',DoubleAttribute{0.0,0.0,0.0})"\
    "\ngbXform:set('rotateZ',DoubleAttribute{0.0,0.0,0.0,1.0})"\
    "\ngbXform:set('rotateY',DoubleAttribute{0.0,0.0,1.0,0.0})"\
    "\ngbXform:set('rotateX',DoubleAttribute{0.0,1.0,0.0,0.0})"\
    "\ngbXform:set('scale',DoubleAttribute{scale,scale,scale})"\
    "\nInterface.SetAttr('xform.interactive',gbXform:build())"\
    "\n\n--set the rendering state"\
    "\nInterface.SetAttr('arnoldStatements.receive_shadows',IntAttribute{0})"\
    "\nInterface.SetAttr('arnoldStatements.self_shadows',IntAttribute{0})"\
    "\nInterface.SetAttr('arnoldStatements.visibility.AI_RAY_CAMERA',IntAttribute{0})"\
    "\nInterface.SetAttr('arnoldStatements.visibility.AI_RAY_SHADOW',IntAttribute{0})"\
    "\nInterface.SetAttr('arnoldStatements.visibility.AI_RAY_DIFFUSE_TRANSMIT',IntAttribute{0})"\
    "\nInterface.SetAttr('arnoldStatements.visibility.AI_RAY_SPECULAR_TRANSMIT',IntAttribute{0})"\
    "\nInterface.SetAttr('arnoldStatements.visibility.AI_RAY_VOLUME',IntAttribute{0})"\
    "\nInterface.SetAttr('arnoldStatements.visibility.AI_RAY_DIFFUSE_REFLECT',IntAttribute{0})"\
    "\nInterface.SetAttr('arnoldStatements.visibility.AI_RAY_SPECULAR_REFLECT',IntAttribute{0})"

def createPlane(nodeName = 'planeFocus',location = '/root/world/cam/focus_plane', rootNode = NodegraphAPI.GetRootNode() ):
    opscriptNode = NodegraphAPI.CreateNode('OpScript',rootNode)
    opscriptNode.setName(nodeName)
    opscriptNode.getParameter('applyWhere').setValue('at specific location',0)
    opscriptNodeParam = opscriptNode.getParameters().createChildGroup('user')
    scale = opscriptNodeParam.createChildNumber('scale', 1)
    scale.setHintString("{'slidercenter': '5.0', 'slider': 'True', 'slidermax': '10.0'}")
    #opscriptNode.getParameter('user.scale').setExpression('getParent().outputCam', True)
    opName = opscriptNodeParam.createChildString('nodeName','')
    opscriptNode.getParameter('user.nodeName').setExpression('self.getNode().getName()', True)
    displayName = opscriptNodeParam.createChildString('displayName',nodeName)
    colorName = opscriptNodeParam.createChildNumberArray('displayColor',3)
    colorName.setHintString("{'widget': 'color'}")
    opscriptNode.getParameter('user.displayColor.i0').setValue(1.0,0.0)
    NodegraphAPI.SetNodeComment(opscriptNode,"create a plane ")
    opscriptNode.getParameter('location').setValue(location,0)
    opscriptNode.getParameter('script.lua').setValue(opNodeScript,0.0)
    return opscriptNode

def nodeToMouse(nodeToselect = ''):
    # put the node under the mouse
    currentSelection = NodegraphAPI.GetAllSelectedNodes()
    for node in currentSelection:
        NodegraphAPI.SetNodeSelected(node, False)
    NodegraphAPI.SetNodeSelected(nodeToselect, True)
    # Get list of selected nodes
    nodeList = NodegraphAPI.GetAllSelectedNodes()
    # Find Nodegraph tab and float nodes
    nodegraphTab = UI4.App.Tabs.FindTopTab('Node Graph')
    if nodegraphTab:
        nodegraphTab.floatNodes(nodeList)

def createFocusGroup(name='FocusGroup',parent = NodegraphAPI.GetRootNode()):
    rootNode = parent
    # create the groupNode
    groupNode = NodegraphAPI.CreateNode('Group', rootNode)
    groupNode.setName(name)
    # add in and out port
    groupNode.addInputPort('in')
    groupNode.addOutputPort('out')
    # add attribute to switch the display of group node to normal node
    groupNodeAttrDict = {'ns_basicDisplay': 1, 'ns_iconName': ''}
    groupNode.setAttributes(groupNodeAttrDict)

    # # create the merge node
    # mergePlanes = NodegraphAPI.CreateNode('Merge', groupNode)
    # mergePlanes.setName('Merge_Planes')
    # for i in range(0, 4):
    #     mergePlanes.addInputPort('i' + str(i))
    # sendGroup = groupNode.getSendPort('in')
    # returnGroup = groupNode.getReturnPort('out')
    # mergePlanes.getInputPort('i0').connect(sendGroup)
    # mergePlanes.getOutputPort('out').connect(returnGroup)
    # centralPos = (0,0)
    #
    # #create the planes nodes
    # dictPlanes = {'nearFocusPlane':{'nodeName':'nearFocus', 'location':'/root/world/cam/near_focus_plane', 'color':[0.0,0.0,1.0], 'pos':(-200,-10), 'inputMerge':'i1'},
    #               'focusPlane': {'nodeName': 'planeFocus', 'location': '/root/world/cam/focus_plane','color': [1.0, 0.0, 0.0], 'pos':(0,-10), 'inputMerge':'i2'},
    #               'farFocusPlane': {'nodeName': 'farFocus', 'location': '/root/world/cam/far_focus_plane','color': [0.0, 1.0, 0.0], 'pos':(200,-10), 'inputMerge':'i3'}}
    #
    # for key in dictPlanes.keys():
    #     plane = createPlane(nodeName = dictPlanes[key]['nodeName'],location = dictPlanes[key]['location'], rootNode = groupNode )
    #     plane.getParameter('user.displayColor.i0').setValue(dictPlanes[key]['color'][0], 0)
    #     plane.getParameter('user.displayColor.i1').setValue(dictPlanes[key]['color'][1], 0)
    #     plane.getParameter('user.displayColor.i2').setValue(dictPlanes[key]['color'][2], 0)
    #     NodegraphAPI.SetNodePosition(plane,dictPlanes[key]['pos'])
    #     planeTransform = NodegraphAPI.CreateNode('Transform3D', parent=groupNode)
    #     planeTransform.getParameter('path').setValue(dictPlanes[key]['location'],0)
    #     planeTransform.getParameter('makeInteractive').setValue('Yes',0)
    #     planeTransform.setName('Transform_'+dictPlanes[key]['nodeName'])
    #     NodegraphAPI.SetNodePosition(planeTransform, (dictPlanes[key]['pos'][0],dictPlanes[key]['pos'][1]-150))
    #     # connect the node
    #     planeTransform.getInputPort('in').connect(plane.getOutputPort('out'))
    #     mergePlanes.getInputPort(dictPlanes[key]['inputMerge']).connect(planeTransform.getOutputPort('out'))
    #
    # NodegraphAPI.SetNodePosition(mergePlanes, (0, -310))

    # get the in and out port
    sendGroup = groupNode.getSendPort('in')
    returnGroup = groupNode.getReturnPort('out')

    # start pos for the node
    posX = 0.0
    posY = 100.0
    #create the planes nodes
    dictPlanes = {'nearFocusPlane':{'nodeName':'nearFocus', 'location':'/root/world/cam/near_focus_plane', 'color':[0.0,0.0,1.0], 'pos':(-200,-10), 'inputMerge':'i1'},
                  'focusPlane': {'nodeName': 'planeFocus', 'location': '/root/world/cam/focus_plane','color': [1.0, 0.0, 0.0], 'pos':(0,-10), 'inputMerge':'i2'},
                  'farFocusPlane': {'nodeName': 'farFocus', 'location': '/root/world/cam/far_focus_plane','color': [0.0, 1.0, 0.0], 'pos':(200,-10), 'inputMerge':'i3'}}

    for key in dictPlanes.keys():
        posY -= 100.0
        plane = createPlane(nodeName = dictPlanes[key]['nodeName'],location = dictPlanes[key]['location'], rootNode = groupNode )
        plane.getParameter('user.displayColor.i0').setValue(dictPlanes[key]['color'][0], 0)
        plane.getParameter('user.displayColor.i1').setValue(dictPlanes[key]['color'][1], 0)
        plane.getParameter('user.displayColor.i2').setValue(dictPlanes[key]['color'][2], 0)
        NodegraphAPI.SetNodePosition(plane,(posX,posY))
        planeTransform = NodegraphAPI.CreateNode('Transform3D', parent=groupNode)
        planeTransform.getParameter('path').setValue(dictPlanes[key]['location'],0)
        planeTransform.getParameter('makeInteractive').setValue('Yes',0)
        planeTransform.setName('Transform_'+dictPlanes[key]['nodeName'])
        posY -= 100.0
        NodegraphAPI.SetNodePosition(planeTransform, (posX, posY))
        # connect the node
        plane.getInputPort('i0').connect(sendGroup)
        planeTransform.getInputPort('in').connect(plane.getOutputPort('out'))
        sendGroup = planeTransform.getOutputPort('out')
    sendGroup.connect(returnGroup)
    nodeToMouse(groupNode)

if __name__ == '__main__':
    main()
