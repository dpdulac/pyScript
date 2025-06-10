#!/usr/bin/env python
# coding:utf-8
#
# David 
#
#
#
#
# katanaCommand.py : 
from Katana import NodegraphAPI
import sys



PATH_TO_ABC = "/s/prods/cu/_sandbox/duda/direction/direction.abc"
PATH_TO_SCENEGRAPH = "/root/world/geo/asset/directionTool"
#create a group Node
root = NodegraphAPI.GetRootNode()
group = NodegraphAPI.CreateNode('Group',root)
group.setName('TransGroup')
#create a MikAbcIn and import the abc
abcIn = NodegraphAPI.CreateNode('MikAbcIn',group)
abcIn.getParameter("name").setValue(PATH_TO_SCENEGRAPH,0)
abcIn.getParameter("abcAsset").setValue(PATH_TO_ABC,0)
#create a visibility Node and set it to False
visi = NodegraphAPI.CreateNode('VisibilityAssign',group)
visi.getParameter('CEL').setValue("/root/world/geo/asset/directionTool/*",0)
visi.getParameter('args.visible.value').setValue(False,0)
posAbcIn = NodegraphAPI.GetNodePosition(abcIn)
atom = (posAbcIn[0],posAbcIn[1] - 100)
print atom, posAbcIn
NodegraphAPI.SetNodePosition(visi, atom)
visi.getInputPort('input').connect(abcIn.getOutputPort('out'))

group.addOutputPort("out")
group.getReturnPort("out").connect(visi.getOutputPort('out'))

#reorder the nodes
DrawingModule.AutoPositionNodes([visi,abcIn])

#get all nodes
NodegraphAPI.GetAllNodes()

nodes = NodegraphAPI.GetAllSelectedNodes()
#to select a node
n = NodegraphAPI.GetNode("Picture_Frame_Wall_Actor1")
NodegraphAPI.SetNodeSelected(n, True)
#to get the viewed node and setting it (blue square)
print NodegraphAPI.GetViewNode().getName() #could also use GetViewNodes() for multiple viewed nodes
NodegraphAPI.SetNodeViewed(group, True, exclusive=True)
#to set an edited node (green square)
NodegraphAPI.GetAllEditedNodes()
NodegraphAPI.SetNodeEdited(group, True, exclusive=True)

#change the name of a backdrop
node= NodegraphAPI.GetAllSelectedNodes()[0]
nodeAttr = node.getAttributes()
nodeAttr["ns_text"] = "newText"
node.setAttributes(nodeAttr)
NodegraphAPI.SetNodeSelected(node, False) # it seems that the text will only be updated once the node is deselected/refreshed
#Louise version
node = NodegraphAPI.CreateNode("Backdrop", NodegraphAPI.GetRootNode())
NodegraphAPI.SetNodeShapeAttr(node, "text", "my text")
NodegraphAPI.SetNodeShapeAttr(node, "fontScale", 1)
NodegraphAPI.SetNodeShapeAttr(node, "sizeX", 300.0)
NodegraphAPI.SetNodeShapeAttr(node, "sizeY", 300.0)
DrawingModule.nodeWorld_setShapeAttr( node, "text", "my text" )
Utils.EventModule.QueueEvent("nodegraph_redraw", 0)

#Marcel example
node = NodegraphAPI.GetNode('AttributeSet')
producer = Nodes3DAPI.GetRenderProducer(node, NodegraphAPI.GetCurrentTime(), True)
sg = ScenegraphManager.getActiveScenegraph()
loc = sg.getSelectedLocations()
prod =  producer.getProducerByPath(loc[0])
attrValue = prod.getGlobalAttribute('geometry').getChildByName('arbitrary').getChildByName('rnd_instancerInstancedObjects').getChildByName('value').getData()[0]

#stack node
stack = NodegraphAPI.CreateNode("GroupStack", NodegraphAPI.GetRootNode())
stack.setChildNodeType("Transform3D")
for i in range(0, 2):
    transform = stack.buildChildNode()
    transform.setName("locator_%d" % i)

#loop example
for i in NodegraphAPI.GetAllNodes() :
    if (i.getType() != 'ImportGroup') and (i.getName().find('overrides') != -1):
        nodes.append(i)
        print i.getName()

#adding a name and group for networkMaterial
n = NodegraphAPI.GetNode('ArnoldShadingNode')
n.getParameter('parameters.Kb').createChildString('hints', "")
n.getParameter('parameters.Kd.hints').setValue("{'dstPage': 'paramGroup', 'dstName': 'paramName'}", 0)

#read the string
a = eval(NodegraphAPI.GetNode('NM_STD_use_rayswitch').getParameter('parameters.firstTerm.hints').getValue(0))
print a['dstName']

#finding if a node has child
n = NodegragraphAPI.GetNode()
hasattr(n, "getChildren")

#xml node
a = NodegraphAPI.GetAllSelectedNodes()[0]
nodesToSerialize = [a]
xlmTree = NodegraphAPI.BuildNodesXmlIO(nodesToSerialize)
print xlmTree.writeString()

#getkatana scene name
FarmAPI.GetKatanaFileName()

#find passes name's in a KLF
lookfile='/s/prods/captain/assets/Library/renderGlobals/light/light_lighting/publish/katana/Library-renderGlobals-base-light_lighting-last.klf'
print GeoAPI.Lookfiles.getPassNamesForFile(lookfile)

#Add a user paramater with comboBox
node = NodegraphAPI.GetAllSelectedNodes()[0]
nodeUserParam = node.getParameters()
userChild = nodeUserParam.getChild("user")
stringParam = userChild.createChildString("globalSetting","SURF_FULL_NO_AOV")
stringParam.setHintString("{'widget':'popup','options':['default','SURF_FULL_NO_AOV','SURF_FULL','SURF_MID']}")

#Add a csript button
node = NodegraphAPI.GetAllSelectedNodes()[0]
nodeUserParam = node.getParameters()
userChild = nodeUserParam.getChild("user")
stringParam = userChild.createChildString("globalSetting","SURF_FULL_NO_AOV")
stringParam.setHintString("{'widget':'scriptButton','buttonText':'refresh klf', 'scriptText': \"print NodegraphAPI.GetAllEditedNodes()  [0].getParameter('source').setValue(\'/s/prods/captain/assets/Library/setupTurn/surface/surface_surfacing/publish/katana/Library-setupTurn-base-surface_surfacing-last.katana\',0) \"}")

#get scene location asset from SG
from sgtkLib import tkutil; tk, sgw, project = tkutil.getTk(fast=True)
def getCastingOnLastAssetModelBase(assetName = 'attendance_office' ) :
    '''return content

    '''
    asset = sgw.Asset(assetName,project =project)
    casting = asset.sg_model_base_casting
    humanCasting = []
    for sgEntity in casting :
        humanCasting.append(sgEntity.code)

    return humanCasting
getCastingOnLastAssetModelBase()


