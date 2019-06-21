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

opNodeScriptTarget = "local scale = Interface.GetOpArg('user.scale'):getValue()"\
    "\nlocal vPt = 0.5*scale"\
    "\n--plane shape"\
    "\nlocal points ={ 0,-vPt,0,"\
    "\n\t\t0,vPt,0," \
    "\n\t\t0,0,-vPt," \
    "\n\t\t0,0,vPt,"\
    "\n\t\t-vPt,0,0,"\
    "\n\t\tvPt,0,0}"\
    "\nlocal numVertices = {2,2,2}"\
    "\nlocal knots = 0"\
    "\nlocal constantWitdth = 0.1"\
    "\nlocal degree = 0"\
    "\nlocal closed = 0"\
    "\nlocal basis = 0"\
    "\n\n-- Set the location's type to 'polymesh'"\
    "\nInterface.SetAttr('type', StringAttribute('curves'))"\
    "\n\n-- Create the 'geometry' group attribute"\
    "\nlocal gb = GroupBuilder()"\
    "\n--point builder"\
    "\nlocal gbPoint  = GroupBuilder()"\
    "\ngbPoint:set('P', FloatAttribute(points, 3))"\
    "\ngb:set('point', gbPoint:build())"\
    "\n\n--curve builder"\
    "\ngb:set('numVertices', IntAttribute(numVertices))"\
    "\ngb:set('knots', FloatAttribute(knots))"\
    "\ngb:set('constantWitdth',FloatAttribute(constantWitdth))"\
    "\ngb:set('degree ',IntAttribute(degree))"\
    "\ngb:set('closed',IntAttribute(closed))"\
    "\ngb:set('basis',IntAttribute(basis))"\
    "\nInterface.SetAttr('geometry', gb:build())"\
    "\n--local nodeName =Interface.GetOpArg('user.nodeName'):getValue()"\
    "\n--Interface.SetAttr('attributeEditor.xform.exclusiveTo',StringAttribute{nodeName})"\
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
    "\n--local nodeName =Interface.GetOpArg('user.nodeName'):getValue()"\
    "\n--Interface.SetAttr('attributeEditor.xform.exclusiveTo',StringAttribute{nodeName})"\
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

