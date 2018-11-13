#!/usr/bin/env python
# coding:utf-8
""":mod:`MyCustomTab` -- dummy module
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

from Katana import NodegraphAPI,UI4
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from sgApi.sgApi import SgApi
from sgtkLib import tkutil, tkm
import os, pprint, errno, argparse, sys, math, operator

_USER_ = os.environ['USER']
_STARTTIME_ = 101

_USER_ = os.environ['USER']
tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg
sgA = SgApi(sgw=sgw, tk=tk, project=project)

imageFilterConfoLayout= {
        'filter_operator' : 'all',
        'filters':[
            ['tag_list', 'name_is','primary'],
            ['published_file_type', 'name_is', 'QCRmovie'],
        ]
    }

imageFilterAsset = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'TurntableMovie'],
        ]
    }

imageFilterLayoutBase = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'name_is', 'GenericMovie'],
            ['published_file_type', 'name_is', 'PlayblastMovie'],
            #['published_file_type', 'name_is', 'CompoMovie'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
            #['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }

imageFilterEditing = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'name_is', 'GenericMovie'],
            #['published_file_type', 'name_is', 'DwaMovie'],
            ['published_file_type', 'name_is', 'PlayblastMovie'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
            #['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }



def findAllSequence(all = False):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
    ]
    res = {}
    seqShots =[]
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','code','description']):
        seq = v['code']
        if all:
            if not seq in res:
                res[seq] = {}
            res[seq]['description'] = v['description']
        else:
            if int(seq[seq.find('s')+1:]) <9000:
                if not seq in res:
                    res[seq] = {}
                if v['description'] != None:
                    res[seq]['description'] = v['description']
                else:
                    res[seq]['description'] = 'None'
            else:
                print 'donuts for: ' + seq
    return res

def findShots( seq='s1300', shotList=[]):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'in',shotList],
        #['entity.Shot.tag_list', 'name_contains', 'mattepainting'],
    ]

    res = {}
    for v in sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_cut_order','entity.Shot.sg_frames_of_interest','entity.Shot.sg_cut_in','entity.Shot.sg_cut_out'], order=[{'field_name':'created_at','direction':'desc'}]):
        entityName = v['entity']['name']
        if v['entity.Shot.sg_cut_order'] > 0:
            if not entityName in res:
                res[entityName] ={}
                frameInterest = v['entity.Shot.sg_frames_of_interest']
                if frameInterest is not None:
                    res[entityName]['frameInterest'] = frameInterest.split(',')
                else:
                    res[entityName]['frameInterest'] = ['101']
                res[entityName]['cutIn'] = v['entity.Shot.sg_cut_in']
                res[entityName]['cutOut'] = v['entity.Shot.sg_cut_out']
                res[entityName]['cutOrder']= v['entity.Shot.sg_cut_order']
    return res

def findSingleShot(shot = 's1300_p00300', taskname = 'compo_precomp'):
    filterType = imFilter(taskname)
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'is', shot],
        ['task', 'name_is', taskname],
        filterType
    ]
    res = []
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type'], order=[{'field_name':'version_number','direction':'desc'}]):
        res.append(v['path']['local_path'])
    return res

def imFilter(taskname = 'compo_precomp'):
    filterDict = {'editing_edt': imageFilterEditing,
                  'layout_base': imageFilterLayoutBase,
                  'confo_layout':imageFilterConfoLayout,
                  'anim_main': imageFilterLayoutBase,
                  'model_base':imageFilterAsset,
                  'model_hi':imageFilterAsset,
                  'hair_surface':imageFilterAsset,
                  'surface_surfacing':imageFilterAsset
                  }
    return filterDict[taskname]

#get all the shot from the sequence
def findShotsInSequence(seq='s1300',dict=False):
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
    if dict:
        return res
    else:
        return sorted(seqShots)

def findCameraPath(seq='s1300',dictShots={},useDict = True):
    if useDict:
        shotInSeq = findShotsInSequence(seq=seq)
        dictShots = findShots(seq,shotInSeq)
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

class MyCustomTab(UI4.Tabs.BaseTab):

    # def __init__(self, parent):
    #     UI4.Tabs.BaseTab.__init__(self, parent)
    #
    #     label = QLabel('This is MyCustomTab')
    #     label.setObjectName('label')
    #     # label.setStyleSheet('font-weight: bold; '
    #     #                     'font-size: 18pt; '
    #     #                     'font-style: italic;')
    #     label.setStyleSheet("QLabel {background-color: rgb(255, 255,255);}")
    #     # self.buttonExecute = QFileDialog()
    #     # self.buttonExecute.setFileMode(QFileDialog.AnyFile)
    #     # self.buttonExecute.setFilter("Katana files (*.katana)")
    #     # self.buttonExecute.setObjectName('executeButton')
    #     # if self.buttonExecute.exec_():
    #     # #     filename = self.buttonExecute.selectedFiles()
    #     # #     filename = str(filename)
    #     #     print "filename"
    #     groupBox = QGroupBox()
    #     groupBox.setFixedSize(25,25)
    #     groupBox.setStyleSheet("QGroupBox {background-color: rgb(255, 0,0);}")
    #     hLayout = QHBoxLayout()
    #     hLayout.setObjectName('hLayout')
    #     hLayout.addStretch()
    #     hLayout.addWidget(label)
    #     hLayout.addWidget(groupBox)
    #     hLayout.addStretch()
    #
    #     vLayout = QVBoxLayout()
    #     vLayout.setObjectName('vLayout')
    #     vLayout.addLayout(hLayout)
    #
    #     self.setLayout(vLayout)

    def __init__(self, parent):
        UI4.Tabs.BaseTab.__init__(self, parent)
        self.initUI()

    def initUI(self):
        pos = 0
        res = findAllSequence()
        self.shotWidgets = []
        self.seqName = ''

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
        self.scroll.setFixedWidth(550)

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

        self.controlCheckFrameOfInt = QCheckBox("Frame of interest", self.controlGroupBox)
        self.controlCheckFrameOfInt.setObjectName('fInt')
        self.controlCheckFrameOfInt.setAutoExclusive(True)
        self.controlCheckFrameOfInt.setChecked(True)

        self.controlButton = QPushButton('create cam')
        self.controlButton.setObjectName('creaCam')

        self.controlLayout.addWidget(self.controlCheckAllShot, 0, 0)
        self.controlLayout.addWidget(self.controlCheckIn, 0, 1)
        self.controlLayout.addWidget(self.controlCheckMid, 0, 2)
        self.controlLayout.addWidget(self.controlCheckOut, 0, 3)
        self.controlLayout.addWidget(self.controlCheckFrameOfInt, 0, 4)
        self.controlLayout.addWidget(self.controlButton, 1, 4)

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
            seqName = QString(key)
            self.seqMenuBar.addAction(seqName)

        self.seqMenuBar.triggered.connect(self.processtrigger)
        self.controlCheckAllShot.stateChanged.connect(self.checkAllShot)
        self.controlCheckIn.stateChanged.connect(self.checkAllShot)
        self.controlCheckOut.stateChanged.connect(self.checkAllShot)
        self.controlCheckMid.stateChanged.connect(self.checkAllShot)
        self.controlCheckFrameOfInt.stateChanged.connect(self.checkAllShot)
        self.controlButton.clicked.connect(self.createCam)
        # self.controlButton.clicked.connect(self.overlay.show)

        self.setGeometry(300, 300, 250, 150)
        self.setFixedWidth(560)
        self.setWindowTitle('MasterSeqCam')
        self.setWindowIcon(QIcon('web.png'))

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # empty the layout and populate it with shot from the sequence
    def processtrigger(self, q):
        self.clearLayout(self.gridLayout)  # clear the layout
        self.controlCheckFrameOfInt.setChecked(True)  # set the check to Frame of interest
        self.shotWidgets = []  # empty the list of shot widgets
        inc = 0  # reset the incrementation for positioning the shot layout
        seqString = str(q.text())  # get the name and description of the sequence
        self.groupBoxSeq.setTitle(seqString)  # set the name of the groupbox to be the sequence name and description
        print seqString
        self.seqName = seqString  # extract the seq name alone
        shotInSeq = findShotsInSequence(self.seqName)  # find all the shot in this sequence
        allCamPath = findShots(self.seqName, shotInSeq)  # find the information for each shot

        # for each shot create it's UI
        for shot in getOrder(allCamPath):
            shot = shotUI(allCamPath[shot], shot)  # create the shot UI
            self.shotWidgets.append(shot)  # append the widget to the list
            self.gridLayout.addWidget(shot, inc, 0)  # add the shot to the layout
            inc += 1
        # print self.seqName+" is triggered"

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

PluginRegistry = [
    ('KatanaPanel', 2.0, 'MyCustomTab', MyCustomTab),
    ('KatanaPanel', 2.0, 'Custom/MyCustomTab', MyCustomTab),
]