#EXPRESSION
#display teh function of a method
"{0}".format(str(dir(getNode("ROTATION4").numberValue.i0.param.setValue)))
#to set a parameter with expression
"{0}".format(int(getParam("Switch_TEST.in")),str(getParam("Switch_TEST.in").param.setValue(1,0)))
#setting a file name
"/s/prods/cu/sequences/test01/t001_s0001/Light/lighting_deliver/work/images/{0}/{1}/{2}/t001_s0001_lighting_deliver.####.exr".format(str(getNode("rootNode").katanaSceneName).split("-")[-1], "L20", getNode("rod_primary7").outputName, str(getNode("rootNode").katanaSceneName).split("-")[-1])
#get the name of the current node
self.getNode().getName()
#get the user value channel on a parent node
getParam(self.getNode().getParent().getName()+".user.globalSetting")
#or
getParent().user.globalSetting


from kCore.asset import assetApi
aApi = assetApi.BaseAsset()


# SCENE GENERATOR
sgNodes = NodegraphAPI.GetAllNodesByType("SceneGenerator")
for node in sgNodes :
  asset = node.getParameter("file").getValue(0)
  asset = asset.replace("/cu/", "/captain/")
  resolveAsset = aApi.resolvePath(os.path.dirname(asset))
  #print resolveAsset
  fields = aApi.getAssetFields(resolveAsset)
  if not len(fields):
     print "invalid %s for node %s" % (resolveAsset, node.getName())
     continue

  fields[assetApi.assetFieldArea] = assetApi.assetPublishSpecialArea
  fields[assetApi.assetFieldSpecialVersion] = "last"

  # TODO : naming convention rules
  name = fields[assetApi.assetFieldAsset]
  if name.endswith("_001"):
     fields[assetApi.assetFieldAsset] = name.replace("_001", "")
     fields[assetApi.assetFieldName] = name.replace("_001", "")

  fields[assetApi.assetFieldStep] = "actor_tk"
  fileType = fields[assetApi.assetFieldFileType]
  if fileType == "ActorPackagerFolder" :
     fields[assetApi.assetFieldTask] = "actor"
  else :
     fields[assetApi.assetFieldTask] = "actor_shading"
  results = aApi.getAssetIds(fields)

  if len(results) :
      newId = os.path.join(results[0], "%s.sd" % fields[assetApi.assetFieldName])
      print "\nSet node %s newId %s" % (node.getName(), newId)
      node.getParameter("file").setValue(newId, 0)

# TEXSET MANAGER
txNodes = NodegraphAPI.GetAllNodesByType("TexsetManager")

for node in txNodes :
   asset =  node.getParameter('asset').getValue(0)
   asset = asset.replace("/cu/", "/captain/")
   fields = aApi.getAssetFields(asset)

   if not len(fields):
      continue
   name = fields[assetApi.assetFieldAsset]

   # TODO : naming convention rules
   if name.endswith("_001"):
      fields[assetApi.assetFieldAsset] = name.replace("_001", "")

   txId = aApi.buildAssetId(fields)
   node.getParameter('asset').setValue(txId, 0)

txDropNodes = NodegraphAPI.GetAllNodesByType("TexturesDrop")
for node in txDropNodes:
    textures = node.getTextures()
    print textures
    for i in range(0,len(textures)):
        textures[i] = ( textures[i][0].replace("_001", "").replace("_002", "_b").replace("_003", "_c").replace("_003", "_d").replace("_004", "_e").replace("_005", "_f").replace("/cu/", "/captain/"), textures[i][1], textures[i][2] )
        print textures[i][0]
    node.setTextures(textures)

# SHADING INIT
siNodes = NodegraphAPI.GetAllNodesByType("ShadingInit")
for node in siNodes:
   asset = node.getParameter("file").getValue(0)
   asset = asset.replace("/cu/", "/captain/")
   resolveAsset = aApi.resolvePath(os.path.dirname(asset))
   fields = aApi.getAssetFields(resolveAsset)
   if not len(fields):
      print "invalid %s for node %s" % (resolveAsset, node.getName())
      continue

   fields[assetApi.assetFieldArea] = assetApi.assetPublishSpecialArea
   fields[assetApi.assetFieldSpecialVersion] = "last"

   # TODO : naming convention rules
   name = fields[assetApi.assetFieldAsset]
   if name.endswith("_001"):
      fields[assetApi.assetFieldAsset] = name.replace("_001", "")
      fields[assetApi.assetFieldName] = name.replace("_001", "")

   results = aApi.getAssetIds(fields)
   if len(results) :
       newId = os.path.join(results[0], "%s.sd" % fields[assetApi.assetFieldName])
       print "\nSet node %s newId %s" % (node.getName(), newId)
       node.getParameter("file").setValue(newId, 0)


#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#TEST
#return the list of parameter if they exist
def param(node=""):
    parmlist = ["CEL",'overrides.CEL',"root","rootLocation","path","asset","paths","parameters.filename.value"]
    paramExist = []
    for i in parmlist:
        if NodegraphAPI.GetNode(node).getParameter(i):
            paramExist.append(i)
    return paramExist

#replace the old name by the new name
def doChange(nodeName = "", paramName = "",oldName = "alarm_001", newName = "alarm"):
    nodeParam = NodegraphAPI.GetNode(nodeName).getParameter(paramName)
    #if the parameter name is paths get it's children and fixe the name
    if paramName == "paths":
        ab = nodeParam.getChildren()
        print ab
        for i in ab:
            concat = paramName + "." + i.getName()
            nodeValue = NodegraphAPI.GetNode(nodeName).getParameter(concat).getValue(0)
            newNodeValue = nodeValue.replace(oldName,newName).replace("__SHADING__:ALL","BDD:ALL")
            NodegraphAPI.GetNode(nodeName).getParameter(concat).setValue(newNodeValue,0)
            nodeValue = NodegraphAPI.GetNode(nodeName).getParameter(concat).getValue(0)
    else:
        #get the value from the parameter
        nodeValue = NodegraphAPI.GetNode(nodeName).getParameter(paramName).getValue(0)
        #change old name with new name
        newNodeValue = nodeValue.replace(oldName,newName)
        NodegraphAPI.GetNode(nodeName).getParameter(paramName).setValue(newNodeValue,0)

        #change "cu" to "captain"
        nodeValue = NodegraphAPI.GetNode(nodeName).getParameter(paramName).getValue(0)
        changeCu = nodeValue.replace("cu","captain").replace("__SHADING__:ALL","BDD:ALL")
        NodegraphAPI.GetNode(nodeName).getParameter(paramName).setValue(changeCu,0)

#change the old name with the new name in the different parameter chanel
def changeName(oldName = "alarm_001", newName = "alarm"):
    #get all the selected nodes
    selectedNodes = NodegraphAPI.GetAllSelectedNodes()
    #check if there is some importGroup if yes get all the node inside and add them to the selectedNodes
    for i in selectedNodes:
        if i.getType() == "ImportGroup":
            groupChild = i.getChildren()
            for j in groupChild:
                selectedNodes.append(j)
    # for all the nodes in selectedNodes check if they have any of the parameters with the old name then change it to the new name
    for i in selectedNodes:
        name = i.getName()
        parameterName = param(name)
        print parameterName
        #if the parameter exist in the node check and change the old name for the new name and replace "cu" by "captain"
        if parameterName :
            for j in parameterName:
               doChange(name,j,oldName, newName)

