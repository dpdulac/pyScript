#!/usr/bin/env python
# coding:utf-8
""":mod:`createBlocker` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2017, Mikros Animation"

from Katana import  NodegraphAPI,UI4


#this path is to use if you want the scripted lus code inside the script lua tabs of the opNode
#__LUA_FILE_PATH = '/homes/duda/.katana/LuaScript/MatrixPrim.lua'

'''create UI parameter for the blocker
-groupNode is the node to add the parameters
-name name of the node
-addBlockerButton add a button to add blocker in param
-addDeleteButton add button to self delete the blocker
'''
def paramui(groupNode = NodegraphAPI.GetRootNode(),name='Blocker1',addBlockerButton = False, addDeleteButton = False):
    if addBlockerButton:
        addButton =groupNode.getParameters().createChildString('addBlocker','add Blocker')
        addButton.setHintString("{'widget': 'scriptButton', 'buttonText': 'add Blocker', 'scriptText': \"from createBlocker import addBlocker\\n"
                                    "addBlocker(node)\", 'help': 'add a new blocker to the group'}")
    #top param group
    groupParam = groupNode.getParameters().createChildGroup(name)
    groupParam.setHintString("{'open': 'True', 'help':' Blocker tunning'}")
    #cel param
    celParam = groupParam.createChildString('CEL','')
    celParam.setHintString("{'widget': 'cel'}")
    # path blocker in scenegraph
    shapePathParam = groupParam.createChildString('path Name','/root/world/geo/BlockerGroup/'+ name)
    shapePathParam.setHintString("{'widget': 'scenegraphLocation', 'help': 'path for the blocker, make sure to change the name of the blocker if you have more than one'}")
    #display the blocker info in the viewer
    displayParam = groupParam.createChildNumber('message',1)
    displayParam.setHintString("{'widget': 'checkBox', 'help': 'display the blocker name as well as the associated light(s)'}")
    #bypass blocker
    disableParam = groupParam.createChildNumber('disable',0)
    disableParam.setHintString("{'widget': 'checkBox', 'help': 'enable or disable the blocker'}")
    #color for the blocker
    colorParam = groupParam.createChildNumberArray('color',3)
    colorParam.setHintString("{'widget': 'color', 'help': 'Display color of the blocker'}")
    channels = ['i0','i1','i2']
    for chan in channels:
        groupNode.getParameter(name+'.color.'+chan).setValue(0.4,0)
    #blocker number to use on the shader
    blockerParam = groupParam.createChildString('blocker Number','blk01')
    blockerParam.setHintString("{'widget': 'popup', 'options': ['blk01', 'blk02', 'blk03', 'blk04', 'blk05', 'blk06', 'blk07', 'blk08'], 'help':'select in between the 8 possible blockers available in the light shader'}")
    #blocker type
    shapeParam = groupParam.createChildString('blocker Type','box')
    shapeParam.setHintString("{'widget': 'popup', 'options': ['box', 'sphere', 'cylinder', 'plane'], 'help':'Determines the shape of the blocked light. A light blocker can be a box, cylinder, sphere, or plane.'}")
    #create the param for density,roundness,width_edge,height_edge and ramp. The use of dictionary of dictionary is to keep the good order of appearance for the param
    listParam = {'1':{'density':'This value is the strength of the light blocker effect. The light blocker will not be apparent unless the density value is above 0'},
                 '2':{'roundness':'Increases the circular shape of plane light blockers'},
                 '3':{'width_edge':'Attenuates the edge of the width of the light blocker'},
                 '4':{'height_edge':'Attenuates the edge of the height of the light blocker'},
                 '5':{'ramp':'This is the magnitude of the ramp multiplier, applying along the Ramp Axis direction.  Negative values flip the Ramp Axis direction'}
                 }
    for key in sorted(listParam.keys()):
        for param in listParam[key].keys():
            paramCreated = groupParam.createChildNumber(param,0.0)
            if param == 'roundness' :
                paramCreated.setHintString("{'slider': 'True', 'conditionalVisOps': {'conditionalVisOp': 'contains', 'conditionalVisPath': '../blocker_Type', 'conditionalVisValue': 'plane'},'help': '"+listParam[key][param]+"'}")
            else:
                paramCreated.setHintString("{'slider': 'True', 'help': '"+listParam[key][param]+"'}")
    #axis parameter
    axisParam = groupParam.createChildString('axis','x')
    axisParam.setHintString("{'widget': 'popup', 'options': ['x','y','z'], 'help':'Attenuates the ramp based on the direction set'}")

    #use projection
    useProjectionParam = groupParam.createChildNumber('use_projection',0)
    useProjectionParam .setHintString("{'widget': 'checkBox', 'conditionalVisOps': {'conditionalVisOp': 'contains', 'conditionalVisPath': '../blocker_Type', 'conditionalVisValue': 'box'}, 'help': 'enable the use of projection file or noise in the blocker'}")
    #file type (i.e file or noise)
    fileTypeParam = groupParam.createChildNumber('file_type',1)
    fileTypeParam.setHintString("{'options__order': ['noise', 'file'], 'widget': 'mapper', 'options': {'noise': 0.0, 'file': 1.0}, 'conditionalVisOps': {'conditionalVis1Path': '../blocker_Type', 'conditionalVis2Op': 'equalTo', 'conditionalVis1Value': 'box', 'conditionalVisOp': 'and', 'conditionalVis1Op': 'contains', 'conditionalVisLeft': 'conditionalVis1', 'conditionalVisRight': 'conditionalVis2', 'conditionalVis2Path': '../use_projection', 'conditionalVis2Value': '1'}, 'widget': 'mapper', 'options': {'noise': 0.0, 'file': 1.0} ,'help': 'choose in between file image or noise'}")
    #file param
    fileParam = groupParam.createChildString('fileIn','')
    fileParam.setHintString("{'widget': 'fileInput', 'conditionalVisOps': {'conditionalVis1Path': '../blocker_Type', 'conditionalVis3Op': 'equalTo', 'conditionalVis2Op': 'and', 'conditionalVis4Value': '1', 'conditionalVis1Value': 'box', 'conditionalVisOp': 'and', 'conditionalVis4Path': '../file_type', 'conditionalVis1Op': 'contains', 'conditionalVisLeft': 'conditionalVis1', 'conditionalVis2Right': 'conditionalVis4', 'conditionalVisRight': 'conditionalVis2', 'conditionalVis3Value': '1', 'conditionalVis4Op': 'equalTo', 'conditionalVis3Path': '../use_projection', 'conditionalVis2Left': 'conditionalVis3'}, 'help': 'apply a texture to use as a masking effect. Unlike gobos you can position a shadow independently of the light transform. It only works when blocker Type is set to Box'}")

    #noise group
    noiseGroupParam = groupParam.createChildGroup('noise')
    noiseGroupParam.setHintString("{'open': 'True', 'conditionalVisOps': {'conditionalVis1Path': '../blocker_Type', 'conditionalVis3Op': 'equalTo', 'conditionalVis2Op': 'and', 'conditionalVis4Value': '0', 'conditionalVis1Value': 'box', 'conditionalVisOp': 'and', 'conditionalVis4Path': '../file_type', 'conditionalVis1Op': 'contains', 'conditionalVisLeft': 'conditionalVis1', 'conditionalVis2Right': 'conditionalVis4', 'conditionalVisRight': 'conditionalVis2', 'conditionalVis3Value': '1', 'conditionalVis4Op': 'equalTo', 'conditionalVis3Path': '../use_projection', 'conditionalVis2Left': 'conditionalVis3'},'help': 'noise tunning'}")
    dictParamNoise = {'1':{'noise_octaves':{'type':'number','hint':"{'int': 'True','slider': 'True', 'slidermax': '10.0', 'slidermin': '1.0','help': 'The number of octaves over which the noise function is calculated (the fractal noise function is repeated at multiple frequencies, known as octaves; normally each octave is at about twice the frequency, i.e., half the size, of the previous one, but you can alter this with the lacunarity control)'}"}},
                      '2':{'noise_distortion':{'type':'number','hint':"{'slider': 'True', 'help': 'Defines a degree of random displacement applied to each point as part of the noise calculation, giving a different aesthetic feel'}"}},
                      '3':{'noise_lacunarity':{'type':'number','hint':"{'slider': 'True', 'slidermax': '5.0', 'slidermin': '0.0', 'help': 'Controls the average size of gaps in the texture pattern produced'}"}},
                      '4':{'noise_amplitude':{'type':'number', 'hint':"{'slider': 'True', 'slidermax': '10.0', 'slidermin': '0.0', 'help': 'Controls the amplitude, or range, of the output. Normally the output has values between 0 and 1, the amplitude control multiplies this'}"}},
                      '5':{'noise_scale':{'type':'array','hint':"{'help':'Controls the scale of the noise function in x, y, and z directions'}"}},
                      '6':{'noise_offset':{'type':'array','hint':"{'help':'Offset the noise in x, y, or z direction'}"}},
                      '7':{'noise_coord_space':{'type':'string', 'hint':"{'options__order': ['world', 'object'], 'widget': 'mapper', 'options': {'world': '0', 'object': '1'}, 'help':'Specifies the coordinate space to use. These include World and Object'}"}}
                      }
    for key in sorted(dictParamNoise.keys()):
        for param in dictParamNoise[key].keys():
            paramCreated = None
            if dictParamNoise[key][param]['type'] == 'number':
                paramCreated =noiseGroupParam.createChildNumber(param,0.0)
            elif dictParamNoise[key][param]['type'] == 'array':
                paramCreated = noiseGroupParam.createChildNumberArray(param,3)
            else:
                paramCreated = noiseGroupParam.createChildString(param,'')
            paramCreated.setHintString(dictParamNoise[key][param]['hint'])
    #set default value for noise
    groupNode.getParameter(name+'.noise.noise_coord_space').setValue('world',0)
    groupNode.getParameter(name+'.noise.noise_octaves').setValue(4,0)
    groupNode.getParameter(name+'.noise.noise_lacunarity').setValue(1.92,0)
    groupNode.getParameter(name+'.noise.noise_amplitude').setValue(1.0,0)
    for chan in channels:
        groupNode.getParameter(name+'.noise.noise_scale.'+chan).setValue(1.0,0)

    # reset and delete button
    scriptReset = 'from createBlocker import resetTransform\\nblockerName = "'+name+'"\\nresetTransform(blockerName, node)'
    #delete button
    if addDeleteButton:
        deleteButton = groupParam.createChildString('deleteBlocker','delete Blocker')
        scriptDel = 'from createBlocker import deleteBlocker\\nblockerName = "'+name+'"\\ndeleteBlocker(blockerName, node)'
        deleteButton.setHintString("{'widget': 'scriptToolbar', 'buttonData': [{'text': 'reset Transform', 'icon': '', 'scriptText': '"+scriptReset+"', 'flat': 0},{},{'text': 'delete "+name+"', 'icon': '', 'scriptText': '"+scriptDel+"', 'flat': 0}], 'help': 'delete the current blocker'}")
    else:
        resetButton = groupParam.createChildString('resetTransform','reset Transform')
        resetButton.setHintString("{'widget': 'scriptToolbar', 'buttonData': [{'text': 'reset Transform', 'icon': '', 'scriptText': '"+scriptReset+"', 'flat': 0},{},{}], 'help': 'delete the current blocker'}")


'''Create the blocker and set the blocker shader for the chosen light
-name: name of the group
-root: parent
-celExp: expression to connect elements to root node
-topNode: True if the node created is the top node to apply the paramui
'''

def createSingleBlocker(root = NodegraphAPI.GetRootNode(),celExp = 'getParent().',topNode = True):
    #open the file contening the lua file
    #fileLua = open(__LUA_FILE_PATH,'r')
    #luaText = fileLua.read()
    # root node
    rootNode = root
    #create the groupNode
    groupNode = NodegraphAPI.CreateNode('Group',rootNode)
    groupNode.setName('Blocker1')
    name = groupNode.getName()
    #add in and out port
    groupNodeIn = groupNode.addInputPort('in')
    groupNodeOut = groupNode.addOutputPort('out')
    #add attribute to switch the display of group node to normal node
    groupNodeAttrDict = {'ns_basicDisplay': 1,'ns_iconName': ''}
    groupNode.setAttributes(groupNodeAttrDict)
    #add the disable param
    disableParam = groupNode.getParameters().createChildNumber('disable',0)
    newCelExp = celExp[:celExp.rfind('getParent().')]  # this is a hack it work but not safe
    disableParam.setExpression(newCelExp+name+'.disable',True)
    #create user param on the groupNode if use as a single entity
    if topNode:
        paramui(groupNode,name)

    #create the opNode who create the primitive
    primitiveOpNode = NodegraphAPI.CreateNode('OpScript', parent=groupNode)
    primitiveOpNode.setName('primitiveType')
    primitiveOpNode.getParameter('applyWhere').setValue('at specific location',0)
    primitiveOpNode.getParameter('location').setExpression(celExp+name+'.path_Name',True)
    #create parameter
    primitiveOpNodeParam = primitiveOpNode.getParameters().createChildGroup('user')
    #param for message
    primitiveOpNodeParamDisplay = primitiveOpNodeParam.createChildNumber('message',1)
    primitiveOpNodeParamDisplay.setExpression(celExp+name+'.message',True)
    #param to get the color
    primitiveOpNodeParamColor = primitiveOpNodeParam.createChildNumberArray('color',3)
    primitiveOpNodeParamColor.setExpression(celExp+name+'.color',True)
    #param to get the light
    primitiveOpNodeParamLight = primitiveOpNodeParam.createChildString('light','')
    primitiveOpNodeParamLight.setExpression(celExp+name+'.CEL',True)
    #param to get the shape
    primitiveOpNodeParamShape = primitiveOpNodeParam.createChildString('shape','box')
    primitiveOpNodeParamShape.setExpression(celExp+name+'.blocker_Type',True)
    #this part is to use if you want the "printed script" in the lua script tab
    #filePrimitiveStart = luaText.find('--PrimitiveModule')
    #filePrimitiveEnd = luaText.find('--endPrimitiveModule')
    #primitiveOpNode.getParameter('script.lua').setValue(luaText[filePrimitiveStart:filePrimitiveEnd],0)
    #this is using a lua script as reference which mean you need to set the LUA_PATH correctly to point at the script(i.eos.environ['LUA_PATH'] = "/homes/duda/.katana/LuaScript/?.lua")
    primitiveOpNode.getParameter('script.lua').setValue("local createPrimitive = require 'blocker'\ncreatePrimitive.primitive()",0)

    #create the transform Node
    transformNode = NodegraphAPI.CreateNode('Transform3D', parent=groupNode)
    transformNode.setName('Transform_Blocker')
    #set the path expression
    transformNode.getParameter('path').setExpression(celExp+name+'.path_Name',True)
    #set the interactive to Yes
    transformNode.getParameter('makeInteractive').setValue('Yes',0)


    #create the opScriptNode for the primitive and set it's lua text to get the transform matrix
    opscriptPrimNode = NodegraphAPI.CreateNode('OpScript', parent=groupNode)
    opscriptPrimNode.setName('MatrixPrim')
    opscriptPrimNode.getParameter('CEL').setExpression(celExp+name+'.path_Name',True)
    #this part is to use if you want the "printed script" in the lua script tab
    #fileMatrixTextStart = luaText.find('--MatrixModule')
    #fileMatrixTextEnd = luaText.find('--endMatrixModule')
    #opscriptPrimNode.getParameter('script.lua').setValue(luaText[fileMatrixTextStart:fileMatrixTextEnd],0)
    #this is using a lua script as reference which mean you need to set the LUA_PATH correctly to point at the script(i.eos.environ['LUA_PATH'] = "/homes/duda/.katana/LuaScript/?.lua")
    opscriptPrimNode.getParameter('script.lua').setValue("local createMatrix = require 'blocker'\ncreateMatrix.getMatrix()",0)

    #create the opscript for the light
    opscriptLightNode = NodegraphAPI.CreateNode('OpScript',groupNode)
    opscriptLightNode.getParameter('CEL').setExpression(celExp+name+".CEL",True)
    opscriptLightNode.setName('MatrixLight')
    opscriptLightUserParam = opscriptLightNode.getParameters().createChildGroup('user')
    opscriptLightUserParamBlocker = opscriptLightUserParam.createChildString('blocker','blk01')
    opscriptLightUserParamBlocker.setExpression(celExp+name+'.blocker_Number',True)
    opscriptLightUserParamPrim = opscriptLightUserParam.createChildString('primitive','')
    opscriptLightUserParamPrim.setExpression(celExp+name+'.path_Name',True)
    listParam = ['density','roundness','width_edge','height_edge','ramp']
    for param in listParam:
        paramCreated = opscriptLightUserParam.createChildNumber(param,0.0)
        paramCreated.setExpression(celExp+name+'.'+param,True)
    opscriptLightUserParamShape = opscriptLightUserParam.createChildString('geometry_type','box')
    opscriptLightUserParamShape.setExpression(celExp+name+'.blocker_Type',True)
    opscriptLightUserParamAxis = opscriptLightUserParam.createChildString('axis','x')
    opscriptLightUserParamAxis.setExpression(celExp+name+'.axis',True)
    opscriptLightUserParamFileIn = opscriptLightUserParam.createChildString('fileIn','')
    opscriptLightUserParamFileIn.setExpression(celExp+name+'.fileIn',True)
    opscriptLightUserParamUseProj = opscriptLightUserParam.createChildNumber('use_projection',0)
    opscriptLightUserParamUseProj.setExpression(celExp+name+'.use_projection',True)
    opscriptLightUserParamFileType = opscriptLightUserParam.createChildNumber('file_type',0)
    opscriptLightUserParamFileType.setExpression(celExp+name+'.file_type',True)
    #noise user param
    dictParamNoise = {'noise_octaves':'number',
                      'noise_distortion':'number',
                      'noise_lacunarity':'number',
                      'noise_amplitude':'number',
                      'noise_scale':'array',
                      'noise_offset':'array',
                      'noise_coord_space':'string'}
    for param in dictParamNoise.keys():
        paramToCreate = None
        if dictParamNoise[param] == 'number':
            paramToCreate = opscriptLightUserParam.createChildNumber(param,0.0)
        elif dictParamNoise[param] == 'array':
            paramToCreate = opscriptLightUserParam.createChildNumberArray(param,3)
        else:
            paramToCreate = opscriptLightUserParam.createChildString(param,'')
        paramToCreate.setExpression(celExp+name+'.noise.'+param,True)

    #this part is to use if you want the "printed script" in the lua script tab
    #fileLightStart = luaText.find('--MatrixLight')
    #fileLightEnd = luaText.find('--endMatrixLight')
    #opscriptLightNode.getParameter('script.lua').setValue(luaText[fileLightStart:fileLightEnd],0)
    #this is using a lua script as reference which mean you need to set the LUA_PATH correctly to point at the script(i.eos.environ['LUA_PATH'] = "/homes/duda/.katana/LuaScript/?.lua")
    opscriptLightNode.getParameter('script.lua').setValue("local paramLight = require 'blocker'\nparamLight.applyBlockerParam()",0)

    #create the mergeNode
    mergeNode = NodegraphAPI.CreateNode('Merge',groupNode)
    mergeNode.setName('MergePrim')
    mergeNode.addInputPort('i0')
    mergeNode.addInputPort('i1')

    #connection
    sendGroup = groupNode.getSendPort('in')
    returnGroup = groupNode.getReturnPort('out')
    mergeNode.getInputPort('i0').connect(sendGroup)
    primitiveOpNode.getOutputPort('out').connect(transformNode.getInputPort('in'))
    transformNode.getOutputPort('out').connect(mergeNode.getInputPort('i1'))
    mergeNode.getOutputPort('out').connect(opscriptPrimNode.getInputPort('i0'))
    opscriptPrimNode.getOutputPort('out').connect(opscriptLightNode.getInputPort('i0'))
    opscriptLightNode.getOutputPort('out').connect(returnGroup)

    #placement of Nodes
    centralPos = NodegraphAPI.GetNodePosition(mergeNode)
    NodegraphAPI.SetNodePosition(primitiveOpNode, (centralPos[0]+100,centralPos[1]+200))
    NodegraphAPI.SetNodePosition(transformNode, (centralPos[0]+100,centralPos[1]+100))
    NodegraphAPI.SetNodePosition(opscriptPrimNode, (centralPos[0],centralPos[1]-100))
    NodegraphAPI.SetNodePosition(opscriptLightNode, (centralPos[0],centralPos[1]-200))

    #close the lua file
    #fileLua.close()

    #put the node under the mouse if single node
    if topNode:
        currentSelection = NodegraphAPI.GetAllSelectedNodes()
        for node in currentSelection:
            NodegraphAPI.SetNodeSelected(node,False)
        NodegraphAPI.SetNodeSelected(groupNode,True)
        # Get list of selected nodes
        nodeList = NodegraphAPI.GetAllSelectedNodes()
        # Find Nodegraph tab and float nodes
        nodegraphTab = UI4.App.Tabs.FindTopTab('Node Graph')
        if nodegraphTab:
            nodegraphTab.floatNodes(nodeList)

    return groupNode

def createMasterBlocker(name='BlockerGroup',parent = NodegraphAPI.GetRootNode()):
    rootNode = parent
    #create the groupNode
    groupNode = NodegraphAPI.CreateNode('Group',rootNode)
    groupNode.setName(name)
    #add in and out port
    groupNode.addInputPort('in')
    groupNode.addOutputPort('out')
    #add attribute to switch the display of group node to normal node
    groupNodeAttrDict = {'ns_basicDisplay': 1,'ns_iconName': ''}
    groupNode.setAttributes(groupNodeAttrDict)
    blockerName = 'Blocker1'

    #create a first blocker
    blocker = createSingleBlocker(groupNode,'getParent().getParent().',False)
    paramui(groupNode,blocker.getName(),True)

    #reorder the button addBlocker to be the last param
    blockerParam = groupNode.getParameters()
    paramAddBlocker = blockerParam.getChild('addBlocker')
    numberOfChild = blockerParam.getNumChildren() -1
    blockerParam.reorderChild(paramAddBlocker,numberOfChild)

    #create a dot node
    dotNode = NodegraphAPI.CreateNode('Dot',groupNode)
    dotNode.setName('outDot')

    #connection
    sendGroup = groupNode.getSendPort('in')
    returnGroup = groupNode.getReturnPort('out')
    blocker.getInputPort('in').connect(sendGroup)
    blocker.getOutputPort('out').connect(dotNode.getInputPort('input'))
    dotNode.getOutputPort('output').connect(returnGroup)

    #set position of nodes
    centralPos = NodegraphAPI.GetNodePosition(blocker)
    NodegraphAPI.SetNodePosition(dotNode,(centralPos[0],centralPos[1]-50))

    #put the node under the mouse
    currentSelection = NodegraphAPI.GetAllSelectedNodes()
    for node in currentSelection:
        NodegraphAPI.SetNodeSelected(node,False)
    NodegraphAPI.SetNodeSelected(groupNode,True)
    # Get list of selected nodes
    nodeList = NodegraphAPI.GetAllSelectedNodes()
    # Find Nodegraph tab and float nodes
    nodegraphTab = UI4.App.Tabs.FindTopTab('Node Graph')
    if nodegraphTab:
        nodegraphTab.floatNodes(nodeList)

def addBlocker(root = NodegraphAPI.GetRootNode()):
    children = root.getChildren()
    dotNode = None
    for child in children:
        if child.getType() == 'Dot':
            dotNode = child
    dotNodePos = NodegraphAPI.GetNodePosition(dotNode)

    newBlocker = createSingleBlocker(root,'getParent().getParent().',False)
    paramui(root,newBlocker.getName(),False,True)
    #reorder the button to be the last param
    newBlockerParam = root.getParameters()
    paramAddBlocker = newBlockerParam.getChild('addBlocker')
    numberOfChild = newBlockerParam.getNumChildren() -1
    newBlockerParam.reorderChild(paramAddBlocker,numberOfChild)

    inputDotNodeProducer = dotNode.getInputSource('input',NodegraphAPI.GetCurrentGraphState())[0]
    inputDotNodeProducer.connect(newBlocker.getInputPort('in'))
    newBlocker.getOutputPort('out').connect(dotNode.getInputPort('input'))
    NodegraphAPI.SetNodePosition(newBlocker,dotNodePos)
    NodegraphAPI.SetNodePosition(dotNode,(dotNodePos[0],dotNodePos[1]-50))

def deleteBlocker(blockerName = 'Blocker1',root = NodegraphAPI.GetRootNode()):
    #get the node to delete
    blockerToDelete = NodegraphAPI.GetNode(blockerName)
    #get the position of the node
    blockerToDeletePos = NodegraphAPI.GetNodePosition(blockerToDelete)

    #get the connected node ports to the blocker to delete and reconnect those ports together
    outPort = blockerToDelete.getInputPort('in').getConnectedPort(0)
    inPort = blockerToDelete.getOutputPort('out').getConnectedPort(0)
    outPort.connect(inPort)

    #delete the blocker node
    blockerToDelete.delete()

    #delete the param of the blocker
    paramToDelete = root.getParameter(blockerName)
    param = root.getParameters()
    param.deleteChild(paramToDelete)

    #reposition the node inside the blockerGroup
    nodeType = 'Group'
    portToFind = inPort
    nodeToMove = portToFind.getNode()
    pos = blockerToDeletePos
    while (nodeType != 'Dot'):
        oldPos = NodegraphAPI.GetNodePosition(nodeToMove)
        nodeType = nodeToMove.getType()
        NodegraphAPI.SetNodePosition(nodeToMove,pos)
        if nodeType != 'Dot':
            portToFind = nodeToMove.getOutputPort('out').getConnectedPort(0)
            nodeToMove = portToFind.getNode()
            pos = oldPos

def resetTransform(blockerName = 'Blocker1',root = NodegraphAPI.GetRootNode()):
    #get the transformNode
    blocker = NodegraphAPI.GetNode(blockerName)
    transNode = None
    for node in blocker.getChildren():
        if node.getType() == 'Transform3D':
            transNode = node
    param = {'translate':[0,0,0],'rotate':[0,0,0],'scale':[1,1,1],'pivot':[0,0,0]}
    chan = ['.i0','.i1','.i2']
    for key in param.keys():
        for channel in chan:
            paramPath = key+channel
            for i in range(3):
                transNode.getParameter(paramPath).setValue(param[key][i],0)
