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

def extractDictFromAss(assPath = "/s/prodanim/ta/_sandbox/duda/assFiles/tmp/robotC.ass"):

    """
    output a dictionary of the node in the .ass file
    """
    pathList =[]

    AiBegin()

    AiMsgSetConsoleFlags(AI_LOG_NONE)
    AiASSLoad(assPath, AI_NODE_ALL)

    iter = AiUniverseGetNodeIterator(AI_NODE_SHAPE);
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
    result['/'] = result.pop('')
    return result

class assUI(QWidget):
    def __init__(self):
        super(assUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.mainLayout = QVBoxLayout()
        self.tw = QTreeWidget()
        result = extractDictFromAss("/s/prodanim/ta/_sandbox/duda/assFiles/tmp/newKitchen.ass")
        #self.tw.setHeaderLabels(['bla','ble'])
        self.a = QTreeWidgetItem(self.tw, '/')
        self.build_paths_tree(result,self.a)
        # self.b = QTreeWidgetItem(self.a,['blu','bly'])
        self.mainLayout.addWidget(self.tw)
        self.setLayout(self.mainLayout)

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
            child.setText(0, k)
            if v:
                parent.addChild(child)
            if isinstance(v, dict):
                self.build_paths_tree(v, child)

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