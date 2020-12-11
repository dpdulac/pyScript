#!/usr/bin/env python
# coding:utf-8
""":mod: OCIOtest.py
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2020.12
   
"""
import PyOpenColorIO as ocio
import os, sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QComboBox, QApplication, QStyleFactory, QCheckBox, QLabel, QGroupBox,QPushButton, QVBoxLayout, QLineEdit, QSpinBox, QFileDialog, QLayout

__FILE_FORMAT__ = ['jpg', 'png', 'exr', 'tif']
__FILE_TYPE__ = ['single frame','from sequences','movie (*.mov, *.qt)']
__CONVERTION_LIST__={'srgb8--->Acescg':'convert from srgb8 images to Acescg \n(i.e:jpg/png/tif/mov/qt to exr/tif)',
                     'srgb8--->linearSrgb':'convert from srgb8 images to linearSrgb \n(i.e:jpg/png/tif/mov/qt to exr/tif)',
                     'Acescg--->linearSrgb':'convert from Acescg images to linearSrgb \n(i.e: exr/tif to exr/tif)',
                     'linearSrgb--->Acescg':'convert from linearSrgb images to Acescg \n(i.e: exr/tif to exr/tif)',
                     'custom':'choose between format'}


class convertWindow(QMainWindow):
    def __init__(self,parent=None):
        super(convertWindow,self).__init__(parent)
        self.colorSpaceIcon = QIcon('/s/prodanim/ta/_sandbox/duda/tmp/colormanager.png')
        self.xSize = 800
        self.InitUI()

    def InitUI(self):
        self.centralWidget = QWidget()
        self.mainLayout = QGridLayout()
        self.centralWidget.setLayout(self.mainLayout)
        self.colorSpacesNames = self.findColorSpacesNames()

        #---------------------------Shot Group Box------------------------------
        self.shotGroupBox = QGroupBox('convert')
        self.shotGroupBox.setCheckable(True)
        self.shotGroupBox.setAttribute(Qt.WA_StyledBackground, True)
        self.shotGroupBox.setStyleSheet("QGroupBox{background-color: rgba(180,180,180,255);},QTreeWidget::QToolTip{ background-color: yellow; }")
        #self.shotGroupBox.setFixedSize(700, 250)
        self.shotLayout = QGridLayout(self.shotGroupBox)

        # Color space group Box
        self.colorSpaceCheckBox = QCheckBox('Use Color Spaces')
        self.colorSpaceCheckBox.setToolTip('use color space convertion')
        self.colorSpaceCheckBox.setIcon(self.colorSpaceIcon)
        self.colorSpaceCheckBox.setChecked(False)
        self.colorSpaceGroupBox = QGroupBox()
        self.colorSpaceGroupBox.setToolTip('choose the in/out color spaces')
        self.colorSpaceGroupBox.setAttribute(Qt.WA_StyledBackground, True)
        self.colorSpaceCheckBox.setStyleSheet("QGroupBox{background-color: rgba(100,100,100,255);},QGroupBox::QToolTip{ background-color: yellow; }")
        self.colorSpaceGroupBox.setVisible(False)
        # self.colorSpaceGroupBox.setCheckable(True)
        # self.colorSpaceGroupBox.setChecked(False)
        self.colorSpaceLayout = QGridLayout(self.colorSpaceGroupBox)
        self.inColorSpaceComboBox = QComboBox()
        self.inColorSpaceComboBox.setFixedSize(120,25)
        self.inColorSpaceComboBox.setToolTip('from color space')
        self.inColorSpaceComboBox.addItems(self.colorSpacesNames)
        self.inColorSpaceComboBox.setCurrentIndex(self.getColorSpace())
        self.outColorSpaceComboBox = QComboBox()
        self.outColorSpaceComboBox.setFixedSize(120,25)
        self.outColorSpaceComboBox.setToolTip('to color space')
        self.outColorSpaceComboBox.addItems(self.colorSpacesNames)
        self.outColorSpaceComboBox.setCurrentIndex(self.getColorSpace('srgb8'))
        self.inLabel = QLabel('in color space')
        self.outLabel = QLabel('out color space')
        self.choiceSpaceLabel = QLabel('conversion type')
        self.choiceSpaceComboBox = QComboBox()
        self.choiceSpaceComboBox.addItems(__CONVERTION_LIST__.keys())
        self.choiceSpaceComboBox.setToolTip(__CONVERTION_LIST__[str(self.choiceSpaceComboBox.currentText())])
        self.choiceSpaceComboBox.setFixedSize(170,25)
        self.widgetSpace= QWidget()
        self.colorSpaceLayout.addWidget(self.choiceSpaceLabel)
        self.colorSpaceLayout.addWidget(self.inLabel,0,1)
        self.colorSpaceLayout.addWidget(self.outLabel,0,2)
        self.colorSpaceLayout.addWidget(self.choiceSpaceComboBox, 1, 0)
        self.colorSpaceLayout.addWidget(self.inColorSpaceComboBox,1,1)
        self.colorSpaceLayout.addWidget(self.outColorSpaceComboBox,1,2)
        self.colorSpaceLayout.addWidget(self.widgetSpace,1,3)
        self.colorSpaceLayout.addWidget(self.widgetSpace, 1, 4)
        self.inLabel.setVisible(False)
        self.outLabel.setVisible(False)
        self.inColorSpaceComboBox.setVisible(False)
        self.outColorSpaceComboBox.setVisible(False)

        # file in/out groupBox
        self.fileGroupBox = QGroupBox('file in/out')
        self.fileGroupBox.setToolTip('in/out setting')
        self.fileMainGridLayout = QGridLayout(self.fileGroupBox)
        # file type
        self.fileTypeLayout = QVBoxLayout()
        self.fileTypeCombo = QComboBox()
        self.fileTypeCombo.addItems(__FILE_TYPE__)
        self.fileTypeCombo.setFixedSize(105,25)
        self.fileTypeCombo.setToolTip('type of file to export (i.e: single frame, sequence of frames, movie)')
        self.fileTypeLabel = QLabel('file type')
        self.fileTypeLayout.addWidget(self.fileTypeLabel)
        self.fileTypeLayout.addWidget(self.fileTypeCombo)
        # in
        self.fileInLayout = QGridLayout()
        self.fileInPushbutton = QPushButton('file in')
        self.fileInPushbutton.setToolTip('dialog box for in file')
        self.fileInLineEdit = QLineEdit()
        self.fileInLineEdit.setMinimumSize(300,25)
        self.fileInLineEdit.setToolTip('image to convert from')
        self.fileInPadLabel = QLabel('padding')
        self.fileInPadLabel.setEnabled(True)
        self.fileInPadSpinBox = QSpinBox()
        self.fileInPadSpinBox.setToolTip("number of frame to use as padding")
        self.fileInPadSpinBox.setEnabled(True)
        self.fileInInFrameLabel = QLabel('cut in')
        self.fileInInFrameLabel.setEnabled(True)
        self.fileInInFrame = QSpinBox()
        self.fileInInFrame.setToolTip('in frame nb to convert')
        self.fileInInFrame.setEnabled(True)
        self.fileInOutFrameLabel = QLabel('cut out')
        self.fileInOutFrameLabel.setEnabled(True)
        self.fileInOutFrame = QSpinBox()
        self.fileInOutFrame.setToolTip('out frame nb to convert')
        self.fileInOutFrame.setEnabled(True)
        self.fileInInputFrameLabel = QLabel('frames')
        self.fileInInputLineEdit = QLineEdit()
        self.fileInInputLineEdit.setFixedSize(100,25)
        self.validator = QRegExpValidator(QRegExp("[0-9,-]*"))
        self.fileInInputLineEdit.setValidator(self.validator)
        self.fileInInputLineEdit.setToolTip('frame to extract separated with a "," or "-"i.e: 20,30,40-50....')
        self.fileInAllCheckbox = QCheckBox('all')
        self.fileInAllCheckbox.setToolTip('convert al frames from sequence/movie')
        self.fileInLayout.addWidget(self.fileInPushbutton,1,0)
        self.fileInLayout.addWidget(self.fileInLineEdit,1,1)
        self.fileInLayout.addWidget(self.fileInInputFrameLabel, 0, 2)
        self.fileInLayout.addWidget(self.fileInInputLineEdit, 1, 2)
        self.fileInLayout.addWidget(self.fileInAllCheckbox, 1, 4)
        self.fileInInputFrameLabel.setVisible(False)
        self.fileInInputLineEdit.setVisible(False)
        self.fileInAllCheckbox.setVisible(False)
        #self.fileInLayout.addWidget(self.fileInPadLabel,0,2)
        #self.fileInLayout.addWidget(self.fileInPadSpinBox,1,2)
        # self.fileInLayout.addWidget(self.fileInInFrameLabel,0,3)
        # self.fileInLayout.addWidget(self.fileInInFrame,1,3)
        # self.fileInLayout.addWidget(self.fileInOutFrameLabel,0,4)
        # self.fileInLayout.addWidget(self.fileInOutFrame,1,4)
        #out
        self.fileOutLayout = QGridLayout()
        self.fileOutPushbutton = QPushButton('file out')
        self.fileOutPushbutton.setToolTip('dialog box for in file')
        self.fileOutPathLabel = QLabel('out directory')
        self.fileOutLineEdit = QLineEdit()
        self.fileOutLineEdit.setMinimumSize(300, 25)
        self.fileOutLineEdit.setToolTip('image to convert too')
        self.fileOutFormatLabel = QLabel('out format')
        self.fileOutComboBox = QComboBox()
        self.fileOutComboBox.addItems(__FILE_FORMAT__)
        self.fileOutComboBox.setToolTip(('output format'))
        self.fileOutNameLineEdit = QLineEdit()
        self.fileOutNameLineEdit.setToolTip('name for output image(s)')
        self.fileOutNameLineEdit.setFixedSize(130,25)
        self.fileOutNameLabel = QLabel('output name')
        self.fileOutLayout.addWidget(self.fileOutPushbutton,1,0)
        self.fileOutLayout.addWidget(self.fileOutLineEdit,1,1)
        self.fileOutLayout.addWidget(self.fileOutNameLineEdit,1,2)
        self.fileOutLayout.addWidget(self.fileOutComboBox,1,3)
        self.fileOutLayout.addWidget(self.fileOutPathLabel, 0, 1)
        self.fileOutLayout.addWidget(self.fileOutFormatLabel,0,3)
        self.fileOutLayout.addWidget(self.fileOutNameLabel, 0,2)

        self.fileMainGridLayout.addLayout(self.fileTypeLayout,0,0)
        self.fileMainGridLayout.addLayout(self.fileInLayout,1,0)
        self.fileMainGridLayout.addLayout(self.fileOutLayout,2,0)

        self.shotLayout.addWidget(self.fileGroupBox, 0, 0)
        self.shotLayout.addWidget(self.colorSpaceCheckBox,1,0)
        self.shotLayout.addWidget(self.colorSpaceGroupBox,2,0)


        #----------------------end Shot Group Box--------------------------------

        self.mainLayout.addWidget(self.shotGroupBox,0,0)

        self.setCentralWidget(self.centralWidget)

        self.setFixedSize(self.xSize,255)

        #self.colorSpaceGroupBox.toggled.connect(self.enableColorSpacesChoice)
        self.colorSpaceCheckBox.toggled.connect(self.displayColorSpace)
        self.fileInAllCheckbox.toggled.connect(self.setAllImages)
        self.fileInPushbutton.clicked.connect(self.findFile)
        self.fileOutPushbutton.clicked.connect(self.findDirectory)
        self.fileTypeCombo.currentTextChanged.connect(self.fileTypeChanged)
        self.choiceSpaceComboBox.currentTextChanged.connect(self.convertionChoice)

    def convertionChoice(self):
        if self.choiceSpaceComboBox.currentText() == 'custom':
            self.inLabel.setVisible(True)
            self.outLabel.setVisible(True)
            self.inColorSpaceComboBox.setVisible(True)
            self.outColorSpaceComboBox.setVisible(True)
            self.widgetSpace.setVisible(False)
        else:
            self.inLabel.setVisible(False)
            self.outLabel.setVisible(False)
            self.inColorSpaceComboBox.setVisible(False)
            self.outColorSpaceComboBox.setVisible(False)
            self.widgetSpace.setVisible(True)

    def displayColorSpace(self,s):
        if s:
            self.setFixedSize(self.xSize, 350)
            self.colorSpaceGroupBox.setVisible(True)
        else:
            self.setFixedSize(self.xSize, 255)
            self.colorSpaceGroupBox.setVisible(False)

    def setAllImages(self,s):
        if s:
            self.fileInInputLineEdit.setVisible(False)
            self.fileInInputFrameLabel.setVisible(False)
        else:
            self.fileInInputLineEdit.setVisible(True)
            self.fileInInputFrameLabel.setVisible(True)

    def fileTypeChanged(self):
        if self.fileTypeCombo.currentText() != __FILE_TYPE__[0]:
            # change the size of combobox
            self.fileTypeCombo.setFixedSize(150, 25)
            # uncheck the all checkbox
            self.fileInAllCheckbox.setChecked(False)
            # reset the frame text
            self.fileInInputLineEdit.setText('')
            # set the line edit to be visible
            self.fileInInputFrameLabel.setVisible(True)
            self.fileInInputLineEdit.setVisible(True)
            self.fileInAllCheckbox.setVisible(True)
        else:
            self.fileTypeCombo.setFixedSize(105, 25)
            self.fileInInputLineEdit.setText('')
            self.fileInAllCheckbox.setChecked(False)
            self.fileInInputFrameLabel.setVisible(False)
            self.fileInInputLineEdit.setVisible(False)
            self.fileInAllCheckbox.setVisible(False)


    def getColorSpace(self,colorSpace='acescg'):
        #indexNb =0
        try:
            indexNb = self.colorSpacesNames.index(colorSpace)
        except:
            return 0
        else:
            return indexNb


    def enableColorSpacesChoice(self,s):
        if s :
            self.setFixedSize(self.xSize,350)
            self.inColorSpaceComboBox.setEnabled(True)
            self.outColorSpaceComboBox.setEnabled(True)
        else:
            self.inColorSpaceComboBox.setEnabled(False)
            self.outColorSpaceComboBox.setEnabled(False)
            self.centralWidget.setFixedHeight(250)

    def findColorSpacesNames(self):
        config = ocio.GetCurrentConfig()
        colorSpaces = [cs.getName() for cs in config.getColorSpaces()]
        return colorSpaces

    def findDirectory(self):
        dirName = QFileDialog.getExistingDirectory(self,'Open directory','/s/prodanim/ta')
        self.fileOutLineEdit.setText(dirName)

    def findFile(self):
        """dialog to open file of type .mov"""
        filename=''
        if self.fileTypeCombo.currentText() == __FILE_TYPE__[0]:
            filename = QFileDialog.getOpenFileName(self, 'Open file', '/s/prodanim/ta',"Image files ( *.exr *.jpg *.png *.tif)")
            filename = str(filename[0])
            self.fileInLineEdit.setText(filename)
            nameframe = filename[filename.rfind('/')+1:filename.rfind('.')]
            # if nameframe.rfind('.') != -1:
            #     nameframe = nameframe[:nameframe.rfind('.')]
            nameLength = len(nameframe)
            self.fileOutNameLineEdit.setFixedSize(nameLength*7,25)
            self.fileOutNameLineEdit.setText(nameframe)
        # fill fileQLineEdit with the string filename
        #self.fileInLineEdit.setText(filename)
        else:
            print str(filename[0])

ex = None


def BuildShotUI():
    global ex
    if ex is not None:
        ex.close()
    parent = QApplication.activeWindow()
    ex = convertWindow(parent)
    ex.show()

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    #app.setStyle(QStyleFactory.create("Cleanlooks"))
    BuildShotUI()
    app.exec_()


if __name__ == '__main__':
    main()
    "oiiotool -a test.mov --colorconvert:subimages=all srgb8 acescg --sisplit -o:all=1 test%04d.exr"