changeName(oldName="trash_bin_001", newName= "trash_bin")

#create a scenegenerator and try to load the last file
def createSceneGenerator(name="donuts"):
    #root
    rootNode = NodegraphAPI.GetRootNode()
    #name to put the asset under
    rootPath = "/root/world/geo/prop/"+name
    #get the selected node and it's position
    selectNode = NodegraphAPI.GetAllSelectedNodes()[0]
    pos = NodegraphAPI.GetNodePosition(selectNode)
    #create a new pos for the sceneGenerator
    newPos = (pos[0], pos[1] + 100)
    #create the SceneGenerator, set is path and position it
    sceneGenerator = NodegraphAPI.CreateNode("SceneGenerator", rootNode)
    sceneGenerator.getParameter('root').setValue(rootPath,0)
    sceneGenerator.setName(name)
    NodegraphAPI.SetNodePosition(sceneGenerator, newPos)

    #connect the SceneGenerator to the next node
    sceneGeneratorOutPort = sceneGenerator.getOutputPort("out")
    selectNodeOutPort = selectNode.getOutputPort("out")
    #get the port to which the selectedNode is connected
    selectNodeOutPortConnected = selectNodeOutPort.getConnectedPorts()[0]
    #connect the output of the SceneGenerator
    sceneGeneratorOutPort.connect(selectNodeOutPortConnected)

    #file to find the last asset
    filePathBase = "/s/prods/captain/assets/Prop/" + name + "/actor_tk/actor/publish/maya/"
    #grab the last directory
    dirList = os.listdir(filePathBase)
    dirLast = ""
    #grab the directory who contain the word "last"
    for i in dirList:
        if i.find("_last"):
            dirLast = i
    filePathLast = filePathBase + dirLast
    dirList = os.listdir(filePathLast)
    dirLast = ""
    for i in dirList:
        if os.path.isdir(filePathLast +"/" + i):
            print i
            dirLast = i
    filePath = filePathLast + "/" + dirLast + "/" + name + ".sd"
    print filePath
    if os.path.isfile(filePath):
        sceneGenerator.getParameter('file').setValue(filePath,0)
    else:
        print "shit"

createSceneGenerator(name="home_room_teacher_desk")

/////////////////////////////////////////////////////////////////////////////////////////
from Katana import NodegraphAPI
from Katana import UI4

# Get list of selected nodes
nodeList = NodegraphAPI.GetAllSelectedNodes()
# Find Nodegraph tab and float nodes
nodegraphTab = UI4.App.Tabs.FindTopTab('Node Graph')
if nodegraphTab:
    nodegraphTab.floatNodes(nodeList)

///////////////////////////////////////////////////////////////////////////////////////////
#creating a graph state variable
def AddGlobalGraphStateVariable(name, options):
    variablesGroup = NodegraphAPI.GetRootNode().getParameter('variables')
    variableParam = variablesGroup.createChildGroup(name)
    variableParam.createChildNumber('enable', 1)
    variableParam.createChildString('value', options[0])
    optionsParam = variableParam.createChildStringArray('options', len(options))
    for optionParam, optionValue in zip(optionsParam.getChildren(), options):
        optionParam.setValue(optionValue, 0)
    return variableParam.getName()

//////////////////////////////////////////////////////
#test to find bounding box
def WalkBoundAttrLocations(producer, attribute = "bound", listValue = [], producerType = "polymesh"):
    '''
    :param producer: input node
    :param attribute: attribute to get
    :param listValue: list for value to be recuparated
    :param producerType: type of producer
    :return: list of value recuparated
    '''
    #if producer is not None and producer.getType() in ("group", "component", "assembly","polymesh") : #
    if producer is not None and producerType in ("group", "component", "assembly","polymesh"):
        if producer.getType() == producerType:
            #print producer.getFullName()
            boundAttr =  producer.getAttribute(attribute)
            if boundAttr is not None :
                listValue.append(boundAttr.getNearestSample(0))

        for child in producer.iterChildren():
            WalkBoundAttrLocations(child, attribute, listValue, producerType)
        return listValue
    else:
        print "producer or producerType not good"

def boundingBox(bound):
    xmin = []
    xmax = []
    ymin = []
    ymax = []
    zmin = []
    zmax = []
    for i in range(0,len(bound)):
        xmin.append(bound[i][0])
        xmax.append(bound[i][1])
        ymin.append(bound[i][2])
        ymax.append(bound[i][3])
        zmin.append(bound[i][4])
        zmax.append(bound[i][5])
    xmin.sort()
    xmax.sort()
    ymin.sort()
    ymax.sort()
    zmin.sort()
    zmax.sort()
    return [xmin[0],xmax[-1],ymin[0],ymax[-1],zmin[0],zmax[-1]]

def getBB(outPutType = "all"):
    node = NodegraphAPI.GetAllSelectedNodes()[0]
    graphState = NodegraphAPI.GetGraphState(0)
    producer = Nodes3DAPI.GetGeometryProducer(node, graphState)
    sg = ScenegraphManager.getActiveScenegraph()
    loc = sg.getSelectedLocations()[0]
    geoProducer = producer.getProducerByPath(loc)
    listValue = []
    if geoProducer is not None :
        WalkBoundAttrLocations(geoProducer, "bound", listValue,"polymesh")
    if outPutType == "all":
        return boundingBox(listValue)
    elif outPutType == "-x":
        return boundingBox(listValue)[0]
    elif outPutType == "x":
        return boundingBox(listValue)[1]
    elif outPutType == "-y":
        return boundingBox(listValue)[2]
    elif outPutType == "y":
        return boundingBox(listValue)[3]
    elif outPutType == "-z":
        return boundingBox(listValue)[4]
    elif outPutType == "z":
        return boundingBox(listValue)[5]
    else:
        return boundingBox(listValue)

print getBB()

////////////////////////////////////////////////////////
#turn output layer off
renderNodes = NodegraphAPI.GetAllNodesByType('Render', includeDeleted=False)
for node in renderNodes:
    outputPass = len(node.getParameter('outputs.enabledFlags').getChildren())
    for i in range(1,outputPass):
        node.getParameter('outputs.enabledFlags.i'+str(i)).setValue(0,0)

////////////////////////////////////////////////////////////
#find the camera path in the scenegraph
import kCore.attribute as kAttr
node = NodegraphAPI.GetAllSelectedNodes()[0]
producer = Nodes3DAPI.GetGeometryProducer(node, 0)
camproducer = producer.getProducerByPath("/root/world/cam")
children = []
kAttr.walkChildrenProducer(camproducer, children)
cameraPath = None
for child in children :
     if child.getType() == "camera":
          cameraPath = child.getFullName()
          print cameraPath

/////////////////////////////
#getting the casting of location
from sgtkLib import tkutil; tk, sgw, project = tkutil.getTk(fast=True)
def getCastingOnLastAssetModelBase(assetName = 'attendance_office' ) :
    '''return content

    '''
    asset = sgw.Asset(assetName,project =project)
    casting = asset.sg_model_base_casting
    humanCasting = []
    for sgEntity in casting :
        humanCasting.append(sgEntity.code)

    return humanCasting
