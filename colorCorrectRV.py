#!/usr/bin/env python
# coding:utf-8
""":mod:`colorCorrectRV` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2017, Mikros Image"

from rv import rvtypes, extra_commands, commands
import sys, pprint
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class SampleDialog(QDockWidget):

    def __init__(self):
        super(SampleDialog, self).__init__()

        self.widget = QWidget()
        self.mainLayout = QGridLayout

        #Exposure Group
        self.exposureGroup = QGroupBox("Exposure")
        self.exposureLayout = QGridLayout(self.exposureGroup)
        self.redLabel = QLabel("red",self.exposureGroup)
        self.redSpinBox = QDoubleSpinBox(self.exposureGroup)
        self.redFader = QSlider(Qt.Vertical,self.exposureGroup)
        self.redFader.setMaximum(10)
        self.redFader.setMinimum(-10)
        self.redFader.setValue(0)
        self.greenLabel = QLabel('Green',self.exposureGroup)
        self.greenSpinBox = QDoubleSpinBox(self.exposureGroup)
        self.greenFader = QSlider(Qt.Vertical,self.exposureGroup)
        self.greenFader.setMaximum(10)
        self.greenFader.setMinimum(-10)
        self.greenFader.setValue(0)
        self.blueLabel = QLabel('Blue',self.exposureGroup)
        self.blueSpinBox = QDoubleSpinBox(self.exposureGroup)
        self.blueFader = QSlider(Qt.Vertical,self.exposureGroup)
        self.blueFader.setMaximum(10)
        self.blueFader.setMinimum(-10)
        self.blueFader.setValue(0)
        self.exposureLayout.addWidget(self.redSpinBox,0,0)
        self.exposureLayout.addWidget(self.greenSpinBox,0,1)
        self.exposureLayout.addWidget(self.blueSpinBox,0,2)
        self.exposureLayout.addWidget(self.redFader,1,0)
        self.exposureLayout.addWidget(self.greenFader,1,1)
        self.exposureLayout.addWidget(self.blueFader,1,2)
        self.exposureLayout.addWidget(self.redLabel,2,0)
        self.exposureLayout.addWidget(self.greenLabel,2,1)
        self.exposureLayout.addWidget(self.blueLabel,2,2)


        combo = QQComboBox()
        combo.addItem("Combo")
        mainLayout.addWidget(combo)

        tree = QtGui.QTreeWidget()
        item = QtGui.QTreeWidgetItem(tree)
        item.setText(0,"Tree Item")
        tree.addTopLevelItem(item)
        mainLayout.addWidget(tree)

        line = QtGui.QLineEdit("Line Edit")
        mainLayout.addWidget(line)

        widget.setLayout(mainLayout)
        self.setWidget(widget)

class PyQtExample(rvtypes.MinorMode):

    def __init__(self):
        rvtypes.MinorMode.__init__(self)
        self.dialog = SampleDialog()
        widgets = QtGui.QApplication.topLevelWidgets()
        for w in widgets:
            if "QMainWindow" in str(w):
                w.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.dialog)

        self.init("PyQtExample", None, [("key-down--X", self.toggleDialog, ""),
            ("before-session-deletion", self.shutdown, "")],
            [("PyQtExample", [("Example 1", self.toggleDialog, "", None)])])
        self.dialog.hide()

    def shutdown(self, event):
        self.deactivate()

    def toggleDialog(self, event):
        if self.dialog.isVisible():
            self.dialog.hide()
        else:
            self.dialog.show()

def createMode():
    return PyQtExample()