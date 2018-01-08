#!/usr/bin/env python
# coding:utf-8
""":mod:`sampleGroupCreate` -- dummy module
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
from PyQt4.QtGui import *
from PyQt4.QtCore import *

'''display a window with a choice of Object,Hair or Light component and a field for name input'''
class displayLineUI(QWidget):
    def __init__(self,root = NodegraphAPI.GetRootNode()):
        super(displayLineUI, self).__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        self.mainGridLayout = QGridLayout()

        self.choiceComboBox = QComboBox()
        self.choiceComboBox.addItem("Object")
        self.choiceComboBox.addItem("Hair")
        self.choiceComboBox.addItem("Light")

        self.nameLabel = QLabel('name')
        self.namelineEdit = QLineEdit()
        self.nameButton = QPushButton('OK')

        self.mainGridLayout.addWidget(self.choiceComboBox,0,0)
        self.mainGridLayout.addWidget(self.nameLabel,1,0)
        self.mainGridLayout.addWidget(self.namelineEdit,1,1)
        self.mainGridLayout.addWidget(self.nameButton,2,1)

        self.nameButton.clicked.connect(self.doIt)
        self.setLayout(self.mainGridLayout)

    def doIt(self):
        name = str(self.namelineEdit.text())
        task = str(self.choiceComboBox.currentText())
        if name == '':
            name = task
        #add the block Object, Light or Hair
        addSampleBlock(self.root,name,task)
        self.close()


def paramUI(groupNode = NodegraphAPI.GetRootNode(), name ='sample',task='Object'):
    groupParam = groupNode.getParameters().createChildGroup(name)
    groupParam.setHintString("{'open': 'True', 'help':' Sample tunning'}")
    #cel param
    celParam = groupParam.createChildString('CEL','')
    celParam.setHintString("{'widget': 'cel'}")
    #bypass sample set
    disableParam = groupParam.createChildNumber('disable',0)
    disableParam.setHintString("{'widget': 'checkBox', 'help': 'enable or disable the sample set'}")
    #create different type of param in function of type of component
    if task == 'Object':
        sampleDict = { '1':['diffuse','diffuse_samples'],'2':['sss','sss_samples'],'3':['backLight','backlighting_samples'],'4':['glossy1','glossy1_samples'],'5':['glossy2','glossy2_samples'],'6':['transmission','transmission_samples']}
        #Sample param
        for pos in sorted(sampleDict.keys()):
            sampleCheckBox = groupParam.createChildNumber(sampleDict[pos][0],0)
            sampleCheckBox.setHintString("{'widget': 'checkBox', 'conditionalLockOps': {'conditionalLockValue': '0', 'conditionalLockOp': 'notEqualTo', 'conditionalLockPath': '../"+sampleDict[pos][1]+"'},'help':'toggle the add_diffuse_sample'}")
            sampleSlider = groupParam.createChildNumber(sampleDict[pos][1],0)
            sampleSlider.setHintString("{'int': 'True', 'slider': 'True', 'slidermax': '10.0', 'conditionalVisOps': {'conditionalVisOp': 'equalTo', 'conditionalVisPath': '../"+sampleDict[pos][0]+"', 'conditionalVisValue': '1'}, 'slidermin': '-10.0', 'help':'add samples to the "+sampleDict[pos][0]+" component'}")
    elif task == 'Hair':
        sampleSlider = groupParam.createChildNumber('diffuse_samples',0)
        sampleSlider.setHintString("{'int': 'True', 'slider': 'True', 'slidermax': '10.0', 'slidermin': '-10.0', 'help':'add samples to the diffuse component for Hair'}")
    else:
        sampleSlider = groupParam.createChildNumber('samples',0)
        sampleSlider.setHintString("{'int': 'True', 'slider': 'True', 'slidermax': '10.0', 'slidermin': '0.0', 'help':'add samples to the Light'}")
    #param to add comment
    comment = groupParam.createChildString('comment','')
    comment.setHintString("{'widget': 'scriptEditor', 'help':'add comment and information for other user'}")
    #delete current sample block
    deleteButton = groupParam.createChildString('deleteSampleBlock','delete block')
    scriptDel = 'from sampleGroupCreate import deleteSampleBlock\\nblockName = "'+name+'"\\ndeleteSampleBlock(blockName, node)'
    deleteButton.setHintString("{'widget': 'scriptToolbar', 'buttonData': [{},{},{'text': 'delete', 'icon': '', 'scriptText': '"+scriptDel+"', 'flat': 0}], 'help': 'delete the current sampleBlock'}")

def createOpScriptSample(groupNode = NodegraphAPI.GetRootNode(),name = 'sample',task='Object'):
    #expression root
    celExp = 'getParent().'+name
    #create the opscript for the samples
    opscriptSampleNode = NodegraphAPI.CreateNode('OpScript',groupNode)
    #set the expression for the CEL to be the one on parent node
    opscriptSampleNode.getParameter('CEL').setExpression(celExp+".CEL",True)
    #set the name of the opScript
    opscriptSampleNode.setName('Opscript_'+name)

    #param
    opscriptUserParam = opscriptSampleNode.getParameters().createChildGroup('user')
    if task == 'Object':
        opscriptSampleNode.getParameter('script.lua').setValue("local sample = require 'addSample'\nsample.Object()",0)
        listParam = ['diffuse_samples','sss_samples','backlighting_samples','glossy1_samples','glossy2_samples','transmission_samples']
        for param in listParam:
            paramCreated = opscriptUserParam.createChildNumber(param,0.0)
            paramCreated.setExpression(celExp+'.'+param,True)
    elif task == 'Hair':
        opscriptSampleNode.getParameter('script.lua').setValue("local sample = require 'addSample'\nsample.Hair()",0)
        paramCreated = opscriptUserParam.createChildNumber('diffuse_samples',0.0)
        paramCreated.setExpression(celExp+'.'+'diffuse_samples',True)
    else:
        opscriptSampleNode.getParameter('script.lua').setValue("local sample = require 'addSample'\nsample.Light()",0)
        paramCreated = opscriptUserParam.createChildNumber('samples',0.0)
        paramCreated.setExpression(celExp+'.'+'samples',True)

    #param to enable/disable node
    disableParam = opscriptSampleNode.getParameters().createChildNumber('disable',0)
    disableParam.setExpression(celExp+'.disable',True)
    return opscriptSampleNode

def createMasterSample(name='SampleGroup',parent = NodegraphAPI.GetRootNode()):
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

    addButton =groupNode.getParameters().createChildString('addSampleNode','add sample node')
    addButton.setHintString("{'widget': 'scriptButton', 'buttonText': 'add Sample Node', 'scriptText': \"from sampleGroupCreate import displayLineUI\\n"
                                    "a=displayLineUI(node)\\na.show()\", 'help': 'add a new sample block to the group'}")

    #create a dot node
    dotOutNode = NodegraphAPI.CreateNode('Dot',groupNode)
    dotOutNode.setName('outDot')

    #connection
    sendGroup = groupNode.getSendPort('in')
    returnGroup = groupNode.getReturnPort('out')
    dotOutNode.getInputPort('input').connect(sendGroup)
    dotOutNode.getOutputPort('output').connect(returnGroup)

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

def addSampleBlock(root = NodegraphAPI.GetRootNode(),name = 'sample',task='Object'):
    children = root.getChildren()
    nbChildren = root.getNumChildren()
    dotNode = None
    for child in children:
        if child.getType() == 'Dot':
            dotNode = child
    dotNodePos = NodegraphAPI.GetNodePosition(dotNode)

    newSampleNode = createOpScriptSample(root,name,task)
    paramUI(root,name,task)

    #reorder the button to be the last param
    newSampleParam = root.getParameters()
    paramAddBlocker = newSampleParam.getChild('addSampleNode')
    numberOfChild = newSampleParam.getNumChildren() -1
    newSampleParam.reorderChild(paramAddBlocker,numberOfChild)

    if nbChildren == 1:
        sendGroup = root.getSendPort('in')
        newSampleNode.getInputPort('i0').connect(sendGroup)
        newSampleNode.getOutputPort('out').connect(dotNode.getInputPort('input'))
        NodegraphAPI.SetNodePosition(dotNode,(dotNodePos[0],dotNodePos[1]-50))
    else:
        inputDotNodeProducer = dotNode.getInputSource('input',NodegraphAPI.GetCurrentGraphState())[0]
        inputDotNodeProducer.connect(newSampleNode.getInputPort('i0'))
        newSampleNode.getOutputPort('out').connect(dotNode.getInputPort('input'))
        NodegraphAPI.SetNodePosition(newSampleNode,dotNodePos)
        NodegraphAPI.SetNodePosition(dotNode,(dotNodePos[0],dotNodePos[1]-50))

def deleteSampleBlock(blockName = 'Sample',root = NodegraphAPI.GetRootNode()):
    opScriptToDeleteName = 'Opscript_'+blockName
    #get the node to delete
    opScriptToDelete = NodegraphAPI.GetNode(opScriptToDeleteName)

    #get the connected node ports to the blocker to delete and reconnect those ports together
    outPort = opScriptToDelete.getInputPort('i0').getConnectedPort(0)
    inPort = opScriptToDelete.getOutputPort('out').getConnectedPort(0)
    outPort.connect(inPort)

    #delete the blocker node
    opScriptToDelete.delete()

    #delete the param of the blocker
    paramToDelete = root.getParameter(blockName)
    param = root.getParameters()
    param.deleteChild(paramToDelete)