getCastingOnLastAssetModelBase()

//////////////////////////
#find if camera asset exist
import glob
import os

PROD = os.environ['PROD_ROOT']
assetList = os.listdir(PROD+"/cameras/Asset/assets/Prop")
goodCam =''
for asset in assetList:
    path = PROD + '/cameras/Asset/assets/Prop/{0}/*/model/model_hi/publish/caches/*-model_hi-last.abc'.format(asset)
    allCam = glob.glob(path)
    #print allCam
    if len(allCam) > 0:
        for cam in allCam:
            if cam.find('turnCamera') > 1:
                goodCam = cam
                print "Good Camera for: " + asset
        if goodCam == '':
            goodCam = allCam[1]
            print "using: " + goodCam + " instead of turnCam"
    else:
        print "No Camera for: "+asset

/////////////////////////
#recursively walk to find parameters
def walkChildParam(param,listChild=[]):
    if param.getChildren() is not None:
        listChild.append(param)
        for child in param.getChildren():
            walkChildParam(child,listChild)

//////////////////////////////////
#print all parameters of root node
def walkChildParam(param,listChild=[]):
    if param.getChildren() is not None:
        listChild.append(param)
        for child in param.getChildren():
            walkChildParam(child,listChild)
listChild=[]
a = NodegraphAPI.GetRootNode().getParameters().getChildren()
print a
for i in a:
    walkChildParam(i,listChild)

for i in listChild:
    print i.getName()

//////////////////////////////////////////
#RenderFilter
def getActiveRenderFilterNodes():
    nodeNames = NodegraphAPI.GetRootNode().getParameter('activeRenderModes').getValue(NodegraphAPI.GetCurrentTime()).split()

    nodes = [NodegraphAPI.GetNode(x) for x in nodeNames]
    nodes = [x for x in nodes if x and x.getBaseType() == 'RenderFilter']
    nodes = [x for x in nodes if x.getParent() and \
            x.getParent().getBaseType() == 'InteractiveRenderFilters']
    return nodes

def setActiveRenderFilterNodes(nodeList):
    parameter = NodegraphAPI.GetRootNode().getParameter('activeRenderModes')
    parameter.setExpressionFlag(True)

    expr = ' + " " + '.join('getNode("%s").getNodeName()' % node.getName() for node in nodeList)
    parameter.setExpression(expr)

test = [ x for x in NodegraphAPI.GetAllNodesByType('RenderFilter', False, False) if x.getBaseType() == 'RenderFilter']

#get the activeRenderModes turn on or off
routNode = NodegraphAPI.GetRootNode().getParameter('activeRenderModes')
routNode.setExpression("")
routNode.setExpression('getNode("OCC5").getNodeName() + " " + getNode("DIFFUSE_OFF3").getNodeName() + " " + getNode("SPEC_OFF3").getNodeName() + " " + getNode("UV5").getNodeName()')

#fit bacdrop to selected node
nodeGraphTab = UI4.App.Tabs.FindTopTab('Node Graph')
nodeGraphTab._NodegraphPanel__fitBackdropNode()

#rename les directory du renderOutput Define
def getAllNodeChild(inputNode = NodegraphAPI.GetAllNodesByType('RenderManager', includeDeleted=False), listNode = []):
    for item in inputNode:
        listNode.append(item)
        try:
            item.getChildren()
        except:
            print item.getName() + " doesn't have child"
        else:
            getAllNodeChild(inputNode=item.getChildren(),listNode=listNode)

def giveCamPassName(exp='getParent().getParent().layerName+"_"+str(getParent().cameraLocation).split("/")[-2]'):
    nodeRender = NodegraphAPI.GetAllNodesByType('RenderManager', includeDeleted=False)
    if len(nodeRender) < 1:
        print "there is no RenderManager in the scene"
    else:
        listNode = []
        listPOD=[]
        getAllNodeChild(nodeRender,listNode)
        for item in listNode:
            if item.getType() == 'ProjectRenderOutputDefine':
                listPOD.append(item)
        for item in listPOD:
            tmp = NodegraphAPI.GetNode(item.getName()).getParameter('outputOptions.layer')
            tmp.setExpression(exp)
giveCamPassName()

#center the transform
#create the group containing the nodes
rotNode =NodegraphAPI.GetRootNode()
offsetGroup = NodegraphAPI.CreateNode('Group', parent=rootNode)
offsetGroup.setName('TransformCenter')
#add input and output connection
inPortGroup = offsetGroup.addInputPort('in')
outPortGroup = offsetGroup.addOutputPort('out')
#add user parameters
param = offsetGroup.getParameters()
#file path
stringPath = param.createChildString("path","/root")
stringPath.setHintString("{'widget': 'scenegraphLocation'}")
#offset
offsetParamGroup = param.createChildGroup("Offset")
offsetX = offsetParamGroup.createChildNumber('X_offset',0)
offsetX.setHintString("{'slider':'True','slidermin':'-100','slidermax':'100'}")
offsetY = offsetParamGroup.createChildNumber('Y_offset',0)
offsetY.setHintString("{'slider':'True','slidermin':'-100','slidermax':'100'}")
offsetZ = offsetParamGroup.createChildNumber('Z_offset',0)
offsetZ.setHintString("{'slider':'True','slidermin':'-100','slidermax':'100'}")
# #rotation
# rotParamGroup = param.createChildGroup("Rotation")
# rotX = rotParamGroup.createChildNumber('X',0)
# rotX.setHintString("{'slider':'True','slidermin':'-360','slidermax':'360'}")
# rotY = rotParamGroup.createChildNumber('Y',0)
# rotY.setHintString("{'slider':'True','slidermin':'-360','slidermax':'360'}")
# rotZ = rotParamGroup.createChildNumber('Z',0)
# rotZ.setHintString("{'slider':'True','slidermin':'-360','slidermax':'360'}")
# #translation
# transParamGroup =  param.createChildGroup("Translate")
# transX = transParamGroup.createChildNumber('X',0)
# transX.setHintString("{'slider':'True','slidermin':'-100','slidermax':'100'}")
# transY = transParamGroup.createChildNumber('Y',0)
# transY.setHintString("{'slider':'True','slidermin':'-100','slidermax':'100'}")
# transZ = transParamGroup.createChildNumber('Z',0)
# transZ.setHintString("{'slider':'True','slidermin':'-100','slidermax':'100'}")
# #scale
# scaleParamGroup = param.createChildGroup("Scale")
# scaleX = scaleParamGroup.createChildNumber('X',0)
# scaleX.setHintString("{'slider':'True','slidermin':'-10','slidermax':'10'}")
# scaleY = scaleParamGroup.createChildNumber('Y',0)
# scaleY.setHintString("{'slider':'True','slidermin':'-10','slidermax':'10'}")
# scaleZ = scaleParamGroup.createChildNumber('Z',0)
# scaleZ.setHintString("{'slider':'True','slidermin':'-10','slidermax':'10'}")

