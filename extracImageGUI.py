#!/usr/bin/env python
# coding:utf-8
""":mod:`extracImageGUI` -- dummy module
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

# from PyQt4.QtGui import *
# from PyQt4.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
#from sgtkLib import tkutil, tkm
import os, errno, sys
import datetime

_USER_ = os.environ['USER']
_OUTPATH_ ="/s/prodanim/asterix2/_source_global/ExportImageJPG/" + _USER_


# tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
# sg = sgw._sg


# display widget for shots
class shotUI(QWidget):
    def __init__(self):
        super(shotUI, self).__init__()
        self.allShots = []
        self.initUI()

    def initUI(self):
        self.mainLayout =QVBoxLayout()
        self.gridLayoutShot = QGridLayout()
        self.gridLayoutExecute = QGridLayout()
        self.gridLayoutFileType = QVBoxLayout()
        self.gridLayoutFileType.setSizeConstraint(QLayout.SetFixedSize)
        self.widget = QWidget()
        self.widget.setLayout(self.gridLayoutShot)
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.widget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(0)

        self.shotCheckBox = QCheckBox('shot')
        self.shotCheckBox.setToolTip('shot mode')
        self.shotCheckBox.setAutoExclusive(True)
        self.shotCheckBox.setChecked(True)
        self.assetCheckBox = QCheckBox('asset')
        self.assetCheckBox.setToolTip('asset mode')
        self.assetCheckBox.setAutoExclusive(True)
        self.movieCheckBox = QCheckBox('file')
        self.movieCheckBox.setToolTip('file mode')
        self.movieCheckBox.setAutoExclusive(True)
        self.gridLayoutFileType.addWidget(self.shotCheckBox)
        self.gridLayoutFileType.addWidget(self.assetCheckBox)
        self.gridLayoutFileType.addWidget(self.movieCheckBox)


        self.buttonExecute = QPushButton('execute')
        self.buttonExecute.setToolTip('extract the frame(s) from the chosen sequences/shots')
        self.buttonAdd = QPushButton('Add')
        self.buttonAdd.setToolTip('add a new file from another shot/asset/movFile')

        self.gridLayoutExecute.addLayout(self.gridLayoutFileType,0,0)
        self.gridLayoutExecute.addWidget(self.buttonExecute,0,2)
        self.gridLayoutExecute.addWidget(self.buttonAdd,0,1)

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

    def addShot(self):
        shot = None
        # get the current number of row in the layout
        row = self.gridLayoutShot.rowCount()
        # determine which type of widget to add in function of the checkbox checked
        if self.shotCheckBox.isChecked():
            shot = findShotUI(self)
        elif self.assetCheckBox.isChecked():
            shot = findAssetUI(self)
        else:
            shot = findFileUI(self)
        # change the height of the scroll to a maximum of 450
        if self.scroll.height() < 450:
            height = self.scroll.height() + 150
            self.scroll.setFixedHeight(height)
            self.setFixedHeight((self.height()+150))
        # append the new widget to the list
        self.allShots.append(shot)
        # add the widget to the layout
        self.gridLayoutShot.addWidget(shot,row,0)

    def executeShot(self):
        # for all widget in the list call the extract method of that widget
        for item in self.allShots:
            item.extract()


class findFileUI(QWidget):
    """widget for finding .mov navigating through directories
        @file button find the file navigating in the directories
        @file lineEdit path of the file
        @frames frames number
    """
    def __init__(self,parent):
        super(findFileUI, self).__init__(parent)
        self.master = parent
        self.initUI()

    def initUI(self):
        self.mainQvboxLayout = QVBoxLayout()

        self.fileGroup = QGroupBox('file')
        self.fileGroup.setCheckable(True)
        self.fileGroup.setChecked(True)
        self.mainFileGridLayout = QGridLayout(self.fileGroup)


        self.fileQVboxLayout = QVBoxLayout()
        self.fileLabel = QLabel('file')
        self.fileQLineEdit = QLineEdit()
        self.fileQLineEdit.setToolTip('movie file from which to extract the frame(s)')
        self.fileQVboxLayout.addWidget(self.fileLabel)
        self.fileQVboxLayout.addWidget(self.fileQLineEdit)

        self.frameQVBoxLayout = QVBoxLayout()
        self.frameLabel = QLabel('Frames')
        self.frameLabel.setAlignment(Qt.AlignCenter)
        self.frameLineEdit = QLineEdit()
        self.frameLineEdit.setToolTip('frame to extract separated with a "," i.e: 20,30....')
        self.frameLineEdit.setToolTip('frame to extract separated with a "," i.e: 20,30....')
        self.validator = QRegExpValidator(QRegExp("[0-9,]*"))
        self.frameLineEdit.setValidator(self.validator)
        self.frameQVBoxLayout.addWidget(self.frameLabel)
        self.frameQVBoxLayout.addWidget(self.frameLineEdit)

        self.fileButtonQVboxLayout = QVBoxLayout()
        self.fileButton = QPushButton('file')
        self.fileButtonQVboxLayout.addStretch(1)
        self.fileButtonQVboxLayout.addWidget(self.fileButton)

        self.deleteButton = QPushButton('delete')

        self.mainFileGridLayout.addLayout(self.fileQVboxLayout,0,1)
        self.mainFileGridLayout.addLayout(self.frameQVBoxLayout,0,2)
        self.mainFileGridLayout.addLayout(self.fileButtonQVboxLayout,0,0)
        self.mainFileGridLayout.addWidget(self.deleteButton,1,2)

        self.fileButton.clicked.connect(self.findFile)
        self.deleteButton.clicked.connect(self.deleteWidget)

        self.mainQvboxLayout.addWidget(self.fileGroup)
        self.mainQvboxLayout.addStretch(1)
        self.setLayout(self.mainQvboxLayout)



    def findFile(self):
        """dialog to open file of type .mov"""
        filename = QFileDialog.getOpenFileName(self, 'Open file', '/s/prodanim/asterix2',"Image files (*.mov)")
        # fill fileQLineEdit with the string filename
        self.fileQLineEdit.setText(filename)

    def extract(self):
        """export the frame(s) chosen if the group is checked"""
        filename = str(self.fileQLineEdit.text())
        if self.returnCheck():
            frames = str(self.frameLineEdit.text()).split(',')
            exportImage(frames = frames, movFile = True, pathMovFile = filename)
        else:
            print 'no jpg created for: ' + filename[filename.rfind('/')+1:]

    def returnCheck(self):
        return self.fileGroup.isChecked()

    def deleteWidget(self):
        """delete the widget and resize the window"""
        tmp = self
        windowSize = self.master.mainLayout.sizeHint().height()
        self.master.allShots.remove(tmp)
        self.deleteLater()
        if len(self.master.allShots) < 3:
            height = self.master.scroll.height() -150
            self.master.scroll.setFixedHeight(height)
        if len(self.master.allShots) < 3:
            newheight = windowSize - 136
            self.master.setFixedHeight(newheight)



class findShotUI(QWidget):
    def __init__(self,parent):
        super(findShotUI, self).__init__(parent)
        self.master = parent
        self.initUI()

    def initUI(self):
        self.mainQvboxLayout = QVBoxLayout()

        self.shotGroup = QGroupBox('shot')
        self.shotGroup.setCheckable(True)
        self.shotGroup.setChecked(True)
        self.mainShotGridLayout = QGridLayout(self.shotGroup)

        self.sequenceQVboxLayout = QVBoxLayout()
        self.sequenceLabel = QLabel('sequence')
        self.sequenceLabel.setAlignment(Qt.AlignCenter)
        self.sequenceQLineEdit = QLineEdit()
        self.sequenceQLineEdit.setToolTip('Sequence number i.e: 1300')
        self.sequenceValidator = QRegExpValidator(QRegExp("[0-9]*"))
        self.sequenceQLineEdit.setValidator(self.sequenceValidator)
        self.sequenceQVboxLayout.addWidget(self.sequenceLabel)
        self.sequenceQVboxLayout.addWidget(self.sequenceQLineEdit)
        self.sequenceQVboxLayout.addStretch(1)

        self.shotQVBoxLayout = QVBoxLayout()
        self.shotLabel = QLabel('shot')
        self.shotLabel.setAlignment(Qt.AlignCenter)
        self.shotLineEdit = QLineEdit()
        self.shotLineEdit.setToolTip('shot number i.e: 20')
        self.shotValidator = QRegExpValidator(QRegExp("[0-9]*"))
        self.shotLineEdit.setValidator(self.shotValidator)
        self.shotQVBoxLayout.addWidget(self.shotLabel)
        self.shotQVBoxLayout.addWidget(self.shotLineEdit)
        self.shotQVBoxLayout.addStretch(1)

        self.frameQVBoxLayout = QVBoxLayout()
        self.frameLabel = QLabel('Frames')
        self.frameLabel.setAlignment(Qt.AlignCenter)
        self.frameLineEdit = QLineEdit()
        self.frameLineEdit.setToolTip('frame to extract separated with a "," i.e: 20,30....')
        self.validator = QRegExpValidator(QRegExp("[0-9,]*"))
        self.frameLineEdit.setValidator(self.validator)
        self.frameQVBoxLayout.addWidget(self.frameLabel)
        self.frameQVBoxLayout.addWidget(self.frameLineEdit)
        self.frameQVBoxLayout.addStretch(1)

        self.offsetBoxLayout = QVBoxLayout()
        self.offsetLabel = QLabel('Use Offset')
        self.offsetLabel.setAlignment(Qt.AlignCenter)
        self.offsetCheckBox = QCheckBox()
        self.offsetCheckBox.setToolTip('check if the frame chosen has shot start at 101 instead of 1')
        self.offsetBoxLayout.addWidget(self.offsetLabel)
        self.offsetBoxLayout.addWidget(self.offsetCheckBox)
        self.offsetBoxLayout.addStretch(1)

        self.taskQVboxLayout = QVBoxLayout()
        self.taskLabel = QLabel('task')
        self.taskLabel.setAlignment(Qt.AlignCenter)
        self.taskComboBox = QComboBox()
        self.taskComboBox.addItem("editing_edt")
        self.taskComboBox.addItem("layout_base")
        self.taskComboBox.addItem("confo_layout")
        self.taskComboBox.addItem("anim_main")
        self.deleteButton = QPushButton('delete')
        self.taskQVboxLayout.addWidget(self.taskLabel)
        self.taskQVboxLayout.addWidget(self.taskComboBox)
        self.taskQVboxLayout.addWidget(self.deleteButton)

        self.mainShotGridLayout.addLayout(self.sequenceQVboxLayout,0,0)
        self.mainShotGridLayout.addLayout(self.shotQVBoxLayout,0,1)
        self.mainShotGridLayout.addLayout(self.frameQVBoxLayout,0,2)
        self.mainShotGridLayout.addLayout(self.offsetBoxLayout,0,3)
        self.mainShotGridLayout.addLayout(self.taskQVboxLayout,0,4)

        #self.taskComboBox.currentIndexChanged.connect(self.setOffset)
        self.deleteButton.clicked.connect(self.deleteWidget)
        self.shotLineEdit.editingFinished.connect(self.setShotName)

        self.mainQvboxLayout.addWidget(self.shotGroup)
        self.mainQvboxLayout.addStretch(1)

        self.setLayout(self.mainQvboxLayout)

    def setOffset(self):
        if self.taskComboBox.currentText() == 'anim_main':
            self.offsetCheckBox.setChecked(True)
        else:
            self.offsetCheckBox.setChecked(False)

    def setShotName(self):
        if self.sequenceQLineEdit.text() != '' and self.shotLineEdit.text() != '':
            self.shotGroup.setTitle('s'+str(self.sequenceQLineEdit.text()).zfill(4)+'_p'+str(self.shotLineEdit.text()).zfill(4))

    def extract(self):
        seq = str(self.sequenceQLineEdit.text())
        shot = str(self.shotLineEdit.text())
        frames = str(self.frameLineEdit.text()).split(',')
        task = str(self.taskComboBox.currentText())
        if self.returnCheck():
            offset = self.offsetCheckBox.isChecked()
            exportImage(sequence = seq,shot = shot, frames = frames, task = task, offset = offset)
        else:
            print 'no jpg created for: ' + 's'+ seq.zfill(4) + '_p'+ shot.zfill(4)

    def returnCheck(self):
        return self.shotGroup.isChecked()

    def deleteWidget(self):
        """delete the widget and resize the window"""
        tmp = self
        windowSize = self.master.mainLayout.sizeHint().height()
        self.master.allShots.remove(tmp)
        self.deleteLater()
        if len(self.master.allShots) < 3:
            height = self.master.scroll.height() -150
            self.master.scroll.setFixedHeight(height)
        if len(self.master.allShots) < 3:
            newheight = windowSize - 136
            self.master.setFixedHeight(newheight)

class findAssetUI(QWidget):
    def __init__(self,parent):
        super(findAssetUI, self).__init__(parent)
        self.master = parent
        self.initUI()

    def initUI(self):
        self.mainQvboxLayout = QVBoxLayout()

        self.assetGroup = QGroupBox('asset')
        self.assetGroup.setCheckable(True)
        self.assetGroup.setChecked(True)
        self.mainShotGridLayout = QGridLayout(self.assetGroup)

        self.assetQVBoxLayout = QVBoxLayout()
        self.assetLabel = QLabel('Asset')
        self.assetLabel.setAlignment(Qt.AlignCenter)
        self.assetLineEdit = QLineEdit()
        self.assetLineEdit.setToolTip('asset name i.e: asterix')
        self.assetQVBoxLayout.addWidget(self.assetLabel)
        self.assetQVBoxLayout.addWidget(self.assetLineEdit)
        self.assetQVBoxLayout.addStretch(1)

        self.frameQVBoxLayout = QVBoxLayout()
        self.frameLabel = QLabel('Frames')
        self.frameLabel.setAlignment(Qt.AlignCenter)
        self.frameLineEdit = QLineEdit()
        self.frameLineEdit.setToolTip('frame to extract separated with a "," i.e: 20,30....')
        self.validator = QRegExpValidator(QRegExp("[0-9,]*"))
        self.frameLineEdit.setValidator(self.validator)
        self.frameQVBoxLayout.addWidget(self.frameLabel)
        self.frameQVBoxLayout.addWidget(self.frameLineEdit)
        self.frameQVBoxLayout.addStretch(1)

        self.offsetBoxLayout = QVBoxLayout()
        self.offsetLabel = QLabel('Use Offset')
        self.offsetLabel.setAlignment(Qt.AlignCenter)
        self.offsetCheckBox = QCheckBox()
        self.offsetCheckBox.setToolTip('check if the frame chosen has shot start at 101 instead of 1')
        self.offsetBoxLayout.addWidget(self.offsetLabel)
        self.offsetBoxLayout.addWidget(self.offsetCheckBox)
        self.offsetBoxLayout.addStretch(1)

        self.taskQVboxLayout = QVBoxLayout()
        self.taskLabel = QLabel('task')
        self.taskLabel.setAlignment(Qt.AlignCenter)
        self.taskComboBox = QComboBox()
        self.taskComboBox.addItem("model_base")
        self.taskComboBox.addItem("model_hi")
        self.taskComboBox.addItem("hair_surface")
        self.taskComboBox.addItem("surface_surfacing")
        self.deleteButton = QPushButton('delete')
        self.taskQVboxLayout.addWidget(self.taskLabel)
        self.taskQVboxLayout.addWidget(self.taskComboBox)
        self.taskQVboxLayout.addWidget(self.deleteButton)

        self.taskComboBox.currentIndexChanged.connect(self.setOffset)
        self.deleteButton.clicked.connect(self.deleteWidget)

        self.mainShotGridLayout.addLayout(self.assetQVBoxLayout,0,0)
        self.mainShotGridLayout.addLayout(self.frameQVBoxLayout,0,2)
        self.mainShotGridLayout.addLayout(self.offsetBoxLayout,0,3)
        self.mainShotGridLayout.addLayout(self.taskQVboxLayout,0,4)

        self.mainQvboxLayout.addWidget(self.assetGroup)
        self.mainQvboxLayout.addStretch(1)

        self.setLayout(self.mainQvboxLayout)

    def setOffset(self):
        if self.taskComboBox.currentText() == 'hair_surface' or self.taskComboBox.currentText() == 'surface_surfacing':
            self.offsetCheckBox.setChecked(True)
        else:
            self.offsetCheckBox.setChecked(False)

    def extract(self):
        #seq = str(self.sequenceQLineEdit.text())
        asset= str(self.assetLineEdit.text())
        frames = str(self.frameLineEdit.text()).split(',')
        task = str(self.taskComboBox.currentText())
        if self.returnCheck() :
            offset = self.offsetCheckBox.isChecked()
            exportImage(frames = frames, task = task, offset = offset,assetFile=True,asset=asset)
        else:
            print 'no jpg created for :\n' + asset + ' frame ' + str(self.frameLineEdit.text()) + ' for the task ' + task

    def returnCheck(self):
        return self.assetGroup.isChecked()

    def deleteWidget(self):
        """delete the widget and resize the window"""
        tmp = self
        windowSize = self.master.mainLayout.sizeHint().height()
        self.master.allShots.remove(tmp)
        self.deleteLater()
        if len(self.master.allShots) < 3:
            height = self.master.scroll.height() -150
            self.master.scroll.setFixedHeight(height)
        if len(self.master.allShots) < 3:
            newheight = windowSize - 136
            self.master.setFixedHeight(newheight)

ex =None
def BuildShotUI():
    global ex
    if ex is not None:
        ex.close()
    ex= shotUI()
    ex.show()

imageFilterConfoLayout= {
        'filter_operator' : 'all',
        'filters':[
            ['tag_list', 'name_is','primary'],
            ['published_file_type', 'name_is', 'QCRmovie'],
        ]
    }

imageFilterAsset = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'TurntableMovie'],
        ]
    }
imageFilterLayoutBase = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'name_is', 'GenericMovie'],
            ['published_file_type', 'name_is', 'PlayblastMovie'],
            #['published_file_type', 'name_is', 'CompoMovie'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
            #['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }

imageFilterEditing = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'name_is', 'GenericMovie'],
            #['published_file_type', 'name_is', 'DwaMovie'],
            ['published_file_type', 'name_is', 'PlayblastMovie'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
            #['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }

def findSingleShot(shot = 's1300_p00300', taskname = 'compo_precomp'):
    """find a single shot in SG
        @shot shot number
        @task task name
    """

    #call the filter type in function of the task
    filterType = imFilter(taskname)
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'is', shot],
        ['task', 'name_is', taskname],
        filterType
    ]
    res = []
    # extract the shot from SG and put it in a dictionary
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type'], order=[{'field_name':'version_number','direction':'desc'}]):
        res.append(v['path']['local_path'])
    return res

def checkDir(path = '/tmp'):
    """check if the directory path exist if not create it"""
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

# select the proper image filter
def imFilter(taskname = 'compo_precomp'):
    filterDict = {'editing_edt': imageFilterEditing,
                  'layout_base': imageFilterLayoutBase,
                  'confo_layout':imageFilterConfoLayout,
                  'anim_main': imageFilterLayoutBase,
                  'model_base':imageFilterAsset,
                  'model_hi':imageFilterAsset,
                  'hair_surface':imageFilterAsset,
                  'surface_surfacing':imageFilterAsset
                  }
    return filterDict[taskname]


# find a single asset .mov
def findSingleAsset(asset = 'asterix', taskname = 'hair_surface'):
    filterType = imFilter(taskname)
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Asset.code', 'is', asset],
        ['task', 'name_is', taskname],
        imageFilterAsset
    ]
    res = []
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type'], order=[{'field_name':'version_number','direction':'desc'}]):
        res.append(v['path']['local_path'])

    return res

def exportImage(sequence = '1300',shot = '300', frames = [10,20,30], task = 'compo_precomp',offset = False,assetFile = False,asset = 'asterix', movFile = False, pathMovFile = ''):
    """ main function to extract the image(s), use ffmpeg
        @sequence sequence number
        @shot shot number
        @frames frame(s) to extract in a list
        @task task from where to find the movie file
        @offset True/False sometime the movie file start at 101 instead of 1 if it's the case offset need to be on True
        @assetFile True/False if we are in asset mode
        @asset name of the asset
        @movFile True/False if we are in movFile mode
        @pathMovFile path of the movie file
    """
    path =[]
    today = _OUTPATH_ + '/'+datetime.date.today().strftime("%y%m%d") + '_exportImage/'   #today date in format day,month,year(only 2 last number of the year)
    if not movFile:
        # if we're in shot mode create the proper shot name and find the shot in SG
        if assetFile == False:
            if sequence.find('s') < 0:
                sequence = 's'+sequence.zfill(4)
            else:
                sequence = sequence.zfill(4)
            shot = sequence +'_p'+ shot.zfill(4)
            path = findSingleShot(shot = shot,taskname=task)
            today = _OUTPATH_ + '/'+datetime.date.today().strftime("%y%m%d") + '_exportImage/'+sequence+'/'
        # in asset mode find the asset in SG
        else:
            path = findSingleAsset(asset,task)
    else:
        path.append(pathMovFile)

    # create the path for the export directory, check if it exist if not create it
    checkDir(today)

    # if the shot or asset return a path
    if len(path) > 0:
        for frame in frames:
            print frame
            frameNb = '0'  #real frame number
            # if the shot start at 101 instead of 1
            if offset:
                # particular case for the task surface_surfacing and hair_surface who's .mov start at 1001
                if task == 'surface_surfacing' or task == 'hair_surface':
                    frameConvert = "{0:.5f}".format((float(frame)-999.0)/24.0)
                else:
                    frameConvert = "{0:.5f}".format((float(frame)-99.0)/24.0)
                frameNb = str(int(frame))
            else:
                frameConvert = "{0:.5f}".format((float(frame)-1)/24)
                if movFile:
                    frameNb = str(int(frame))
                else:
                    frameNb = str(int(frame)+100)
            # if we are in asset mode put the name of the asset name instead of the shot name
            if assetFile:
                shot = asset
            if movFile:
                shot = 'file'
            commandLine = 'ffmpeg -y -loglevel error -ss ' + frameConvert + ' -i ' + path[0] +  ' -vframes 1 -f image2 ' + today + shot + '_f'+frameNb + '.jpg'
        #commandLine = '/s/apps/lin/rv/current/bin/rvio [ '+ path[0] + ' -in ' + frame + ' -out ' + frame + ' ]'+ ' -o ' + output + '.jpg'
            os.system(commandLine)
            print "creating : "+today + shot + '_f'+frameNb + '.jpg'
    else:
        print shot + " doesn't exist"


def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    BuildShotUI()
    app.exec_()

if __name__ == '__main__':
    main()
