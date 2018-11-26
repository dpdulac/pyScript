


# import sys
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
#
# class menudemo(QMainWindow):
#    def __init__(self, parent = None):
#       super(menudemo, self).__init__(parent)
#
#       layout = QHBoxLayout()
#       bar = self.menuBar()
#       file = bar.addMenu("File")
#       file.addAction("New")
#
#       save = QAction("Save",self)
#       save.setShortcut("Ctrl+S")
#       file.addAction(save)
#
#       edit = file.addMenu("Edit")
#       edit.addAction("copy")
#       edit.addAction("paste")
#
#       quit = QAction("Quit",self)
#       file.addAction(quit)
#       quit.triggered.connect(self.processtrigger)
#       self.setLayout(layout)
#       self.setWindowTitle("menu demo")
#
#    def processtrigger(self):
#       print self.sender().text()+" is triggered"
#
# def main():
#    app = QApplication(sys.argv)
#    ex = menudemo()
#    ex.show()
#    sys.exit(app.exec_())
#
# if __name__ == '__main__':
#    main()

# from Katana import QT4FormWidgets, QtGui
#
# dataSource = {
#     'Passes' : 'bty',
#     'String' : 'hello',
#     'Number' : 0,
#     'Build Template' : int(True),
#     'Favorite Color' : 'Red',
#     'color': (1,1,1),
#     '__childOrder' : ['String', 'Number', 'Passes', 'Build Template',
# 'Favorite Color','color'],
#     '__childHints' : {
#         'Build Template' : {
#             'widget' : 'checkBox',
#         },
#         'String' : {
#             'help' : """This is <strong>important</strong>."""
#         },
#         'Number' : {
#             'constant' : True,
#             'int' : True,
#             'min' : 1,
#         },
#         'Favorite Color' : {
#             'widget' : 'popup',
#             'options' : ['Red', 'Orange', 'Yellow', 'Green', 'Blue',
# 'Eggplant'],
#         },
#         'Passes' : {
#             'widget' : 'capsule',
#             'exclusive' : False,
#             'delimiter' : ' ',
#             'options' : ['bty', 'ambocc', 'shd', 'dshd'],
#         },
#         'color' : {
#             'widget' : 'color',
#         },
#     }
# }
#
# d = QT4FormWidgets.FormDialog(dataSource, title='This is my Dialog')
#
# if d.exec_() == QtGui.QDialog.Accepted:
#     message = 'Accepted\n\n'
#     for keyName, value in dataSource.iteritems():
#         if keyName.startswith('__'):
#             continue
#         message += ("%s:\t'%s'\n" % (keyName, value)) # ex:
# else:
#     message = 'Canceled'
# dataSource['Number']
#
#
# QtGui.QMessageBox.information(None, 'Message', message)
#
# from PyQt4 import QtCore, QtGui
#
#
# class DragButton(QtGui.QPushButton):
#
#     def mousePressEvent(self, event):
#         self.__mousePressPos = None
#         self.__mouseMovePos = None
#         if event.button() == QtCore.Qt.LeftButton:
#             self.__mousePressPos = event.globalPos()
#             self.__mouseMovePos = event.globalPos()
#
#         super(DragButton, self).mousePressEvent(event)
#
#     def mouseMoveEvent(self, event):
#         if event.buttons() == QtCore.Qt.LeftButton:
#             # adjust offset from clicked point to origin of widget
#             currPos = self.mapToGlobal(self.pos())
#             globalPos = event.globalPos()
#             diff = globalPos - self.__mouseMovePos
#             newPos = self.mapFromGlobal(currPos + diff)
#             self.move(newPos)
#
#             self.__mouseMovePos = globalPos
#
#         super(DragButton, self).mouseMoveEvent(event)
#
#     def mouseReleaseEvent(self, event):
#         if self.__mousePressPos is not None:
#             moved = event.globalPos() - self.__mousePressPos
#             if moved.manhattanLength() > 3:
#                 event.ignore()
#                 return
#
#         super(DragButton, self).mouseReleaseEvent(event)
#
# def clicked():
#     print "click as normal!"
#
# if __name__ == "__main__":
#     app = QtGui.QApplication([])
#     w = QtGui.QWidget()
#     w.resize(800,600)
#
#     button = DragButton("Drag", w)
#     button.clicked.connect(clicked)
#
#     w.show()
#     app.exec_()
# import sip
# sip.setapi('QString', 2)
# sip.setapi('QVariant', 2)
# from PyQt4 import QtCore, QtGui
#
#
# class MainWindow(QtGui.QMainWindow):
#     MaxRecentFiles = 5
#     windowList = []
#
#     def __init__(self):
#         super(MainWindow, self).__init__()
#
#         self.recentFileActs = []
#
#         self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
#
#         self.textEdit = QtGui.QTextEdit()
#         self.setCentralWidget(self.textEdit)
#
#         self.createActions()
#         self.createMenus()
#         self.statusBar()
#
#         self.setWindowTitle("Recent Files")
#         self.resize(400, 300)
#
#     def newFile(self):
#         other = MainWindow()
#         MainWindow.windowList.append(other)
#         other.show()
#
#     def open(self):
#         fileName = QtGui.QFileDialog.getOpenFileName(self)
#         if fileName:
#             self.loadFile(fileName)
#
#     def save(self):
#         if self.curFile:
#             self.saveFile(self.curFile)
#         else:
#             self.saveAs()
#
#     def saveAs(self):
#         fileName = QtGui.QFileDialog.getSaveFileName(self)
#         if fileName:
#             self.saveFile(fileName)
#
#     def openRecentFile(self):
#         action = self.sender()
#         if action:
#             self.loadFile(action.data())
#
#     def about(self):
#         QtGui.QMessageBox.about(self, "About Recent Files",
#                 "The <b>Recent Files</b> example demonstrates how to provide "
#                 "a recently used file menu in a Qt application.")
#
#     def createActions(self):
#         self.newAct = QtGui.QAction("&New", self,
#                 shortcut=QtGui.QKeySequence.New,
#                 statusTip="Create a new file", triggered=self.newFile)
#
#         self.openAct = QtGui.QAction("&Open...", self,
#                 shortcut=QtGui.QKeySequence.Open,
#                 statusTip="Open an existing file", triggered=self.open)
#
#         self.saveAct = QtGui.QAction("&Save", self,
#                 shortcut=QtGui.QKeySequence.Save,
#                 statusTip="Save the document to disk", triggered=self.save)
#
#         self.saveAsAct = QtGui.QAction("Save &As...", self,
#                 shortcut=QtGui.QKeySequence.SaveAs,
#                 statusTip="Save the document under a new name",
#                 triggered=self.saveAs)
#
#         for i in range(MainWindow.MaxRecentFiles):
#             self.recentFileActs.append(
#                     QtGui.QAction(self, visible=False,
#                             triggered=self.openRecentFile))
#
#         self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
#                 statusTip="Exit the application",
#                 triggered=QtGui.qApp.closeAllWindows)
#
#         self.aboutAct = QtGui.QAction("&About", self,
#                 statusTip="Show the application's About box",
#                 triggered=self.about)
#
#         self.aboutQtAct = QtGui.QAction("About &Qt", self,
#                 statusTip="Show the Qt library's About box",
#                 triggered=QtGui.qApp.aboutQt)
#
#     def createMenus(self):
#         self.fileMenu = self.menuBar().addMenu("&File")
#         self.fileMenu.addAction(self.newAct)
#         self.fileMenu.addAction(self.openAct)
#         self.fileMenu.addAction(self.saveAct)
#         self.fileMenu.addAction(self.saveAsAct)
#         self.separatorAct = self.fileMenu.addSeparator()
#         for i in range(MainWindow.MaxRecentFiles):
#             self.fileMenu.addAction(self.recentFileActs[i])
#         self.fileMenu.addSeparator()
#         self.fileMenu.addAction(self.exitAct)
#         self.updateRecentFileActions()
#
#         self.menuBar().addSeparator()
#
#         self.helpMenu = self.menuBar().addMenu("&Help")
#         self.helpMenu.addAction(self.aboutAct)
#         self.helpMenu.addAction(self.aboutQtAct)
#
#     def loadFile(self, fileName):
#         file = QtCore.QFile(fileName)
#         if not file.open( QtCore.QFile.ReadOnly | QtCore.QFile.Text):
#             QtGui.QMessageBox.warning(self, "Recent Files",
#                     "Cannot read file %s:\n%s." % (fileName, file.errorString()))
#             return
#
#         instr = QtCore.QTextStream(file)
#         QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
#         self.textEdit.setPlainText(instr.readAll())
#         QtGui.QApplication.restoreOverrideCursor()
#
#         self.setCurrentFile(fileName)
#         self.statusBar().showMessage("File loaded", 2000)
#
#     def saveFile(self, fileName):
#         file = QtCore.QFile(fileName)
#         if not file.open( QtCore.QFile.WriteOnly | QtCore.QFile.Text):
#             QtGui.QMessageBox.warning(self, "Recent Files",
#                     "Cannot write file %s:\n%s." % (fileName, file.errorString()))
#             return
#
#         outstr = QtCore.QTextStream(file)
#         QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
#         outstr << self.textEdit.toPlainText()
#         QtGui.QApplication.restoreOverrideCursor()
#
#         self.setCurrentFile(fileName)
#         self.statusBar().showMessage("File saved", 2000)
#
#     def setCurrentFile(self, fileName):
#         self.curFile = fileName
#         if self.curFile:
#             self.setWindowTitle("%s - Recent Files" % self.strippedName(self.curFile))
#         else:
#             self.setWindowTitle("Recent Files")
#
#         settings = QtCore.QSettings('Trolltech', 'Recent Files Example')
#         files = settings.value('recentFileList')
#
#         try:
#             files.remove(fileName)
#         except ValueError:
#             pass
#
#         files.insert(0, fileName)
#         del files[MainWindow.MaxRecentFiles:]
#
#         settings.setValue('recentFileList', files)
#
#         for widget in QtGui.QApplication.topLevelWidgets():
#             if isinstance(widget, MainWindow):
#                 widget.updateRecentFileActions()
#
#     def updateRecentFileActions(self):
#         settings = QtCore.QSettings('Trolltech', 'Recent Files Example')
#         files = settings.value('recentFileList')
#
#         numRecentFiles = min(len(files), MainWindow.MaxRecentFiles)
#
#         for i in range(numRecentFiles):
#             text = "&%d %s" % (i + 1, self.strippedName(files[i]))
#             self.recentFileActs[i].setText(text)
#             self.recentFileActs[i].setData(files[i])
#             self.recentFileActs[i].setVisible(True)
#
#         for j in range(numRecentFiles, MainWindow.MaxRecentFiles):
#             self.recentFileActs[j].setVisible(False)
#
#         self.separatorAct.setVisible((numRecentFiles > 0))
#
#     def strippedName(self, fullFileName):
#         return QtCore.QFileInfo(fullFileName).fileName()
#
#
# if __name__ == '__main__':
#
#     import sys
#
#     app = QtGui.QApplication(sys.argv)
#     mainWin = MainWindow()
#     mainWin.show()
#     sys.exit(app.exec_())
#!/usr/bin/python
# -*- coding: utf-8 -*-