#create the transform node
transNode = NodegraphAPI.CreateNode('Transform3D',offsetGroup)
#set the path to the parent node path using expression
transExp = transNode.getParameter('path')
transExp.setExpression('getParent().path')
transNodeName = transNode.getName()
transPos = NodegraphAPI.GetNodePosition(transNode)

#create the Op node
script = 'local userOffset = Interface.GetOpArg("user.offset"):getNearestSample(0.0) \nlocal bound = Interface.GetAttr("bound"):getNearestSample(0)\nlocal pivotX = ((bound[1]+bound[2])/2)+userOffset[1]\nlocal pivotY = ((bound[3]+bound[4])/2)+userOffset[2]\nlocal pivotZ = ((bound[5]+bound[6])/2)+userOffset[3]\nlocal gb = GroupBuilder()\ngb:set("locationPath", StringAttribute(Interface.GetInputLocationPath()))\ngb:set("pivot", DoubleAttribute({pivotX, pivotY, pivotZ}))\ngb:set("makeInteractive", IntAttribute(1))\ngb:set("applyFirst", IntAttribute(0))\nInterface.ExecOp("Transform", gb:build())'
opNode = NodegraphAPI.CreateNode('OpScript',offsetGroup)
opNodeScript = opNode.getParameter('script.lua')
opNodeScript.setValue(script,0)
opNodeCEL = opNode.getParameter('CEL')
opNodeCEL.setExpression('getParent().path')
opNodePos = (transPos[0], transPos[1]-100)
NodegraphAPI.SetNodePosition(opNode,opNodePos)
opParam = opNode.getParameters()
#user parameter for the opScript
opOffsetGroup = opParam.createChildGroup("user")
opOffset = opOffsetGroup.createChildNumberArray('offset',3)
opNode.getParameter('user.offset.i0').setExpression("getParent().Offset.X_offset")
opNode.getParameter('user.offset.i1').setExpression("getParent().Offset.Y_offset")
opNode.getParameter('user.offset.i2').setExpression("getParent().Offset.Z_offset")

#tansformEdit Node
transEditNode = NodegraphAPI.CreateNode("TransformEdit",offsetGroup)
transEditExp = transEditNode.getParameter('path')
transEditExp.setExpression('getParent().path')
action = transEditNode.getParameter('action')
action.setValue("override interactive transform",0)
transEditPos = (opNodePos[0],opNodePos[1]-100)
NodegraphAPI.SetNodePosition(transEditNode ,transEditPos)

#connect the node
sendGroup = offsetGroup.getSendPort('in')
returnGroup = offsetGroup.getReturnPort('out')
transNode.getInputPort('in').connect(sendGroup)
transNode.getOutputPort('out').connect(opNode.getInputPort('i0'))
opNode.getOutputPort('out').connect(transEditNode.getInputPort('in'))
transEditNode.getOutputPort('out').connect(returnGroup)



#renameLayer in renderManager
def renameRenderManagerLayer(prefix = 'midBlur_'):
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
        newName = prefix + item.getName()
        item.setName(newName)


#find path in scenegraph
def WalkBoundAttrLocations(producer,listPath=['/root','/root/world','/root/world/geo']):
    listWord = ['BDD:ALL','RIG','/rig']
    if producer is not None :
        path = producer.getFullName()
        if not any(word in path for word in listWord):
            listPath.append(producer.getFullName())

        for child in producer.iterChildren():
            WalkBoundAttrLocations(child,listPath)
    else:
        print "producer or producerType not good"
    return listPath

sg = ScenegraphManager.getActiveScenegraph()
node = NodegraphAPI.GetNode( 'root' )
time = NodegraphAPI.GetCurrentTime()
producer = Nodes3DAPI.GetGeometryProducer( node, time)
prod = producer.getProducerByPath('/root/world/geo/location')
pathToOpen = WalkBoundAttrLocations(prod)
sg.openLocations(pathToOpen)
sg.clearOpenLocations()

#pinne mesh to be view without opening the sceneGraph
def WalkBoundAttrLocations(producer,listPath=[]):
    listWord = ['BDD:ALL']
    if producer is not None :
        path = producer.getFullName()
        if any(word in path for word in listWord):
            listPath.append(producer.getFullName())

        for child in producer.iterChildren():
            WalkBoundAttrLocations(child,listPath)
    else:
        print "producer or producerType not good"
    return listPath

sg = ScenegraphManager.getActiveScenegraph()
node = NodegraphAPI.GetNode( 'root' )
time = NodegraphAPI.GetCurrentTime()
producer = Nodes3DAPI.GetGeometryProducer( node, time)
prod = producer.getProducerByPath('/root/world/geo/location')
pathToOpen = WalkBoundAttrLocations(prod)
for item in pathToOpen:
    sg.addPinnedLocation(item)

#add interactive param with expression
topNode = NodegraphAPI.GetNode('Env_mod_Setup')
topNodeName = topNode.getName()
children = topNode.getChildren()
gafferNode = None
for node in children:
    if node.getType() == 'GafferThree':
        gafferNode = node
        break
gafferNodeName = gafferNode.getName()
gafferRootPackage  = gafferNode.getRootPackage()
newLight = gafferRootPackage.createChildPackage("LightPackage", name='User_light', peerNames=None)
newLight.setShader('arnoldLight', 'quad_light', asExpression=False)
newLightName = newLight.getName()
materialNode = gafferRootPackage.getChildPackage(newLightName).getMaterialNode()

#user param
userParam = topNode.getParameter('user')
#create a new group for the light
lightParamGroup = userParam.createChildGroup(newLightName)
lightParamGroup.setHintString("{'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../useOccShader', 'conditionalVisValue': '0'}, 'open': 'True'}")

# create parameter for the new light to expose
colParam = lightParamGroup.createChildNumberArray('color',3)       #color parameter
colParam.setHintString("{'widget': 'color'}")
topNode.getParameter('user.'+newLightName+'.color.i0').setValue(1.0,0)
topNode.getParameter('user.'+newLightName+'.color.i1').setValue(1.0,0)
topNode.getParameter('user.'+newLightName+'.color.i2').setValue(1.0,0)
expressionPathBase = "getParam('" + topNodeName + ".user."+ newLightName

expParam = lightParamGroup.createChildNumber('exposure',1)
expParam.setHintString("{'slider': 'True', 'slidermax': '100.0'}")

butParam = lightParamGroup.createChildString('deleteButon',"delete")
butParam.setHintString("{'widget': 'scriptButton', 'buttonText': 'delete', 'scriptText': \"topNode = node  \\nlightName ='"+newLightName+"' \\nprint  'deleting '+lightName\\ngafferNodeName = '"+gafferNodeName+"' \\ngafferNode = NodegraphAPI.GetNode(gafferNodeName) \\ngafferRootPackage  = gafferNode.getRootPackage()\\nlightToDelete = gafferRootPackage.getChildPackage(lightName) \\nlightToDelete.delete()\\nparaToDelete = topNode.getParameter('user').getChild(lightName) \\ntopNode.getParameter('user').deleteChild(paraToDelete) \"}")

materialNode.checkDynamicParameters()