calculFocusPlane = "--- Convenience function to retrieve a global transform matrix for a given"\
    "\n-- location path"\
    "\nfunction getXFormMatrix(locationPath)"\
    "\n\tlocal xformAttr = Interface.GetGlobalXFormGroup(locationPath)"\
    "\n\tlocal matAttr = XFormUtils.CalcTransformMatrixAtTime(xformAttr, 0.0)" \
    "\n\tlocal matData = matAttr:getNearestSample(0.0)"\
    "\n\tlocal mat = Imath.M44d(matData)"\
    "\n\treturn mat"\
    "\nend"\
    "\n\nfunction calcMatrix(distance, mat,aspectRatio,fov)"\
    "\n\tlocal width = 2 * distance* math.tan(math.rad(fov)/2)"\
    "\n\tlocal height = width/aspectRatio"\
    "\n\tlocal scale = Imath.V3d(width,height,1)"\
    "\n\tlocal trans = Imath.V3d(0.0,0.0,-distance)"\
    "\n\tmat:translate(trans)"\
    "\n\tmat:scale(scale)"\
    "\n\treturn mat"\
    "\nend"\
    "\n\n--get the cam"\
    "\nlocal camPath = Interface.GetOpArg('user.camPath'):getValue()"\
    "\nlocal fov = Interface.GetAttr('geometry.fov',camPath):getValue()"\
    "\nlocal filmAspectRatio = Interface.GetOpArg('user.filmAspectRatio'):getValue()"\
    "\n\n--set the fStop for calculation"\
    "\nlocal fStop = 0.0"\
    "\nlocal fStopMetadata = tonumber(Interface.GetOpArg('user.fstopMetadata'):getValue())"\
    "\nlocal fStopUser = Interface.GetOpArg('user.fstop'):getValue()"\
    "\n-- set fStop to metadata if True else use user fStop"\
    "\nif fStopMetadata == 1 then"\
    "\n\tfStop = tonumber(Interface.GetAttr('info.abcCamera.fStop',camPath):getValue())"\
    "\nelse"\
    "\n\tfStop = fStopUser "\
    "\nend"\
    "\n\n--set the focalLength for calculation"\
    "\nlocal fol = 0.0"\
    "\nlocal overrideFocalLength = Interface.GetOpArg('user.overrideFocalLength'):getValue()"\
    "\nlocal userFocalLength = (Interface.GetOpArg('user.userFocalLength'):getValue())/100.0"\
    "\nif overrideFocalLength == 1 then"\
    "\n\tfol = userFocalLength"\
    "\nelse"\
    "\n\t-- retrieve the value of fol in metadata if not exist calculate in function of fov"\
    "\n\tfolValue = Interface.GetAttr('info.abcCamera.focalLength',camPath)"\
    "\n\tif folValue ~= nil then"\
    "\n\t\tfol = tonumber(folValue:getValue())/100.0"\
    "\n\telse"\
    "\n\t\tlocal hoA = Interface.GetAttr('info.abcCamera.horizontalAperture',camPath):getValue()*10"\
    "\n\t\tfol = (hoA/(2*math.tan(math.rad(fov)/2)))/100.0"\
    "\n\tend"\
    "\nend"\
    "\n\n--calculate the dist focus"\
    "\n-- Retrieve the global transform for camera "\
    "\nlocal CamXFormat = getXFormMatrix(camPath)"\
    "\n-- get the method"\
    "\nlocal method = tonumber(Interface.GetOpArg('user.method'):getValue())"\
    "\nlocal nfpPath = Interface.GetOpArg('user.nearFocusPlane'):getValue()"\
    "\nlocal focusPlanePath = Interface.GetOpArg('user.focusPlanePath'):getValue()"\
    "\nlocal ffpPath = Interface.GetOpArg('user.farFocusPlane'):getValue()"\
    "\nlocal targetPath = Interface.GetOpArg('user.focusTarget'):getValue()"\
    "\nlocal dist = 10.0"\
    "\nlocal inputLoc = Interface.GetInputLocationPath()"\
    "\nif (inputLoc == focusPlanePath or inputLoc == nfpPath or inputLoc == ffpPath or inputLoc == targetPath or inputLoc == '/root') then"\
    "\n\tif method == 0 then"\
    "\n\t\tlocal targetXFormMat = Imath.M44d()"\
    "\n\t\t--if target constraint is on"\
    "\n\t\tif (Interface.GetOpArg('user.targetConstraint'):getValue() == 1 ) then"\
    "\n\t\t\t-- get the path of the target object"\
    "\n\t\t\tlocal targetConstraintObjectPath = Interface.GetOpArg('user.targetConstraintObject'):getValue()"\
    "\n\t\t\ttargetXFormMat = getXFormMatrix(targetConstraintObjectPath)"\
    "\n\t\t\t-- set the target pos to the target object"\
    "\n\t\t\tInterface.SetAttr('xform.group0.matrix', DoubleAttribute(targetXFormMat:toTable(), 4))"\
    "\n\t\telse"\
    "\n\t\t\tlocal tmpMat = Imath.M44d()"\
    "\n\t\t\tInterface.SetAttr('xform.group0.matrix', DoubleAttribute(tmpMat:toTable(), 4))"\
    "\n\t\t\ttargetXFormMat = getXFormMatrix(targetPath)"\
    "\n\t\tend"\
    "\n\t\t-- Calculate the position for camera and target locations"\
    "\n\t\tlocal targetPoint = Imath.V3d() * targetXFormMat"\
    "\n\t\tlocal camPos = Imath.V3d() * CamXFormat"\
    "\n\t\tlocal dir = camPos - targetPoint"\
    "\n\t\tdist = Imath.V3d().length(dir)"\
    "\n\n\telseif method == 1 then"\
    "\n\t\tlocal alembicPath = Interface.GetOpArg('user.alembicPath'):getValue()"\
    "\n\t\tlocal alembicAttr = Interface.GetOpArg('user.alembicAttr'):getValue()"\
    "\n\t\tlocal alembicName = Interface.GetOpArg('user.alembicName'):getValue()"\
    "\n\t\tif alembicAttr == ''  or alembicName == '' then "\
    "\n\t\t\tdist = 20.0"\
    "\n\t\telse"\
    "\n\t\t\tlocal alembicObjName = alembicPath..'/'..Interface.GetPotentialChildren(alembicPath):getNearestSample(0)[1]"\
    "\n\t\t\tdist = Interface.GetAttr(alembicAttr,alembicObjName):getValue()"\
    "\n\t\tend"\
    "\n\n\telseif method == 2 then"\
    "\n\t\tdist = Interface.GetOpArg('user.focusDistance'):getValue()"\
    "\n\telse"\
    "\n\t\tdist = Interface.GetAttr('info.abcCamera.focusDistance',camPath):getValue()"\
    "\n\tend"\
    "\n\t--set the scaling and pos for the focus plane"\
    "\n\tif inputLoc == focusPlanePath then"\
    "\n\t\tlocal text = Interface.GetAttr('viewer.default.annotation.text'):getValue()"\
    "\n\t\tlocal newText = text..' dist= '..tostring(dist)"\
    "\n\t\tInterface.SetAttr('viewer.default.annotation.text',StringAttribute(newText))"\
    "\n\t\tlocal matFplane = calcMatrix(dist, CamXFormat,filmAspectRatio,fov)"\
    "\n\t\tInterface.SetAttr('xform.group0.matrix', DoubleAttribute(matFplane:toTable(), 16))"\
    "\n\tend"\
    "\n\n\t--calculate the close and far plane"\
    "\n\tlocal coc = tonumber(Interface.GetOpArg('user.CoC'):getValue()) / 100.0"\
    "\n\tlocal dof = 0.0"\
    "\n\tlocal hyperfocal = math.pow(fol, 2) / (coc * fStop)"\
    "\n\tlocal nfp = dist * hyperfocal / (hyperfocal + dist)"\
    "\n\tlocal ffp = dist * hyperfocal / (hyperfocal - dist)"\
    "\n\tif dist > hyperfocal then"\
    "\n\t\tffp = 99999999999999999999.0"\
    "\n\t\tdof = 99999999999999999999.0"\
    "\n\telse "\
    "\n\t\tdof = 2 * hyperfocal * math.pow(dist, 2) / (math.pow(hyperfocal, 2) - math.pow(dist, 2))"\
    "\n\tend"\
    "\n\n\t--set the near focus plane"\
    "\n\tif inputLoc == nfpPath then"\
    "\n\t--set the scaling"\
    "\n\t\tlocal matnFplane = calcMatrix(nfp, CamXFormat,filmAspectRatio,fov)"\
    "\n\t\tInterface.SetAttr('xform.group0.matrix', DoubleAttribute(matnFplane:toTable(), 16))"\
    "\n\tend"\
    "\n\n\t--set the far focus plane"\
    "\n\tif inputLoc == ffpPath then"\
    "\n\t\t--set the scaling and translate"\
    "\n\t\tlocal matfFplane = calcMatrix(ffp, CamXFormat,filmAspectRatio,fov)"\
    "\n\t\tInterface.SetAttr('xform.group0.matrix', DoubleAttribute(matfFplane:toTable(), 16))"\
    "\n\tend"\
    "\n\n\tif inputLoc == '/root' then"\
    "\n\t\t--set the primary header exr with all the DOF values"\
    "\n\t\tlocal path = 'renderSettings.outputs.primary.rendererSettings.exrheaders.DOF/' "\
    "\n\t\tlocal render3D = Interface.GetOpArg('user.render3D'):getValue()"\
    "\n\t\tInterface.SetAttr(path..'hyperfocal', FloatAttribute(hyperfocal))"\
    "\n\t\tInterface.SetAttr(path..'near_focus_plane', FloatAttribute(nfp))"\
    "\n\t\tInterface.SetAttr(path..'far_focus_plane', FloatAttribute(ffp))"\
    "\n\t\tInterface.SetAttr(path..'depth_of_field', FloatAttribute(dof))"\
    "\n\t\tInterface.SetAttr(path..'focus_distance', FloatAttribute(dist))"\
    "\n\t\tInterface.SetAttr(path..'fStop', FloatAttribute(fStop))"\
    "\n\t\tInterface.SetAttr(path..'focal', FloatAttribute(fol*100.0))"\
    "\n\t\t-- if render DOF via arnold set the arnold camera and add the data to metadata"\
    "\n\t\tif render3D == 1 then"\
    "\n\t\t\tlocal apertureRatio = Interface.GetOpArg('user.apertureAspectRatio'):getValue()"\
    "\n\t\t\tlocal apertureBlades = Interface.GetOpArg('user.apertureBlades'):getValue()"\
    "\n\t\t\tlocal apertureCurvature = Interface.GetOpArg('user.apertureBladeCurvature'):getValue()"\
    "\n\t\t\tlocal apertureRot = Interface.GetOpArg('user.apertureRotation'):getValue()"\
    "\n\t\t\tlocal flatFieldFocus = Interface.GetOpArg('user.flatFieldFocus'):getValue()"\
    "\n\t\t\tInterface.SetAttr(path..'aperture_blades', IntAttribute(apertureBlades))"\
    "\n\t\t\tInterface.SetAttr(path..'aperture_ratio', FloatAttribute(apertureRatio))"\
    "\n\t\t\tInterface.SetAttr(path..'aperture_curvature_blade', FloatAttribute(apertureCurvature))"\
    "\n\t\t\tInterface.SetAttr(path..'aperture_rotation', FloatAttribute(apertureRot))"\
    "\n\t\t\tInterface.SetAttr('arnoldGlobalStatements.focus_distance',FloatAttribute(dist))"\
    "\n\t\t\tInterface.SetAttr('arnoldGlobalStatements.aperture_size',FloatAttribute(1/fStop))"\
    "\n\t\t\tInterface.SetAttr('arnoldGlobalStatements.aperture_blades',IntAttribute(apertureBlades))"\
    "\n\t\t\tInterface.SetAttr('arnoldGlobalStatements.aperture_aspect_ratio', FloatAttribute(apertureRatio))"\
    "\n\t\t\tInterface.SetAttr('arnoldGlobalStatements.flat_field_focus',IntAttribute(flatFieldFocus))"\
    "\n\t\t\tInterface.SetAttr('arnoldGlobalStatements.aperture_blade_curvature',FloatAttribute(apertureCurvature))"\
    "\n\t\t\tInterface.SetAttr('arnoldGlobalStatements.aperture_rotation',FloatAttribute(apertureRot))"\
    "\n\t\telse"\
    "\n\t\t\t-- set the arnold aperture to 0 to make sure no DOF will be rendered"\
    "\n\t\t\tInterface.SetAttr('arnoldGlobalStatements.aperture_size',FloatAttribute(0.0)) "\
    "\n\t\tend"\
    "\n\tend"\
    "\nend"

