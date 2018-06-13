#!/usr/bin/env python
# coding:utf-8
""":mod: contactSheetUI --- Module Title
=================================

   2018.06
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
#import nuke
#from nukeCore.nodes import sequenceGroup
import os, sys
from sgtkLib import tkutil, tkm
from PyQt4.QtGui import *
from PyQt4.QtCore import *

_USER_ = os.environ['USER']
_OUTIMAGEPATH_ = '/s/prodanim/asterix2/_sandbox/'+_USER_
_TASKLIST_=['compo_comp','light_precomp','light_prelight','art_reference','mattepaint_deliver']
tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

"""find the sequence in the project
   @all if true output also the sequence > 9000"""
def findAllSequence(all = False):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
    ]
    seqShots =[]
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','code','description']):
        seq = v['code']
        if all:
            if not seq in seqShots:
                seqShots.append(seq)
        else:
            if int(seq[seq.find('s')+1:]) <9000:
                if not seq in seqShots:
                    seqShots.append(seq)
            else:
                print  seq + ' will not be included'
    seqShots=sorted(seqShots)
    return seqShots

def findShotsInSequence(seq='s1300',dict=False):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['code','is',seq]
    ]
    res = {}
    seqShots =[]
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','shots']):
        if not 'Shots' in res:
            tmp = v['shots']
            for item in tmp:
                seqShots.append(item['name'])
            res['Shots'] = sorted(seqShots)
    if dict:
        return res
    else:
        return sorted(seqShots)

def createNukeFile(res = {}):
    import nuke
    from nukeCore.nodes import sequenceGroup

    allWriteNode = []
    for key in res.keys():
        if not os.path.isdir(res[key]['outDir']):
            os.makedirs(res[key]['outDir'])
        seq = res[key]['seq']
        task = res[key]['task']
        outFile = res[key]['fileOut']
        format = res[key]['fileType']
        showTask = res[key]['showTask']
        status = res[key]['status']
        name = res[key]['name']
        label= res[key]['showLabel']
        version = res[key]['version']
        cutOrder = res[key]['cutOrder']
        artist = res[key]['artist']
        outDir = res[key]['outDir']

        nbShots = len(findShotsInSequence(seq,False))
        intNb = nbShots/5
        floatNb = nbShots/5.0
        if floatNb-intNb > 0:
            intNb += 1
        sequenceGroupNode = sequenceGroup.create()
        sequenceGroupNode['sequence'].setValue(seq)
        sequenceGroupNode['task'].setValue(task)
        sequenceGroupNode['outputMode'].setValue('contactSheet')
        sequenceGroupNode['Rebuild'].execute()
        sequenceGroupNode['RowCol'].setValue([intNb, 5])
        sequenceGroupNode['Resolution'].setValue([5*2048,intNb*858])
        sequenceGroupNode['showName'].setValue(name)
        sequenceGroupNode['showStatus'].setValue(status)
        sequenceGroupNode['showTask'].setValue(showTask)
        sequenceGroupNode['showLabel'].setValue(label)
        sequenceGroupNode['showVersion'].setValue(version)
        sequenceGroupNode['showArtist'].setValue(artist)
        sequenceGroupNode['showCutOrder'].setValue(cutOrder)

        colorConvertNode = nuke.nodes.OCIOColorSpace(in_colorspace="Linear", out_colorspace="Lut")
        #colorConvertNode = nuke.nodes.OCIOColorSpace( out_colorspace="Lut")
        colorConvertNode.setInput(0,sequenceGroupNode)

        if format == 'jpg':
            writeNode = nuke.nodes.Write(name=seq + "WriteLutBurn", colorspace="linear", file_type="jpeg",_jpeg_sub_sampling="4:2:2", file=outFile)
            writeNode['_jpeg_quality'].setValue(0.75)
        else:
            writeNode = nuke.nodes.Write(name = seq + "WriteLutBurn", colorspace = "linear", file_type = "tiff",file =outFile)
            writeNode['datatype'].setValue('16 bit')
        writeNode['use_limit'].setValue(1)
        #writeNode['views'].setValue('left left')
        writeNode.setInput(0,colorConvertNode)
        allWriteNode.append(writeNode)
        nuke.scriptSave(outDir + seq + '_contactSheet.nk')
        # time.sleep(5)
        #nuke.execute(writeNode, 1, 1,1)
    masterNukeFile = '/tmp/tmpContactSheet.nk'
    nuke.scriptSave(masterNukeFile)
    fRange = nuke.FrameRanges('1-1')
    os.system('nuke -x '+masterNukeFile+' 1,1')
    os.remove(masterNukeFile)
    for key in res.keys():
        rmTmpFile = 'rm '+res[key]['outDir']+'tmp* '
        os.system(rmTmpFile)
    print 'done'
    #nuke.executeMultiple(tuple(allWriteNode),fRange,continueOnError=True)

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
        self.scroll.setFixedHeight(250)


        self.firstShot = findFileUI(self,False)
        self.allShots.append(self.firstShot)
        self.gridLayoutShot.addWidget(self.firstShot)
        self.buttonExecute = QPushButton('execute')
        self.buttonExecute.setToolTip('create the contactSheet(s)')
        self.buttonAdd = QPushButton('Add')
        self.buttonAdd.setToolTip('add a new contactSheet to be created')
        self.showLabelCheckBox = QCheckBox("show Label")
        self.showLabelCheckBox.setChecked(True)
        self.cutOrderCheckBox = QCheckBox("cut order")
        self.cutOrderCheckBox.setChecked(True)
        self.nameCheckBox = QCheckBox("name")
        self.nameCheckBox.setChecked(True)
        self.firstHBoxlayout = QHBoxLayout()
        self.firstHBoxlayout.addWidget(self.showLabelCheckBox)
        self.firstHBoxlayout.addWidget(self.cutOrderCheckBox)
        self.firstHBoxlayout.addWidget(self.nameCheckBox)
        self.taskCheckBox = QCheckBox("task")
        self.taskCheckBox.setChecked(True)
        self.versionCheckBox = QCheckBox("version")
        self.versionCheckBox.setChecked(True)
        self.statusCheckBox = QCheckBox("show status")
        self.statusCheckBox.setChecked(True)
        self.artistCheckBox = QCheckBox("artist")
        self.artistCheckBox.setChecked(True)
        self.secondHBoxlayout = QHBoxLayout()
        self.secondHBoxlayout.addWidget(self.versionCheckBox)
        self.secondHBoxlayout.addWidget(self.artistCheckBox)
        self.secondHBoxlayout.addWidget(self.statusCheckBox)
        self.secondHBoxlayout.addWidget(self.taskCheckBox)

        self.gridLayoutExecute.addLayout(self.firstHBoxlayout,0,0)
        self.gridLayoutExecute.addLayout(self.secondHBoxlayout, 0, 1)
        self.gridLayoutExecute.addWidget(self.buttonExecute,1,1)
        self.gridLayoutExecute.addWidget(self.buttonAdd,1,0)

        self.mainLayout.addWidget(self.scroll)
        self.mainLayout.addLayout(self.gridLayoutExecute)
        self.mainLayout.addStretch(1)

        self.setLayout(self.mainLayout)

        self.buttonAdd.clicked.connect(self.addShot)
        self.buttonExecute.clicked.connect(self.executeShot)


        self.size = QSize(900,81)
        #self.setFixedSize(self.size)
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
        for item in self.allShots:
            if item.returnCheck():
                dicExtract = item.extract()
                res.update(dicExtract)
        for key in res.keys():
            res[key]['artist']=self.artistCheckBox.isChecked()
            res[key]['status'] = self.statusCheckBox.isChecked()
            res[key]['version'] = self.versionCheckBox.isChecked()
            res[key]['name'] = self.nameCheckBox.isChecked()
            res[key]['cutOrder'] = self.cutOrderCheckBox.isChecked()
            res[key]['showLabel'] = self.showLabelCheckBox.isChecked()
            res[key]['showTask'] = self.taskCheckBox.isChecked()
        a = createNukeFile(res)
        print 'bla'




class findFileUI(QWidget):
    def __init__(self,parent,dodelete=True):
        super(findFileUI, self).__init__(parent)
        self.dodelete = dodelete
        self.master = parent
        self.initUI()

    def initUI(self):
        self.fileNb = self.master.fileNb
        self.mainQvboxLayout = QVBoxLayout()

        self.fileGroup = QGroupBox('contactSheet'+str(self.fileNb))
        self.fileGroup.setCheckable(True)
        self.fileGroup.setChecked(True)
        self.mainFileGridLayout = QGridLayout(self.fileGroup)


        self.fileInGridLayout = QGridLayout()
        self.seqInCombobox = QComboBox()
        self.seqInCombobox.setToolTip('sequence for contactSheet')
        self.listOfShots = findAllSequence()
        self.seqInCombobox.addItems(self.listOfShots)
        self.seqInLabel = QLabel('sequence')
        self.seqInLabel.setAlignment(Qt.AlignCenter)
        self.taskInLabel = QLabel('task')
        self.taskInLabel.setAlignment(Qt.AlignCenter)
        self.taskInCombobox = QComboBox()
        self.taskInCombobox.setToolTip('task used for contactSheet')
        self.taskInCombobox.addItems(_TASKLIST_)
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
        self.contactOutPathLineEdit.setText(_OUTIMAGEPATH_+'/contactSheet/')

        self.contactOutPathLineEdit.setToolTip('path for frame output')
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
        self.fileOutButton.clicked.connect(self.findDir)

        self.seqComboChanged()
        self.mainQvboxLayout.addWidget(self.fileGroup)
        self.mainQvboxLayout.addStretch(1)
        self.setLayout(self.mainQvboxLayout)

    def seqComboChanged(self):
        self.seqName = self.seqInCombobox.currentText()
        self.contactOutPathLineEdit.setText(_OUTIMAGEPATH_ + '/contactSheet/'+self.seqName+'/'+self.taskInCombobox.currentText()+'/')
        self.fileOutNameLineEdit.setText(self.seqName+'_contactSheet')
        self.comboChanged()

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

def testDict(listSeq=['s0180', 's0010', 's0200', 's0080']):
    nbContactSheet = 1
    res = {}
    for seq in listSeq:
        res['contatSheet' + str(nbContactSheet)] = {
            'status': True,
            'showTask': True,
            'task': 'compo_comp',
            'name': True,
            'seq': seq,
            'artist': True,
            'fileOut': '/s/prodanim/asterix2/_sandbox/duda/contactSheet/' + seq + '/compo_comp/' + seq + '_contactSheet.tif',
            'fileType': 'tif',
            'cutOrder': True,
            'showLabel': True,
            'version': True,
            'outDir': '/s/prodanim/asterix2/_sandbox/duda/contactSheet/' + seq + '/compo_comp/'
        }
        nbContactSheet = nbContactSheet + 1

    return res

def main():
    #createNukeFile(testDict())
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    BuildShotUI()
    app.exec_()

if __name__ == '__main__':
    main()