#!/usr/bin/env python
# coding:utf-8
""":mod: oiioContactSheetUI --- Module Title
=================================

   2018.08
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""


import os, sys, argparse
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import oiioContactSheet as pg
import tmpRes as testData

class shotUI(QWidget):
    def __init__(self):
        super(shotUI, self).__init__()
        self.allShots = []
        self.fileNb = 1
        self.allSeqName = []
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
        self.scroll.setFixedHeight(274)

        self.sequenceComboBox = QComboBox()
        #self.sequenceComboBox.addItems(pg.findAllSequence())
        self.sequenceComboBox.addItems(testData._TMPSEQ_)
        self.sequenceComboBox.setToolTip('sequence for contactSheet')
        self.taskComboBox = QComboBox()
        self.taskComboBox.addItems(pg._TASKLIST_)
        self.taskComboBox.setToolTip('task for contactSheet')
        self.firstShot = findFileUI(self,False)
        self.allShots.append(self.firstShot)
        self.gridLayoutShot.addWidget(self.firstShot)
        self.buttonExecute = QPushButton('create')
        self.buttonExecute.setToolTip('create the contactSheet(s)')
        self.buttonAdd = QPushButton('Add')
        self.buttonAdd.setToolTip('add a new contactSheet to be created')
        # self.cutInCheckBox = QCheckBox("cutIn")
        # self.cutInCheckBox.setChecked(False)
        # self.cutInCheckBox.setAutoExclusive(True)
        # self.cutInCheckBox.setToolTip('use in frame of cut as contactSheet frame')
        # self.cutMidCheckBox = QCheckBox("cutMid")
        # self.cutMidCheckBox.setChecked(True)
        # self.cutMidCheckBox.setAutoExclusive(True)
        # self.cutMidCheckBox.setToolTip('use mid frame of cut as contactSheet frame')
        # self.cutOutCheckBox = QCheckBox("cutOut")
        # self.cutOutCheckBox.setChecked(False)
        # self.cutOutCheckBox.setAutoExclusive(True)
        # self.cutOutCheckBox.setToolTip('use out frame of cut as contactSheet frame')
        # self.taskCheckBox = QCheckBox("task")
        # self.taskCheckBox.setChecked(True)
        self.firstHBoxlayout = QHBoxLayout()
        self.firstHBoxlayout.addWidget(self.sequenceComboBox)
        self.firstHBoxlayout.addWidget(self.taskComboBox)
        self.firstHBoxlayout.addWidget(self.buttonAdd)
        # self.firstHBoxlayout.addWidget(self.taskCheckBox)
        # self.versionCheckBox = QCheckBox("version")
        # self.versionCheckBox.setChecked(True)
        # self.statusCheckBox = QCheckBox("show status")
        # self.statusCheckBox.setChecked(True)
        # self.artistCheckBox = QCheckBox("artist")
        # self.artistCheckBox.setChecked(True)
        self.displatInRV = QCheckBox("RV")
        self.displatInRV.setChecked(True)
        # self.secondHBoxlayout = QHBoxLayout()
        # self.secondHBoxlayout.addWidget(self.versionCheckBox)
        # self.secondHBoxlayout.addWidget(self.artistCheckBox)
        # self.secondHBoxlayout.addWidget(self.statusCheckBox)
        # self.secondHBoxlayout.addWidget(self.displatInRV)

        self.gridLayoutExecute.addWidget(self.sequenceComboBox,0,0)
        self.gridLayoutExecute.addWidget(self.taskComboBox, 0, 1)
        self.gridLayoutExecute.addWidget(self.buttonAdd, 0, 2)
        # self.gridLayoutExecute.addLayout(self.secondHBoxlayout, 0, 1)
        self.gridLayoutExecute.addWidget(self.buttonExecute,1,2)
        self.gridLayoutExecute.addWidget(self.displatInRV,1,1)

        self.mainLayout.addWidget(self.scroll)
        self.mainLayout.addLayout(self.gridLayoutExecute)
        self.mainLayout.addStretch(1)

        self.setLayout(self.mainLayout)

        self.buttonAdd.clicked.connect(self.addShot)
        self.buttonExecute.clicked.connect(self.executeShot)


        self.size = QSize(900,81)
        self.setFixedWidth(900)
        self.setWindowTitle('contactSheet creator')

    """add findFileUI widget to the layout"""
    def addShot(self):
        row = self.gridLayoutShot.rowCount()
        self.fileNb += 1
        shot = findFileUI(self)
        self.allShots.append(shot)
        self.gridLayoutShot.addWidget(shot,row,0)
        # change the height of the scroll to a maximum of 450
        if self.scroll.height() < 550:
            height = self.scroll.height() + 275
            self.scroll.setFixedHeight(height)
            self.setFixedHeight((self.height()+275))

    """extract all the data from each findFileUI widget and send them to the function convertImage"""
    def executeShot(self):
        res ={}
        imageList = []
        for item in self.allShots:
            if item.returnCheck():
                dicExtract = item.extract()
                res.update(dicExtract)
        for key in res.keys():
            res[key]['artist']=self.artistCheckBox.isChecked()
            res[key]['status'] = self.statusCheckBox.isChecked()
            res[key]['version'] = self.versionCheckBox.isChecked()
            res[key]['name'] = self.cutOutCheckBox.isChecked()
            res[key]['cutOrder'] = self.cutMidCheckBox.isChecked()
            res[key]['showLabel'] = self.cutInCheckBox.isChecked()
            res[key]['showTask'] = self.taskCheckBox.isChecked()
            res[key]['nbShots'] = len(findShotsInSequence(res[key]['seq']))
            imageList.append(res[key]['fileOut'])
        #createNukeFile(res)
        #command = 'rez env asterix2Nuke -- nuke -t createContactSheet.py "'+ str(res)+'"'
        command = 'nuke -t /s/prodanim/asterix2/_source_global/Software/Nuke/scripts/createContactSheet.py "' + str(res) + '"'
        os.system(command)

        if self.displatInRV.isChecked():
            print 'opening RV'
            playInRv(imageList)

        print "you're a legend"


def playInRv(imagesList=[]):
    rvCommand = 'rv '
    for image in imagesList:
        rvCommand = rvCommand + ' ' + image
    #rvCommand = rvCommand + ' -pyeval "import rv.commands; rv.commands.stop(); print \'donuts\'"'
    os.system(rvCommand)
    #os.system("rvpush py-eval 'rv.commands.stop()'")

class findFileUI(QWidget):
    def __init__(self,parent,dodelete=True):
        super(findFileUI, self).__init__(parent)
        self.dodelete = dodelete
        self.master = parent
        self.initUI()

    def initUI(self):
        self.fileNb = self.master.fileNb
        self.mainQvboxLayout = QVBoxLayout()
        self.qwidgetList = []
        self.sequenceName = self.master.sequenceComboBox.currentText()
        self.task = self.master.taskComboBox.currentText()

        self.fileGroup = QGroupBox(self.sequenceName+' ' +self.task)
        self.fileGroup.setCheckable(True)
        self.fileGroup.setChecked(True)
        self.fileGroup.setFlat(False)
        self.wipQvboxLayout = QVBoxLayout(self.fileGroup)
        self.wid = QWidget()
        self.mainFileGridLayout = QGridLayout()
        self.wid.setLayout(self.mainFileGridLayout)
        self.wipQvboxLayout.addWidget(self.wid)


        self.fileInGridLayout = QGridLayout()
        self.seqInCombobox = QComboBox()
        self.seqInCombobox.setToolTip('sequence for contactSheet')
        self.qwidgetList.append(self.seqInCombobox)
        if len(self.master.allShots)==0:
            #self.listOfShots = pg.findAllSequence()
            self.listOfShots = testData._TMPSEQ_
            self.seqInCombobox.addItems(self.listOfShots)
            self.master.allSeqName=[str(self.seqInCombobox.itemText(i)) for i in range(self.seqInCombobox.count())]
        else:
            self.seqInCombobox.addItems(self.master.allSeqName)
        self.seqInLabel = QLabel('sequence')
        self.seqInLabel.setAlignment(Qt.AlignCenter)
        self.taskInLabel = QLabel('task')
        self.taskInLabel.setAlignment(Qt.AlignCenter)
        self.taskInCombobox = QComboBox()
        self.taskInCombobox.setToolTip('task used for contactSheet')
        self.taskInCombobox.addItems(pg._TASKLIST_)
        self.spacerItem = QSpacerItem(100, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.fileInGridLayout.addWidget(self.seqInCombobox,1,0)
        self.fileInGridLayout.addItem(self.spacerItem,0,1)
        self.fileInGridLayout.addWidget(self.seqInLabel,0,0)
        self.fileInGridLayout.addWidget(self.taskInLabel, 2, 0)
        self.fileInGridLayout.addWidget(self.taskInCombobox,3,0)

        self.fileOutGridLayout = QGridLayout()
        self.fileOutButton = QPushButton('path')
        self.fileOutButton.setToolTip('choose directory for output image')
        self.fileOutPathLabel = QLabel('out path')
        self.fileOutPathLabel.setAlignment(Qt.AlignCenter)
        self.contactOutPathLineEdit = QLineEdit()
        self.contactOutPathLineEdit.setText(pg._OUTPATH_)
        self.contactOutPathLineEdit.setToolTip('path for frame output')
        self.fileOutNameLabel = QLabel('out name')
        self.fileOutNameLabel.setAlignment(Qt.AlignCenter)
        self.fileOutNameLineEdit = QLineEdit()
        self.fileOutNameLineEdit.setToolTip('name for the output frame')
        self.qwidgetList.append(self.fileOutNameLineEdit)
        self.fileOutTypeLabel = QLabel('file type')
        self.fileOutTypeLabel.setAlignment(Qt.AlignCenter)
        self.fileOutTypComboBox = QComboBox()
        self.fileOutTypComboBox.addItems(pg._OUTPUTFORMAT_)
        self.fileOutGridLayout.addWidget(self.fileOutButton,1,0)
        self.fileOutGridLayout.addWidget(self.fileOutPathLabel,0,1)
        self.fileOutGridLayout.addWidget(self.contactOutPathLineEdit,1,1)
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

        self.fileOutTypComboBox.currentIndexChanged.connect(self.comboChanged)
        self.seqInCombobox.currentIndexChanged.connect(self.seqComboChanged)
        self.taskInCombobox.currentIndexChanged.connect(self.taskComboChanged)
        self.fileOutButton.clicked.connect(self.findDir)
        self.fileGroup.toggled.connect(self.test)

        self.seqComboChanged()
        self.mainQvboxLayout.addWidget(self.fileGroup)
        self.mainQvboxLayout.addStretch(1)
        self.setLayout(self.mainQvboxLayout)


    def test(self):
        if not self.fileGroup.isChecked():
            self.wid.setVisible(False)
            self.fileGroup.setFlat(True)
            height = self.master.scroll.height() - 197
            self.master.scroll.setFixedHeight(height)
            #if len(self.master.allShots) <3:
            self.master.setFixedHeight(self.master.height() - 197)
        else:
            self.wid.setVisible(True)
            self.fileGroup.setFlat(False)
            height = self.master.scroll.height() + 197
            self.master.scroll.setFixedHeight(height)
            #if len(self.master.allShots) <3:
            self.master.setFixedHeight(self.master.height() + 197)

    def seqComboChanged(self):
        self.seqName = self.seqInCombobox.currentText()
        self.contactOutPathLineEdit.setText(pg._OUTPATH_+self.seqName+'/'+self.taskInCombobox.currentText()+'/')
        self.fileOutNameLineEdit.setText(self.seqName+'_contactSheet')
        self.comboChanged()

    def taskComboChanged(self):
        self.taskName = self.taskInCombobox.currentText()
        self.contactOutPathLineEdit.setText(pg._OUTPATH_+self.seqInCombobox.currentText()+'/'+self.taskName+'/')
        # self.fileOutNameLineEdit.setText(self.seqInCombobox.currentText()+ '_contactSheet')
        # self.comboChanged()


    def comboChanged(self):
        nameText = str(self.fileOutNameLineEdit.text())
        if nameText.rfind('.') < 0:
            newFileType = self.fileOutNameLineEdit.text() + '.' + str(self.fileOutTypComboBox.currentText())
            self.fileOutNameLineEdit.setText(newFileType)
        else:
            fileNoType = nameText[:nameText.rfind('.') + 1]
            newFileType = fileNoType + str(self.fileOutTypComboBox.currentText())
            self.fileOutNameLineEdit.setText(newFileType)

    def findDir(self):
        dirName = QFileDialog.getExistingDirectory(self,'Open directory','/s/prodanim/asterix2')
        self.contactOutPathLineEdit.setText(dirName+'/')

    def extract(self):
        task = str(self.taskInCombobox.currentText())
        seq = str(self.seqInCombobox.currentText())

        fileOut = str(self.contactOutPathLineEdit.text()+self.fileOutNameLineEdit.text())
        outDir = str(self.contactOutPathLineEdit.text())
        fileType = str(self.fileOutTypComboBox.currentText())
        dictKey = str(self.fileGroup.title())
        res = {}
        res[dictKey]={'task': task, 'seq': seq, 'fileOut': fileOut, 'fileType': fileType, 'outDir': outDir}
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
            height = self.master.scroll.height() -275
            self.master.scroll.setFixedHeight(height)
        if len(self.master.allShots) < 3:
            newheight = windowSize - 275
            self.master.setFixedHeight(newheight)

ex =None
def BuildShotUI():

    global ex
    if ex is not None:
        ex.close()
    ex= shotUI()
    ex.show()

def main():
    # seq, useGui,task, format, noMeta = get_args()
    # if not useGui or len(seq) < 1:
    #     app = QApplication(sys.argv)
    #     app.setStyle(QStyleFactory.create("plastique"))
    #     BuildShotUI()
    #     app.exec_()
    # else:
    #     imagesList = commandLine(seq,task,format,noMeta)
    #     print 'opening RV'
    #     playInRv(imagesList)
    #     # rvCommand = 'rv'
    #     # for image in imagesList:
    #     #     rvCommand = rvCommand + ' ' + image
    #     # os.system(rvCommand)
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    BuildShotUI()
    app.exec_()

    print "you're a legend"

if __name__ == '__main__':
    main()