# create an opscript for a plane or the target node
def createPlane(nodeName = 'planeFocus',location = '/root/world/cam/focus_plane', rootNode = NodegraphAPI.GetRootNode(),targetMode = False ):
    opscriptNode = NodegraphAPI.CreateNode('OpScript',rootNode)
    opscriptNode.setName(nodeName)
    opscriptNode.getParameter('applyWhere').setValue('at specific location',0)
    opscriptNode.getParameters().createChildNumber('disable', 0)
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
    if targetMode:
        opscriptNode.getParameter('script.lua').setValue(opNodeScriptTarget, 0.0)
    else :
        opscriptNode.getParameter('script.lua').setValue(opNodeScript,0.0)
    return opscriptNode

# put a selected node under the mouse
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

# create parameter for the main group node
def createParam(groupNode = NodegraphAPI.GetRootNode()):
    fstopCameraMetadataParam = groupNode.getParameters().createChildNumber('fstop_camera_metadata', 1)
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
    #advanced settings
    advancedSettigsGroup = groupNode.getParameters().createChildGroup('advanced_settings')
    advancedSettigsGroup.setHintString("{'help': 'edit advanced setting like name, color and path of the geometry plane representing the focus plane'}")
    filmAspectRatio = advancedSettigsGroup.createChildNumber('filmAspectRatio', 2)
    filmAspectRatio.setHintString("{'help': 'film aspect ratio (i.e 2.35, 1.85...)'}")
    CoCParam = advancedSettigsGroup.createChildNumber('Coc', 0.013)
    CoCParam.setHintString("{'widget': 'popup', 'options': ['0.013', '0.025', '0.035', '0.05'], 'help': 'Circle of confusion (https://improvephotography.com/53601/conquering-the-circle-of-confusion-for-photography/)'}")
    CoCParam.setValue(0.013,0.0)
    overrideFocalLengthParam = advancedSettigsGroup.createChildNumber('override_focal_length',0)
    overrideFocalLengthParam.setHintString("{'widget': 'checkBox', 'helpAlert': 'warning', 'help': 'check to override the fov this will not change the fov of the camera but change the calculations of DOF'}")
    focalLenghtParam = advancedSettigsGroup.createChildNumber('focal_length', 50)
    focalLenghtParam.setHintString("{'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../override_focal_length', 'conditionalVisValue': '1'}, 'help': 'fov used for calculation of DOF'}")
    # arnold render 3D
    render3DDOFParam = advancedSettigsGroup.createChildNumber('render_3D_DOF', 0)
    render3DDOFParam.setHintString(
        "{'widget': 'boolean', 'help': 'If yes Arnold will render the DOF in 3D and the data will be pushed to the metadata of the primary pass if no only the data will be pushed to the metadata of the primary pass'}")
    lensSettingGroup = advancedSettigsGroup.createChildGroup('DOF_settings_3D')
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
    # camera group in advanced settings
    cameraPathGroup = advancedSettigsGroup.createChildGroup('camera_path')
    cameraPathGroup.setHintString("{'help': 'camera to use for calculate the DOF'}")
    changeCameraParam = cameraPathGroup.createChildNumber('change_camera', 0)
    changeCameraParam.setHintString("{'widget': 'checkBox', 'help': 'unlock the camera field to change camera'}")
    cameraParam = cameraPathGroup.createChildString('camera', '/root/world/cam/stereoCameraLeft/stereoCameraLeftShape')
    cameraParam.setHintString(
        "{'conditionalLockOps': {'conditionalLockValue': '0', 'conditionalLockOp': 'equalTo', 'conditionalLockPath': '../change_camera'}, 'widget': 'scenegraphLocation', 'help': 'camera path to use for DOF calculation'}")
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
    scalePlaneParam = geometrySettingsGroup.createChildNumber('scale_focus_planes',1.0)
    scalePlaneParam.setHintString("{'slider': 'True', 'slidermax': '100.0', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../scale_plane_gang', 'conditionalVisValue': '1'}, 'help': 'scale all the planes uniformaly'}")
    nearFocusPlaneScaleParam = geometrySettingsGroup.createChildNumber('near_focus_plane_scale',1.0)
    nearFocusPlaneScaleParam.setHintString("{'slider': 'True', 'slidermax': '100.0', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../scale_plane_gang', 'conditionalVisValue': '0'}, 'help': 'scale the near focus plane'}")
    focusPlaneScaleParam = geometrySettingsGroup.createChildNumber('focus_plane_scale', 1.0)
    focusPlaneScaleParam.setHintString(
        "{'slider': 'True', 'slidermax': '100.0', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../scale_plane_gang', 'conditionalVisValue': '0'}, 'help': 'scale the focus plane'}")
    farFocusPlaneScaleParam = geometrySettingsGroup.createChildNumber('far_focus_plane_scale', 1.0)
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

