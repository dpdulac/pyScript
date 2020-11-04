#!/usr/bin/env python
# coding:utf-8
""":mod: uberShaderBuilt
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2020.06
   
"""
def changePortInOutName(node = NodegraphAPI.GetRootNode(),oldParamName='diffuse', newParamName='sheen'):
    nodeInputPorts = node.getInputPorts()
    nodeOutputPorts = node.getOutputPorts()
    for port in nodeInputPorts:
        if port.getName().find(oldParamName) >= 0:
            port.addOrUpdateMetadata('label', port.getName().replace(oldParamName, newParamName))
            node.renameInputPort(port.getName(), port.getName().replace(oldParamName, newParamName))
        else:
            print 'NOOOOOOOO'
    for port in nodeOutputPorts:
        if port.getName().find(oldParamName) >= 0:
            port.addOrUpdateMetadata('label', port.getName().replace(oldParamName, newParamName))
            node.renameOutputPort(port.getName(), port.getName().replace(oldParamName, newParamName))
        else:
            print 'NOOOOOOOO'

def walkChildNode(node = NodegraphAPI.GetRootNode(),listChild=[]):
    try:
        node.getChildren()
    except:
        listChild.append(node)
        print 'No child for: ', node.getName()
    else:
        listChild.append(node)
        for child in node.getChildren():
            walkChildNode(child,listChild)
    return listChild

def changeParamName(node=NodegraphAPI.GetNode('root'), oldParamName='diffuse', newParamName='sheen'):
    nodeAllParm = node.getParameter('parameters')
    for i in nodeAllParm.getChildren():
        paramPath = 'parameters.' + i.getName() + '.hints'
        try:
            value = node.getParameter(paramPath).getValue(0)
        except:
            print i.getName() + ' NO HINTS'
        else:
            node.getParameter(paramPath).setValue(value.replace(oldParamName, newParamName), 0)

def builMaterialInterfaceControls(matNodeName='Standard', newParamName ='sheen'):
    matControlDict = {'colorCorrect': {'name': 'L0_diffuse_MapSetting_colorCorrect_Controls'.replace('diffuse', newParamName),
                                       'targetName': 'L0.DiffuseComponent.diffuse.MapSetting_diffuse.Color.colorCorrect'.replace('diffuse',newParamName),
                                       'targetType': 'page',
                                       'path': 'L0_diffuse_colorCorrect'.replace('diffuse', newParamName),
                                       'value': '1'},
                        'mapSetting': {'name': 'L0_diffuse_MapSetting_Controls'.replace('diffuse', newParamName),
                                       'targetName': 'L0.DiffuseComponent.diffuse.MapSetting_diffuse'.replace('diffuse', newParamName),
                                       'targetType': 'page',
                                       'path': 'L0_diffuse_input_diffuse_Mode'.replace('diffuse', newParamName),
                                       'value': '1'},
                          'colorMap': {'name': 'L0_diffuse_ColorMap_Controls'.replace('diffuse', newParamName),
                                       'targetName': 'L0_diffuse_ColorMap'.replace('diffuse', newParamName),
                                       'targetType': 'parameter',
                                       'path': 'L0_diffuse_input_diffuse_Mode'.replace('diffuse', newParamName),
                                       'value': '1'},
                             'color': {'name': 'L0_diffuse_Color_Controls'.replace('diffuse', newParamName),
                                       'targetName': 'L0_diffuse_Color'.replace('diffuse', newParamName),
                                       'targetType': 'parameter',
                                       'path': 'L0_diffuse_input_diffuse_Mode'.replace('diffuse', newParamName),
                                       'value': '0'}
         }

    matNode = NodegraphAPI.GetNode(matNodeName)
    matNodeChildren = matNode.getChildren()
    for node in matNodeChildren:
    #groupStackNode = ''
        if node.getType() == 'GroupStack':
            for key in matControlDict.keys():
                childNode = node.buildChildNode()
                childNode.setName(matControlDict[key]['name'])
                childNode.getParameter('targetType').setValue(matControlDict[key]['targetType'],0)
                childNode.getParameter('targetName').setValue(matControlDict[key]['targetName'],0)
                groupChild = childNode.getParameter('operators.ops').createChildGroup('ops1')
                groupChild.createChildString('op','equalTo')
                groupChild.createChildString('path',matControlDict[key]['path'])
                groupChild.createChildString('value',matControlDict[key]['value'])


def copyNode(node = NodegraphAPI.GetRootNode(),getParent = False):
    xmlNode = NodegraphAPI.BuildNodesXmlIO([node])
    if getParent:
        return KatanaFile.Paste(xmlNode, node.getParent())[0]
    else:
        return KatanaFile.Paste(xmlNode, NodegraphAPI.GetRootNode())[0]


