#!/usr/bin/env python
# coding:utf-8
""":mod: arnoldApiTest
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
from PyQt4.QtGui import *
from PyQt4.QtCore import *


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

def extractDictFromAss(assPath = "/s/prodanim/ta/_sandbox/duda/assFiles/tmp/light.ass", nodeType = AI_NODE_ALL ):

    """
    output a dictionary of the node in the .ass file
    """
    pathList =[]

    AiBegin()

    AiMsgSetConsoleFlags(AI_LOG_NONE)
    AiASSLoad(assPath, AI_NODE_ALL)

    iter = AiUniverseGetNodeIterator(nodeType);
    while not AiNodeIteratorFinished(iter):
        node = AiNodeIteratorGetNext(iter)
        name = AiNodeGetStr(node, "name")
        AiMsgInfo(name)
        AiMsgInfo( node )
        pathList.append(name)
        # if AiNodeIs(node, "polymesh"):
        #     name = AiNodeGetStr(node, "name")
        #     AiMsgInfo(name)
        #     pathList.append(name)

    AiNodeIteratorDestroy(iter)
    AiEnd()
    result = get_path_dict(pathList)
    if '' in result.keys():
        result['/'] = result.pop('')
    # else:
    #     result['/'] = result
    if 'root' in result.keys():
        result.pop('root')
    return result


class MyTreeWidget(QTreeWidget):
    def __init__(self, parent = None):
        QTreeWidget.__init__(self, parent)
        self.setDragEnabled(True)

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
                        self.item, QTreeWidget.PositionAtCenter)
                    itemrect = self.visualItemRect(self.item)
                itemrect.setLeft(portrect.left())
                itemrect.setWidth(portrect.width())
                pos = self.mapToGlobal(itemrect.center())
        if pos is not None:
            self.menu = QMenu(self)
            #menu.addAction(item.toolTip(0))
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

    def openAll(self):
        self.expandAll()

    def collapseAllBranch(self):
        self.collapseAll()

    def expandBranch(self):
        self.RecursiveChildItem(self.item,True)

    def collapseBranch(self):
        self.RecursiveChildItem(self.item,False)

    def copyPath(self):
        text = self.item.toolTip(0)
        QApplication.clipboard().setText(text)

    def RecursiveChildItem(self,item,openBranch = True):
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
            for nb in range(0,nbChild):
                child = item.child(nb)
                self.RecursiveChildItem(child,openBranch)



class assUI(QWidget):
    def __init__(self):
        super(assUI, self).__init__()
        self.dictNodeTypeSorted = {
            0: {'All': {'imagePath': '/s/prodanim/ta/_sandbox/duda/tmp/world.png', 'nodeType': AI_NODE_ALL}},
            1: {'Shape': {'imagePath': '/s/prodanim/ta/_sandbox/duda/tmp/shape.png', 'nodeType': AI_NODE_SHAPE}},
            2: {'Camera': {'imagePath': '/s/prodanim/ta/_sandbox/duda/tmp/camera.png', 'nodeType': AI_NODE_CAMERA}},
            3: {'Light': {'imagePath': '/s/prodanim/ta/_sandbox/duda/tmp/light.png', 'nodeType': AI_NODE_LIGHT}},
            4: {'Shader': {'imagePath': '/s/prodanim/ta/_sandbox/duda/tmp/shader.png', 'nodeType': AI_NODE_SHADER}},
            5: {'Filter': {'imagePath': '/s/prodanim/ta/_sandbox/duda/tmp/filter.png', 'nodeType': AI_NODE_FILTER}},
            6: {'Driver': {'imagePath': '/s/prodanim/ta/_sandbox/duda/tmp/driver.png', 'nodeType': AI_NODE_DRIVER}},
            7: {'Option': {'imagePath': '/s/prodanim/ta/_sandbox/duda/tmp/option.png', 'nodeType': AI_NODE_OPTIONS}},
            8: {'Override': {'imagePath': '/s/prodanim/ta/_sandbox/duda/tmp/override.png',
                             'nodeType': AI_NODE_OVERRIDE}},
            9: {'ColorManager': {'imagePath': '/s/prodanim/ta/_sandbox/duda/tmp/colormanager.png',
                                 'nodeType': AI_NODE_COLOR_MANAGER}}}
        self.dictNodeType = {}
        for key in self.dictNodeTypeSorted.keys():
            keyName = self.dictNodeTypeSorted[key].keys()[0]
            self.dictNodeType[keyName] = self.dictNodeTypeSorted[key][keyName]
        self.initUI()

    def initUI(self):
        self.mainLayout = QGridLayout()
        self.tw = MyTreeWidget()
        self.tw.setHeaderLabels(['ass content...'])
        #self.tw.setDragEnabled(True)
        self.fileButton = QPushButton('ass file')
        self.fileQLineEdit = QLineEdit()
        self.fileQHBoxLayout = QHBoxLayout()
        self.fileQHBoxLayout.addWidget(self.fileButton)
        self.fileQHBoxLayout.addWidget(self.fileQLineEdit)



        self.allNodeCheckBox = QCheckBox('All')
        self.allNodeCheckBox.setIcon(QIcon('/s/prodanim/ta/_sandbox/duda/tmp/world.png'))
        self.allNodeCheckBox.setObjectName('allNode')
        self.allNodeCheckBox.setAutoExclusive(True)
        self.allNodeCheckBox.setChecked(True)
        self.shapeNodeCheckBox = QCheckBox('Shape')
        self.shapeNodeCheckBox.setIcon(QIcon('/s/prodanim/ta/_sandbox/duda/tmp/shape.png'))
        self.shapeNodeCheckBox.setObjectName('shapeNode')
        self.shapeNodeCheckBox.setAutoExclusive(True)
        self.cameraNodeCheckBox= QCheckBox('Camera')
        self.cameraNodeCheckBox.setIcon(QIcon('/s/prodanim/ta/_sandbox/duda/tmp/camera.png'))
        self.cameraNodeCheckBox.setObjectName('cameraNode')
        self.cameraNodeCheckBox.setAutoExclusive(True)
        self.lightNodeCheckBox = QCheckBox('Light')
        self.lightNodeCheckBox.setIcon(QIcon('/s/prodanim/ta/_sandbox/duda/tmp/light.png'))
        self.lightNodeCheckBox.setObjectName('lightNode')
        self.lightNodeCheckBox.setAutoExclusive(True)
        self.shaderNodeCheckBox = QCheckBox('Shader')
        self.shaderNodeCheckBox.setIcon(QIcon('/s/prodanim/ta/_sandbox/duda/tmp/shader.png'))
        self.shaderNodeCheckBox.setObjectName('shaderNode')
        self.shaderNodeCheckBox.setAutoExclusive(True)
        self.filterNodeCheckBox = QCheckBox('Filter')
        self.filterNodeCheckBox.setIcon(QIcon('/s/prodanim/ta/_sandbox/duda/tmp/filter.png'))
        self.filterNodeCheckBox.setObjectName('filterNode')
        self.filterNodeCheckBox.setAutoExclusive(True)
        self.driverNodeCheckBox = QCheckBox('Driver')
        self.driverNodeCheckBox.setIcon(QIcon('/s/prodanim/ta/_sandbox/duda/tmp/driver.png'))
        self.driverNodeCheckBox.setObjectName('driverNode')
        self.driverNodeCheckBox.setAutoExclusive(True)
        self.optionNodeCheckBox = QCheckBox('Option')
        self.optionNodeCheckBox.setIcon(QIcon('/s/prodanim/ta/_sandbox/duda/tmp/option.png'))
        self.optionNodeCheckBox.setObjectName('optionNode')
        self.optionNodeCheckBox.setAutoExclusive(True)
        self.overrideNodeCheckBox = QCheckBox('Override')
        self.overrideNodeCheckBox.setIcon(QIcon('/s/prodanim/ta/_sandbox/duda/tmp/override.png'))
        self.overrideNodeCheckBox.setObjectName('overrideNode')
        self.overrideNodeCheckBox.setAutoExclusive(True)
        self.colorNodeCheckBox = QCheckBox('ColorManager')
        self.colorNodeCheckBox.setIcon(QIcon('/s/prodanim/ta/_sandbox/duda/tmp/colormanager.png'))
        self.colorNodeCheckBox.setObjectName('colorNode')
        self.colorNodeCheckBox.setAutoExclusive(True)
        self.nodeComboBox = QComboBox()
        for node in sorted(self.dictNodeTypeSorted.keys()):
            nodeName = self.dictNodeTypeSorted[node].keys()[0]
            self.nodeComboBox.addItem(nodeName)
            self.nodeComboBox.setItemIcon(node, QIcon(self.dictNodeTypeSorted[node][nodeName]['imagePath']))
        # self.nodeComboBox.addItems((['All', 'shapeNode']))
        # self.nodeComboBox.setItemIcon(0,QIcon('/s/prodanim/ta/_sandbox/duda/tmp/world.png'))

        self.nodeGroupBox = QGroupBox('ass part to view')
        self.nodeGroupBox.setDisabled(True)
        self.nodeBoxLayout = QHBoxLayout(self.nodeGroupBox )
        self.nodeBoxLayout.addWidget(self.nodeComboBox)
        self.nodeBoxLayout.addWidget(self.allNodeCheckBox)
        self.nodeBoxLayout.addWidget(self.shapeNodeCheckBox)
        self.nodeBoxLayout.addWidget(self.cameraNodeCheckBox)
        self.nodeBoxLayout.addWidget(self.lightNodeCheckBox)
        self.nodeBoxLayout.addWidget(self.shaderNodeCheckBox)
        self.nodeBoxLayout.addWidget(self.driverNodeCheckBox)
        self.nodeBoxLayout.addWidget(self.filterNodeCheckBox)
        self.nodeBoxLayout.addWidget(self.optionNodeCheckBox)
        self.nodeBoxLayout.addWidget(self.colorNodeCheckBox)
        self.nodeBoxLayout.addWidget(self.overrideNodeCheckBox)


        # create the top level
        self.topLevel = QTreeWidgetItem(self.tw)
        self.topLevel.setText(0,'/')

        #self.build_paths_tree(result,self.topLevel)

        self.mainLayout.addLayout(self.fileQHBoxLayout,0,0)
        self.mainLayout.addWidget(self.nodeGroupBox,1,0)
        #self.mainLayout.addLayout(self.nodeBoxLayout, 1, 0)
        self.mainLayout.addWidget(self.tw,2,0)

        self.fileButton.clicked.connect(self.findFile)
        self.shapeNodeCheckBox.clicked.connect(self.setTreeView)
        self.allNodeCheckBox.clicked.connect(self.setTreeView)
        self.nodeComboBox.currentIndexChanged.connect(self.filter)
        
        self.setLayout(self.mainLayout)

    def filter(self):
        currentText = str(self.nodeComboBox.currentText())
        self.tw.clear()
        self.topLevel = QTreeWidgetItem(self.tw)
        self.topLevel.setText(0, '/')
        self.nodeType = AI_NODE_ALL
        text = str(self.fileQLineEdit.text())
        result = extractDictFromAss(text, self.dictNodeType[currentText]['nodeType'])
        print result
        if len(result.keys()) > 0:
            result = result['/']
            self.build_paths_tree(result, self.topLevel)
        else:
            self.tw.clear()
            tmp = QTreeWidgetItem(self.tw)
            tmp.setText(0,'no ' + currentText + ' in this ass')
            tmp.setTextColor(0,QColor(255, 0, 0))
        
        #self.build_paths_tree(result, self.topLevel)

    def setTreeView(self):
        #if self.sender().isChecked():
        self.tw.clear()
        self.topLevel = QTreeWidgetItem(self.tw)
        self.topLevel.setText(0, '/')
        self.nodeType = AI_NODE_ALL
        text = str(self.fileQLineEdit.text())
        if self.sender().objectName() == 'shapeNode':
            self.nodeType = AI_NODE_SHAPE
        result = extractDictFromAss(text,self.nodeType)
        result = result['/']
        self.build_paths_tree(result, self.topLevel)


    def build_paths_tree(self,d, parent):
        """Builds the directory path using Qt's TreeWidget items.

        Args:
          d (dict): A nested dictionary of file paths to construct our QTreeWidget.
          parent (QtGui.QTreeWidgetItem): The top-level parent of the path tree.

        """
        if not d:
            return
        for k, v in d.iteritems():
            child = QTreeWidgetItem(parent)
            parentName = parent.text(0)
            toolTipStr = parent.toolTip(0)
            if parentName == '/':
                #child.setText(0, '/'+k)
                child.setToolTip(0,'/'+k)
            else:
                #child.setText(0,parentName+'/'+k)
                child.setToolTip(0, toolTipStr+'/'+k)
            child.setText(0, k)
            if v:
                parent.addChild(child)
            if isinstance(v, dict):
                self.build_paths_tree(v, child)

    def findFile(self):
        """dialog to open file of type .ass"""
        filename = QFileDialog.getOpenFileName(self, 'Open file', '/s/prodanim/ta',"Image files (*.ass)")
        self.tw.clear()
        self.topLevel = QTreeWidgetItem(self.tw)
        self.topLevel.setText(0, '/')
        self.nodeGroupBox.setDisabled(False)
        # fill fileQLineEdit with the string filename
        self.fileQLineEdit.setText(filename)
        result = extractDictFromAss(str(filename))
        result = result['/']
        self.build_paths_tree(result, self.topLevel)

ex = None

def BuildShotUI():
    global ex
    if ex is not None:
        ex.close()
    ex = assUI()
    ex.show()

def main():
    # result = extractDictFromAss()
    # pprint.pprint(result)
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    BuildShotUI()
    app.exec_()

if __name__ == '__main__':
    main()