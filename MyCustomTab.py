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

from Katana import UI4
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MyCustomTab(UI4.Tabs.BaseTab):

    def __init__(self, parent):
        UI4.Tabs.BaseTab.__init__(self, parent)

        label = QLabel('This is MyCustomTab')
        label.setObjectName('label')
        # label.setStyleSheet('font-weight: bold; '
        #                     'font-size: 18pt; '
        #                     'font-style: italic;')
        label.setStyleSheet("QLabel {background-color: rgb(255, 255,255);}")
        # self.buttonExecute = QFileDialog()
        # self.buttonExecute.setFileMode(QFileDialog.AnyFile)
        # self.buttonExecute.setFilter("Katana files (*.katana)")
        # self.buttonExecute.setObjectName('executeButton')
        # if self.buttonExecute.exec_():
        # #     filename = self.buttonExecute.selectedFiles()
        # #     filename = str(filename)
        #     print "filename"
        groupBox = QGroupBox()
        groupBox.setFixedSize(25,25)
        groupBox.setStyleSheet("QGroupBox {background-color: rgb(255, 0,0);}")
        hLayout = QHBoxLayout()
        hLayout.setObjectName('hLayout')
        hLayout.addStretch()
        hLayout.addWidget(label)
        hLayout.addWidget(groupBox)
        hLayout.addStretch()

        vLayout = QVBoxLayout()
        vLayout.setObjectName('vLayout')
        vLayout.addLayout(hLayout)

        self.setLayout(vLayout)

PluginRegistry = [
    ('KatanaPanel', 2.0, 'MyCustomTab', MyCustomTab),
    ('KatanaPanel', 2.0, 'Custom/MyCustomTab', MyCustomTab),
]