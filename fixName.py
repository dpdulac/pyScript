#!/usr/bin/env python
# coding:utf-8
""":mod:`fixName.py` -- dummy module
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
# from sgApi.sgApi import SgApi
# from sgtkLib import tkutil, tkm
import os, sys

class fixNameUI(QWidget):
    def __init__(self):
        super(fixNameUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.mainGridLayout = QGridLayout()

        #do it button
        self.buttonExecute = QPushButton('Do it')
        self.buttonExecute.setToolTip('check and fix the name of nodes')

        self.nodeTypeGroup = QGroupBox()
        self.nodeTypeGroup.setEnabled(False)
        #nodeType choice
        self.nodeTypeQVboxLayout = QVBoxLayout(self.nodeTypeGroup)
        self.nodeTypeLabel = QLabel('nodeType',self.nodeTypeGroup)
        self.nodeTypeLabel.setAlignment(Qt.AlignCenter)
        self.nodeTypeComboBox = QComboBox(self.nodeTypeGroup)
        self.nodeTypeComboBox.addItem("ArnoldShadingNode")
        self.nodeTypeComboBox.addItem("NetworkMaterialSplice")
        self.nodeTypeComboBox.addItem("CameraCreate")
        self.nodeTypeQVboxLayout.addWidget(self.nodeTypeLabel)
        self.nodeTypeQVboxLayout.addWidget(self.nodeTypeComboBox)
        self.nodeTypeQVboxLayout.addStretch()
        
        #useNodeType
        self.useNodeTypeBoxLayout = QVBoxLayout()
        self.useNodeTypeLabel = QLabel('Node Type')
        self.useNodeTypeLabel.setAlignment(Qt.AlignCenter)
        self.useNodeTypeCheckBox = QCheckBox()
        #self.useNodeTypeCheckBox.setAutoExclusive(True)
        self.useNodeTypeCheckBox.setToolTip('find node of type in the whole scene')
        self.useNodeTypeBoxLayout.addWidget(self.useNodeTypeLabel)
        self.useNodeTypeBoxLayout.addWidget(self.useNodeTypeCheckBox)
        self.useNodeTypeBoxLayout.addStretch()
        
        #selectedNode
        self.selectedNodeBoxLayout = QVBoxLayout()
        self.selectedNodeLabel = QLabel('selected Nodes')
        self.selectedNodeLabel.setAlignment(Qt.AlignCenter)
        self.selectedNodeCheckBox = QCheckBox()
        self.selectedNodeCheckBox.setAutoExclusive(True)
        self.selectedNodeCheckBox.setChecked(True)
        self.selectedNodeCheckBox.setToolTip('use selected nodes only')
        self.selectedNodeBoxLayout.addWidget(self.selectedNodeLabel)
        self.selectedNodeBoxLayout.addWidget(self.selectedNodeCheckBox)
        self.selectedNodeBoxLayout.addStretch()
        
        #allNode
        self.allNodesBoxLayout = QVBoxLayout()
        self.allNodesLabel = QLabel('all Nodes')
        #self.allNodesLabel.setAlignment(Qt.AlignCenter)
        self.allNodesCheckBox = QCheckBox()
        self.allNodesCheckBox.setAutoExclusive(True)
        self.allNodesCheckBox.setToolTip('use all the node in the whole scene')
        self.allNodesBoxLayout.addWidget(self.allNodesLabel)
        self.allNodesBoxLayout.addWidget(self.allNodesCheckBox)
        self.allNodesBoxLayout.addStretch()
        self.allNodesBoxLayout.setAlignment(Qt.AlignCenter)

        self.mainGridLayout.addWidget(self.nodeTypeGroup,1,1)
        self.mainGridLayout.addLayout(self.useNodeTypeBoxLayout,1,0)
        self.mainGridLayout.addLayout(self.selectedNodeBoxLayout,0,0)
        self.mainGridLayout.addLayout(self.allNodesBoxLayout,0,1)
        self.mainGridLayout.addWidget(self.buttonExecute,2,1)
        self.mainGridLayout.setAlignment(Qt.AlignCenter)

        self.setLayout(self.mainGridLayout)

        self.useNodeTypeCheckBox.clicked.connect(self.enableCombo)
        self.buttonExecute.clicked.connect(self.doItMan)

    def enableCombo(self):
        state = self.useNodeTypeCheckBox.isChecked()
        self.nodeTypeGroup.setEnabled(state)

    def doItMan(self):
        allNodeState = self.allNodesCheckBox.isChecked()
        selectNodeState = self.selectedNodeCheckBox.isChecked()
        allSelectedNodes =[]
        nodesSelected = []
        if allNodeState:
             allSelectedNodes  = NodegraphAPI.GetAllNodes()
        else:
            allSelectedNodes = NodegraphAPI.GetAllSelectedNodes()
        for node in allSelectedNodes:
            #check if there is a parameter name on the node
            if node.getParameter('name') != None:
                if self.useNodeTypeCheckBox.isChecked():
                    if node.getType() == str(self.nodeTypeComboBox.currentText()):
                        nodesSelected.append(node)
                else:
                    nodesSelected.append(node)
        for node in nodesSelected:
            nodeName = node.getName()
            nodeParamName = node.getParameter('name').getValue(0)
            if nodeParamName != nodeName:
                node.getParameter('name').setValue(nodeName,0)
                print 'changing '+ nodeParamName + ' to: '+ nodeName




ex =None

def BuildFixNameUI():

    global ex
    if ex is not None:
        ex.close()
    ex= fixNameUI()
    ex. setWindowFlags(Qt.WindowStaysOnTopHint)
    ex.show()

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    BuildFixNameUI()
    app.exec_()

if __name__ == '__main__':
    main()