def createOpScriptParam(opNode = NodegraphAPI.GetRootNode()):
    userGroup = opNode.getParameters().createChildGroup('user')

    paramDict = { 'camPath' : { 'format': 's', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.camera_path.camera')"},
                  'method' : {'format': 's', 'exp': "getParam(self.getNode().getParent().getName()+'.focus_distance.method')"},
                  'focusDistance':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.focus_distance.focus_distance')"},
                  'fstopMetadata':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.fstop_camera_metadata')"},
                  'fstop':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.fstop')"},
                  'userFocalLength':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.focal_length')"},
                  'overrideFocalLength':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.override_focal_length')"},
                  'alembicFile':{'format': 's', 'exp': "getParam(self.getNode().getParent().getName()+'.focus_distance.alembic_setting.alembic_path')"},
                  'focusTarget':{'format': 's', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.geometry_settings.geometry_path')+'/'+getParam(self.getNode().getParent().getName()+'.advanced_settings.geometry_settings.target_name')"},
                  'focusTargetColor':{'format': 'a', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.geometry_settings.target_color')"},
                  'focusPlanePath':{'format': 's', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.geometry_settings.geometry_path')+'/'+getParam(self.getNode().getParent().getName()+'.advanced_settings.geometry_settings.focus_plane_name')"},
                  'CoC': {'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.Coc')"},
                  'nearFocusPlane':{'format': 's', 'exp': 'getParam(self.getNode().getParent().getName()+".advanced_settings.geometry_settings.geometry_path")+"/"+getParam(self.getNode().getParent().getName()+".advanced_settings.geometry_settings.near_focus_plane_name")'},
                  'farFocusPlane':{'format': 's', 'exp': 'getParam(self.getNode().getParent().getName()+".advanced_settings.geometry_settings.geometry_path")+"/"+getParam(self.getNode().getParent().getName()+".advanced_settings.geometry_settings.far_focus_plane_name")'},
                  'targetConstraint':{'format': 'n', 'exp': 'getParam(self.getNode().getParent().getName()+".focus_distance.target_setting.target_constraint")'},
                  'targetConstraintObject':{'format': 's', 'exp': "getParam(self.getNode().getParent().getName()+'.focus_distance.target_setting.target_constraint_Object') if getParam(self.getNode().getParent().getName()+'.focus_distance.target_setting.target_constraint_Object') != '' else getParam(self.getNode().getParent().getName()+'.advanced_settings.camera_path.camera')"},
                  'alembicPath':{'format': 's', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.geometry_settings.geometry_path')+'/AlembicFocus'"},
                  'alembicAttr':{'format': 's', 'exp': "getParam(self.getNode().getParent().getName()+'.focus_distance.alembic_setting.alembic_attr_name')"},
                  'alembicName':{'format': 's', 'exp': "getParam(self.getNode().getParent().getName()+'.focus_distance.alembic_setting.alembic_path')"},
                  'apertureBlades':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.DOF_settings_3D.aperture_blades')"},
                  'apertureAspectRatio':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.DOF_settings_3D.aperture_aspect_ratio')"},
                  'apertureBladeCurvature':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.DOF_settings_3D.aperture_blade_Curvature')"},
                  'apertureRotation':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.DOF_settings_3D.aperture_rotation')"},
                  'flatFieldFocus':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.DOF_settings_3D.flat_field_focus')"},
                  'render3D':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.render_3D_DOF')"},
                  'filmAspectRatio':{'format': 'n', 'exp': "getParam(self.getNode().getParent().getName()+'.advanced_settings.filmAspectRatio')"}}
    for key in paramDict.keys():
        paramName = key
        paramFormat = paramDict[key]['format']
        paramExp = paramDict[key]['exp']
        paramCreated = ''
        if paramFormat == 's':
            paramCreated = userGroup.createChildString(paramName,'')
        elif paramFormat == 'n':
            paramCreated = userGroup.createChildNumber(paramName, 1.0)
        else:
            paramCreated = userGroup.createChildNumberArray(paramName, 3)
        opNode.getParameter('user.'+paramName).setExpression(paramExp, True)



def createFocusGroup(name='FocusGroup',parent = NodegraphAPI.GetRootNode(),geoPath = '/root//world/cam/DOF'):
    currentSelection = NodegraphAPI.GetAllSelectedNodes()
    if len(currentSelection) == 0:
        rootNode = parent
    else:
        rootNode = NodegraphAPI.GetNode(currentSelection[0].getParent().getName())
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

    #create the planes nodes
    # start pos for the node
    posX = -100.0
    posY = 100.0
    #expression to set the op script
    expressionBase = 'getParam(self.getNode().getParent().getName()+".advanced_settings.geometry_settings.'
    expressionScale = expressionBase+'scale_focus_planes") if '+ expressionBase +'scale_plane_gang") else ' +expressionBase
    #dictionary containing the data for the focus planes and target
    dictPlanes = {'nearFocusPlane': {'nodeName': 'nearFocusPlane', 'location': geoPath + '/near_focus_plane','expressionName': expressionBase+'near_focus_plane_name")','expressionScale': expressionScale+'near_focus_plane_scale")',
                                     'expressionColor': expressionBase+'near_focus_plane_color")', 'pos': (-200, -10), 'inputMerge': 'i1', 'targetMode': False},
                  'focusPlane': {'nodeName': 'focusPlane', 'location': geoPath + '/focus_plane', 'expressionName': expressionBase+'focus_plane_name")', 'expressionScale': expressionScale+'focus_plane_scale")',
                                 'expressionColor': expressionBase+'focus_plane_color")', 'pos': (0, -10), 'inputMerge': 'i2', 'targetMode': False},
                  'farFocusPlane': {'nodeName': 'farFocusPlane', 'location': geoPath + '/far_focus_plane', 'expressionName': expressionBase+'far_focus_plane_name")', 'expressionScale': expressionScale+'far_focus_plane_scale")',
                                    'expressionColor': expressionBase+'far_focus_plane_color")', 'pos': (200, -10), 'inputMerge': 'i3', 'targetMode': False},
                  'focusTarget': {'nodeName': 'focusTarget', 'location': geoPath + '/focus_target','expressionName': expressionBase + 'target_name")','expressionScale': expressionBase + 'scale_target")',
                                    'expressionColor': expressionBase + 'target_color")', 'pos': (200, -10),'inputMerge': 'i4', 'targetMode': True}}

    for key in dictPlanes.keys():
        posY -= 100.0
        #create the 3 planes
        plane = createPlane(nodeName = dictPlanes[key]['nodeName'],location = dictPlanes[key]['location'], rootNode = groupNode,targetMode= dictPlanes[key]['targetMode'])
        #set the expression
        plane.getParameter('user.displayColor').setExpression(dictPlanes[key]['expressionColor'],True)
        plane.getParameter('user.displayName').setExpression(dictPlanes[key]['expressionName'], True)
        plane.getParameter('user.scale').setExpression(dictPlanes[key]['expressionScale'], True)
        plane.getParameter('location').setExpression(expressionBase+'geometry_path")'+'+"/"+'+dictPlanes[key]['expressionName'], True)
        if dictPlanes[key]['targetMode']:
            plane.getParameter('disable').setExpression("0 if getParam(self.getNode().getParent().getName()+'.focus_distance.method') == '0' else 1", True)
        NodegraphAPI.SetNodePosition(plane,(posX,posY))
        # connect the node
        plane.getInputPort('i0').connect(sendGroup)
        sendGroup = plane.getOutputPort('out')

    # transform node for focus target
    transFormNode = NodegraphAPI.CreateNode('Transform3D',groupNode)
    transFormNode.setName('TransformTarget')
    transFormNode.getParameter('makeInteractive').setValue('Yes',0)
    transFormNode.getParameters().createChildNumber('disable',0)
    transFormNode.getParameter('disable').setExpression("0 if getParam(self.getNode().getParent().getName()+'.focus_distance.method') == '0' and getParam(self.getNode().getParent().getName()+'.focus_distance.target_setting.target_constraint') == 0 else 1", True)
    transFormNode.getParameter('path').setExpression("getParam(self.getNode().getParent().getName()+'.advanced_settings.geometry_settings.geometry_path')+'/'+getParam(self.getNode().getParent().getName()+'.advanced_settings.geometry_settings.target_name')", True)
    posY -= 100.0
    NodegraphAPI.SetNodePosition(transFormNode, (posX, posY))
    transFormNode.getInputPort('in').connect(sendGroup)
    sendGroup = transFormNode.getOutputPort('out')

    # create the alembic node
    alembicNode = NodegraphAPI.CreateNode('Alembic_In', groupNode)
    alembicNode.setName('AlembicTarget')
    alembicNode.getParameters().createChildNumber('disable', 0)
    alembicNode.getParameter('disable').setExpression("0 if getParam(self.getNode().getParent().getName()+'.focus_distance.method') == '1' and getParam(self.getNode().getParent().getName()+'.focus_distance.alembic_setting.alembic_path') != '' else 1", True)
    alembicNode.getParameter('name').setExpression("getParam(self.getNode().getParent().getName()+'.advanced_settings.geometry_settings.geometry_path')+'/AlembicFocus'", True)
    alembicNode.getParameter('abcAsset').setExpression("getParam(self.getNode().getParent().getName()+'.focus_distance.alembic_setting.alembic_path')", True)
    posX = 100.0
    NodegraphAPI.SetNodePosition(alembicNode, (posX, posY))

    # create the mergeNode
    mergeNode = NodegraphAPI.CreateNode('Merge', groupNode)
    mergeNode.setName('MergeAlembic')
    mergeNode.addInputPort('i0')
    mergeNode.addInputPort('i1')
    posX = 0.0
    posY -= 100.0
    NodegraphAPI.SetNodePosition(mergeNode, (posX, posY))
    mergeNode.getInputPort('i0').connect(sendGroup)
    mergeNode.getInputPort('i1').connect(alembicNode.getOutputPort('out'))
    sendGroup = mergeNode.getOutputPort('out')

    # create the opScript node which calculate the DOF and plane position
    opScriptDOFNode = NodegraphAPI.CreateNode('OpScript', groupNode)
    createOpScriptParam(opScriptDOFNode)
    opScriptDOFNode.getParameter('CEL').setExpression("'( /' + getParam(self.getNode().getParent().getName()+'.advanced_settings.geometry_settings.geometry_path')+'//* + /root)'",True)
    opScriptDOFNode.getParameter('script.lua').setValue(calculFocusPlane, 0.0)
    posY -= 100.0
    NodegraphAPI.SetNodePosition(opScriptDOFNode, (posX, posY))
    opScriptDOFNode.getInputPort('i0').connect(sendGroup)
    sendGroup = opScriptDOFNode.getOutputPort('out')


    sendGroup.connect(returnGroup)
    nodeToMouse(groupNode)

if __name__ == '__main__':
    main()
