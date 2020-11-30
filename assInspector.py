#!/usr/bin/env python
# coding:utf-8
""":mod: assInspector.py
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2020.11
   
"""
from arnold import *
from collections import defaultdict
import pprint
#from PyQt4.QtGui import *
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import *
#from PyQt4.QtCore import *


IMAGE_PATH = '/s/prodanim/ta/_sandbox/duda/tmp/'

def nested_dict():
    """
    Creates a default dictionary where each value is an other default dictionary.
    """
    return defaultdict(nested_dict)


def default_to_regular(d):
    """
    Converts defaultdicts of defaultdicts to dict of dicts.
    """
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


def get_path_dict(paths):
    new_path_dict = nested_dict()
    for path in paths:
        parts = path.split('/')
        if parts:
            marcher = new_path_dict
            for key in parts[:-1]:
                marcher = marcher[key]
            marcher[parts[-1]] = parts[-1]
    return default_to_regular(new_path_dict)


def extractDictFromAss(assPath="/s/prodanim/ta/_sandbox/duda/assFiles/tmp/light.ass", nodeType=AI_NODE_ALL):
    """
    output a dictionary of the node in the .ass file
    """
    pathList = []

    AiBegin()

    AiMsgSetConsoleFlags(AI_LOG_NONE)
    AiASSLoad(assPath, AI_NODE_ALL)

    iter = AiUniverseGetNodeIterator(nodeType);
    while not AiNodeIteratorFinished(iter):
        node = AiNodeIteratorGetNext(iter)
        name = AiNodeGetStr(node, "name")
        AiMsgInfo(name)
        AiMsgInfo(node)
        #pathList.append(name)
        entry = AiNodeGetNodeEntry(node)
        nodeTypeName = AiNodeEntryGetTypeName(entry)
        pathList.append(name+'__'+nodeTypeName)
        # print AiNodeEntryGetType(entry),AI_NODE_LIGHT
        # print '\n\n'
        # iterParam = AiNodeEntryGetParamIterator(entry)
        # while not AiParamIteratorFinished(iterParam):
        #     pentry = AiParamIteratorGetNext(iterParam)
        #     paramName = AiParamGetName(pentry)
        #     para= AiNodeEntryLookUpParameter(entry,paramName)
        #     print paramName,AiParamGetTypeName(AiParamGetType(para))
        #
        # AiParamIteratorDestroy(iterParam)
        # print '\n\n'


    AiNodeIteratorDestroy(iter)
    AiEnd()
    result = get_path_dict(pathList)
    if '' in result.keys():
        result['/'] = result.pop('')
    # else:1
    #     result['/'] = result
    if 'root__shape' in result.keys():
        result.pop('root__shape')
    return result


class MyTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.setDragEnabled(True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("QTreeWidget{background-color: rgba(180,180,180,255);},QTreeWidget::QToolTip{ background-color: yellow; }")
        # self.setStyleSheet(" QToolTip{ background-color: yellow }")
        # self.pal = QtGui.QPalette()
        # self.pal.setColor(QtGui.QPalette.Foreground, QtGui.QColor('#348ceb'))
        # self.setPalette(self.pal)

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            pos = event.globalPos()
            self.item = self.itemAt(event.pos())
        else:
            pos = None
            selection = self.selectedItems()
            if selection:
                self.item = selection[0]
            else:
                self.item = self.currentItem()
                if self.item is None:
                    self.item = self.invisibleRootItem().child(0)
            if self.item is not None:
                parent = self.item.parent()
                while parent is not None:
                    parent.setExpanded(True)
                    parent = parent.parent()
                itemrect = self.visualItemRect(self.item)
                portrect = self.viewport().rect()
                if not portrect.contains(itemrect.topLeft()):
                    self.scrollToItem(
                        self.item, QtWidgets.QTreeWidget.PositionAtCenter)
                    itemrect = self.visualItemRect(self.item)
                itemrect.setLeft(portrect.left())
                itemrect.setWidth(portrect.width())
                pos = self.mapToGlobal(itemrect.center())
        if pos is not None:
            self.menu = QtWidgets.QMenu(self)
            # menu.addAction(item.toolTip(0))
            self.menu.addSeparator()
            openAll = self.menu.addAction('Open All')
            openAll.triggered.connect(self.openAll)
            collapseAll = self.menu.addAction('CollapseAll')
            self.menu.addSeparator()
            collapseAll.triggered.connect(self.collapseAllBranch)
            openBranch = self.menu.addAction('Open Branch')
            openBranch.setToolTip('bla')
            openBranch.triggered.connect(self.expandBranch)
            collapseBranch = self.menu.addAction('Collapse Branch')
            collapseBranch.triggered.connect(self.collapseBranch)
            self.menu.addSeparator()
            copyPath = self.menu.addAction('copy path')
            copyPath.triggered.connect(self.copyPath)
            self.menu.popup(pos)
        event.accept()

    def dragMoveEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if data.hasText():
            event.acceptProposedAction()

    def openAll(self):
        self.expandAll()

    def collapseAllBranch(self):
        self.collapseAll()

    def expandBranch(self):
        self.RecursiveChildItem(self.item, True)

    def collapseBranch(self):
        self.RecursiveChildItem(self.item, False)

    def copyPath(self):
        text = self.item.toolTip(0)
        QtWidgets.QApplication.clipboard().setText(text)

    def RecursiveChildItem(self, item, openBranch=True):
        try:
            item.childCount() > 0
        except:
            print 'no child'
        else:
            if openBranch:
                item.setExpanded(True)
            else:
                item.setExpanded(False)
            nbChild = item.childCount()
            for nb in range(0, nbChild):
                child = item.child(nb)
                self.RecursiveChildItem(child, openBranch)


class assUI(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(assUI, self).__init__(parent)
        # dictionary with sorting number for menu to be consistant
        self.dictNodeTypeSorted = {
            0: {'All': {'imagePath': IMAGE_PATH+'all.png', 'nodeType': AI_NODE_ALL}},
            1: {'Shape': {'imagePath': IMAGE_PATH+'shape.png', 'nodeType': AI_NODE_SHAPE}},
            2: {'Camera': {'imagePath': IMAGE_PATH+'camera.png', 'nodeType': AI_NODE_CAMERA}},
            3: {'Light': {'imagePath': IMAGE_PATH+'light.png', 'nodeType': AI_NODE_LIGHT}},
            4: {'Shader': {'imagePath': IMAGE_PATH+'shader.png', 'nodeType': AI_NODE_SHADER}},
            5: {'Filter': {'imagePath': IMAGE_PATH+'filter.png', 'nodeType': AI_NODE_FILTER}},
            6: {'Driver': {'imagePath': IMAGE_PATH+'driver.png', 'nodeType': AI_NODE_DRIVER}},
            7: {'Options': {'imagePath': IMAGE_PATH+'option.png', 'nodeType': AI_NODE_OPTIONS}},
            8: {'Override': {'imagePath': IMAGE_PATH+'override.png','nodeType': AI_NODE_OVERRIDE}},
            9: {'Color_manager': {'imagePath': IMAGE_PATH+'colormanager.png','nodeType': AI_NODE_COLOR_MANAGER}},
            10: {'Operator': {'imagePath': IMAGE_PATH+'operator.png','nodeType': AI_NODE_OPERATOR}}}
        self.dictNodeType = {}

        # dictionary without ordering number
        for key in self.dictNodeTypeSorted.keys():
            keyName = self.dictNodeTypeSorted[key].keys()[0]
            self.dictNodeType[keyName] = self.dictNodeTypeSorted[key][keyName]
        # add a key Transform which is not part of the Arnold API
        self.dictNodeType['Transform'] = {'imagePath': IMAGE_PATH+'transform.png'}

        self.assName = ''
        self.topLevel = QtWidgets.QTreeWidgetItem()
        self.initUI()

    def initUI(self):
        self.resize(600,300)
        self.setWindowTitle('assInspector')
        # self.setAttribute(Qt.WA_StyledBackground, True)
        # self.setStyleSheet('background-color: rgba(128,128,128,255)')

        self.mainLayout = QtWidgets.QGridLayout()

        self.tw = MyTreeWidget()
        self.tw.setHeaderLabels(['ass content...'])


        self.fileButton = QtWidgets.QPushButton('ass file')
        self.fileQLineEdit = QtWidgets.QLineEdit()
        self.nodeComboBox = QtWidgets.QComboBox()
        for node in sorted(self.dictNodeTypeSorted.keys()):
            nodeName = self.dictNodeTypeSorted[node].keys()[0]
            self.nodeComboBox.addItem(nodeName)
            self.nodeComboBox.setItemIcon(node, QtGui.QIcon(self.dictNodeTypeSorted[node][nodeName]['imagePath']))
        self.nodeComboBox.setDisabled(True)

        self.fileQHBoxLayout = QtWidgets.QHBoxLayout()
        self.fileQHBoxLayout.addWidget(self.fileButton)
        self.fileQHBoxLayout.addWidget(self.fileQLineEdit)
        self.fileQHBoxLayout.addWidget(self.nodeComboBox)

        # create the top level
        # self.topLevel = QTreeWidgetItem(self.tw)
        # self.topLevel.setText(0,'/')
        # self.topLevel.setIcon(0,QIcon('/s/prodanim/ta/_sandbox/duda/tmp/file.png'))

        self.mainLayout.addLayout(self.fileQHBoxLayout, 0, 0)
        self.mainLayout.addWidget(self.tw, 1, 0)

        self.fileButton.clicked.connect(self.findFile)
        self.nodeComboBox.currentIndexChanged.connect(self.filter)

        self.setLayout(self.mainLayout)


    def filter(self):
        currentText = str(self.nodeComboBox.currentText())
        self.tw.clear()
        self.topLevel = QtWidgets.QTreeWidgetItem(self.tw)
        self.topLevel.setText(0, self.assName)
        self.topLevel.setForeground(0,QtGui.QBrush(QtGui.QColor(255, 180, 0)))
        #self.topLevel.setTextColor(0, QtWidgets.QColor(180, 180, 0))
        self.topLevel.setIcon(0, QtGui.QIcon('/s/prodanim/ta/_sandbox/duda/tmp/file.png'))
        self.tw.expandItem(self.topLevel)
        self.nodeType = AI_NODE_ALL
        text = str(self.fileQLineEdit.text())
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        result = extractDictFromAss(text, self.dictNodeType[currentText]['nodeType'])
        # print result
        if len(result.keys()) > 0:
            # result = result['/']
            self.build_paths_tree(result, self.topLevel)
        else:
            self.tw.clear()
            tmp = QtWidgets.QTreeWidgetItem(self.tw)
            tmp.setText(0, 'no ' + currentText + ' in this ass')
            tmp.setForeground(0,QtGui.QBrush(QtGui.QColor(255, 0, 0)))
        QtWidgets.QApplication.restoreOverrideCursor()

    def build_paths_tree(self, d, parent):
        """Builds the directory path using Qt's TreeWidget items.

        Args:
          d (dict): A nested dictionary of file paths to construct our QTreeWidget.
          parent (QtWidgets.QTreeWidgetItem): The top-level parent of the path tree.

        """
        if not d:
            return
        for k, v in d.iteritems():
            pathName = ''
            nodeType = ''
            if k.find('__') > 0:
                pathName = k[:k.find('__')]
                nodeType = k[k.find('__')+2:].capitalize()
            else:
                pathName = k
                nodeType = 'Transform'
            self.child = QtWidgets.QTreeWidgetItem(parent)
            parentName = parent.text(0)
            toolTipStr = parent.toolTip(0)
            if parentName == self.assName:
                self.child.setToolTip(0, pathName)
            else:
                if parentName == '/':
                    self.child.setToolTip(0, '/' + pathName)
                else:
                    self.child.setToolTip(0, toolTipStr + '/' + pathName)
            self.child.setText(0, pathName)
            self.child.setIcon(0,QtGui.QIcon(self.dictNodeType[nodeType]['imagePath']))
            if v:
                parent.addChild(self.child)
            if isinstance(v, dict):
                self.build_paths_tree(v, self.child)

    def findFile(self):
        """dialog to open file of type .ass"""
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/s/prodanim/ta', "Image files (*.ass)")
        filename = str(filename[0])
        self.assName = filename[filename.rfind('/') + 1:]
        self.tw.clear()
        self.topLevel = QtWidgets.QTreeWidgetItem(self.tw)
        self.topLevel.setText(0, self.assName)
        self.topLevel.setForeground(0, QtGui.QBrush(QtGui.QColor(255, 180, 0)))
        #self.topLevel.setIcon(0, QtGui.QIcon(IMAGE_PATH+'file.png'))
        self.tw.expandItem(self.topLevel)
        # fill fileQLineEdit with the string filename
        self.fileQLineEdit.setText(filename)
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        result = extractDictFromAss(str(filename))
        # result = result['/']
        self.build_paths_tree(result, self.topLevel)
        QtWidgets.QApplication.restoreOverrideCursor()
        self.nodeComboBox.setCurrentIndex(0)
        self.nodeComboBox.setDisabled(False)





ex = None


def BuildShotUI():
    global ex
    if ex is not None:
        ex.close()
    parent = QtWidgets.QApplication.activeWindow()
    ex = assUI(parent)
    ex.show()


def main():
    # result = extractDictFromAss("/s/prodanim/ta/_sandbox/duda/assFiles/tmp/light.ass")
    # pprint.pprint(result)
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle(QtWidgets.QStyleFactory.create("plastique"))
    app.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))
    BuildShotUI()
    app.exec_()


if __name__ == '__main__':
    main()