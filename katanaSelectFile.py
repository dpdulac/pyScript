#!/usr/bin/env python
# coding:utf-8
""":mod:`katanaSelectFile` -- dummy module
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


from PyQt4.QtGui import *
from PyQt4.QtCore import *
from UI4.App import MainWindow, MainMenu, Tabs
from Katana import  Callbacks, KatanaFile, NodegraphAPI


class customMenu(QWidget):
    def __init__(self,parent = MainWindow.CurrentMainWindow()):
        super(customMenu, self).__init__(parent)
        self.mainMenu = parent.findChild(MainMenu.MainMenu)
        self.initUI()

    def initUI(self):
        self.customMenu = QMenu('&Custom',self.mainMenu)
        self.customMenu.setObjectName('customMenu')
        self.customMenu.setToolTip('alternative Open, Save....')

        self.openAction = QAction('Open...',self.customMenu,statusTip = 'open file',triggered =self.displayOpenDialog)
        self.openAction.setObjectName('openAction')
        self.openAction.setShortcut('Alt+X')
        self.customMenu.addAction(self.openAction)

        self.saveAction = QAction('Save',self.customMenu,statusTip = 'save file',triggered =self.displaySaveDialog)
        self.saveAction.setObjectName('saveAction')
        self.saveAction.setShortcut('Alt+Z')
        self.customMenu.addSeparator()
        self.customMenu.addAction(self.saveAction)

        self.importAction = QAction('Import',self.customMenu,statusTip = 'import file',triggered =self.displayOpenDialog)
        self.importAction.setObjectName('importAction')
        self.importAction.setShortcut('Alt+>')
        self.customMenu.addSeparator()
        self.customMenu.addAction(self.importAction)

        self.customMenu.hovered.connect(self.menuToolTip)
        self.mainMenu.addMenu(self.customMenu)


    def menuToolTip(self):
        tip = self.toolTip()
        QToolTip.showText(tip)

    def displaySaveDialog(self):
        fname = str(QFileDialog.getSaveFileName(self, 'Save file','/s/prodanim/asterix2',"Katana files (*.katana)"))
        if fname == '':
            print 'No file has been saved'
        else:
            KatanaFile.Save(fname)
            print 'Saving : '+fname
    def displayOpenDialog(self):
        fname = str(QFileDialog.getOpenFileName(self, 'Open file','/s/prodanim/asterix2',"Katana files (*.katana)"))
        if fname == '':
            print 'No file has been open'
        if self.sender().objectName() == 'openAction':
            KatanaFile.Load(fname)
            print 'Loading : '+fname
        else:
            currentSelection = NodegraphAPI.GetAllSelectedNodes()
            #deselect all the node to select only the 2 created nodes and put them floating under the mouse
            for node in currentSelection:
                NodegraphAPI.SetNodeSelected(node,False)
            KatanaFile.Import(fname, floatNodes=True)
            print 'importing : '+fname
            nodeList = NodegraphAPI.GetAllSelectedNodes()
            # Find Nodegraph tab and float nodes
            nodegraphTab = Tabs.FindTopTab('Node Graph')
            if nodegraphTab:
                nodegraphTab.floatNodes(nodeList)

def onStartupComplete(**kwargs):
    from Katana import UI4
    katanaWindow = UI4.App.MainWindow.CurrentMainWindow()
    customMenu(parent=katanaWindow)
    print 'Custom menu loaded'

def customMenuCallback():
    Callbacks.addCallback(Callbacks.Type.onStartupComplete, onStartupComplete)
