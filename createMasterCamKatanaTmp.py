#!/usr/bin/env python
# coding=utf-8
""":mod:`createMasterCamKatanaTmp` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2018, Mikros Animation"

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from sgApi2 import SgApi2 as SgApi
from sgtkLib import tkutil, tkm
import os, pprint, errno, argparse, sys, math, operator
from Katana import NodegraphAPI, UI4

_USER_ = os.environ['USER']
_STARTTIME_ = 101

_USER_ = os.environ['USER']
tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg
sgA = SgApi(sgw=sgw, tk=tk, project=project)

opNodeScript = "local camVal = Interface.GetOpArg('user.outCamValue'):getValue()" \
               "\nlocal camType = Interface.GetOpArg('user.outCamType'):getValue()" \
               "\nlocal tableCamList = {}" \
               "\nlocal camList = Interface.GetAttr('globals.cameraList')" \
               "\ntableCamList = camList:getNearestSample(0)" \
               "\nlocal newCamList = {}" \
               "\nif camVal == 1 then" \
               "\n\tif camType == 0 then" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCamera/stereoCameraCenterCamShape')" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCameraLeft/stereoCameraLeftShape')" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCameraRight/stereoCameraRightShape')" \
               "\n\telseif(camType == 1) then" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCameraLeft/stereoCameraLeftShape')" \
               "\n\telseif camType == 2 then" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCamera/stereoCameraCenterCamShape')" \
               "\n\telse" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCameraRight/stereoCameraRightShape')" \
               "\n\tend " \
               "\nelse" \
               "\n\tif camType == 0 then" \
               "\n\t\tnewCamList = tableCamList" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCamera/stereoCameraCenterCamShape')" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCameraLeft/stereoCameraLeftShape')" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCameraRight/stereoCameraRightShape')" \
               "\n\telseif(camType == 1) then" \
               "\n\t\tlocal count = 1" \
               "\n\t\tfor i = 1,#tableCamList,1 do" \
               "\n\t\t\tlocal cam = tableCamList[i]" \
               "\n\t\t\tlocal center = cam:find('CameraLeftShape')" \
               "\n\t\t\tif center ~= nil then" \
               "\n\t\t\t\ttable.insert(newCamList,count,cam)" \
               "\n\t\t\t\tcount = count +1" \
               "\n\t\t\tend" \
               "\n\t\tend" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCameraLeft/stereoCameraLeftShape')" \
               "\n\telseif(camType == 2) then" \
               "\n\t\tlocal count = 1" \
               "\n\t\tfor i = 1,#tableCamList,1 do" \
               "\n\t\t\tlocal cam = tableCamList[i]" \
               "\n\t\t\tlocal center = cam:find('CameraCenterCamShape')" \
               "\n\t\t\tif center ~= nil then" \
               "\n\t\t\t\ttable.insert(newCamList,count,cam)" \
               "\n\t\t\t\tcount = count +1" \
               "\n\t\t\tend" \
               "\n\t\tend" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCamera/stereoCameraCenterCamShape')" \
               "\n\telse" \
               "\n\t\tlocal count = 1" \
               "\n\t\tfor i = 1,#tableCamList,1 do" \
               "\n\t\t\tlocal cam = tableCamList[i]" \
               "\n\t\t\tlocal center = cam:find('CameraRightShape')" \
               "\n\t\t\tif center ~= nil then" \
               "\n\t\t\t\t	table.insert(newCamList,count,cam)" \
               "\n\t\t\t\t	count = count +1" \
               "\n\t\t\tend" \
               "\n\t\tend" \
               "\n\t\ttable.insert(newCamList,'/root/world/cam/MasterCam/stereoCameraRight/stereoCameraRightShape')" \
               "\n\t\tend" \
               "\nend" \
               "\nInterface.SetAttr('globals.cameraList',StringAttribute(newCamList))"

imageFilterConfoLayout = {
    'filter_operator': 'all',
    'filters': [
        ['tag_list', 'name_is', 'primary'],
        ['published_file_type', 'name_is', 'QCRmovie'],
    ]
}

imageFilterAsset = {
    'filter_operator': 'any',
    'filters': [
        ['published_file_type', 'name_is', 'TurntableMovie'],
    ]
}

imageFilterLayoutBase = {
    'filter_operator': 'any',
    'filters': [
        # ['published_file_type', 'name_is', 'GenericMovie'],
        ['published_file_type', 'name_is', 'PlayblastMovie'],
        # ['published_file_type', 'name_is', 'CompoMovie'],
        # ['published_file_type', 'name_is', 'GenericImageSequence'],
        # ['published_file_type', 'name_is', 'PlayblastMovie'],
    ]
}

imageFilterEditing = {
    'filter_operator': 'any',
    'filters': [
        # ['published_file_type', 'name_is', 'GenericMovie'],
        # ['published_file_type', 'name_is', 'DwaMovie'],
        ['published_file_type', 'name_is', 'PlayblastMovie'],
        # ['published_file_type', 'name_is', 'GenericImageSequence'],
        # ['published_file_type', 'name_is', 'PlayblastMovie'],
    ]
}

cameraFiltering = {
    'filter_operator': 'any',
    'filters': [['published_file_type', 'name_is', 'CameraAlembic']],
}


def findAllSequence(all=False):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
    ]
    res = {}
    seqShots = []
    # get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence', filters, ['entity', 'code', 'description']):
        seq = v['code']
        if all:
            if not seq in res:
                res[seq] = {}
            res[seq]['description'] = v['description']
        else:
            if int(seq[:3]) < 800:  # only take the first 3 characters
                if not seq in res:
                    res[seq] = {}
                if v['description'] != None:
                    res[seq]['description'] = v['description']
                else:
                    res[seq]['description'] = 'None'
            else:
                print 'donuts for: ' + seq
    return res


def findShots(seq='s1300', shotList=[]):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity.Shot.code', 'in', shotList],
        # ['entity.Shot.tag_list', 'name_contains', 'mattepainting'],
    ]

    res = {}
    for v in sg.find('PublishedFile', filters,
                     ['code', 'entity', 'entity.Shot.sg_cut_order', 'entity.Shot.sg_master_layout',
                      'entity.Shot.sg_master_lighting',
                      'entity.Shot.sg_frames_of_interest', 'entity.Shot.sg_cut_in', 'entity.Shot.sg_cut_out'],
                     order=[{'field_name': 'created_at', 'direction': 'desc'}]):
        entityName = v['entity']['name']
        if v['entity.Shot.sg_cut_order'] > 0:
            if not entityName in res:
                res[entityName] = {}
                frameInterest = v['entity.Shot.sg_frames_of_interest']
                if frameInterest is not None:
                    frameInterestList = frameInterest.split()
                    addComma = ''
                    listFame = []
                    for i in frameInterestList:
                        if i != frameInterestList[-1]:
                            addComma += i + ','
                        else:
                            addComma += i
                    listFame.append(addComma)
                    res[entityName]['frameInterest'] = listFame
                else:
                    res[entityName]['frameInterest'] = ['101']
                res[entityName]['cutIn'] = v['entity.Shot.sg_cut_in']
                res[entityName]['cutOut'] = v['entity.Shot.sg_cut_out']
                res[entityName]['cutOrder'] = v['entity.Shot.sg_cut_order']
                try:
                    test = v['entity.Shot.sg_master_layout']['name']
                except :
                    res[entityName]['masterLayout'] = v['entity.Shot.sg_master_layout']
                else:
                    res[entityName]['masterLayout'] = v['entity.Shot.sg_master_layout']['name']
                # res[entityName]['masterLighting'] = v['entity.Shot.sg_master_lighting']['name']
    return res


def findSingleShot(shot='s1300_p00300', taskname='compo_precomp'):
    filterType = imFilter(taskname)
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity.Shot.code', 'is', shot],
        ['task', 'name_is', taskname],
        filterType
    ]
    res = []
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        res.append(v['path']['local_path'])
    return res


def imFilter(taskname='compo_precomp'):
    filterDict = {'editing_edt': imageFilterEditing,
                  'layout_base': imageFilterLayoutBase,
                  'confo_layout': imageFilterConfoLayout,
                  'anim_main': imageFilterLayoutBase,
                  'model_base': imageFilterAsset,
                  'model_hi': imageFilterAsset,
                  'hair_surface': imageFilterAsset,
                  'surface_surfacing': imageFilterAsset
                  }
    return filterDict[taskname]


# get all the shot from the sequence
def findShotsInSequence(seq='s1300', dict=False):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['code', 'is', seq]
    ]
    res = {}
    seqShots = []
    # get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence', filters, ['entity', 'shots']):
        if not 'Shots' in res:
            tmp = v['shots']
            for item in tmp:
                seqShots.append(item['name'])
            res['Shots'] = sorted(seqShots)
    if dict:
        return res
    else:
        return sorted(seqShots)


# find the camera path
def findCamera(shot='0600_0010'):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity.Shot.code', 'is', shot],
        cameraFiltering
    ]
    res = []
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'path'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        res.append(v['path']['local_path'])
    return res[-1]


def findCameraPath(seq='s1300', dictShots={}, useDict=True):
    if useDict:
        shotInSeq = findShotsInSequence(seq=seq)
        dictShots = findShots(seq, shotInSeq)
    for shot in dictShots.keys():
        try:
            camPath = findCamera(shot)
        except AttributeError:
            dictShots.pop(shot, None)
            print "no cam for: " + shot
        else:
            dictShots[shot]['camPath'] = camPath
    # pprint.pprint(dictShots)
    return dictShots


# ____________________________________KATANA_____________________________________________________________________________

def createCam(seq='s0060', camDict={}):
    # print getNewOrder(camDict)
    pos = (0, 0)
    mergeInput = 0
    maxOutTime = 0
    inputName = 'i'
    camFrame = _STARTTIME_
    # set the sart time of the project to _STARTTIME_ and end time to 500
    root = NodegraphAPI.GetRootNode()
    root.getParameter('inTime').setValue(_STARTTIME_, 0)
    root.getParameter('outTime').setValue(500, 0)

    # find the number of camera
    nbCamNode = len(camDict.keys())

    # create a group node which will contains all the camera for the sequence
    group = NodegraphAPI.CreateNode("Group", NodegraphAPI.GetRootNode())
    group.setName('PublishedCam_Group_' + seq)
    # add attribute to switch the display of group node to normal node
    groupNodeAttrDict = {'ns_basicDisplay': 1, 'ns_iconName': ''}
    group.setAttributes(groupNodeAttrDict)
    group.addOutputPort('out')
    # create parameter for the group node
    celParamOutCam = group.getParameters().createChildNumber('outputCam', 0)
    celParamOutCam.setHintString(
        "{'options__order': ['All', 'masterCam'], 'help': 'choose if all the camera of the sequences will be display in the SceneGraph or only the masterCam', 'widget': 'mapper', 'options': {'All': 0.0, 'masterCam': 1.0}}")
    outTypeParam = group.getParameters().createChildNumber('outputType', 0)
    outTypeParam.setHintString(
        "{'options__order': ['stereo', 'left', 'center', 'right'], 'help': 'out cam type (i.e: stereo,Left,Center or Right)', 'widget': 'mapper', 'options': {'stereo': 0.0, 'right': 3.0, 'center': 2.0, 'left': 1.0}}")
    # create the merge node which assemble al the camera
    mergeNode = NodegraphAPI.CreateNode('Merge', group)
    NodegraphAPI.SetNodeComment(mergeNode, "merge all the sequence cameras and the masterCam together")
    # create the switch Node
    switchNode = NodegraphAPI.CreateNode('Switch', group)
    NodegraphAPI.SetNodeComment(switchNode, "switch between all cameras to create the masterCam animation")
    switchNodeIn = switchNode.getParameter('in')

    for key in getOrder(camDict):
        # start the animation process of the switch node if we are at the startframe value
        if camFrame == _STARTTIME_:
            switchNodeIn.setAutoKey(True)
            switchNodeIn.setValueAutoKey(0, _STARTTIME_)
        # create the PublishedCamera Node
        PublishedCameraNode = NodegraphAPI.CreateNode('PublishedCamera', group)
        # set the Name of the PublishedCamera node
        PublishedCameraNode.setName('Cam_' + key)
        # set the path of the camera abc
        camFile = PublishedCameraNode.getParameter('file')
        camFile.setValue(camDict[key]['camPath'], 0)

        # set the name for the camera in the camera tree
        camName = PublishedCameraNode.getParameter('name')
        camName.setValue('/root/world/cam/Cam_' + key, 0)
        # set the position of the node
        NodegraphAPI.SetNodePosition(PublishedCameraNode, pos)
        # create a new input connection on the merge and connect the PublishedCamera node to it
        inputName = 'i' + str(mergeInput)
        mergeNode.addInputPort(inputName)
        PublishedCameraNode.getOutputPort('out').connect(mergeNode.getInputPort(inputName))

        # create the timeOfset node
        timeOffsetNode = NodegraphAPI.CreateNode('TimeOffset', group)
        timeOffsetNode.setName('TimeOffset_Cam' + key)
        # set value for the inputFrame parameter of the timeOffset node
        inputFrame = timeOffsetNode.getParameter('inputFrame')
        inputFrame.setExpressionFlag(False)
        inputFrame.setAutoKey(True)
        allFramesInterest = camDict[key]['frameInterest']
        # if there is multiple frameInterest loop
        for frame in allFramesInterest:
            inputFrame.setValueAutoKey(frame, camFrame)
            camFrame += 1
        inputFrame.setAutoKey(False)
        # position the timeOffset node
        NodegraphAPI.SetNodePosition(timeOffsetNode, (pos[0], pos[1] - 50))
        PublishedCameraNode.getOutputPort('out').connect(timeOffsetNode.getInputPort('input'))

        # create the RenameNode
        renameNode = NodegraphAPI.CreateNode('Rename', group)
        # set the name of the rename
        renameNode.setName('Rename_Cam_' + key)
        # set the rootlocation for the rename node
        renameNode.getParameter('rootLocation').setValue('/root/world/cam', 0)
        # set the pattern
        renameNode.getParameter('pattern').setValue('Cam_' + key, 0)
        # set the replace string
        renameNode.getParameter('replace').setValue('MasterCam', 0)
        # position of the rename node
        NodegraphAPI.SetNodePosition(renameNode, (pos[0], pos[1] - 100))
        # connect the publishedcam node to the rename Node
        timeOffsetNode.getOutputPort('output').connect(renameNode.getInputPort('in'))
        # connect the rename node to the switch node
        switchNode.addInputPort(inputName)
        renameNode.getOutputPort('out').connect(switchNode.getInputPort(inputName))

        # increment the input nb for the merge node
        mergeInput += 1
        # set the next key for the switch node(with inputMerge incremented) if inputMerge is less than the number of cam node
        if mergeInput < nbCamNode:
            switchNodeIn.setValueAutoKey(mergeInput, camFrame)
        else:
            switchNodeIn.setAutoKey(False)

        # increment the pos
        pos = (pos[0] + 300, pos[1])
        # find the maxOutTime
        if allFramesInterest[-1] > maxOutTime:
            maxOutTime = allFramesInterest[-1]

    # set the animation curve of the switch to be constant
    curve = switchNodeIn.getCurve()
    segments = curve.getSegments()
    for seg in segments:
        seg.setExpression('constant()')

    # position of the merge node
    mergePos = (pos[0] / 2, -300)
    NodegraphAPI.SetNodePosition(mergeNode, mergePos)

    # create the switch node to output all camera or only the master camera
    switchMasterNode = NodegraphAPI.CreateNode('Switch', group)
    switchMasterNode.setName('switchMasterNode')
    NodegraphAPI.SetNodeComment(switchMasterNode, 'swich to all camera or only masterCam')
    switchMasterNode.getParameter('in').setExpression('getParent().outputCam', True)
    # connect the port
    switchMasterNode.addInputPort('i0')
    switchMasterNode.addInputPort('i1')
    mergeNode.getOutputPort('out').connect(switchMasterNode.getInputPort('i0'))
    switchNode.getOutputPort('output').connect(switchMasterNode.getInputPort('i1'))
    # position the switchMasterNode
    switchMasterNodePos = (mergePos[0], mergePos[1] - 50)
    NodegraphAPI.SetNodePosition(switchMasterNode, switchMasterNodePos)

    # position for the switch node
    NodegraphAPI.SetNodePosition(switchNode, (mergePos[0] + 300, -200))
    # connect the switch node to the merge node
    inputName = 'i' + str(mergeInput)
    mergeNode.addInputPort(inputName)
    switchNode.getOutputPort('output').connect(mergeNode.getInputPort(inputName))

    # create the opscript node to add the masterCam in the cameraList
    opscriptNode = NodegraphAPI.CreateNode('OpScript', group)
    opscriptNode.setName('addCamMasterToCamList')
    opscriptNodeParam = opscriptNode.getParameters().createChildGroup('user')
    opscriptNodeParam.createChildNumber('outCamValue', 0)
    opscriptNode.getParameter('user.outCamValue').setExpression('getParent().outputCam', True)
    opscriptNodeParam.createChildNumber('outCamType', 0)
    opscriptNode.getParameter('user.outCamType').setExpression('getParent().outputType', True)
    NodegraphAPI.SetNodeComment(opscriptNode, "add the masterCam center,left and right to the cameraList ")
    opscriptNode.getParameter('CEL').setValue('/root/world', 0)
    # set the script node
    # opscriptNode.getParameter('script.lua').setValue("local camVal = Interface.GetOpArg('user.outCamValue'):getValue()"
    #                                                  "\nlocal camType = Interface.GetOpArg('user.outCamType'):getValue()"
    #                                                  "\nlocal tableCamList = {}"
    #                                                  "\nif camVal == 1 then"
    #                                                  "\n\tif camType == 0 then"
    #                                                  "\n\t\ttable.insert(tableCamList,'/root/world/cam/MasterCam/stereoCamera/stereoCameraCenterCamShape')"
    #                                                  "\n\t\ttable.insert(tableCamList,'/root/world/cam/MasterCam/stereoCameraLeft/stereoCameraLeftShape')"
    #                                                  "\n\t\ttable.insert(tableCamList,'/root/world/cam/MasterCam/stereoCameraRight/stereoCameraRightShape')"
    #                                                  "\n\telseif(camType == 1) then"
    #                                                  "\n\t\ttable.insert(tableCamList,'/root/world/cam/MasterCam/stereoCameraLeft/stereoCameraLeftShape')"
    #                                                  "\n\telseif camType == 2 then"
    #                                                  "\n\t\ttable.insert(tableCamList,'/root/world/cam/MasterCam/stereoCamera/stereoCameraCenterCamShape')"
    #                                                  "\n\telse"
    #                                                  "\n\t\ttable.insert(tableCamList,'/root/world/cam/MasterCam/stereoCameraRight/stereoCameraRightShape')"
    #                                                  "\n\tend"
    #                                                  "\nelse"
    #                                                  "\n\tlocal camList = Interface.GetAttr('globals.cameraList')"
    #                                                  "\n\ttableCamList = camList:getNearestSample(0)"
    #                                                  "\n\ttable.insert(tableCamList,'/root/world/cam/MasterCam/stereoCamera/stereoCameraCenterCamShape')"
    #                                                  "\n\ttable.insert(tableCamList,'/root/world/cam/MasterCam/stereoCameraLeft/stereoCameraLeftShape')"
    #                                                  "\n\ttable.insert(tableCamList,'/root/world/cam/MasterCam/stereoCameraRight/stereoCameraRightShape')"
    #                                                  "\nend"
    #                                                  "\nInterface.SetAttr('globals.cameraList',StringAttribute(tableCamList))",0)
    opscriptNode.getParameter('script.lua').setValue(opNodeScript, 0)
    # connect the opscriptnode to the merge node
    switchMasterNode.getOutputPort('output').connect(opscriptNode.getInputPort('i0'))
    opscriptNodePos = (mergePos[0], mergePos[1] - 100)
    NodegraphAPI.SetNodePosition(opscriptNode, opscriptNodePos)

    # create  prunes nodes to switch off non disired cameras
    # prune for left cam
    pruneNodeLeft = NodegraphAPI.CreateNode('Prune', group)
    pruneNodeLeft.setName('leftCam_' + seq)
    # set the cel node to eliminate all camera but the left one
    pruneNodeLeft.getParameter('cel').setValue(
        "((/root/world/cam/Cam_s*/stereoCameraRight /root/world/cam/Cam_s*/stereoCamera /root/world/cam/MasterCam/stereoCameraRight /root/world/cam/MasterCam/stereoCamera))",
        0)
    # connect the merge group to the prune node
    opscriptNode.getOutputPort('out').connect(pruneNodeLeft.getInputPort('A'))
    prunePos = (mergePos[0] - 200, mergePos[1] - 200)
    NodegraphAPI.SetNodePosition(pruneNodeLeft, prunePos)
    # prune for right cam
    pruneNodeRight = NodegraphAPI.CreateNode('Prune', group)
    pruneNodeRight.setName('rightCam_' + seq)
    # set the cel node to eliminate all camera but the right ones
    pruneNodeRight.getParameter('cel').setValue(
        "((/root/world/cam/Cam_s*/stereoCameraLeft /root/world/cam/Cam_s*/stereoCamera /root/world/cam/MasterCam/stereoCameraLeft /root/world/cam/MasterCam/stereoCamera))",
        0)
    # connect the merge group to the prune node
    opscriptNode.getOutputPort('out').connect(pruneNodeRight.getInputPort('A'))
    prunePos = (mergePos[0] + 200, mergePos[1] - 200)
    NodegraphAPI.SetNodePosition(pruneNodeRight, prunePos)
    # prune for center cam
    pruneNodeCenter = NodegraphAPI.CreateNode('Prune', group)
    pruneNodeCenter.setName('centerCam_' + seq)
    # set the cel node to eliminate all camera but the center ones
    pruneNodeCenter.getParameter('cel').setValue(
        "((/root/world/cam/Cam_s*/stereoCameraRight /root/world/cam/Cam_s*/stereoCameraLeft /root/world/cam/MasterCam/stereoCameraLeft /root/world/cam/MasterCam/stereoCameraRight))",
        0)
    # connect the merge group to the prune node
    opscriptNode.getOutputPort('out').connect(pruneNodeCenter.getInputPort('A'))
    prunePos = (mergePos[0], mergePos[1] - 200)
    NodegraphAPI.SetNodePosition(pruneNodeCenter, prunePos)

    # create the switch node for the prune camera
    switchPrune = NodegraphAPI.CreateNode('Switch', group)
    switchPrune.setName('switchPrune')
    NodegraphAPI.SetNodeComment(switchPrune, 'swich to to prune the non needed camera')
    switchPrune.getParameter('in').setExpression('getParent().outputType', True)
    # connect the port
    switchPrune.addInputPort('i0')
    switchPrune.addInputPort('i1')
    switchPrune.addInputPort('i2')
    switchPrune.addInputPort('i3')
    opscriptNode.getOutputPort('out').connect(switchPrune.getInputPort('i0'))
    pruneNodeLeft.getOutputPort('out').connect(switchPrune.getInputPort('i1'))
    pruneNodeCenter.getOutputPort('out').connect(switchPrune.getInputPort('i2'))
    pruneNodeRight.getOutputPort('out').connect(switchPrune.getInputPort('i3'))
    # position the switchPrune
    switchPrunePos = (mergePos[0], mergePos[1] - 300)
    NodegraphAPI.SetNodePosition(switchPrune, switchPrunePos)

    # connect the switchprune to the out port of the group
    returnGroup = group.getReturnPort('out')
    switchPrune.getOutputPort('output').connect(returnGroup)
    # set the out time of the project to maxOutTime
    root.getParameter('outTime').setValue(camFrame - 1, 0)
    print maxOutTime, camFrame

    # put the node under the mouse
    currentSelection = NodegraphAPI.GetAllSelectedNodes()
    for node in currentSelection:
        NodegraphAPI.SetNodeSelected(node, False)
    NodegraphAPI.SetNodeSelected(group, True)
    # Get list of selected nodes
    nodeList = NodegraphAPI.GetAllSelectedNodes()
    # Find Nodegraph tab and float nodes
    nodegraphTab = UI4.App.Tabs.FindTopTab('Node Graph')
    if nodegraphTab:
        nodegraphTab.floatNodes(nodeList)


'''order the shot in cut order'''


def getOrder(res={}):
    shotNb = []
    for key in res.keys():
        shotNb.append(key)
    for j in range(len(shotNb)):
        # initially swapped is false
        swapped = False
        i = 0
        while i < len(res) - 1:
            # comparing the adjacent elements
            if res[shotNb[i]]['cutOrder'] > res[shotNb[i + 1]]['cutOrder']:
                # swapping
                shotNb[i], shotNb[i + 1] = shotNb[i + 1], shotNb[i]
                # Changing the value of swapped
                swapped = True
            i = i + 1
        # if swapped is false then the list is sorted
        # we can stop the loop
        if swapped == False:
            break
    return shotNb


# _________________________________________________________UI____________________________________________________________

class CamMixUI(QMainWindow):

    def __init__(self):
        super(CamMixUI, self).__init__()
        self.initUI()

    def initUI(self):
        pos = 0
        res = findAllSequence()
        self.shotWidgets = []
        self.seqName = ''
        self.allCamPath = {}
        self.masterLayoutDict = {}
        self.masterLightDict = {}
        self.shotInSeq = []
        self.layoutPath = {}

        self.statusBar().showMessage('Ready')
        self.menuBar = self.menuBar()
        self.seqMenuBar = self.menuBar.addMenu('&Sequences')

        centralwidget = QWidget()
        self.groupBoxSeq = QGroupBox()
        # self.groupBoxSeq.setCheckable(True)
        self.groupBoxSeq.setFlat(False)
        self.mainLayout = QVBoxLayout(centralwidget)
        self.gridLayout = QGridLayout()
        # self.gridLayout.setColumnMinimumWidth(0,20)
        # self.gridLayout.setColumnStretch(0,20)
        # self.gridLayout.setColumnMinimumWidth(1,20)
        # self.gridLayout.setColumnStretch(1,20)
        self.groupBoxSeq.setLayout(self.gridLayout)
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.groupBoxSeq)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedWidth(750)

        self.controlGroupBox = QGroupBox()
        self.controlLayout = QGridLayout(self.controlGroupBox)

        self.controlCheckAllShot = QCheckBox("check all", self.controlGroupBox)
        self.controlCheckAllShot.setObjectName('GroupBox')
        self.controlCheckAllShot.setChecked(True)

        self.controlCheckIn = QCheckBox("In", self.controlGroupBox)
        self.controlCheckIn.setObjectName('in')
        self.controlCheckIn.setAutoExclusive(True)

        self.controlCheckMid = QCheckBox("Mid", self.controlGroupBox)
        self.controlCheckMid.setObjectName('mid')
        self.controlCheckMid.setAutoExclusive(True)

        self.controlCheckOut = QCheckBox("Out", self.controlGroupBox)
        self.controlCheckOut.setObjectName('out')
        self.controlCheckOut.setAutoExclusive(True)

        self.controlCheckInMidOut = QCheckBox("In Mid Out", self.controlGroupBox)
        self.controlCheckInMidOut.setObjectName('inMidOut')
        self.controlCheckInMidOut.setAutoExclusive(True)
        self.controlCheckInMidOut.setChecked(True)

        self.controlCheckFrameOfInt = QCheckBox("Frame of interest", self.controlGroupBox)
        self.controlCheckFrameOfInt.setObjectName('fInt')
        self.controlCheckFrameOfInt.setAutoExclusive(True)

        self.controlButton = QPushButton('create cam')
        self.controlButton.setObjectName('creaCam')

        self.masterGroup = QGroupBox()
        self.useAllShotCheckBox = QCheckBox('All shots')
        self.useAllShotCheckBox.setChecked(True)
        self.useAllShotCheckBox.setAutoExclusive(True)
        self.useLayoutMasterCheckBox = QCheckBox('Masters Layout')
        self.useLayoutMasterCheckBox.setChecked(False)
        self.useLayoutMasterCheckBox.setAutoExclusive(True)
        self.useLightMasterCheckBox = QCheckBox('Masters Light')
        self.useLightMasterCheckBox.setChecked(False)
        self.useLightMasterCheckBox.setAutoExclusive(True)
        self.useLayoutMasterComboBox = QComboBox()
        self.useLayoutMasterComboBox.setEnabled(False)
        self.useLightMasterComboBox = QComboBox()
        self.useLightMasterComboBox.setEnabled(False)
        self.layoutMaster = QGridLayout(self.masterGroup)
        self.layoutMaster.addWidget(self.useAllShotCheckBox, 0, 0)
        self.layoutMaster.addWidget(self.useLayoutMasterCheckBox, 0, 1)
        self.layoutMaster.addWidget(self.useLightMasterCheckBox, 0, 2)
        self.layoutMaster.addWidget(self.useLayoutMasterComboBox, 1, 1)
        self.layoutMaster.addWidget(self.useLightMasterComboBox, 1, 2)
        self.masterGroup.setVisible(False)

        self.controlLayout.addWidget(self.controlCheckAllShot, 0, 0)
        self.controlLayout.addWidget(self.controlCheckIn, 0, 1)
        self.controlLayout.addWidget(self.controlCheckMid, 0, 2)
        self.controlLayout.addWidget(self.controlCheckOut, 0, 3)
        self.controlLayout.addWidget(self.controlCheckFrameOfInt, 0, 5)
        self.controlLayout.addWidget(self.controlCheckInMidOut, 0, 4)
        self.controlLayout.addWidget(self.controlButton, 1, 5)

        self.mainLayout.addWidget(self.masterGroup)
        self.mainLayout.addWidget(self.scroll)
        self.mainLayout.addWidget(self.controlGroupBox)
        # centralwidget.setLayout(scroll)
        self.setCentralWidget(centralwidget)
        # self.overlay = Overlay(self.centralWidget())
        # self.overlay.hide()

        for key in sorted(res.keys()):
            description = res[key]['description']
            if description == None:
                description = ""
            # seqName = QString(key+" ["+ description +"]")
            # seqName = QString(key)
            seqName = str(key)
            self.seqMenuBar.addAction(seqName)

        self.seqMenuBar.triggered.connect(self.processtrigger)
        self.controlCheckAllShot.stateChanged.connect(self.checkAllShot)
        self.controlCheckIn.stateChanged.connect(self.checkAllShot)
        self.controlCheckOut.stateChanged.connect(self.checkAllShot)
        self.controlCheckMid.stateChanged.connect(self.checkAllShot)
        self.controlCheckFrameOfInt.stateChanged.connect(self.checkAllShot)
        self.controlCheckInMidOut.stateChanged.connect(self.checkAllShot)
        self.controlButton.clicked.connect(self.createCam)
        self.useAllShotCheckBox.stateChanged.connect(self.useAllShot)
        self.useLayoutMasterCheckBox.stateChanged.connect(self.useLayoutMaster)
        self.useLayoutMasterComboBox.currentTextChanged.connect(self.useLayoutMaster)
        # self.controlButton.clicked.connect(self.overlay.show)

        self.setGeometry(300, 300, 250, 150)
        self.setFixedWidth(760)
        self.setWindowTitle('MasterSeqCam')
        self.setWindowIcon(QIcon('web.png'))

    def useLayoutMaster(self):
        self.layoutPath = {}
        self.useLightMasterComboBox.setEnabled(False)
        self.useLayoutMasterComboBox.setEnabled(True)
        currentMaster = str(self.useLayoutMasterComboBox.currentText())
        if currentMaster != '':
            self.clearLayout(self.gridLayout)
            inc = 0  # reset the incrementation for positioning the shot layout
            self.controlCheckInMidOut.setChecked(True)  # set the check to In Mid Out
            self.shotWidgets = []  # empty the list of shot widgets
            self.layoutPath = self.masterLayoutDict[currentMaster]
            for shot in getOrder(self.layoutPath):
                shot = shotUI(self.layoutPath[shot], shot)  # create the shot UI
                self.shotWidgets.append(shot)  # append the widget to the list
                self.gridLayout.addWidget(shot, inc, 0)  # add the shot to the layout
                inc += 1

    def useAllShot(self):
        self.useLayoutMasterComboBox.setEnabled(False)
        self.useLightMasterComboBox.setEnabled(False)
        self.clearLayout(self.gridLayout)
        inc = 0  # reset the incrementation for positioning the shot layout
        self.controlCheckInMidOut.setChecked(True)  # set the check to In Mid Out
        self.shotWidgets = []  # empty the list of shot widgets
        # for each shot create it's UI
        for shot in getOrder(self.allCamPath):
            shot = shotUI(self.allCamPath[shot], shot)  # create the shot UI
            self.shotWidgets.append(shot)  # append the widget to the list
            self.gridLayout.addWidget(shot, inc, 0)  # add the shot to the layout
            inc += 1

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # empty the layout and populate it with shot from the sequence
    def processtrigger(self, q):
        self.allCamPath = {}
        self.masterLayoutDict = {}
        self.masterLightDict = {}
        self.shotInSeq = []
        self.clearLayout(self.gridLayout)  # clear the layout
        self.controlCheckInMidOut.setChecked(True)  # set the check to In Mid Out
        self.useAllShotCheckBox.setChecked(True)
        self.shotWidgets = []  # empty the list of shot widgets

        seqString = str(q.text())  # get the name and description of the sequence
        self.groupBoxSeq.setTitle(seqString)  # set the name of the groupbox to be the sequence name and description
        self.seqName = seqString  # extract the seq name alone
        self.shotInSeq = findShotsInSequence(self.seqName)  # find all the shot in this sequence
        self.allCamPath = findShots(self.seqName, self.shotInSeq)  # find the information for each shot
        self.useLayoutMasterComboBox.clear()
        self.createMasterDict('masterLayout')

        self.masterGroup.setVisible(True)

        self.useAllShot()

    # set the dict for The Master
    def createMasterDict(self, masterType='masterLayout'):
        masterNb = []
        self.masterLayoutDict = {}
        for key in self.allCamPath.keys():
            master = self.allCamPath[key][masterType]
            if master not in masterNb:
                masterNb.append(master)
            if master not in self.masterLayoutDict.keys():
                self.masterLayoutDict[master] = {}
                self.masterLayoutDict[master][key] = self.allCamPath[key]
            else:
                self.masterLayoutDict[master][key] = self.allCamPath[key]
        if None in masterNb:
            masterNb.remove(None)
        self.useLayoutMasterComboBox.addItems(sorted(masterNb))

    # check al shot to be on/off at the same time
    def checkAllShot(self):
        checkState = self.sender().isChecked()
        name = str(self.sender().objectName())
        for widget in self.shotWidgets:
            widget.checkShot(checkState, name)

    def createCam(self):
        frameList = []
        res = {}
        # for each shot
        for widget in self.shotWidgets:
            shotNb = widget.getShotName()  # get the name of the shot
            order = widget.getCutOrderNumber()
            if shotNb is not None:
                if not shotNb in res:  # if the shot is not alrady in the dict create it
                    res[shotNb] = {}
                    frames = str(widget.getFrame())  # get the chosen frames
                    splitFrames = frames.split(',')  # find if the is multiple frame and split them
                    for frameNb in splitFrames:  # add the frame to the list
                        if frameNb.find('-') < 0:  # if it'a a single frame
                            frameList.append(int(frameNb))
                        else:  # if multiple frames (range)
                            tmpIntList = []
                            tmpList = frameNb.split('-')
                            for nb in tmpList:
                                tmpIntList.append(int(nb))
                            for i in range(tmpIntList[0],
                                           tmpIntList[1] + 1):  # add the frames corresponding to the frame range
                                frameList.append(i)

                    frameList = sorted(list(set(frameList)))  # get rid of duplicate and sort the list
                    res[shotNb]['frameInterest'] = frameList
                    res[shotNb]['cutOrder'] = order
                    frameList = []
        camRes = findCameraPath(dictShots=res, useDict=False)
        # pprint.pprint(camRes)
        createCam(seq=self.seqName, camDict=camRes)
        print 'done'

    # def resizeEvent(self, event):
    #     self.overlay.resize(event.size())
    #     event.accept()


class shotUI(QWidget):
    def __init__(self, dicShot={}, shotName="donuts"):
        super(shotUI, self).__init__()
        self.shotName = shotName
        self.dicShot = dicShot
        self.initUI()

    def initUI(self):
        self.shotGroupBox = QGroupBox(self.shotName)
        self.shotGroupBox.setCheckable(True)
        self.shotLayout = QGridLayout(self.shotGroupBox)

        self.masterNameLabel = QLabel('Master: ' + str(self.dicShot['masterLayout']))
        self.masterNameLayout = QVBoxLayout()
        self.masterNameLayout.addWidget(self.masterNameLabel)
        self.shotLayout.addLayout(self.masterNameLayout, 0, 1)

        self.cutOrderLabel = QLabel(str(self.dicShot['cutOrder']))
        # self.cutOrderLineEdit = QLineEdit()
        # self.cutOrderLineEdit.setText(str(self.dicShot['cutOrder']))
        # self.cutOrderLineEdit.setEnabled(False)
        self.cutOrderLayout = QVBoxLayout()
        self.cutOrderLayout.addWidget(self.cutOrderLabel)
        # self.cutOrderLayout.addWidget(self.cutOrderLineEdit)
        self.shotLayout.addLayout(self.cutOrderLayout, 1, 0)

        self.cutInLabel = QLabel('Cut In')
        self.cutInLineEdit = QLineEdit()
        self.cutInLineEdit.setText(str(self.dicShot['cutIn']))
        self.cutInLineEdit.setEnabled(False)
        self.cutInCheckBox = QCheckBox()
        self.cutInCheckBox.setAutoExclusive(True)
        self.cutInLayout = QVBoxLayout()
        self.cutInLayout.addWidget(self.cutInLabel)
        self.cutInLayout.addWidget(self.cutInLineEdit)
        self.cutInLayout.addWidget(self.cutInCheckBox)
        self.shotLayout.addLayout(self.cutInLayout, 1, 1)
        # cutInCheckBox.clicked.connect(self.)

        self.cutMidLabel = QLabel('Cut Mid')
        self.cutMidLineEdit = QLineEdit()
        self.cutMidLineEdit.setText(str(int((self.dicShot['cutIn'] + self.dicShot['cutOut']) / 2)))
        self.cutMidLineEdit.setEnabled(False)
        self.cutMidCheckBox = QCheckBox()
        self.cutMidCheckBox.setAutoExclusive(True)
        self.cutMidLayout = QVBoxLayout()
        self.cutMidLayout.addWidget(self.cutMidLabel)
        self.cutMidLayout.addWidget(self.cutMidLineEdit)
        self.cutMidLayout.addWidget(self.cutMidCheckBox)
        self.shotLayout.addLayout(self.cutMidLayout, 1, 2)

        self.cutOutLabel = QLabel('Cut Out')
        self.cutOutLineEdit = QLineEdit()
        self.cutOutLineEdit.setText(str(self.dicShot['cutOut']))
        self.cutOutLineEdit.setEnabled(False)
        self.cutOutCheckBox = QCheckBox()
        self.cutOutCheckBox.setAutoExclusive(True)
        self.cutOutLayout = QVBoxLayout()
        self.cutOutLayout.addWidget(self.cutOutLabel)
        self.cutOutLayout.addWidget(self.cutOutLineEdit)
        self.cutOutLayout.addWidget(self.cutOutCheckBox)
        self.shotLayout.addLayout(self.cutOutLayout, 1, 3)

        self.inMidOutLabel = QLabel('In Mid Out')
        self.inMidOutLineEdit = QLineEdit()
        self.inMidOutLineEdit.setText(str(self.dicShot['cutIn']) + ',' + str(
            int((self.dicShot['cutIn'] + self.dicShot['cutOut']) / 2)) + ',' + str(self.dicShot['cutOut']))
        self.inMidOutLineEdit.setEnabled(False)
        self.inMidOutCheckBox = QCheckBox()
        self.inMidOutCheckBox.setAutoExclusive(True)
        self.inMidOutCheckBox.setChecked(True)
        self.inMidOutLayout = QVBoxLayout()
        self.inMidOutLayout.addWidget(self.inMidOutLabel)
        self.inMidOutLayout.addWidget(self.inMidOutLineEdit)
        self.inMidOutLayout.addWidget(self.inMidOutCheckBox)
        self.shotLayout.addLayout(self.inMidOutLayout, 1, 4)

        self.frameOfInterestLabel = QLabel('Frame of Interest')
        self.frameOfInterestLineEdit = QLineEdit()
        finterest = ''
        nbItem = 1
        for elem in self.dicShot['frameInterest']:
            finterest += elem
            if nbItem < len(self.dicShot['frameInterest']):
                finterest += ','
        self.validator = QRegExpValidator(QRegExp("[0-9,-]*"))
        self.frameOfInterestLineEdit.setValidator(self.validator)
        self.frameOfInterestLineEdit.setText(finterest)
        self.frameOfInterestCheckBox = QCheckBox()
        # self.frameOfInterestCheckBox.setChecked(True)
        self.frameOfInterestCheckBox.setAutoExclusive(True)
        self.frameOfInterestLayout = QVBoxLayout()
        self.frameOfInterestLayout.addWidget(self.frameOfInterestLabel)
        self.frameOfInterestLayout.addWidget(self.frameOfInterestLineEdit)
        self.frameOfInterestLayout.addWidget(self.frameOfInterestCheckBox)
        self.shotLayout.addLayout(self.frameOfInterestLayout, 1, 5)

        self.playRvPushButton = QPushButton("RV")
        self.playRvComboBox = QComboBox()
        self.playRvComboBox.addItem("layout_base")
        self.playRvComboBox.addItem("editing_edt")
        self.playRvComboBox.addItem("anim_main")
        self.playRvLayout = QVBoxLayout()
        self.playRvLayout.addWidget(self.playRvPushButton)
        self.playRvLayout.addWidget(self.playRvComboBox)
        self.shotLayout.addLayout(self.playRvLayout, 1, 6)
        self.playRvPushButton.clicked.connect(self.rvExecute)

        self.dummyWidget = QWidget()
        self.dummyWidget.setFixedHeight(10)
        self.shotLayout.addWidget(self.dummyWidget, 2, 1)

        self.shotGroupBox.setLayout(self.shotLayout)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.shotGroupBox)
        self.setLayout(mainLayout)
        self.setFixedHeight(120)

    def rvExecute(self):
        shot = ''
        taskname = str(self.playRvComboBox.currentText())
        shot = findSingleShot(str(self.shotName), taskname)
        if len(shot) == 0:
            shot = findSingleShot(str(self.shotName), 'editing_edt')
        commandLine = 'rv ' + shot[0]
        os.system(commandLine)

    def checkShot(self, check=True, name='GroupBox'):
        if name == 'GroupBox':
            self.shotGroupBox.setChecked(check)
        elif name == 'in':
            self.cutInCheckBox.setChecked(check)
        elif name == 'out':
            self.cutOutCheckBox.setChecked(check)
        elif name == 'mid':
            self.cutMidCheckBox.setChecked(check)
        elif name == 'fInt':
            self.frameOfInterestCheckBox.setChecked(check)
        elif name == 'inMidOut':
            self.inMidOutCheckBox.setChecked(check)

    def getShotName(self):
        if self.shotGroupBox.isChecked():
            return self.shotName

    def getCutOrderNumber(self):
        return int(self.cutOrderLabel.text())

    def getFrame(self):
        listCheckBox = {self.inMidOutCheckBox: self.inMidOutLineEdit, self.cutInCheckBox: self.cutInLineEdit,
                        self.cutOutCheckBox: self.cutOutLineEdit, self.cutMidCheckBox: self.cutMidLineEdit,
                        self.frameOfInterestCheckBox: self.frameOfInterestLineEdit}
        for box in listCheckBox.keys():
            if box.isChecked():
                return listCheckBox[box].text()


class Overlay(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
        painter.setPen(QPen(Qt.NoPen))
        for i in range(6):
            if (self.counter / 5) % 6 == i:
                painter.setBrush(QBrush(QColor(127 + (self.counter % 5) * 32, 127, 127)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))
                painter.drawEllipse(self.width() / 2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                                    self.height() / 2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,
                                    20, 20)

        painter.end()

    def showEvent(self, event):

        self.timer = self.startTimer(50)
        self.counter = 0

    def timerEvent(self, event):

        self.counter += 1
        self.update()
        if self.counter == 60:
            self.killTimer(self.timer)
            self.hide()


ex = None


def BuildCamMixUI():
    global ex
    if ex is not None:
        ex.close()
    ex = CamMixUI()
    ex.show()


def main():
    # print findCameraPath('s0200')
    # app = QApplication(sys.argv)
    # app.setStyle(QStyleFactory.create("plastique"))
    # BuildCamMixUI()
    # app.exec_()
    shots = findShotsInSequence(600)
    print(shots)


if __name__ == '__main__':
    main()