listColor = ['i0','i1','i2']
materialNode.getParameter('shaders.arnoldLightParams.color.enable').setValue(1,0)
for col in listColor:
    expression = expressionPathBase + ".color."+col +"')"
    channel = materialNode.getParameter('shaders.arnoldLightParams.color.value.'+col)
    channel.setExpression(expression,True)

expression = expressionPathBase + ".exposure')"
materialNode.getParameter('shaders.arnoldLightParams.exposure.enable').setValue(1,0)
materialNode.getParameter('shaders.arnoldLightParams.exposure.value').setExpression(expression,True)
nodeView = NodegraphAPI.GetViewNode()
print 'light '+newLightName+' created'

################################################################################################
#set node color
def setNodeColor( r =1.0, g = 1.0, b =1.0):
    nodes = NodegraphAPI.GetAllSelectedNodes()
    for node in nodes:
        NodegraphAPI.SetNodeShapeAttr( node,  "colorr", r )
        NodegraphAPI.SetNodeShapeAttr( node,  "colorg", g )
        NodegraphAPI.SetNodeShapeAttr( node,  "colorb", b )
        DrawingModule.SetCustomNodeColor( node, r, g, b)

############################################################################################
#create a mikeMaterial nodes
def makeMikeMat():
    #create a shading node for the mikMaterial
    mikMaterial = NodegraphAPI.CreateNode('ArnoldShadingNode',NodegraphAPI.GetRootNode())
    #set the node name
    mikMaterial.getParameter('name').setValue('mikMaterial',0)
    #set the material to a mikMaterial node
    mikMaterial.getParameter('nodeType').setValue('mikMaterial',0)
    #get the pos of the node
    mikMaterialPos = NodegraphAPI.GetNodePosition(mikMaterial)
    #create a shading node for the mikMaterialBase
    mikMaterialBase = NodegraphAPI.CreateNode('ArnoldShadingNode',NodegraphAPI.GetRootNode())
    mikMaterialBase.getParameter('name').setValue('mikMaterialBase',0)
    mikMaterialBase.getParameter('nodeType').setValue('mikMaterialBase',0)
    #set the pos of the mikMaterialBase under the mikMaterial
    mikMaterialBasePos = (mikMaterialPos[0],mikMaterialPos[1] - 50)
    NodegraphAPI.SetNodePosition(mikMaterialBase,mikMaterialBasePos)
    #checkDynamicParameters otherwise there is no connections possible
    mikMaterial.checkDynamicParameters()
    mikMaterialBase.checkDynamicParameters()
    #connect the ports
    mikeMaterialOutPort = mikMaterial.getOutputPort('out')
    mikMaterialBaseInPort = mikMaterialBase.getInputPort('layer0')
    mikeMaterialOutPort.connect(mikMaterialBaseInPort)
    currentSelection = NodegraphAPI.GetAllSelectedNodes()
    #deselect all the node to select only the 2 created nodes and put them floating under the mouse
    for node in currentSelection:
        NodegraphAPI.SetNodeSelected(node,False)
    NodegraphAPI.SetNodeSelected(mikMaterialBase,True)
    NodegraphAPI.SetNodeSelected(mikMaterial,True)
    # Get list of selected nodes
    nodeList = NodegraphAPI.GetAllSelectedNodes()
    # Find Nodegraph tab and float nodes
    nodegraphTab = UI4.App.Tabs.FindTopTab('Node Graph')
    if nodegraphTab:
        nodegraphTab.floatNodes(nodeList)

//////////////////////////////////////////////////////////////////////////////////////
# change the name of hints in shader
selectedNodes = NodegraphAPI.GetAllSelectedNodes()
for node in selectedNodes:
    parameters = 'parameters'
    allParam = node.getParameter('parameters')
    for param in allParam.getChildren():
        paramPath = parameters+'.'+param.getName()+'.hints'
        try:
            value = node.getParameter(paramPath).getValue(0)
        except :
            print 'no hints \n'
        else:
            a = value.replace('roughness','rotation_vector')
            b = a.replace('wwwwwww','specular')
            node.getParameter(paramPath).setValue(b,0)
            print b


/////////////////////////////////////////////////////////////////////
#switch shader node
def createSwitcher(name = 'diffuse', nodeColor=True, pageName = 'diffuse', valueDefault = 1.0, groupNodeColor = [.2,.36,.1]):
    #create the Group node
    groupNode = NodegraphAPI.CreateNode('Group', parent=NodegraphAPI.GetRootNode())
    groupNode.setName(name+'_Switch')
    groupNode.addOutputPort('out')
    groupNode.addInputPort('i0')

    #create the switcher
    switcher = NodegraphAPI.CreateNode('ArnoldShadingNode',groupNode)
    switcher.getParameter('name').setValue('switcher_'+name+'_user',0)
    switcher.getParameter('nodeType').setValue('user_data_int',0)
    switcher.checkDynamicParameters()
    switcher.getParameter('parameters.attribute.enable').setValue(1,0)
    switcher.getParameter('parameters.attribute.value').setValue('user'+name.title()+'Choice',0)
    switcher.getParameter('parameters.default.enable').setValue(1,0)
    #create the hint string for the parameters
    hintString = "{'widget': 'mapper', 'dstName': '"+name+"_source', 'options__order': ['map', 'user'], 'dstPage': '"+pageName+"', 'options': {'map': 0.0, 'user': 1.0}}"
    switcher.getParameter('parameters.default').createChildString('hints', hintString)
    switcher.getParameter('parameters.default.value').setValue(1,0)
    #reposition the switcher node
    switcherPos = NodegraphAPI.GetNodePosition(switcher)
    switcherNewPos = (switcherPos[0]-300,switcherPos[1])
    NodegraphAPI.SetNodePosition(switcher,switcherNewPos)

    #create the switch Node
    switch = NodegraphAPI.CreateNode('ArnoldShadingNode',groupNode)
    switch.getParameter('name').setValue('switch_'+name+'_source',0)
    if nodeColor:
        switch.getParameter('nodeType').setValue('switch_rgba',0)
        switch.checkDynamicParameters()
        switch.getParameter('parameters.input1.enable').setValue(1,0)
        # create the hint string
        switchHintString = "{'dstPage': '"+pageName+"', 'dstName': '"+name+"_user'}"
        switch.getParameter('parameters.input1').createChildString('hints', switchHintString)
        #set the default value
        for channel in ['i0','i1','i2']:
            switch.getParameter('parameters.input1.value.'+channel).setValue(valueDefault,0)
        #connect the switcher to the switch Node
        switcher.getOutputPort('out').connect(switch.getInputPort('index'))
        #connect teh switch to the group node
        sendNodeGroup = groupNode.getSendPort('i0')
        sendNodeGroup.connect(switch.getInputPort('input0'))
        returnNodeGroup = groupNode.getReturnPort('out')
        switch.getOutputPort('out').connect(returnNodeGroup)
    else:
        switch.getParameter('nodeType').setValue('alSwitchFloat',0)
        switch.checkDynamicParameters()
        switch.getParameter('parameters.inputB.enable').setValue(1,0)
        #create the hint string and seting the widget to be a slider
        switchHintString = "{'slider': 'True','dstPage': '"+pageName+"', 'dstName': '"+name+"_user'}"
        switch.getParameter('parameters.inputB').createChildString('hints', switchHintString)
        #set the default value
        switch.getParameter('parameters.inputB.value').setValue(valueDefault,0)
        #connect the switcher to the switch Node
        switcher.getOutputPort('out').connect(switch.getInputPort('mix'))
        #connect teh switch to the group node
        sendNodeGroup = groupNode.getSendPort('i0')
        sendNodeGroup.connect(switch.getInputPort('inputA'))
        returnNodeGroup = groupNode.getReturnPort('out')
        switch.getOutputPort('out').connect(returnNodeGroup)

    #color the group node
    NodegraphAPI.SetNodeShapeAttr( groupNode,  "colorr", groupNodeColor[0] )
    NodegraphAPI.SetNodeShapeAttr( groupNode,  "colorg", groupNodeColor[1] )
    NodegraphAPI.SetNodeShapeAttr( groupNode,  "colorb", groupNodeColor[2] )
    #DrawingModule.SetCustomNodeColor( node, r, g, b)
    #deselect all the node to select only the 2 created nodes and put them floating under the mouse
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