def changeNodeNameAndParameters(oldParamName='diffuse', newParamName='sheen'):
    node = NodegraphAPI.GetAllSelectedNodes()[0]
    childNodes = node.getChildren()
    for child in childNodes:
        # child.checkDynamicParameters()
        child.checkDynamicParameters()
        changeParamName(child, oldParamName, newParamName)
        checkNodeName(child, oldParamName, newParamName)
    checkNodeName(node, oldParamName, newParamName)
    nodeInputPorts = node.getInputPorts()
    nodeOutputPorts = node.getOutputPorts()
    for port in nodeInputPorts:
        if port.getName().find(oldParamName) >= 0:
            port.addOrUpdateMetadata('label', port.getName().replace(oldParamName, newParamName))
            node.renameInputPort(port.getName(), port.getName().replace(oldParamName, newParamName))
    for port in nodeOutputPorts:
        if port.getName().find(oldParamName) >= 0:
            port.addOrUpdateMetadata('label', port.getName().replace(oldParamName, newParamName))
            node.renameOutputPort(port.getName(), port.getName().replace(oldParamName, newParamName))

def checkNodeName(node=NodegraphAPI.GetNode('root'), oldParamName='diffuse', newParamName='sheen'):
    nodeName = node.getName().replace(oldParamName, newParamName)
    if nodeName[-1].isdigit():
        nodeName = nodeName[:-1]
    node.setName(nodeName)
    try:
        node.getParameter('name').getValue(0)
    except:
        print 'no parameter name in this node'
    else:
        node.getParameter('name').setValue(nodeName,0)


def changeNodeNameAndParameters(oldParamName='diffuse', newParamName='sheen'):
    node = NodegraphAPI.GetAllSelectedNodes()[0]
    childNodes = node.getChildren()
    for child in childNodes:
        # child.checkDynamicParameters()
        child.checkDynamicParameters()
        changeParamName(child, oldParamName, newParamName)
        checkNodeName(child, oldParamName, newParamName)
    checkNodeName(node, oldParamName, newParamName)
    changePortInOutName(node, oldParamName, newParamName)


def createNewLayer(oldParamName='L0', newParamName='L1'):
    #change the layer name
    startNode = NodegraphAPI.GetAllSelectedNodes()[0]
    newNode = copyNode(startNode,True)
    noList = []
    childList = walkChildNode(newNode,noList)
    for child in childList:
        checkNodeName(child,oldParamName,newParamName)
        if child.getType() == 'ShadingGroup':
            changePortInOutName(child,oldParamName,newParamName)
        elif child.getType() == 'ArnoldShadingNode':
            changeParamName(child,oldParamName,newParamName)
        else:
            print 'Ah bon!!!'

    #copy the interfaceControl
    materialNode = startNode
    run = True
    while run:
        if materialNode.getType() == 'NetworkMaterialCreate':
            run = False
        else :
            materialNode = materialNode.getParent()

    matNodeChildren = materialNode.getChildren()
    for node in matNodeChildren:
        #groupStackNode = ''
            if node.getType() == 'GroupStack':
                groupStackChild = node.getChildren()
                for child in groupStackChild:
                    if child.getName().find(oldParamName) >= 0:
                        oldName = child.getName()
                        newName = oldName.replace(oldParamName,newParamName)
                        newNode = copyNode(child)
                        newNode.setName(newName)
                        targetName = newNode.getParameter('targetName').getValue(0).replace(oldParamName,newParamName)
                        newNode.getParameter('targetName').setValue(targetName,0)
                        node.buildChildNode(adoptNode=newNode)
                        path = newNode.getParameter('operators.ops').getChildren()[0].getChild('path').getValue(0).replace(oldParamName,newParamName)
                        newNode.getParameter('operators.ops').getChildren()[0].getChild('path').setValue(path,0)

#change the name to another
changeNodeNameAndParameters(oldParamName='diffuse', newParamName='sheen')

#change the node and children node name
node = NodegraphAPI.GetAllSelectedNodes()[0]
childList = walkChildNode(node)
for child in childList:
    checkNodeName(child,'L0','L1')

#misc function
a = NodegraphAPI.GetAllSelectedNodes()[0]
listPort =[]
for i in a.getInputPorts():
    if i.getName().find('displacementTangent') > 0:
        listPort.append(i)
for port in listPort:
    newName = port.getName().replace('Displacement','SpecularReflection')
    newName = newName.replace('displacementTangent','clearcoat.coatColor')
    a.addInputPort(newName.replace('displacement','coat'))

