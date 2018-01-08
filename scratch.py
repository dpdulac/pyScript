#!/usr/bin/env python
# coding:utf-8
""":mod:`scratch` -- dummy module
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

import rv.rvtypes
import rv.commands
import rv.extra_commands
from pymu import MuSymbol

# from sgtkLib import tkutil, tkm
#
# tk, sgw, project = tkutil.getTk(fast=True, scriptName='duda')
#
#
# import time
#
#
# def lastMoviePublished(seqShot='s0300', task='Layout'):
#     project = {'type': 'Project', 'id': 70}
#
#     #Get entity SG
#     sg_filter = [['project', 'is', project],
#                  ['code', 'is', seqShot]]
#     entity = sgw.sg_find('Sequence', sg_filter, ['sequence'])
#     if not entity:
#         print 'No Shot %s exists !' % (seqShot)
#         return 0
#     print entity
#
#     #Get task SG
#     sg_filter = [['project', 'is', project],
#                  ['content', 'is', task],
#                  ['entity', 'is', entity]]
#     taskSG = sgw.sg_find('Task', sg_filter, ['content'])
#     if not taskSG:
#         print 'No task %s exists in Sequence %s !'# % (task, entity['code'])
#         return 0
#     print taskSG

    # sg_filter = [['project', 'is', project],
    #                 ['task', 'is', taskSG],
    #                 ['entity', 'is', entity]]
    #
    # if task == 'anim_main':
    #     sg_filter.append(['code','contains', 'default-base-anim_main'])
    #     sg_filter.append(['published_file_type', 'is', {'type':'PublishedFileType', 'id':19}])
    # else:
    #     sg_filter.append(['code','contains', 'ambientOcc-mono'])
    #     sg_filter.append(['published_file_type', 'is', {'type':'PublishedFileType', 'id':23}])
    #
    # pub = sgw.sg_find('PublishedFile', sg_filter, ['path'], order=[{'field_name':'version_number','direction':'desc'}])
    #
    # if not pub:
    #     print 'No version found for %s %s' % (entity['code'], taskSG['content'])
    #     return 0
    # #print 'Last movie found : "%s"' % last_movie
    # return pub['path']['local_path']



# def seqShotList(seq='s0300',task='anim_main'):
#     shotNameList = []
#     project = {'type': 'Project', 'id': 70}
#
#     #Get entity SG
#     sg_filter = [['project', 'is', project],
#                  #['content','is',task],
#                  ['code', 'is', seq]]
#     for atom in sgw.sg_find('Sequence', sg_filter, ['shots']):
#         #print atom['shots']
#         if atom['shots']:
#             for shot in atom['shots']:
#                 shotNameList.append(shot['name'])
#     return shotNameList



def addShots(seqDic={}):

    #sort the shot in croissant order
    listOfShot = sorted(seqDic["shots"])

    taskA = seqDic["taskA"]
    taskB = seqDic["taskB"]
    taskAll = []


    #clear the session and get rid of the customOverlay( that mode slowdown the whole process)
    rv.commands.clearSession()
    rv.commands.deactivateMode("RvCustomOverlay")

    #create the sequences node and the stack node
    taskAll.append(rv.commands.newNode("RVSequenceGroup",taskA))
    taskAll.append(rv.commands.newNode("RVSequenceGroup",taskB))
    rv.commands.newNode("RVStackGroup", "ABStack")

    # uiNames = seqDic[listOfShot[0]].keys()
    # taskName_A = uiNames[0]
    # taskName_B = uiNames[1]

    #load the shots for sequence A
    for i in listOfShot:
        rv.commands.addSource(seqDic["shots"][i][taskA])
    #collect the node of type RVSourceGroup
    rvSourceAnim = rv.commands.nodesOfType("RVSourceGroup")
    for i in range(0,len(rvSourceAnim)):
        rv.extra_commands.setUIName(rvSourceAnim[i],listOfShot[i]+"_"+taskA)
    #connect the source to sequence A
    rv.commands.setNodeInputs(taskAll[0],rvSourceAnim)

    #load the shots for sequence B
    for i in listOfShot:
        rv.commands.addSource(seqDic["shots"][i][taskB])
    rvTotalSource = rv.commands.nodesOfType("RVSourceGroup")
    s = set(rvSourceAnim)
    rvSourceLayout = [ x for x in rvTotalSource if x not in s]
    for i in range(0,len(rvSourceLayout)):
        rv.extra_commands.setUIName(rvSourceLayout[i],listOfShot[i]+"_"+taskB)

    rv.commands.setNodeInputs(taskAll[1],rvSourceLayout)

    rv.commands.setNodeInputs("ABStack",taskAll)
    rv.commands.setViewNode("ABStack")

    F = MuSymbol("rvui.toggleWipe")
    F()
    #rv.rvui.toggleWipe()
    #print rv.commands.activeModes()
    #print(time.time()-startTime)


def createMode(seqDic={}):
  "Required to initialize the module. RV will call this function to create your mode."
  #return  PyHello()
  return addShots(seqDic)

#lastMoviePublished(seqShot='s0300', task='Layout')