def setNodeColor( r =1.0, g = 1.0, b =1.0):
    nodes = NodegraphAPI.GetAllSelectedNodes()
    for node in nodes:
        NodegraphAPI.SetNodeShapeAttr( node,  "colorr", r )
        NodegraphAPI.SetNodeShapeAttr( node,  "colorg", g )
        NodegraphAPI.SetNodeShapeAttr( node,  "colorb", b )
        DrawingModule.SetCustomNodeColor( node, r, g, b)

#################################change the hints on shader

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

##########################starting arnold 5

rez env asterix2TkConfig katana-2.1 kToA-2.0 mimtoaShaders mikrosShaders mikAbcIn-rc.0.6.0  sceneGenerator-rc.0.5.0 setupInstancer asterix2Core katanatk katanaCore katanaTools katanaResources animCurveApply mikMetamorphose mikParentConstraint mikScaleConstraint multiLayerLookFileResolve multiplyDoubleAndSet projectRenderOutputDefine rectifyController setDress shallowHierarchyCopy shadingInit -- katana

#######################################################################
#change param name to match node name
def checkNodeName(nodeType = 'ArnoldShadingNode',select = False):
    nodesSelected = []
    if select:
        allSelectedNodes  = NodegraphAPI.GetAllSelectedNodes()
        for node in allSelectedNodes:
            #check if there is a parameter name on the node
            if node.getParameter('name') != None:
                nodesSelected.append(node)
    else:
        nodesSelected = NodegraphAPI.GetAllNodesByType(nodeType)
    for node in nodesSelected:
        nodeName = node.getName()
        nodeParamName = node.getParameter('name').getValue(0)
        if nodeParamName != nodeName:
            node.getParameter('name').setValue(nodeName,0)
            print 'changing '+ nodeParamName + ' to: '+ nodeName

