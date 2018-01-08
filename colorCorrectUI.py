#!/usr/bin/env python
# coding:utf-8
""":mod:`colorCorrectUI` -- dummy module
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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from functools import partial
import os, pprint, errno, argparse, sys, math
import datetime

class ColorCorrectUI(QWidget):

    def __init__(self):
        super(ColorCorrectUI, self).__init__()

        #self.widget = QWidget()
        self.mainLayout = QGridLayout()

        self.colorValue = {"redFader" : 0.0, "greenFader": 0.0, "blueFader": 0.0 }
        self.maxValue = 10.0
        self.minValue = -10.0

        #Exposure Group
        self.exposureGroup = QGroupBox("Exposure")
        self.exposureGroup.setMinimumHeight(500)
        self.exposureGroup.setMaximumHeight(500)
        self.exposureGroup.setMinimumWidth(300)
        self.exposureGroup.setMaximumWidth(300)
        self.exposureLayout = QGridLayout(self.exposureGroup)
        self.exposureLayout.setColumnMinimumWidth(0,20)
        self.exposureLayout.setColumnStretch(0,20)
        self.exposureLayout.setColumnMinimumWidth(1,20)
        self.exposureLayout.setColumnStretch(1,20)
        self.exposureLayout.setRowMinimumHeight(0,20)
        self.exposureLayout.setRowStretch(0,20)
        self.exposureLayout.setRowMinimumHeight(1,100)
        self.exposureLayout.setRowStretch(1,20)

        self.gangCheckBox = QCheckBox("gang",self.exposureGroup)
        self.resetPush = QPushButton("Reset",self.exposureGroup)
        self.resetPush.clicked.connect(self.resetFader)

        self.redLabel = QLabel("red",self.exposureGroup)
        self.redSpinBox = QDoubleSpinBox(self.exposureGroup)
        self.redSpinBox.setObjectName("redSpinBox")
        self.redSpinBox.setSingleStep(0.01)
        self.redSpinBox.setRange(self.minValue,self.maxValue)
        self.redFader = QSlider(Qt.Vertical,self.exposureGroup)
        self.redFader.setFixedHeight(380)
        self.redFader.setObjectName("redFader")
        self.redFader.setSingleStep(1)
        self.redFader.setRange(self.minValue*100,self.maxValue*100)
        self.redFader.setValue(0)
        self.redSpinBox.valueChanged.connect(partial(self.spinBoxValue,self.redFader))
        self.redFader.sliderMoved.connect(partial(self.faderValue,self.redSpinBox))

        self.greenLabel = QLabel('Green',self.exposureGroup)
        self.greenSpinBox = QDoubleSpinBox(self.exposureGroup)
        self.greenSpinBox.setObjectName("greenSpinBox")
        self.greenSpinBox.setSingleStep(0.01)
        self.greenSpinBox.setRange(self.minValue,self.maxValue)
        self.greenFader = QSlider(Qt.Vertical,self.exposureGroup)
        self.greenFader.setFixedHeight(380)
        self.greenFader.setObjectName("greenFader")
        self.greenFader.setRange(self.minValue*100,self.maxValue*100)
        self.greenFader.setValue(0)
        self.greenSpinBox.valueChanged.connect(partial(self.spinBoxValue,self.greenFader))
        self.greenFader.sliderMoved.connect(partial(self.faderValue,self.greenSpinBox))

        self.blueLabel = QLabel('Blue',self.exposureGroup)
        self.blueSpinBox = QDoubleSpinBox(self.exposureGroup)
        self.blueSpinBox.setObjectName("blueSpinBox")
        self.blueSpinBox.setSingleStep(0.01)
        self.blueSpinBox.setRange(self.minValue,self.maxValue)
        self.blueFader = QSlider(Qt.Vertical,self.exposureGroup)
        self.blueFader.setFixedHeight(380)
        self.blueFader.setObjectName("blueFader")
        self.blueFader.setRange(self.minValue*100,self.maxValue*100)
        self.blueFader.setValue(0)
        self.blueSpinBox.valueChanged.connect(partial(self.spinBoxValue,self.blueFader))
        self.blueFader.sliderMoved.connect(partial(self.faderValue,self.blueSpinBox))

        self.exposureLayout.addWidget(self.redSpinBox,0,0)
        self.exposureLayout.addWidget(self.greenSpinBox,0,1)
        self.exposureLayout.addWidget(self.blueSpinBox,0,2)
        self.exposureLayout.addWidget(self.redFader,1,0)
        self.exposureLayout.addWidget(self.greenFader,1,1)
        self.exposureLayout.addWidget(self.blueFader,1,2)
        self.exposureLayout.addWidget(self.redLabel,2,0)
        self.exposureLayout.addWidget(self.greenLabel,2,1)
        self.exposureLayout.addWidget(self.blueLabel,2,2)
        self.exposureLayout.addWidget(self.resetPush,4,3)
        self.exposureLayout.addWidget(self.gangCheckBox,0,3)
        self.exposureGroup.setLayout(self.exposureLayout)

        self.mainLayout.addWidget(self.exposureGroup,0,0)
        self.setLayout(self.mainLayout)
        #self.widget.setLayout(self.mainLayout)
        #self.setWidget(self.widget)

    def spinBoxValue(self,fader):
        spinbox = self.sender()
        fader.setValue(spinbox.value()*100)
        self.redValue = self.redSpinBox.value()
        self.greenValue = self.greenSpinBox.value()
        self.blueValue = self.blueSpinBox.value()

    def faderValue(self,spinbox):
        #list of fader and spinbox
        faderList = ["redFader","greenFader","blueFader"]
        spinboxList = ["redSpinBox","greenSpinBox","blueSpinBox"]
        #max of the fader
        maxColor = False
        fader = self.sender()
        #get the name of the fader
        faderName = str(fader.objectName())
        #create a copy of the fader list and remove the current fader from the list
        newFaderList = list(faderList)
        newFaderList.remove(faderName)
        #if in gang mode
        if self.gangCheckBox.isChecked():
            #calculate the delta variation of the current fader
            delta = fader.value() - (self.colorValue[faderName]*100)
            #check to see if the color for each fader is not greater than maxValue or less than minValue if so set maxColor to True
            for key in self.colorValue.keys():
                if (self.colorValue[key] + (delta/100.0)) > self.maxValue or (self.colorValue[key] + (delta/100.0)) < self.minValue:
                    maxColor = True
                    break
            #if it's not over the maxColor
            if not maxColor:
                #set the colorValue of the current fader to it's value
                self.colorValue[faderName] = fader.value()/100.0
                #add the delta to the other fader
                for item in newFaderList:
                    widget = self.findChild(QSlider,item)
                    currentValue = widget.value()
                    widget.setValue(currentValue + delta)
                    self.colorValue[item] = widget.value()/100.0
                #set the spinbox to the fader value
                for item, key in zip(spinboxList, faderList):
                    widgetSpin = self.findChild(QDoubleSpinBox,item)
                    #widgetFader = self.findChild(QSlider,key)
                    widgetSpin.setValue(self.colorValue[key])
            #if it's over or under the maxcolor keep the fader at the same position
            else:
                fader.setValue(self.colorValue[faderName])
        #if gang not checked
        else:
            spinbox.setValue(fader.value()/100.0)
            self.colorValue[faderName] = fader.value()/100.0


    def resetFader(self):
        widget = [self.greenSpinBox,self.redSpinBox,self.blueSpinBox,self.blueFader,self.redFader,self.greenFader]
        for item in widget:
            item.setValue(0.0)





ex =None
def BuildColorCorrectUI():

    global ex
    if ex is not None:
        ex.close()
    ex= ColorCorrectUI()
    ex.show()


def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    BuildColorCorrectUI()
    app.exec_()

if __name__ == '__main__':
    main()