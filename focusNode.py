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

opNodeScript = "local scale = Interface.GetOpArg('user.scale'):getValue()"\
    "\nlocal vPt = 0.5*scale"\
    "\n--plane shape"\
    "\npoints ={-vPt,-vPt,0,"\
    "\n\tvPt,-vPt,0," \
    "\n\t-vPt,vPt,0," \
    "\n\tvPt,vPt,0}"\
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
    "\nlocal bounds = {-vPt, vPt, -vPt, vPt, -vPt,vPt }"\
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
    "\n--local gbXform = GroupBuilder()"\
    "\n--gbXform:set('translate',DoubleAttribute{0.0,0.0,0.0})"\
    "\n--gbXform:set('rotateZ',DoubleAttribute{0.0,0.0,0.0,1.0})"\
    "\n--gbXform:set('rotateY',DoubleAttribute{0.0,0.0,1.0,0.0})"\
    "\n--gbXform:set('rotateX',DoubleAttribute{0.0,1.0,0.0,0.0})"\
    "\n--gbXform:set('scale',DoubleAttribute{scale,scale,scale})"\
    "\n--Interface.SetAttr('xform.interactive',gbXform:build())"\
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

def createFocusGroup(name='FocusGroup',parent = NodegraphAPI.GetRootNode(),geoPath = '/root//world/cam/DOF'):
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

    #create the parameters for groupNode
    fstopCameraMetadata = groupNode.getParameters().createChildNumber('fstop_camera_metadata',0)
    fstopCameraMetadata.setHintString("{'widget': 'checkBox', 'help': 'use the fstop inside the camera metadata'}")
    fstop = groupNode.getParameters().createChildNumber('fstop',64)
    fstop.setHintString("{'widget': 'popup', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../use_fstop_metadata', 'conditionalVisValue': '0'}, 'options': ['1.0', '1.2', '1.4', '1.7', '2.0', '2.4', '2.8', '3.3', '4.0', '4.8', '5.6', '6.7', '8.0', '9.5', '11.0', '13.0', '16.0', '19.0', '22.0', '27.0', '32.0', '38.0', '45.0', '54.0', '64.0'], 'help': 'fstop increment in half stop'}")
    fstop.setValue(64,0.0)
    #focus distance group
    fdistGroup = groupNode.getParameters().createChildGroup('focus_distance')
    fdistGroup.setHintString("{'open': 'True'}")
    methodParam = fdistGroup.createChildString('method','manual')
    methodParam.setHintString("{'widget': 'mapper', 'options': {'manual': '2', 'target': '0', 'alembic': '1', 'metadata': '3'}, 'options__order': ['target', 'alembic', 'manual', 'metadata'], 'help': 'choose between target, manual or metadata'}")
    methodParam.setValue('manual', 0.0)
    targetTestingGroup = fdistGroup.createChildGroup('target_setting')
    targetTestingGroup.setHintString("{'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../method', 'conditionalVisValue': '0'}, 'open': 'True'}")
    targetConstraintParam = targetTestingGroup.createChildNumber('target_constraint', 0)
    targetConstraintParam.setHintString("{'widget': 'checkBox', 'help': 'check to set an object as target constraint'}")
    targetConstraintObjectParam = targetTestingGroup.createChildString('target_constraint_Object', '')
    targetConstraintObjectParam.setHintString("{'widget': 'scenegraphLocation', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../target_constraint', 'conditionalVisValue': '1'}, 'help': 'target constraint object to calculate the focus distance'}")
    alembicSettingGroup = fdistGroup.createChildGroup('alembic_setting')
    alembicSettingGroup.setHintString("{'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../method', 'conditionalVisValue': '1'}, 'open': 'True'}")
    alembicPathParam = alembicSettingGroup.createChildString('alembic_path', '')
    alembicPathParam.setHintString("{'widget': 'fileInput', 'help': 'alembic object wich contains the focus distance'}")
    alembicAttributeNameParam = alembicSettingGroup.createChildString('alembic_attr_name', '')
    alembicAttributeNameParam.setHintString("{'help': 'attribute name of the alembic wich contain the focus distance\n(i.e: xform.translate)'}")
    focusDistanceParam = fdistGroup.createChildNumber('focus_distance', 10)
    focusDistanceParam.setHintString("{'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../method', 'conditionalVisValue': '2'}, 'help': 'manualy put the focus distance'}")
    


    # get the in and out port
    sendGroup = groupNode.getSendPort('in')
    returnGroup = groupNode.getReturnPort('out')

    # start pos for the node
    posX = 0.0
    posY = 100.0
    #create the planes nodes
    dictPlanes = {'nearFocusPlane':{'nodeName':'nearFocus', 'location':geoPath+'/near_focus_plane', 'color':[0.0,0.0,1.0], 'pos':(-200,-10), 'inputMerge':'i1'},
                  'focusPlane': {'nodeName': 'planeFocus', 'location': geoPath+'/focus_plane','color': [1.0, 0.0, 0.0], 'pos':(0,-10), 'inputMerge':'i2'},
                  'farFocusPlane': {'nodeName': 'farFocus', 'location': geoPath+'/far_focus_plane','color': [0.0, 1.0, 0.0], 'pos':(200,-10), 'inputMerge':'i3'}}

    # for key in dictPlanes.keys():
    #     posY -= 100.0
    #     plane = createPlane(nodeName = dictPlanes[key]['nodeName'],location = dictPlanes[key]['location'], rootNode = groupNode )
    #     plane.getParameter('user.displayColor.i0').setValue(dictPlanes[key]['color'][0], 0)
    #     plane.getParameter('user.displayColor.i1').setValue(dictPlanes[key]['color'][1], 0)
    #     plane.getParameter('user.displayColor.i2').setValue(dictPlanes[key]['color'][2], 0)
    #     NodegraphAPI.SetNodePosition(plane,(posX,posY))
    #     planeTransform = NodegraphAPI.CreateNode('Transform3D', parent=groupNode)
    #     planeTransform.getParameter('path').setValue(dictPlanes[key]['location'],0)
    #     planeTransform.getParameter('makeInteractive').setValue('Yes',0)
    #     planeTransform.setName('Transform_'+dictPlanes[key]['nodeName'])
    #     posY -= 100.0
    #     NodegraphAPI.SetNodePosition(planeTransform, (posX, posY))
    #     # connect the node
    #     plane.getInputPort('i0').connect(sendGroup)
    #     planeTransform.getInputPort('in').connect(plane.getOutputPort('out'))
    #     sendGroup = planeTransform.getOutputPort('out')
    for key in dictPlanes.keys():
        posY -= 100.0
        plane = createPlane(nodeName = dictPlanes[key]['nodeName'],location = dictPlanes[key]['location'], rootNode = groupNode )
        plane.getParameter('user.displayColor.i0').setValue(dictPlanes[key]['color'][0], 0)
        plane.getParameter('user.displayColor.i1').setValue(dictPlanes[key]['color'][1], 0)
        plane.getParameter('user.displayColor.i2').setValue(dictPlanes[key]['color'][2], 0)
        NodegraphAPI.SetNodePosition(plane,(posX,posY))
        # connect the node
        plane.getInputPort('i0').connect(sendGroup)
        sendGroup = plane.getOutputPort('out')
    sendGroup.connect(returnGroup)
    nodeToMouse(groupNode)

if __name__ == '__main__':
    main()
