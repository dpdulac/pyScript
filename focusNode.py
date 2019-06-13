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

def createParam(groupNode = NodegraphAPI.GetRootNode()):
    fstopCameraMetadataParam = groupNode.getParameters().createChildNumber('fstop_camera_metadata', 0)
    fstopCameraMetadataParam.setHintString("{'widget': 'checkBox', 'help': 'use the fstop inside the camera metadata'}")
    fstopParam = groupNode.getParameters().createChildNumber('fstop', 64)
    fstopParam.setHintString(
        "{'widget': 'popup', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../fstop_camera_metadata', 'conditionalVisValue': '0'}, 'options': ['1.0', '1.2', '1.4', '1.7', '2.0', '2.4', '2.8', '3.3', '4.0', '4.8', '5.6', '6.7', '8.0', '9.5', '11.0', '13.0', '16.0', '19.0', '22.0', '27.0', '32.0', '38.0', '45.0', '54.0', '64.0'], 'help': 'fstop increment in half stop'}")
    fstopParam.setValue(64, 0.0)
    # focus distance group
    fdistGroup = groupNode.getParameters().createChildGroup('focus_distance')
    fdistGroup.setHintString("{'open': 'True'}")
    methodParam = fdistGroup.createChildString('method', 'manual')
    methodParam.setHintString(
        "{'widget': 'mapper', 'options': {'manual': '2', 'target': '0', 'alembic': '1', 'metadata': '3'}, 'options__order': ['target', 'alembic', 'manual', 'metadata'], 'help': 'choose between target, manual or metadata'}")
    methodParam.setValue('metadata', 0.0)
    targetTestingGroup = fdistGroup.createChildGroup('target_setting')
    targetTestingGroup.setHintString(
        "{'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../method', 'conditionalVisValue': '0'}, 'open': 'True'}")
    targetConstraintParam = targetTestingGroup.createChildNumber('target_constraint', 0)
    targetConstraintParam.setHintString("{'widget': 'checkBox', 'help': 'check to set an object as target constraint'}")
    targetConstraintObjectParam = targetTestingGroup.createChildString('target_constraint_Object', '')
    targetConstraintObjectParam.setHintString(
        "{'widget': 'scenegraphLocation', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../target_constraint', 'conditionalVisValue': '1'}, 'help': 'target constraint object to calculate the focus distance'}")
    alembicSettingGroup = fdistGroup.createChildGroup('alembic_setting')
    alembicSettingGroup.setHintString(
        "{'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../method', 'conditionalVisValue': '1'}, 'open': 'True'}")
    alembicPathParam = alembicSettingGroup.createChildString('alembic_path', '')
    alembicPathParam.setHintString("{'widget': 'fileInput', 'help': 'alembic object wich contains the focus distance'}")
    alembicAttributeNameParam = alembicSettingGroup.createChildString('alembic_attr_name', '')
    alembicAttributeNameParam.setHintString(
        "{'help': 'attribute name of the alembic wich contain the focus distance\n(i.e: xform.translate)'}")
    focusDistanceParam = fdistGroup.createChildNumber('focus_distance', 10)
    focusDistanceParam.setHintString(
        "{'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../method', 'conditionalVisValue': '2'}, 'help': 'manualy put the focus distance'}")
    # arnold render 3D
    render3DDOFParam = groupNode.getParameters().createChildNumber('render_3D_DOF', 0)
    render3DDOFParam.setHintString(
        "{'widget': 'boolean', 'help': 'If yes Arnold will render the DOF in 3D and the data will be pushed to the metadata of the primary pass if no only the data will be pushed to the metadata of the primary pass'}")
    lensSettingGroup = groupNode.getParameters().createChildGroup('DOF_settings_3D')
    lensSettingGroup.setHintString(
        "{'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../render_3D_DOF', 'conditionalVisValue': '1'}, 'open': 'True'}")
    apertureBladeParam = lensSettingGroup.createChildNumber('aperture_blades', 0)
    apertureBladeParam.setHintString("{'int': 'True', 'max': '1.0', 'slidermax': '12.0', 'slider': 'True'}")
    apertureAspectRatioParam = lensSettingGroup.createChildNumber('aperture_aspect_ratio', 1)
    apertureAspectRatioParam.setHintString(
        "{'slidercenter': '1.0', 'slider': 'True', 'slidermax': '2.0', 'slidermin': '0.0'}")
    apertureBladeCurvatureParam = lensSettingGroup.createChildNumber('aperture_blade_Curvature', 0)
    apertureBladeCurvatureParam.setHintString("{'slider': 'True'}")
    apertureRotationParam = lensSettingGroup.createChildNumber('aperture_rotation', 0)
    apertureRotationParam.setHintString("{'slider': 'True', 'slidermax': '360.0'}")
    flatFieldFocusParam = lensSettingGroup.createChildNumber('flat_field_focus', 0)
    flatFieldFocusParam.setHintString("{'widget': 'boolean'}")
    #advanced settings
    advancedSettigsGroup = groupNode.getParameters().createChildGroup('advanced_settings')
    advancedSettigsGroup.setHintString("{'help': 'edit advanced setting like name, color and path of the geometry plane representing the focus plane'}")
    CoCParam = advancedSettigsGroup.createChildNumber('Coc', 0.013)
    CoCParam.setHintString("{'widget': 'popup', 'options': ['0.013', '0.025', '0.035', '0.05'], 'help': 'Circle of confusion (https://improvephotography.com/53601/conquering-the-circle-of-confusion-for-photography/)'}")
    CoCParam.setValue(0.013,0.0)
    overrideFocalLengthParam = advancedSettigsGroup.createChildNumber('override_focal_length',0)
    overrideFocalLengthParam.setHintString("{'widget': 'checkBox', 'helpAlert': 'warning', 'help': 'check to override the fov this will not change the fov of the camera but change the calculations of DOF'}")
    focalLenghtParam = advancedSettigsGroup.createChildNumber('focal_length', 50)
    focalLenghtParam.setHintString("{'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../override_focal_length', 'conditionalVisValue': '1'}, 'help': 'fov used for calculation of DOF'}")
    #camera group in advanced settings
    cameraPathGroup = advancedSettigsGroup.createChildGroup('camera_path')
    cameraPathGroup.setHintString("{'help': 'camera to use for calculate the DOF'}")
    changeCameraParam = cameraPathGroup.createChildNumber('change_camera', 0)
    changeCameraParam.setHintString("{'widget': 'checkBox', 'help': 'unlock the camera field to change camera'}")
    cameraParam = cameraPathGroup.createChildString('camera','/root/world/cam/stereoCameraLeft/stereoCameraLeftShape')
    cameraParam.setHintString("{'conditionalLockOps': {'conditionalLockValue': '0', 'conditionalLockOp': 'equalTo', 'conditionalLockPath': '../change_camera'}, 'widget': 'scenegraphLocation', 'help': 'camera path to use for DOF calculation'}")
    #geometry group in advanced setting
    geometrySettingsGroup = advancedSettigsGroup.createChildGroup('geometry_settings')
    geometrySettingsGroup.setHintString("{'help': 'setting for name,color and path of the focus planes and target_focus'}")
    geometryPathParam = geometrySettingsGroup.createChildString('geometry_path','/root/world/cam/DOF')
    geometryPathParam.setHintString("{'widget': 'scenegraphLocation', 'help': 'path where to put the geometry planes representing the DOF'}")
    #near focus plane geometry setting
    nearFocusPlaneNameParam = geometrySettingsGroup.createChildString('near_focus_plane_name','nearFocusPlane')
    nearFocusPlaneNameParam.setHintString("{'help': 'name for the near focus plane'}")
    nearFocusPlaneColorParam = geometrySettingsGroup.createChildNumberArray('near_focus_plane_color',3)
    nearFocusPlaneColorParam.setHintString("{'widget': 'color', 'help': 'near focus plane color'}")
    groupNode.getParameter('advanced_settings.geometry_settings.near_focus_plane_color.i0').setValue(0,0.0)
    groupNode.getParameter('advanced_settings.geometry_settings.near_focus_plane_color.i1').setValue(1, 0.0)
    groupNode.getParameter('advanced_settings.geometry_settings.near_focus_plane_color.i2').setValue(0, 0.0)
    #focus plane geometry setting
    focusPlaneNameParam = geometrySettingsGroup.createChildString('focus_plane_name', 'focusPlane')
    focusPlaneNameParam.setHintString("{'help': 'name for the focus plane'}")
    focusPlaneColorParam = geometrySettingsGroup.createChildNumberArray('focus_plane_color', 3)
    focusPlaneColorParam.setHintString("{'widget': 'color', 'help': 'focus plane color'}")
    groupNode.getParameter('advanced_settings.geometry_settings.focus_plane_color.i0').setValue(1, 0.0)
    groupNode.getParameter('advanced_settings.geometry_settings.focus_plane_color.i1').setValue(0, 0.0)
    groupNode.getParameter('advanced_settings.geometry_settings.focus_plane_color.i2').setValue(0, 0.0)
    #far focus plane geometry setting
    farFocusPlaneNameParam = geometrySettingsGroup.createChildString('far_focus_plane_name', 'farFocusPlane')
    farFocusPlaneNameParam.setHintString("{'help': 'name for the far focus plane'}")
    farFocusPlaneColorParam = geometrySettingsGroup.createChildNumberArray('far_focus_plane_color', 3)
    farFocusPlaneColorParam.setHintString("{'widget': 'color', 'help': 'far focus plane color'}")
    groupNode.getParameter('advanced_settings.geometry_settings.far_focus_plane_color.i0').setValue(0, 0.0)
    groupNode.getParameter('advanced_settings.geometry_settings.far_focus_plane_color.i1').setValue(0, 0.0)
    groupNode.getParameter('advanced_settings.geometry_settings.far_focus_plane_color.i2').setValue(1, 0.0)
    # focus plane scaling
    scalePlaneGangParam = geometrySettingsGroup.createChildNumber('scale_plane_gang', 0)
    scalePlaneGangParam.setHintString("{'widget': 'checkBox', 'help': 'if on scale all the plane uniformaly if off each plane can be scale independently'}")
    scalePlaneGangParam.setValue(1.0,0.0)
    scalePlaneParam = geometrySettingsGroup.createChildNumber('scale_focus_planes',10)
    scalePlaneParam.setHintString("{'slider': 'True', 'slidermax': '100.0', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../scale_plane_gang', 'conditionalVisValue': '1'}, 'help': 'scale all the planes uniformaly'}")
    nearFocusPlaneScaleParam = geometrySettingsGroup.createChildNumber('near_focus_plane_scale',10)
    nearFocusPlaneScaleParam.setHintString("{'slider': 'True', 'slidermax': '100.0', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../scale_plane_gang', 'conditionalVisValue': '0'}, 'help': 'scale the near focus plane'}")
    focusPlaneScaleParam = geometrySettingsGroup.createChildNumber('focus_plane_scale', 10)
    focusPlaneScaleParam.setHintString(
        "{'slider': 'True', 'slidermax': '100.0', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../scale_plane_gang', 'conditionalVisValue': '0'}, 'help': 'scale the focus plane'}")
    farFocusPlaneScaleParam = geometrySettingsGroup.createChildNumber('far_focus_plane_scale', 10)
    farFocusPlaneScaleParam.setHintString(
        "{'slider': 'True', 'slidermax': '100.0', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../scale_plane_gang', 'conditionalVisValue': '0'}, 'help': 'scale the far focus plane'}")
    # target geometry settings
    targetNameParam = geometrySettingsGroup.createChildString('target_name', 'focusTarget')
    targetNameParam.setHintString("{'help': 'name for the target focus '}")
    targetColorParam = geometrySettingsGroup.createChildNumberArray('target_color', 3)
    targetColorParam.setHintString("{'widget': 'color', 'help': 'target color'}")
    groupNode.getParameter('advanced_settings.geometry_settings.target_color.i0').setValue(1, 0.0)
    groupNode.getParameter('advanced_settings.geometry_settings.target_color.i1').setValue(1, 0.0)
    groupNode.getParameter('advanced_settings.geometry_settings.target_color.i2').setValue(0, 0.0)
    scaleTargetParam = geometrySettingsGroup.createChildNumber('scale_target', 10)
    scaleTargetParam.setHintString("{'slider': 'True', 'slidermax': '100.0', 'help': 'scale of target'}")



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
    createParam(groupNode)

    # get the in and out port
    sendGroup = groupNode.getSendPort('in')
    returnGroup = groupNode.getReturnPort('out')

    # start pos for the node
    posX = 0.0
    posY = 100.0
    #create the planes nodes
    expressionBase = 'getParam(self.getNode().getParent().getName()+".advanced_settings.geometry_settings.'

    dictPlanes = {'nearFocusPlane': {'nodeName': 'nearFocusPlane', 'location': geoPath + '/near_focus_plane','expressionName': expressionBase+'near_focus_plane_name")',
                                     'expressionColor': expressionBase+'near_focus_plane_color")', 'pos': (-200, -10), 'inputMerge': 'i1'},
                  'focusPlane': {'nodeName': 'focusPlane', 'location': geoPath + '/focus_plane', 'expressionName': expressionBase+'focus_plane_name")',
                                 'expressionColor': expressionBase+'focus_plane_color")', 'pos': (0, -10), 'inputMerge': 'i2'},
                  'farFocusPlane': {'nodeName': 'farFocusPlane', 'location': geoPath + '/far_focus_plane', 'expressionName': expressionBase+'far_focus_plane_name")',
                                    'expressionColor': expressionBase+'far_focus_plane_color")', 'pos': (200, -10), 'inputMerge': 'i3'}}

    for key in dictPlanes.keys():
        posY -= 100.0
        plane = createPlane(nodeName = dictPlanes[key]['nodeName'],location = dictPlanes[key]['location'], rootNode = groupNode )
        plane.getParameter('user.displayColor').setExpression(dictPlanes[key]['expressionColor'],True)
        plane.getParameter('user.displayName').setExpression(dictPlanes[key]['expressionName'], True)
        NodegraphAPI.SetNodePosition(plane,(posX,posY))
        # connect the node
        plane.getInputPort('i0').connect(sendGroup)
        sendGroup = plane.getOutputPort('out')
    sendGroup.connect(returnGroup)
    nodeToMouse(groupNode)

if __name__ == '__main__':
    main()
