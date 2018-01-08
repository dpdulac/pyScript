#!/usr/bin/env python
# coding:utf-8
""":mod:`camForKatana` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2016, Mikros Image"

from sgApi.sgApi import SgApi
from sgtkLib import tkutil, tkm
import os, pprint
import kCore.attribute as kAttr
from Katana import  NodegraphAPI,UI4

_USER_ = os.environ['USER']
_STARTTIME_ = 101

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg
sgA = SgApi(sgw=sgw, tk=tk, project=project)



def findShots( seq='s1300', shotList=[]):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'in',shotList],
        #['entity.Shot.tag_list', 'name_contains', 'mattepainting'],
    ]

    res = {}
    for v in sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_frames_of_interest','entity.Shot.sg_cut_in','entity.Shot.sg_cut_out'], order=[{'field_name':'created_at','direction':'desc'}]):
        entityName = v['entity']['name']
        if not entityName in res:
            res[entityName] ={}
            frameInterest = v['entity.Shot.sg_frames_of_interest']
            if frameInterest is not None:
                res[entityName]['frameInterest'] = frameInterest.split(',')
            else:
                mid = int(v['entity.Shot.sg_cut_out']+v['entity.Shot.sg_cut_in'])/2
                res[entityName]['frameInterest'] = [mid]
            res[entityName]['cutIn'] = v['entity.Shot.sg_cut_in']
            res[entityName]['cutOut'] = v['entity.Shot.sg_cut_out']
    return res

#get all the shot from the sequence
def findShotsInSequence(seq='1300'):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['code','is',seq]
    ]
    res = {}
    seqShots =[]
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','shots']):
        if not 'Shots' in res:
            tmp = v['shots']
            for item in tmp:
                seqShots.append(item['name'])
            res['Shots'] = sorted(seqShots)
    return sorted(seqShots)

def findCameraPath(seq='s1300'):
    shotInSeq = findShotsInSequence(seq=seq)
    dictShots = findShots(seq,shotInSeq)
    res = {}
    for shot in dictShots.keys():
        try:
            camPath = sgA.getLastCamera(shot, taskPriority=['dwa_camera']).getPath()
        except AttributeError:
            dictShots.pop(shot,None)
            print "no cam for: " + shot
        else:
            dictShots[shot]['camPath'] = camPath
    #pprint.pprint(dictShots)
    return dictShots



def createCam(seq='s4650', frame='interest'):
    pos= (0,0)
    mergeInput=0
    maxOutTime = 0
    inputName = 'i'
    camFrame = _STARTTIME_
    #set the sart time of the project to _STARTTIME_ and end time to 500
    root = NodegraphAPI.GetRootNode()
    root.getParameter('inTime').setValue(_STARTTIME_,0)
    root.getParameter('outTime').setValue(500,0)
    #find the camera path for the sequence
    camDict = findCameraPath(seq=seq)
    nbCamNode = len(camDict.keys())
    #create a group node which will contains all the camera for the sequence
    group = NodegraphAPI.CreateNode("Group", NodegraphAPI.GetRootNode())
    group.setName('PublishedCam_Group_'+seq)
    group.addOutputPort('out')
    #create the merge node which assemble al the camera
    mergeNode = NodegraphAPI.CreateNode('Merge',group)
    #create the switch Node
    switchNode = NodegraphAPI.CreateNode('Switch',group)
    switchNodeIn = switchNode.getParameter('in')

    for key in sorted(camDict.keys()):
        #start the animation process of the switch node if we are at the startframe value
        if camFrame == _STARTTIME_:
            switchNodeIn.setAutoKey(True)
            switchNodeIn.setValueAutoKey(0,_STARTTIME_)
        #create the PublishedCamera Node
        PublishedCameraNode = NodegraphAPI.CreateNode('PublishedCamera',group)
        #set the Name of the PublishedCamera node
        PublishedCameraNode.setName('Cam_'+key)
        #set the path of the camera abc
        camFile = PublishedCameraNode.getParameter('file')
        camFile.setValue(camDict[key]['camPath'],0)
        # #put the timing mode of the cam to Hold Frame
        # camTimingMode = PublishedCameraNode.getParameter('timing.mode')
        # camTimingMode.setValue('Hold Frame',0)
        # #set the value for the holding frame to the frame of interest or start, mid, end
        # cameTimingHoldTime = PublishedCameraNode.getParameter('timing.holdTime')
        # cameTimingHoldTime.setExpressionFlag(False)
        # if frame == 'mid':
        #     frameInterest = int((camDict[key]['cutIn'] + camDict[key]['cutOut'])/2)
        #     cameTimingHoldTime.setValue(frameInterest,0)
        # elif frame == 'end':
        #     cameTimingHoldTime.setValue(camDict[key]['cutOut'],0)
        # elif frame == 'start':
        #     cameTimingHoldTime.setValue(camDict[key]['cutIn'],0)
        # else:
        #     cameTimingHoldTime.setValue(int(camDict[key]['frameInterest'][0]),0)
        #set the name for the camera in the camera tree
        camName = PublishedCameraNode.getParameter('name')
        camName.setValue('/root/world/cam/Cam_' + key, 0)
        #set the position of the node
        NodegraphAPI.SetNodePosition(PublishedCameraNode,pos)
        #create a new input connection on the merge and connect the PublishedCamera node to it
        inputName = 'i'+str(mergeInput)
        mergeNode.addInputPort(inputName)
        PublishedCameraNode.getOutputPort('out').connect(mergeNode.getInputPort(inputName))

        #create the timeOfset node
        timeOffsetNode = NodegraphAPI.CreateNode('TimeOffset',group)
        timeOffsetNode.setName('TimeOffset_Cam'+key)
        #set value for the inputFrame parameter of the timeOffset node
        inputFrame = timeOffsetNode.getParameter('inputFrame')
        inputFrame.setExpressionFlag(False)
        #choice for the input frame type
        if frame == 'mid':
            frameInterest = int((camDict[key]['cutIn'] + camDict[key]['cutOut'])/2)
            inputFrame.setValue(frameInterest,0)
            camFrame += 1
        elif frame == 'end':
            inputFrame.setValue(camDict[key]['cutOut'],0)
            camFrame += 1
        elif frame == 'start':
            inputFrame.setValue(camDict[key]['cutIn'],0)
            camFrame += 1
        else:
            inputFrame.setAutoKey(True)
            allFramesInterest = camDict[key]['frameInterest']
            #if there is multiple frameInterest loop
            for i in allFramesInterest:
                inputFrame.setValueAutoKey(int(camDict[key]['frameInterest'][0]),camFrame)
                camFrame += 1
            inputFrame.setAutoKey(False)
        #position the timeOffset node
        NodegraphAPI.SetNodePosition(timeOffsetNode,(pos[0],pos[1]-50))
        PublishedCameraNode.getOutputPort('out').connect(timeOffsetNode.getInputPort('input'))
        #create the RenameNode
        renameNode = NodegraphAPI.CreateNode('Rename',group)
        #set the name of the rename
        renameNode.setName('Rename_Cam_'+key)
        #set the rootlocation for the rename node
        renameNode.getParameter('rootLocation').setValue('/root/world/cam',0)
        # set the pattern
        renameNode.getParameter('pattern').setValue('Cam_'+key,0)
        # set the replace string
        renameNode.getParameter('replace').setValue('MasterCam',0)
        #position of the rename node
        NodegraphAPI.SetNodePosition(renameNode,(pos[0],pos[1]-100))
        #connect the publishedcam node to the rename Node
        timeOffsetNode.getOutputPort('output').connect(renameNode.getInputPort('in'))
        #connect the rename node to the switch node
        switchNode.addInputPort(inputName)
        renameNode.getOutputPort('out').connect(switchNode.getInputPort(inputName))
        #increment the input nb for the merge node
        mergeInput += 1
        #set the next key for the switch node(with inputMerge incremented) if inputMerge is less than the number of cam node
        if mergeInput < nbCamNode:
            switchNodeIn.setValueAutoKey(mergeInput,camFrame)
        else:
            switchNodeIn.setAutoKey(False)
        #increment the pos
        pos = (pos[0]+300,pos[1])
        #find the maxOutTime
        if camDict[key]['cutOut'] > maxOutTime:
            maxOutTime = camDict[key]['cutOut']
    #position of the merge node
    mergePos = (pos[0]/2,-300)
    NodegraphAPI.SetNodePosition(mergeNode,mergePos)
    #position for the switch node
    NodegraphAPI.SetNodePosition(switchNode,(mergePos[0]+300,-200))
    #connect the switch node to the merge node
    inputName = 'i'+str(mergeInput)
    mergeNode.addInputPort(inputName)
    switchNode.getOutputPort('output').connect(mergeNode.getInputPort(inputName))
    #connect the merge to the out port of the group
    returnGroup = group.getReturnPort('out')
    mergeNode.getOutputPort('out').connect(returnGroup)
    #set the out time of the project to maxOutTime
    root.getParameter('outTime').setValue(maxOutTime,0)
    
def addAllCamToRenderManager(layerName = 'ALL', camPattern = 'CameraLeftShape'):
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

    rndLayer = None
    for item in renderManagerNode.getRenderLayers():
        if item.getName() == layerName:
            rndLayer = item
        else:
            rndLayer = renderManagerNode.addRenderLayer(layerName)

    producer = Nodes3DAPI.GetGeometryProducer(renderManagerNode, 0)
    camproducer = producer.getProducerByPath("/root/world/cam")
    children = []
    allCameraPath =[]
    kAttr.walkChildrenProducer(camproducer, children)
    cameraPath = None
    for child in children :
         if child.getType() == "camera" and child.getFullName().find(camPattern ) > 0:
              allCameraPath.append(child.getFullName())
    for cam in sorted(allCameraPath):
        rendrOutput = renderManagerNode.addRenderOutput(cam,rndLayer)
        renderNode = rendrOutput.getRenderNode()
        start = renderNode.getParameter('user.start')
        end = renderNode.getParameter('user.end')
        start.setExpressionFlag(False)
        end.setExpressionFlag(False)

    # renderOutputs = renderManagerNode.getRenderOutputs(rndLayer)
    # for node in renderOutputs:
    #     renderNode = node.getRenderNode()
    #     start = renderNode.getParameter('user.start')
    #     end = renderNode.getParameter('user.end')
    #     start.setExpressionFlag(False)
    #     end.setExpression(False)


