#!/usr/bin/env python
# coding:utf-8
""":mod:`createMovie` -- dummy module
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
import sys,os,pprint
from sgtkLib import tkutil, tkm

_USER_ = os.environ['USER']
tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg


FFMPEG_ = "ffmpeg -loglevel error -f concat -safe 0 -r '24' -i "
#COMPFORMAT_ = " -pix_fmt yuv422p10 -vcodec dnxhd -b:v 175M -minrate 175M -maxrate 175M -strict -2 -y "
COMPFORMAT_ = " -codec:v copy -codec:a copy -strict -2  -y "
COMPNOSOUND_ = " -codec:v copy -an -strict -2 -y "
COMPSOUNDFORMAT_ = ' -map 0:v -map 1:a -codec:v copy -c:a libvorbis -strict -2 -y '
OTHERFORMAT_ = " -pix_fmt yuv411p -vcodec dnxhd -b:v 36M -minrate 36M -maxrate 36M -strict -2 -y "


class createMovieUI(QWidget):
    def __init__(self):
        super(createMovieUI, self).__init__()
        self.allShots = []
        self.initUI()

    def initUI(self):
        mainLayout =QVBoxLayout()
        self.gridLayoutShot = QGridLayout()
        self.gridLayoutExecute = QGridLayout()

        self.buttonExecute = QPushButton('execute')
        self.buttonExecute.setToolTip('create movie(s) for the chosen sequences')
        self.buttonAdd = QPushButton('Add')
        self.buttonAdd.setToolTip('add a new sequence')

        self.gridLayoutExecute.addWidget(self.buttonExecute,0,1)
        self.gridLayoutExecute.addWidget(self.buttonAdd,0,0)

        shot = sequenceUI()
        self.allShots.append(shot)
        self.gridLayoutShot.addWidget(shot,0,0)

        mainLayout.addLayout(self.gridLayoutShot)
        mainLayout.addLayout(self.gridLayoutExecute)

        self.setLayout(mainLayout)

        self.buttonAdd.clicked.connect(self.addShot)
        self.buttonExecute.clicked.connect(self.executeShot)

    def addShot(self):
        row = self.gridLayoutShot.rowCount()
        shot = sequenceUI()
        self.allShots.append(shot)
        #print self.allShots
        self.gridLayoutShot.addWidget(shot,row,0)

    def executeShot(self):
        for item in self.allShots:
            item.extract()


class sequenceUI(QWidget):
    def __init__(self):
        super(sequenceUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.mainGridLayout = QGridLayout()

        self.shotgunRvLayout = QHBoxLayout()

        self.shotgunGroup = QGroupBox('Shotgun')
        self.shotgunGroup.setObjectName('shotgun')
        self.shotgunGroup.setCheckable(True)
        self.shotgunGroup.setChecked(True)
        self.shotgunLayout = QHBoxLayout(self.shotgunGroup)

        self.sequenceQVboxLayout = QVBoxLayout()
        self.sequenceLabel = QLabel('sequence',self.shotgunGroup)
        self.sequenceLabel.setAlignment(Qt.AlignCenter)
        self.sequenceQLinrEdit = QLineEdit(self.shotgunGroup)
        self.sequenceQLinrEdit.setToolTip('Sequence number i.e: 1300')
        self.sequenceQVboxLayout.addWidget(self.sequenceLabel)
        self.sequenceQVboxLayout.addWidget(self.sequenceQLinrEdit)

        self.taskQVboxLayout = QVBoxLayout()
        self.taskLabel = QLabel('task')
        self.taskLabel.setAlignment(Qt.AlignCenter)
        self.taskComboBox = QComboBox(self.shotgunGroup)
        self.taskComboBox.addItem("compo_deliver")
        self.taskComboBox.addItem("anim_main")
        self.taskComboBox.addItem("editing_edt")
        self.taskQVboxLayout.addWidget(self.taskLabel)
        self.taskQVboxLayout.addWidget(self.taskComboBox)

        self.shotgunLayout.addLayout(self.sequenceQVboxLayout)
        self.shotgunLayout.addLayout(self.taskQVboxLayout)
        self.shotgunGroup.setLayout(self.shotgunLayout)

        self.rvSessionGroup = QGroupBox('rv session')
        self.rvSessionGroup.setObjectName('rv_session')
        self.rvSessionGroup.setCheckable(True)
        self.rvSessionGroup.setChecked(False)
        self.rvSessionLayout = QHBoxLayout()

        self.rvSessionLineEdit = QLineEdit(self.rvSessionGroup)
        self.rvSessionButton = QPushButton('File',self.rvSessionGroup)

        self.rvSessionLayout.addWidget(self.rvSessionLineEdit)
        self.rvSessionLayout.addWidget(self.rvSessionButton)
        self.rvSessionGroup.setLayout(self.rvSessionLayout)

        self.shotgunRvLayout.addWidget(self.shotgunGroup)
        self.shotgunRvLayout.addWidget(self.rvSessionGroup)

        self.outputGroup =QGroupBox('output')
        self.outputLayout = QHBoxLayout(self.outputGroup)

        self.outputPathLayout = QVBoxLayout()
        self.outputPathLabel = QLabel(self.outputGroup)
        self.outputPathLineEdit = QLineEdit(self.outputGroup)
        self.outputPathLayout.addWidget(self.outputPathLabel)
        self.outputPathLayout.addWidget(self.outputPathLineEdit)

        self.outputButtonLayout = QVBoxLayout()
        self.outputButtonLabel = QLabel('path',self.outputGroup)
        self.outputButton = QPushButton('dir',self.outputGroup)
        self.outputButtonLayout.addWidget(self.outputButtonLabel)
        self.outputButtonLayout.addWidget(self.outputButton)


        self.outputLineLayout = QVBoxLayout()
        self.outputLineLabel = QLabel('file name',self.outputGroup)
        self.outputFileLineEdit = QLineEdit(self.outputGroup)
        self.outputLineLayout.addWidget(self.outputLineLabel)
        self.outputLineLayout.addWidget(self.outputFileLineEdit)

        self.outTypeGroup = QGroupBox('output type')
        self.outTypeLayout = QHBoxLayout(self.outTypeGroup)
        self.outTypererenderCheck = QCheckBox('force render',self.outTypeGroup)
        self.outTypererenderCheck.setChecked(True)
        self.outTypeLeftCheck = QCheckBox('Left',self.outTypeGroup)
        self.outTypeLeftCheck.setChecked(True)
        self.outTypeLeftCheck.setAutoExclusive(True)
        self.outTypeRightCheck = QCheckBox('Right',self.outTypeGroup)
        self.outTypeRightCheck.setAutoExclusive(True)
        self.outTypeStereoCheck = QCheckBox('Stereo',self.outTypeGroup)
        self.outTypeStereoCheck.setAutoExclusive(True)
        self.outTypeLayout.addWidget(self.outTypererenderCheck)
        self.outTypeLayout.addWidget(self.outTypeLeftCheck)
        self.outTypeLayout.addWidget(self.outTypeRightCheck)
        self.outTypeLayout.addWidget(self.outTypeStereoCheck)


        self.outputLayout.addLayout(self.outputButtonLayout)
        self.outputLayout.addLayout(self.outputPathLayout)
        self.outputLayout.addLayout(self.outputLineLayout)
        self.outputLayout.addWidget(self.outTypeGroup)
        #self.outputGroup.setLayout(self.outputLineLayout)

        self.mainGridLayout.addLayout(self.shotgunRvLayout,0,0)
        #self.mainGridLayout.addWidget(self.rvSessionGroup,0,1)
        self.mainGridLayout.addWidget(self.outputGroup,1,0)

        self.rvSessionButton.clicked.connect(self.findRvSession)
        self.rvSessionGroup.clicked.connect(self.fileMode)
        self.shotgunGroup.clicked.connect(self.fileMode)
        self.outputButton.clicked.connect(self.findDir)
        self.sequenceQLinrEdit.editingFinished.connect(self.autoFillPath)

        self.setLayout(self.mainGridLayout)

    def findRvSession(self):
        dir = '/s/prods/captain/_sandbox/' +_USER_
        dlg = QFileDialog()
        #dlg.setFileMode(QFileDialog.AnyFile)
        filters = "Text files (*.txt);; rv (*.rv)"
        selected_filter= "rv (*.rv)"
        filename = dlg.getOpenFileName(self, " File dialog ", dir, filters, selected_filter)
        self.rvSessionLineEdit.setText(filename)

    def fileMode(self):
        checkValue = self.sender().isChecked()
        senderName = self.sender().objectName()
        if senderName == 'rv_session':
            self.shotgunGroup.setChecked(not checkValue)
        else:
            self.rvSessionGroup.setChecked(not checkValue)

    def findDir(self):
        dlg = QFileDialog()
        dir = '/s/prods/captain/_sandbox/' +_USER_
        dlg.setDirectory(dir)
        dlg.setFileMode(QFileDialog.DirectoryOnly)
        dlg.setOption(QFileDialog.ShowDirsOnly, True)
        if dlg.exec_():
           self.outputPathLineEdit.setText(dlg.selectedFiles()[0])

    def extract(self):
        shotgun = True
        path = str(self.outputPathLineEdit.text())
        if path == '':
            path = '/s/prods/captain/_sandbox/' +_USER_
        movFile = str(self.outputFileLineEdit.text())
        if movFile == '':
            movFile = 'donuts'
        outputPath = path + '/' + movFile
        if self.shotgunGroup.isChecked():
            shotgun = True
        else:
            shotgun = False
        if shotgun:
            seq = 's'+str(self.sequenceQLinrEdit.text()).zfill(4)
        else:
            seq = str(self.outputFileLineEdit.text())
        rvSession = str(self.rvSessionLineEdit.text())
        checkDir(path)
        if self.outTypeLeftCheck.isChecked():
            mode = 'left'
        else:
            mode = 'stereo'
        print 'starting'
        executeMovie(task = str(self.taskComboBox.currentText()), seq = seq, shotgun = shotgun, rvSession = rvSession,outputPath =path, mode = mode)

    def autoFillPath(self):
        if self.shotgunGroup.isChecked():
            seqName = 's'+str(self.sequenceQLinrEdit.text()).zfill(4)
            outPath = '/s/prods/captain/sequences/'+seqName+'/masters/mov'
            self.outputPathLineEdit.setText(QString(outPath))
            self.outputFileLineEdit.setText(seqName)


        # seq = str(self.sequenceQLinrEdit.text())
        # shot = str(self.shotLineEdit.text())
        # frames = str(self.frameLineEdit.text()).split(',')
        # task = str(self.taskComboBox.currentText())
        # offset = self.offsetCheckBox.isChecked()
        # exportImage(sequence = seq,shot = shot, frames = frames, task = task, offset = offset)

def checkDir(path = '/tmp'):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

ex =None
def BuildCreateMovieUI():

    global ex
    if ex is not None:
        ex.close()
    ex= createMovieUI()
    ex.show()



imageFilterCompo = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'name_is', 'GenericMovie'],
            #['published_file_type', 'name_is', 'DwaMovie'],
            ['published_file_type', 'name_is', 'CompoMovie'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
            #['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }
imageFilterDWA = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'name_is', 'GenericMovie'],
            ['published_file_type', 'name_is', 'DwaMovie'],
            #['published_file_type', 'name_is', 'CompoMovie'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
            #['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }
imageFilterOther = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'name_is', 'GenericMovie'],
            #['published_file_type', 'name_is', 'DwaMovie'],
            #['published_file_type', 'name_is', 'CompoMovie'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
            ['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }

def getShots(seq = 's0300',task = 'anim_main',mode ='left'):
    tmp = []
    shotList = []
    wavFileList =[]
    seqPath = '/s/prods/captain/sequences/'+seq+'/editings/'+seq+'_official/editingVersions/'
    lastDir = sorted(os.listdir(seqPath))[-1]
    lastDirPath = os.path.join(seqPath,lastDir)+'/cuts/'+lastDir+'_'
    publishDirPath = os.path.join(seqPath,lastDir)+'/publish'
    fileInDir = os.listdir(publishDirPath)
    for item in fileInDir:
        if item.endswith('.wav'):
            wavFileList.append(item)
    lastWavFile = publishDirPath +'/'+sorted(wavFileList)[-1]
    print lastWavFile


    if task == 'compo_deliver':
        filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'in',shotList],
        ['task', 'name_is', task],
        ['sg_tank_eye', 'is','left'],
        imageFilterCompo
        ]
    elif task == 'anim_main':
        filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'in',shotList],
        ['task', 'name_is', task],
        imageFilterDWA
        ]
    else:
        filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'in',shotList],
        ['task', 'name_is', task],
        imageFilterOther
        ]
    filterSequence = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['code', 'is', seq],
    ]
    # filterSound = [
    #     ['project', 'is', {'type':'Project', 'id':project.id}],
    #     ['entity.Shot.code', 'in',shotList],
    #     ['task', 'name_is', task],
    #     soundFilter
    # ]

    for v in sg.find('Sequence',filterSequence,['entity','shots']):
        tmp = v['shots']
    for item in tmp:
        shotName = item['name']
        if int(shotName[shotName.find('p')+1:]) < 10000:
            shotList.append( item['name'])



    res = {}
    for v in sg.find('PublishedFile', filters, ['code', 'entity','path','entity.Shot.sg_cut_order','entity.Shot.sg_cut_in','entity.Shot.sg_cut_out'], order=[{'field_name':'created_at','direction':'desc'}]):
        entityName = v['entity.Shot.sg_cut_order']
        if not entityName in res:
            res[entityName] ={}
            shotName = v['entity']['name']
            path = v['path']['local_path']
            soundPath = lastDirPath + shotName + '/publish/'
            soundFile = os.listdir(soundPath)[-1]
            sound = os.path.join(soundPath,soundFile)

            res[entityName]['shotname']=shotName
            res[entityName]['path']=path
            res[entityName]['cut_in'] = "{0:.4f}".format(float(v['entity.Shot.sg_cut_in']-100)/24.0)
            res[entityName]['cut_out'] = "{0:.4f}".format(float(v['entity.Shot.sg_cut_out']-100)/24.0)
            res[entityName]['sound'] = sound
            if mode == 'stereo':
                rightEyePath = ''
                imagePath = path[:path.rfind('/')]
                listFile = os.listdir(imagePath)
                rightPath = path.replace('-left','-right')
                rightPath = rightPath[:rightPath.rfind('-right')+6]
                rightPath = rightPath[rightPath.rfind('/')+1:]
                for item in listFile:
                    if item.find(rightPath) >= 0:
                        rightEyePath = os.path.join(imagePath,item)
                if rightEyePath != '':
                    res[entityName]['rightEye'] = rightEyePath
                else:
                    res[entityName]['rightEye'] = 'na'
    res['seqSound'] = lastWavFile




    return res

def createMovieSequence(task='anim_main',res={},shotgun =True, rvSession = '/s/prods/captain/_sandbox/duda/misc/s1280movie.rv',seq='s0300',outputPath ="/s/prods/captain/_sandbox/duda/misc", mode='left'):
    fileName = '/s/prods/captain/_sandbox/duda/misc/donuts.tx'
    fileNameb = '/s/prods/captain/_sandbox/duda/misc/donutsb.tx'
    if shotgun:
        doStereo = True
        leftMov = ''
        rightMov = ''
        orderKey=[]
        tmpListOutName = []
        commandLine = FFMPEG_
        fileTx = open(fileName,"w")
        pathLeft = outputPath+'/left'
        pathRight = outputPath+'/right'
        pathStereo = outputPath+'/stereo'
        checkDir(pathLeft)
        checkDir(pathRight)
        checkDir(pathStereo)
        for key in res.keys():
            if key == 'seqSound':
                continue
            else:
                orderKey.append(key)
        for item in sorted(orderKey):
            tmpOutName = '/s/prods/captain/_sandbox/duda/misc/'+res[item]['shotname']+'.mov'
            tmpListOutName.append(tmpOutName)
            shotLine = "ffmpeg -loglevel error -r 24 -i '"+ res[item]['path'] + "' -r 24 -i '"+res[item]['sound']+ "'" +COMPSOUNDFORMAT_ + tmpOutName
            print shotLine
            os.system(shotLine)
            pathTomov = tmpOutName
            fileTx.write("file '" + pathTomov+"'\n")
            # pathTomov = "file '" + res[item]['path']+ "'"
            # print "processing "+ res[item]['path']
            #fileTx.write(pathTomov+'\n')
        fileTx.close()
        if task == 'compo_deliver':
            commandLine += fileName + COMPFORMAT_
            #commandLine += fileName  + COMPFORMAT_
        else:
            commandLine += fileName + OTHERFORMAT_
        leftMov = pathLeft+'/'+seq+"_Movie.mov"
        commandLine += pathLeft+'/'+seq+"_Movie.mov"
        print 'rendering '+ pathLeft+'/'+seq+"_Movie.mov"
        os.system(commandLine)
        os.remove(fileName)
        for item in tmpListOutName:
            os.remove(item)

        if task == 'compo_deliver' and mode == 'stereo':
            tmpListOutName = []
            fileTx = open(fileNameb,"w")
            commandLine = FFMPEG_
            for item in sorted(orderKey):
                tmpOutName = '/s/prods/captain/_sandbox/duda/misc/'+res[item]['shotname']+'-right.mov'
                # tmpListOutName.append(tmpOutName)
                # shotLine = "ffmpeg -loglevel error -r 24 -i '"+ res[item]['rightEye'] + "' -t " + res[item]['cut_out'] +COMPNOSOUND_ + tmpOutName
                # print shotLine
                # os.system(shotLine)
                if res[item]['rightEye'] == 'na':
                    print 'missing stereo file for ' + res[item]['shotname']
                    doStereo = False
                    break
                pathTomov = "file '" + res[item]['rightEye']+ "'"
                fileTx.write(pathTomov+'\n')
            fileTx.close()
            if doStereo:
                rightMov = pathRight+'/'+seq+"-right_Movie.mov"
                commandLine += fileNameb + COMPNOSOUND_+ pathRight+'/'+seq+"-right_Movie.mov"
                print commandLine
                os.system(commandLine)
                os.remove(fileNameb)
                commandLine = 'ffmpeg -loglevel error -r 24 -i '+ leftMov + ' -r 24 -i '+ rightMov + "  -codec:v copy -codec:a copy -map 0:v -map 1:v -map 0:a -metadata stereo_mode=left_right -y "+ pathStereo + '/'+ seq+'_stereo_Movie.mov'
                print commandLine
                os.system(commandLine)
                # for item in tmpListOutName:
                #     os.remove(item)
    else:
        tmpListOutName = []
        commandLine = FFMPEG_
        fileTx = open(fileName,"w")
        with open(rvSession, "r") as ins:
            array = []
            for line in ins:
                if line.find("string movie =")>1:
                    movieFile =  "file '" + line[line.find('"')+1:].rstrip('\n').lstrip(' ').rstrip('"')+ "'"
                    array.append(movieFile)
            for filePath in array:
                fileTx.write(filePath+'\n')
        ins.close()
        fileTx.close()
        if task == 'compo_deliver':
            commandLine += fileName + COMPFORMAT_
        else:
            commandLine += fileName + OTHERFORMAT_
        commandLine += outputPath +'/'+seq+"_Movie.mov"
        print commandLine
        os.system(commandLine)
        os.remove(fileName)
        for path in tmpListOutName:
            os.remove(path)
    print "done"


def executeMovie(task = 'compo_precomp', seq = 's1300', shotgun = True, rvSession = '/s/prods/captain/_sandbox/duda/misc/s1280movie.rv',outputPath ="/s/prods/captain/_sandbox/duda/misc",mode ='left'):
    if shotgun:
        res = getShots(seq,task,mode)
    else:
        res ={}
    createMovieSequence(res=res,task=task,seq=seq,shotgun=shotgun,rvSession=rvSession,outputPath=outputPath,mode = mode)

def main():
    # seq = 's0300'
    # task = 'compo_deliver'
    # res = getShots(seq = seq,task = task, mode = 'stereo')
    # pprint.pprint(res)
    # executeMovie(res=res,task=task,seq=seq)
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    BuildCreateMovieUI()
    app.exec_()

if __name__ == '__main__':
    main()