# """
# ZetCode PyQt4 tutorial
#
# In this program, we can press on a button
# with a left mouse click or drag and drop the
# button with  the right mouse click.
#
# author: Jan Bodnar
# website: zetcode.com
# last edited: October 2013
# """
#
# import sys
# from PyQt4 import QtCore, QtGui
#
#
# class Button(QtGui.QPushButton):
#
#     def __init__(self, title, parent):
#         super(Button, self).__init__(title, parent)
#
#     def mouseMoveEvent(self, e):
#
#         if e.buttons() != QtCore.Qt.RightButton:
#             return
#
#         mimeData = QtCore.QMimeData()
#
#         drag = QtGui.QDrag(self)
#         drag.setMimeData(mimeData)
#         drag.setHotSpot(e.pos() - self.rect().topLeft())
#
#         dropAction = drag.start(QtCore.Qt.MoveAction)
#
#     def mousePressEvent(self, e):
#
#         super(Button, self).mousePressEvent(e)
#
#         if e.button() == QtCore.Qt.LeftButton:
#             print 'press'
#
#
# class Example(QtGui.QWidget):
#
#     def __init__(self):
#         super(Example, self).__init__()
#
#         self.initUI()
#
#     def initUI(self):
#
#         self.setAcceptDrops(True)
#
#         self.button = Button('Button', self)
#         self.button.move(100, 65)
#
#         self.setWindowTitle('Click or Move')
#         self.setGeometry(300, 300, 280, 150)
#         self.show()
#
#     def dragEnterEvent(self, e):
#
#         e.accept()
#
#     def dropEvent(self, e):
#
#         position = e.pos()
#         self.button.move(position)
#
#         e.setDropAction(QtCore.Qt.MoveAction)
#         e.accept()

