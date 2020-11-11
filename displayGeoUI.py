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

        self.pathLabel = QtGui.QLabel('path')
        self.pathlineEdit = fileEdit()
        self.pathButon = QtGui.QPushButton('Display')

        self.mainGridLayout.addWidget(self.pathLabel,0,0)
        self.mainGridLayout.addWidget(self.pathlineEdit,1,0)
        self.mainGridLayout.addWidget(self.pathButon,2,0)

        self.pathButon.clicked.connect(self.displayIt)
        self.setLayout(self.mainGridLayout)

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
        print str(self.pathlineEdit.text())
        sg = ScenegraphManager.getActiveScenegraph()
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
    sg = ScenegraphManager.getActiveScenegraph()
    sg.clearPinnedLocations()
    # if ex is not None:
    #     ex.close()
    print('donuts')
    parent = QtGui.QApplication.activeWindow()
    ex= displayGeoUI()
    ex.setWindowFlags(Qt.WindowStaysOnTopHint)
    ex.show()


def main():
    app = QtGui.QApplication(sys.argv)
    app.setStyle(QtGui.QStyleFactory.create("plastique"))
    BuildisplayGeoUI()
    app.exec_()

if __name__ == '__main__':
    main()