c = NodegraphAPI.GetNode('L0_coatTransparencyColor_ShadingGroup').getInputPort('L0_coatTransparencyColor_mikFile.Parameters.Color.clampMax.a')
d = NodegraphAPI.GetNode('L0_ShadingGroup').getSendPort('L0_mikLayer.SpecularReflection.clearcoat.coatTransparency.Color.clampMax.a')
c.connect(d)

a = NodegraphAPI.GetNode('L0_ShadingGroup')
x = NodegraphAPI.GetNode('L0_specularRotationUVs_ShadingGroup')
listPort =[]
for i in x.getInputPorts():
    listPort.append(i)
for i in a.getInputPorts():
    if i.getName().find('L0_mikLayer.SpecularReflection.specular.specularColor') == 0:
        endName = i.getName().rsplit('L0_mikLayer.SpecularReflection.specular.specularColor')[1]
        for j in listPort:
            if j.getName().rfind(endName)>0:
                print j.getName() + ' IS CONNECTED TO: ' + i.getName()
                sendPort = a.getSendPort(i.getName())
                j.connect(sendPort)


a = NodegraphAPI.GetNode('mikLayerMix_ShadingGroup')
b = NodegraphAPI.GetNode('L0_ShadingGroup')
c =[]
c= b.getInputPorts()
for i in c:
    newname = i.getName().replace('L0_mikLayer','Layers.L0')
    a.addInputPort(newName)
    sendPort = a.getSendPort(newName)
    i.connect(sendPort)

def changeNameParamInOut():
    listOfNode =  NodegraphAPI.GetAllSelectedNodes()
    for node in listOfNode:
        #node = NodegraphAPI.GetNode('L0_diffuse_ShadingGroup')
        inPort = node.getInputPorts()
        outPort = node.getOutputPorts()
        for port in inPort:
            if port.getName().find('attribute') > 0:
                node.removeInputPort(port.getName())
            if port.getName().find('default.') > 0:
                node.removeInputPort(port.getName())
            name = port.getName().replace('_mikFile','')
            name = name.replace('_user_data_rgba','')
            name = name.replace('default','color')
            node.renameInputPort(port.getName(),name)
            port.addOrUpdateMetadata('label',name)
            print name
        for port in outPort:
            if port.getName().find('out.') > 0:
                node.removeOutputPort(port.getName())
            name = port.getName().replace('mikStaticCondition','color')
            node.renameOutputPort(port.getName(),name)
            port.addOrUpdateMetadata('label',name)
changeNameParamInOut()

node = NodegraphAPI.GetNode('L0_ShadingGroup')
for port in node.getInputPorts():
    name = port.getName().replace('Parameter','Parameter_L0')
    node.renameInputPort(port.getName(),name)
    port.addOrUpdateMetadata('label',name)

#add the mix layer parameters
mixLayerNode = NodegraphAPI.GetNode('mikLayerMix')
shadingGroup = NodegraphAPI.GetNode('mix_ShadingGroup')
layername = '3'
for input in mixLayerNode.getParameter('parameters').getChildren():
    inputName = input.getName()
    #print inputName
    if inputName.find(layername) > 0 :
        if inputName != 'layer'+layername and inputName.find('mask') < 0:
            inShadGroup = 'Layer.Parameters.L'+layername+'.'+input.getName().replace('layer'+layername,'L'+layername+'_')
            print inShadGroup
            shadingGroup.addInputPort(inShadGroup)
            sendPort = shadingGroup.getSendPort(inShadGroup)
            mixLayerNode.getInputPort(inputName).connect(sendPort)
        elif inputName.find('mask') >= 0:
            inShadGroup = 'Layer.Parameters.L'+layername+'.L'+layername+'_'+input.getName().replace(layername,'')
            print inShadGroup,'ddd'
            shadingGroup.addInputPort(inShadGroup)
            sendPort = shadingGroup.getSendPort(inShadGroup)
            mixLayerNode.getInputPort(inputName).connect(sendPort)
        else:
            print 'Bah'

#create in port in function of the page metadata of the shader
topNode = NodegraphAPI.GetNode('L0_ShadingGroup')
node = NodegraphAPI.GetNode('L0_standard_surface')
groupType = 'ID AOVs'
for inPort in node.getInputPorts():
    if len(inPort.getConnectedPorts()) == 0:
        if inPort.getMetadata('page') == groupType:
            if groupType.find(' ') > 0:
                name = 'L0.Parameters.'+groupType.replace(' ','_')+'.'+ inPort.getName()
            else:
                name = 'L0.Parameters.'+groupType+'.'+ inPort.getName()
            topNode.addInputPort(name)
            sendPort = topNode.getSendPort(name)
            inPort.connect(sendPort)