from sgApi.sgApi import SgApi
from sgtkLib import tkutil, tkm
import os, pprint
#import kCore.attribute as kAttr

_USER_ = os.environ['USER']
_STARTTIME_ = 101

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg
sgA = SgApi(sgw=sgw, tk=tk, project=project)

def findAllSequence(all = False):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
    ]
    res = {}
    seqShots =[]
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','code','description']):
        seq = v['code']
        if all:
            if not seq in res:
                res[seq] = {}
            res[seq]['description'] = v['description']
            print seq[:3]
        else:
            if int(seq[:3]) <800:
                if not seq in res:
                    res[seq] = {}
                if v['description'] != None:
                    res[seq]['description'] = v['description']
                else:
                    res[seq]['description'] = 'None'
            else:
                print 'donuts for: ' + seq
    return res

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

def findShots( seq='s1300', shotList=[]):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'in',shotList],
        #['entity.Shot.tag_list', 'name_contains', 'mattepainting'],
    ]

    res = {}
    for v in sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_frames_of_interest','entity.Shot.sg_cut_in','entity.Shot.sg_cut_out'], order=[{'field_name':'created_at','direction':'desc'}]):
        entityName = v['entity']['name']
        if not entityName in res:
            res[entityName] ={}
            frameInterest = v['entity.Shot.sg_frames_of_interest']
            if frameInterest is not None:
                res[entityName]['frameInterest'] = frameInterest.split(',')
            else:
                mid = str((int(v['entity.Shot.sg_cut_out'])+int(v['entity.Shot.sg_cut_in']))/2)
                res[entityName]['frameInterest'] = [mid]
            res[entityName]['cutIn'] = v['entity.Shot.sg_cut_in']
            res[entityName]['cutOut'] = v['entity.Shot.sg_cut_out']
    return res

#get all the shot from the sequence
def findShotsInSequence(seq='s1300'):
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
    return sorted(seqShots)

def findCameraPath(seq='s1300'):
    shotInSeq = findShotsInSequence(seq=seq)
    dictShots = findShots(seq,shotInSeq)
    res = {}
    for shot in dictShots.keys():
        try:
            camPath = sgA.getLastCamera(shot, taskPriority=['dwa_camera']).getPath()
        except AttributeError:
            dictShots.pop(shot,None)
            print "no cam for: " + shot
        else:
            dictShots[shot]['camPath'] = camPath
    #pprint.pprint(dictShots)
    return dictShots



def main():

    a = findAllSequence().keys()[0]
    b = findShotsInSequence(a)
    pprint.pprint(b)


if __name__ == '__main__':
    main()