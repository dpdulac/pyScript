#!/usr/bin/env python
# coding:utf-8
""":mod: displayGeoUI_v002.py
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2020.11
   
"""
console_print('Pin down the BDD')

import sys
import PyQt5.QtGui
import PyQt5.QtWidgets as QtGui
from PyQt5.QtCore import *
from Katana import  NodegraphAPI,ScenegraphManager,Nodes3DAPI

class fileEdit(QtGui.QLineEdit):
    def __init__(self):
        super(fileEdit, self).__init__()

        self.setDragEnabled(True)

    def dragEnterEvent( self, event ):
            data = event.mimeData()
            urls = data.urls()
            if data.hasText():
            #if ( urls and urls[0].scheme() == 'file' ):
                event.acceptProposedAction()

    def dragMoveEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if data.hasText():
        #if ( urls and urls[0].scheme() == 'file' ):
            event.acceptProposedAction()

    def dropEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if data.hasText():
        #if ( urls and urls[0].scheme() == 'file' ):
            # for some reason, this doubles up the intro slash
            #filepath = str(urls[0].path())
            filepath = data.text()
            self.setText(filepath)


class displayGeoUI(QtGui.QWidget):
    def __init__(self,parent=None):
        super(displayGeoUI, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.mainGridLayout = QtGui.QGridLayout()

        self.nameLabel = QtGui.QLabel('name')
        self.namelineEdit = QtGui.QLineEdit()
        self.namelineEdit.setToolTip('name or part of name to look for')
        self.namelineEdit.setText('_hiShape')
        self.pathLabel = QtGui.QLabel('path')
        self.pathLineEdit = fileEdit()
        self.pathLineEdit.setToolTip('path(s) from the sceneGraph where to match the name')
        self.pathButon = QtGui.QPushButton('Display')
        self.pathButon.setToolTip('Display the object containing the name in selected path')
        self.resetButon = QtGui.QPushButton('Reset')
        self.resetButon.setToolTip('reset the name, path and undisplay all the displayed objects')
        self.resetName = QtGui.QPushButton('ResetName')
        self.resetName.setToolTip("reset the name to '_hiShape'")
        self.resetPath = QtGui.QPushButton('ResetPath')
        self.resetPath.setToolTip('empty the path')

        self.mainGridLayout.addWidget(self.nameLabel,0,0)
        self.mainGridLayout.addWidget(self.namelineEdit,0,1)
        self.mainGridLayout.addWidget(self.resetName,0,2)
        self.mainGridLayout.addWidget(self.pathLabel,1,0)
        self.mainGridLayout.addWidget(self.pathLineEdit,1,1)
        self.mainGridLayout.addWidget(self.resetPath,1,2)
        self.mainGridLayout.addWidget(self.pathButon,2,0)
        self.mainGridLayout.addWidget(self.resetButon,2,1)

        self.pathButon.clicked.connect(self.displayModel)
        self.resetButon.clicked.connect(self.resetDisplay)
        self.resetName.clicked.connect(self.resetTheName)
        self.resetPath.clicked.connect(self.resetThePath)

        self.setLayout(self.mainGridLayout)

    def resetDisplay(self):
        sg = ScenegraphManager.getActiveScenegraph()
        sg.clearPinnedLocations()
        self.namelineEdit.setText('_hiShape')
        self.pathLineEdit.setText('')

    def resetTheName(self):
        self.namelineEdit.setText('_hiShape')

    def resetThePath(self):
        self.pathLineEdit.setText('')

    def recursiveFindPath(self,producer, listPath=[], nameInNode='_hiShape'):
        if producer is not None:
            path = producer.getFullName()
            if path.find(nameInNode) >= 0:
                listPath.append(path)
            for child in producer.iterChildren():
                self.recursiveFindPath(child, listPath, nameInNode)
        else:
            print('no producer for :',producer)
        return listPath

    def displayModel(self,node=NodegraphAPI.GetRootNode(), nameInNode='_hiShape'):
        allPath =[]
        nameInNode = self.namelineEdit.text()
        node = NodegraphAPI.GetNode( 'root' )
        sg = ScenegraphManager.getActiveScenegraph()
        time = NodegraphAPI.GetCurrentTime()
        producer = Nodes3DAPI.GetGeometryProducer(node, time)
        splitText = str(self.pathLineEdit.text()).split(' ')
        if len(splitText) > 0 and splitText[0] != '' :
            for prodpath in splitText:
                producer =producer.getProducerByPath(prodpath)
                a = self.recursiveFindPath(producer, allPath, nameInNode=nameInNode)
                producer = Nodes3DAPI.GetGeometryProducer(node, time)
        else:
            allPath = self.recursiveFindPath(producer, listPath=[], nameInNode=nameInNode)
        for item in allPath:
            sg.addPinnedLocation(item)
            
ex =None

def BuildisplayGeoUI():

    global ex
    sg = ScenegraphManager.getActiveScenegraph()
    sg.clearPinnedLocations()
    # if ex is not None:
    #     ex.close()
    print('donuts')
    parent = QtGui.QApplication.activeWindow()
    ex= displayGeoUI()
    ex.setWindowFlags(Qt.WindowStaysOnTopHint)
    ex.show()