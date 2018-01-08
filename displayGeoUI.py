#!/usr/bin/env python
# coding:utf-8
""":mod:`displayGeoUI` -- dummy module
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

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Katana import  NodegraphAPI,ScenegraphManager,Nodes3DAPI

class fileEdit(QLineEdit):
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



class displayGeoUI(QWidget):
    def __init__(self):
        super(displayGeoUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.menu_bar = QMenuBar()
        self.help_menu = self.menu_bar.addMenu('Help')

        self.mainLayout = QVBoxLayout()
        self.mainGridLayout = QGridLayout()

        self.pathLabel = QLabel('path')
        self.pathlineEdit = fileEdit()
        self.pathlineEdit.setToolTip('enter/drop the path for object to be pinned (i.e /world/geo/location)')
        self.pathButon = QPushButton('Display')
        self.pathButon.setToolTip('apply the selection')
        self.pathCheck = QCheckBox('clear pinned')
        self.pathCheck.setChecked(True)
        self.pathCheck.setToolTip('clear the pinned object in the scene before applying the selection')


        self.mainGridLayout.addWidget(self.pathLabel,0,0)
        self.mainGridLayout.addWidget(self.pathlineEdit,0,1)
        self.mainGridLayout.addWidget(self.pathCheck,1,0)
        self.mainGridLayout.addWidget(self.pathButon,1,1)

        self.mainLayout.addWidget(self.menu_bar)
        self.mainLayout.addLayout(self.mainGridLayout)

        self.pathButon.clicked.connect(self.displayIt)
        self.setLayout(self.mainLayout)

    def WalkBoundAttrLocations(self,producer,listPath=[]):
        listWord = ['BDD:ALL']
        if producer is not None :
            path = producer.getFullName()
            if any(word in path for word in listWord):
                listPath.append(producer.getFullName())

            for child in producer.iterChildren():
                self.WalkBoundAttrLocations(child,listPath)
        else:
            print "producer or producerType not good"
        return listPath

    def displayIt(self):
        sg = ScenegraphManager.getActiveScenegraph()
        if self.pathCheck.isChecked():
            sg.clearPinnedLocations()
        node = NodegraphAPI.GetNode( 'root' )
        time = NodegraphAPI.GetCurrentTime()
        producer = Nodes3DAPI.GetGeometryProducer( node, time)
        prod = producer.getProducerByPath(str(self.pathlineEdit.text()))
        pathToOpen = self.WalkBoundAttrLocations(prod)
        for item in pathToOpen:
            sg.addPinnedLocation(item)

ex =None

def BuildisplayGeoUI():

    global ex
    if ex is not None:
        ex.close()
    ex= displayGeoUI()
    ex. setWindowFlags(Qt.WindowStaysOnTopHint)
    ex.show()

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    BuildisplayGeoUI()
    app.exec_()

if __name__ == '__main__':
    main()
