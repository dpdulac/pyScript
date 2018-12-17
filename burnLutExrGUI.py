#!/usr/bin/env python
# coding:utf-8
""":mod:`burnLutExrGUI` -- dummy module
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
import OpenImageIO as oiio
#import PyOpenColorIO as OCIO
from array import *
import os, sys

_USER_ = os.environ['USER']
_OUTPATH_ ="/s/prodanim/asterix2/_sandbox/" + _USER_

# display widget for shots
class shotUI(QWidget):
    def __init__(self):
        super(shotUI, self).__init__()
        self.allShots = []
        self.fileNb = 1
        self.initUI()

    def initUI(self):
        self.mainLayout =QVBoxLayout()
        self.gridLayoutShot = QGridLayout()
        self.gridLayoutExecute = QGridLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.gridLayoutShot)
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.widget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(200)


        self.firstShot = findFileUI(self,False)
        self.allShots.append(self.firstShot)
        self.gridLayoutShot.addWidget(self.firstShot)
        self.buttonExecute = QPushButton('execute')
        self.buttonExecute.setToolTip('extract the frame from the chosen file(s)')
        self.buttonAdd = QPushButton('Add')
        self.buttonAdd.setToolTip('add a new file to be converted')

        self.gridLayoutExecute.addWidget(self.buttonExecute,0,1)
        self.gridLayoutExecute.addWidget(self.buttonAdd,0,0)

        self.mainLayout.addWidget(self.scroll)
        self.mainLayout.addLayout(self.gridLayoutExecute)
        self.mainLayout.addStretch(1)

        self.setLayout(self.mainLayout)

        self.buttonAdd.clicked.connect(self.addShot)
        self.buttonExecute.clicked.connect(self.executeShot)


        self.size = QSize(700,81)
        #self.setFixedSize(self.size)
        self.setFixedWidth(700)
        self.setWindowTitle('extract image')

    """add findFileUI widget to the layout"""
    def addShot(self):
        row = self.gridLayoutShot.rowCount()
        self.fileNb += 1
        shot = findFileUI(self)
        self.allShots.append(shot)
        self.gridLayoutShot.addWidget(shot,row,0)
        # change the height of the scroll to a maximum of 450
        if self.scroll.height() < 450:
            height = self.scroll.height() + 200
            self.scroll.setFixedHeight(height)
            self.setFixedHeight((self.height()+200))

    """extract all the data from each findFileUI widget and send them to the function convertImage"""
    def executeShot(self):
        res ={}
        #comandLine = 'echo "starting conversion";rez env a2 nuke -- nuke -t /s/prodanim/asterix2/_source_global/Software/Katana/Scripts/burnLutExr.py '
        for item in self.allShots:
            if item.returnCheck():
                dicExtract = item.extract()
                res.update(dicExtract)
        for key in res.keys():
            print 'creating: '+res[key]['fileOut']
            convertImageOIIO(res[key]['fileIn'],res[key]['fileOut'],res[key]['fileType'])

        #strRes =  '"' + str(res) + '"'
        #os.system(comandLine + strRes + ' ; echo "done"')


class findFileUI(QWidget):
    def __init__(self,parent,dodelete=True):
        super(findFileUI, self).__init__(parent)
        self.dodelete = dodelete
        self.master = parent
        self.initUI()

    def initUI(self):
        self.fileNb = self.master.fileNb
        self.mainQvboxLayout = QVBoxLayout()

        self.fileGroup = QGroupBox('file'+str(self.fileNb))
        self.fileGroup.setCheckable(True)
        self.fileGroup.setChecked(True)
        self.mainFileGridLayout = QGridLayout(self.fileGroup)


        self.fileInGridLayout = QGridLayout()
        self.fileInButton = QPushButton('file')
        self.fileInLabel = QLabel('in')
        self.fileInLabel.setAlignment(Qt.AlignCenter)
        self.fileInQLineEdit = QLineEdit()
        self.fileInGridLayout.addWidget(self.fileInButton,1,0)
        self.fileInGridLayout.addWidget(self.fileInLabel,0,1)
        self.fileInGridLayout.addWidget(self.fileInQLineEdit,1,1)

        self.fileOutGridLayout = QGridLayout()
        self.fileOutButton = QPushButton('path')
        self.fileOutButton.setToolTip('choose directory for output image')
        self.fileOutPathLabel = QLabel('out path')
        self.fileOutPathLabel.setAlignment(Qt.AlignCenter)
        self.fileOutPathLineEdit = QLineEdit()
        #self.fileOutPathLineEdit.setText(_OUTPATH_)
        self.fileOutPathLineEdit.setToolTip('path for frame output')
        self.fileOutNameLabel = QLabel('out name')
        self.fileOutNameLabel.setAlignment(Qt.AlignCenter)
        self.fileOutNameLineEdit = QLineEdit()
        self.fileOutNameLineEdit.setToolTip('name for the output frame')
        self.fileOutTypeLabel = QLabel('file type')
        self.fileOutTypeLabel.setAlignment(Qt.AlignCenter)
        self.fileOutTypComboBox = QComboBox()
        self.fileOutTypComboBox.addItem("tif")
        self.fileOutTypComboBox.addItem("jpg")
        self.fileOutGridLayout.addWidget(self.fileOutButton,1,0)
        self.fileOutGridLayout.addWidget(self.fileOutPathLabel,0,1)
        self.fileOutGridLayout.addWidget(self.fileOutPathLineEdit,1,1)
        self.fileOutGridLayout.addWidget(self.fileOutNameLabel,0,2)
        self.fileOutGridLayout.addWidget(self.fileOutNameLineEdit,1,2)
        self.fileOutGridLayout.addWidget(self.fileOutTypeLabel,0,3)
        self.fileOutGridLayout.addWidget(self.fileOutTypComboBox,1,3)

        self.mainFileGridLayout.addLayout(self.fileInGridLayout,0,0)
        self.mainFileGridLayout.addLayout(self.fileOutGridLayout,1,0)
        if self.dodelete:
            self.deleteButton = QPushButton('delete')
            self.mainFileGridLayout.addWidget(self.deleteButton,2,1)
            self.deleteButton.clicked.connect(self.deleteWidget)

        self.fileInButton.clicked.connect(self.findFile)
        self.fileOutTypComboBox.currentIndexChanged.connect(self.comboChanged)
        self.fileOutButton.clicked.connect(self.findDir)


        self.mainQvboxLayout.addWidget(self.fileGroup)
        self.mainQvboxLayout.addStretch(1)
        self.setLayout(self.mainQvboxLayout)


    def comboChanged(self):
        nameText = str(self.fileOutNameLineEdit.text())
        if nameText != '':
            fileNoType = nameText[:nameText.rfind('.')+1]
            newFileType = fileNoType +str(self.fileOutTypComboBox.currentText())
            self.fileOutNameLineEdit.setText(newFileType)

    def findDir(self):
        dirName = QFileDialog.getExistingDirectory(self,'Open directory','/s/prodanim/asterix2')
        self.fileOutPathLineEdit.setText(dirName+'/')

    def findFile(self):
        filename = QFileDialog.getOpenFileName(self, 'Open file', '/s/prodanim/asterix2',"Image files (*.exr)")
        filenameStr = str(filename)
        fileType = filenameStr[filenameStr.rfind('/')+1:].replace('exr',str(self.fileOutTypComboBox.currentText()))
        self.fileInQLineEdit.setText(filename)
        if self.fileOutPathLineEdit.text() == '':
            self.fileOutPathLineEdit.setText(filenameStr[:filenameStr.rfind('/')+1])
        self.fileOutNameLineEdit.setText(fileType)

    def extract(self):
        fileIn = str(self.fileInQLineEdit.text())
        fileOut = str(self.fileOutPathLineEdit.text()+self.fileOutNameLineEdit.text())
        fileType = str(self.fileOutTypComboBox.currentText())
        dictKey = str(self.fileGroup.title())
        res = {}
        res[dictKey]={'fileIn': fileIn, 'fileOut': fileOut, 'fileType': fileType}
        return res

    def returnCheck(self):
        return self.fileGroup.isChecked()

    def deleteWidget(self):
        tmp = self
        windowSize = self.master.mainLayout.sizeHint().height()
        self.master.allShots.remove(tmp)
        self.deleteLater()
        self.master.fileNb -= 1
        if len(self.master.allShots) < 3:
            height = self.master.scroll.height() -200
            self.master.scroll.setFixedHeight(height)
        if len(self.master.allShots) < 3:
            newheight = windowSize - 200
            self.master.setFixedHeight(newheight)

def convertImage(filename = '',fileOutName = '',format='tif'):
    # open the file
    inputFile = oiio.ImageInput.open(filename)
    # check if the input file is valid
    if not inputFile:
        print 'Could not open: "' + filename + '"'
        print '\tError: "', oiio.geterror()
        return
    # get the spec of the input file
    spec = inputFile.spec()
    nchans = spec.nchannels
    # read the image and return the pixels as array type
    pixels = inputFile.read_image(oiio.FLOAT)
    # check that the pixels are ok
    if not pixels:
        print 'Could not read:', inputFile.geterror()
        return
    inputFile.close() #we're done with the file at this point
    # open the OCIO config
    config = OCIO.GetCurrentConfig()
    """
    transform = OCIO.ColorSpaceTransform()
    transform.setSrc('srgb8')
    transform.setDst('Asterix2_Film')
    transform.setDirection(OCIO.Constants.TRANSFORM_DIR_INVERSE)
    processor = config.getProcessor(transform)
    """
    #"""
    # get the processor to transform from linear to Asterix2_Film space
    processor = config.getProcessor('linear','Asterix2_Film')
    #processor = config.getProcessor('linear','srgb8')

    #"""
    # apply the transform
    buf = processor.applyRGBA(pixels)
    # convert the list to an array type
    imgTrans = array('f',[0,0,0,0])
    imgTrans.fromlist(buf)
    # create an output image
    output = oiio.ImageOutput.create(fileOutName)
    # if tif format output as 16bit otherwise 8bit
    if format != 'tif':
        spec.set_format(oiio.UINT8)
    else:
        spec.set_format(oiio.UINT16)
    # open and write the data transformed
    output.open(fileOutName,spec,oiio.Create)
    output.write_image(imgTrans)
    output.close()
    print 'done'

def convertImageOIIO(filename = '',fileOutName = '',format='tif'):
    inFile = oiio.ImageBuf(filename)
    if not inFile.has_error :
        oiio.ImageBufAlgo.colorconvert(inFile,inFile,'linear','SK_Film')
        if format != 'tif':
            inFile.set_write_format(oiio.UINT16)
        else:
            inFile.set_write_format(oiio.UINT8)
        inFile.write(fileOutName)
        print 'done'
    if inFile.has_error :
        print "Error writing ",fileOutName, ": ", inFile.geterror()




ex =None
def BuildShotUI():

    global ex
    if ex is not None:
        ex.close()
    ex= shotUI()
    ex.show()

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    BuildShotUI()
    app.exec_()

if __name__ == '__main__':
    main()