###########################################################################################
#connect widget to blocker
def createBlocker(name='Blocker01',root = NodegraphAPI.GetRootNode(),celExp = 'getParent().'):
    #root node
    rootNode = root
    #create the groupNode
    groupNode = NodegraphAPI.CreateNode('Group',rootNode)
    groupNode.setName(name)
    #add in and out port
    groupNodeIn = groupNode.addInputPort('in')
    groupNodeOut = groupNode.addOutputPort('out')
    #add attribute to switch the display of group node to normal node
    groupNodeAttrDict = {'ns_basicDisplay': 1,'ns_iconName': ''}
    groupNode.setAttributes(groupNodeAttrDict)
    #userParam
    groupParam = groupNode.getParameters().createChildGroup(name)
    groupParam.setHintString("{'open': 'True'}")
    celParam = groupParam.createChildString('CEL','')
    shapePathParam = groupParam.createChildString('path Name','/root/world/geo/Blocker1')
    shapePathParam.setHintString("{'widget': 'scenegraphLocation'}")
    shapeParam = groupParam.createChildString('blocker Type','cube')
    shapeParam.setHintString("{'widget': 'popup', 'options': ['cube', 'sphere', 'plane']}")
    celParam.setHintString("{'widget': 'cel'}")
    blockerParam = groupParam.createChildString('blocker Number','blk01')
    blockerParam.setHintString("{'widget': 'popup', 'options': ['blk01', 'blk02', 'blk03', 'blk04', 'blk05', 'blk06', 'blk07', 'blk08']}")
    listParam = ['density','roundness','width_edge','height_edge','ramp']
    for param in listParam :
        paramCreated = groupParam.createChildNumber(param,0.0)
        paramCreated.setHintString("{'slider': 'True'}")
    axisParam = groupParam.createChildString('axis','x')
    axisParam.setHintString("{'widget': 'popup', 'options': ['x','y','z']}")
    fileParam = groupParam.createChildString('fileIn','')
    fileParam.setHintString("{'widget': 'fileInput'}")



    #create the primitive node and set the shape to be a cube
    primitiveNode = NodegraphAPI.CreateNode('PrimitiveCreate', parent=groupNode)
    primitiveNode.getParameter('name').setExpression('getParent().'+name+'.path_Name',True)
    #set the type of shape in function of the user choice on the group node
    primitiveNode.getParameter('type').setExpression('getParent().'+name+'.blocker_Type',True)
    #this is important because the name chosen in the group node might be change by katana if duplicate so we need the reel name/path of the prim
    primitivePath = primitiveNode.getParameter('name').getValue(0)
    #set the primitive node name
    primitiveNodeName = "Blocker_"+primitivePath[primitivePath.rfind('/'):]
    primitiveNode.setName(primitiveNodeName)

    #create the opScriptNode for the primitive and set it's lua text to get the transform matrix
    opscriptPrimNode = NodegraphAPI.CreateNode('OpScript', parent=groupNode)
    opscriptPrimNode.setName('MatrixPrim')
    opscriptPrimNode.getParameter('CEL').setValue(primitivePath,0)
    opscriptPrimNode.getParameter('script.lua').setValue("-- Retrieve the object's transform group attribute \n"
                                                         "local xformAttr = Interface.GetGlobalXFormGroup() \n\n"
                                                         "-- Calculate the matrix representing the global transform \n"
                                                         "local matAttr = XFormUtils.CalcTransformMatrixAtTime(xformAttr, 0.0) \n"
                                                         "local matData = matAttr:getNearestSample(0.0) \n\n"
                                                         "-- Copy the matrix data into the 'info' attribute \n"
                                                         "Interface.SetAttr('info.xform.matrix', DoubleAttribute(matData, 4)) \n\n"
                                                         "-- set the color of the primitive to be red \n"
                                                         "local color = {1,.5,.5} \n"
                                                         "Interface.SetAttr('viewer.default.drawOptions.color', FloatAttribute(color))\n"
                                                         "Interface.SetAttr('viewer.default.drawOptions.fill',StringAttribute('wireframe'))\n\n"
                                                         "--set the visibility to 0\n"
                                                         "Interface.SetAttr('visible',IntAttribute(0))\n\n"
                                                         "--display the name of the blocker in the viewer\n"
                                                         "local nameBlocker = Interface.GetOutputName()\n"
                                                         "Interface.SetAttr('viewer.default.annotation.text', StringAttribute(nameBlocker))\n"
                                                         "Interface.SetAttr('viewer.default.annotation.color', FloatAttribute(color))",0)

    #create the opscript for the light
    opscriptLightNode = NodegraphAPI.CreateNode('OpScript',groupNode)
    #opscriptLightNode.getParameter('CEL.enable').setValue(1,0)
    opscriptLightNode.getParameter('CEL').setExpression("getParent()."+name+".CEL",True)
    opscriptLightNode.setName('MatrixLight')
    opscriptLightUserParam = opscriptLightNode.getParameters().createChildGroup('user')
    opscriptLightUserParamBlocker = opscriptLightUserParam.createChildString('blocker','blk01')
    opscriptLightUserParamBlocker.setExpression('getParent().'+name+'.blocker_Number',True)
    opscriptLightUserParamPrim = opscriptLightUserParam.createChildString('primitive',primitivePath)
    for param in listParam:
        paramCreated = opscriptLightUserParam.createChildNumber(param,0.0)
        paramCreated.setExpression('getParent().'+name+'.'+param,True)
    opscriptLightUserParamShape = opscriptLightUserParam.createChildString('shape','cube')
    opscriptLightUserParamShape.setExpression('getParent().'+name+'.blocker_Type',True)
    opscriptLightUserParamAxis = opscriptLightUserParam.createChildString('axis','x')
    opscriptLightUserParamAxis.setExpression('getParent().'+name+'.axis',True)
    opscriptLightUserParamFileIn = opscriptLightUserParam.createChildString('fileIn','')
    opscriptLightUserParamFileIn.setExpression('getParent().'+name+'.fileIn',True)
    opscriptLightNode.getParameter('script.lua').setValue("local blocker = Interface.GetOpArg('user.blocker'):getValue() \n"
                                                          "local primitive = Interface.GetOpArg('user.primitive'):getValue() \n"
                                                          "local matrix = Interface.GetAttr('info.xform.matrix',primitive) \n"
                                                          "local matrixSize = matrix:getTupleSize() \n"
                                                          "local matrixValues = matrix:getNearestSample(0.0) \n"
                                                          "Interface.SetAttr('material.parameters.'..blocker..'_geometry_matrix',DoubleAttribute(matrixValues, matrixSize))\n\n"
                                                          "--setting the density, roundness,width_edge,height_edge,ramp,axis,file parameters\n"
                                                          "local paramTable = {\n"
                                                          "\tdensity = 'Float',\n"
                                                          "\troundness = 'Float',\n"
                                                          "\twidth_edge = 'Float',\n"
                                                          "\theight_edge = 'Float',\n"
                                                          "\tramp = 'Float',\n"
                                                          "\taxis = 'String',\n"
                                                          "\tfileIn = 'String',\n"
                                                          "}\n"
                                                          "for name, type in pairs(paramTable) do\n"
                                                          "\tlocal att = Interface.GetOpArg('user.'..name):getValue()\n"
                                                          "\tlocal attrType = nil\n"
                                                          "\tif type == 'Float' then\n"
                                                          "\t\tattrType = FloatAttribute(att)\n"
                                                          "\telse\n"
                                                          "\t\tattrType = StringAttribute(att)\n"
                                                          "\tend\n"
                                                          "\tInterface.SetAttr('material.parameters.'..blocker..'_'..name,attrType)\n"
                                                          "end\n\n"
                                                          "--set the shape attribute on the material\n"
                                                          "local shape = Interface.GetOpArg('user.shape'):getValue()\n"
                                                          "if shape == 'cube' then\n"
                                                          "\tshape = 'box'\n"
                                                          "end\n"
                                                          "Interface.SetAttr('material.parameters.'..blocker..'_geometry_type',StringAttribute(shape))",0)

    #create the mergeNode
    mergeNode = NodegraphAPI.CreateNode('Merge',groupNode)
    mergeNode.setName('MergePrim')
    mergeNode.addInputPort('i0')
    mergeNode.addInputPort('i1')

    #connection
    sendGroup = groupNode.getSendPort('in')
    returnGroup = groupNode.getReturnPort('out')
    mergeNode.getInputPort('i0').connect(sendGroup)
    primitiveNode.getOutputPort('out').connect(mergeNode.getInputPort('i1'))
    mergeNode.getOutputPort('out').connect(opscriptPrimNode.getInputPort('i0'))
    opscriptPrimNode.getOutputPort('out').connect(opscriptLightNode.getInputPort('i0'))
    opscriptLightNode.getOutputPort('out').connect(returnGroup)

    #placement of Nodes
    centralPos = NodegraphAPI.GetNodePosition(mergeNode)
    NodegraphAPI.SetNodePosition(primitiveNode, (centralPos[0]+100,centralPos[1]+100))
    NodegraphAPI.SetNodePosition(opscriptPrimNode, (centralPos[0],centralPos[1]-100))
    NodegraphAPI.SetNodePosition(opscriptLightNode, (centralPos[0],centralPos[1]-200))

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

#to find field in sg
pprint.pprint(sg.schema_field_read('Camera'))
pprint.pprint(sg.schema_field_read('Shot'))
pprint.pprint(sg.schema_field_read('Asset'))

#to disable node via script
NodegraphAPI.GetNode('Alembic_In1').getParameters().createChildNumber('disable',1)


#server license
print os.environ['foundry_LICENSE'], os.environ['solidangle_LICENSE']
4101@licserv01.mikros.int 5053@licserv01.mikros.int


###########################################display model in katana################################################
def displayModel(node = NodegraphAPI.GetRootNode(),nameInNode = '_hiShape'):
    sg = ScenegraphManager.getActiveScenegraph()
    time = NodegraphAPI.GetCurrentTime()
    producer = Nodes3DAPI.GetGeometryProducer( node, time)
    allPath = recursiveFindPath(producer,listPath=[],nameInNode = nameInNode)
    for item in allPath:
        sg.addPinnedLocation(item)

def recursiveFindPath(producer,listPath=[],nameInNode = '_hiShape'):
    if producer is not None :
        path = producer.getFullName()
        if path.find(nameInNode ) >= 0:
            listPath.append(path)
        for child in producer.iterChildren():
            recursiveFindPath(child,listPath,nameInNode )
    else:
        print('no producer for :' )
    return listPath
####################################################################################################################
# event handler
def myParamCallback(eventType, eventID, node, param):
    test = param.getFullName()
    if (test == 'ArnoldObjectSettings.args.arnoldStatements.invert_normals.value'):
        if param.getValue(0):
            print('yes')
        else:
            print('No')

Utils.EventModule.RegisterEventHandler(myParamCallback, "parameter_finalizeValue")
Utils.EventModule.ProcessAllEvents()
Utils.EventModule.UnregisterEventHandler(myParamCallback, "parameter_finalizeValue")