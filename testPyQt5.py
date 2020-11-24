#!/usr/bin/env python
# coding:utf-8
""":mod: testPyQt5
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2020.11
   
"""
from PyQt5.QtWidgets import QApplication, QMainWindow,QPushButton, QHBoxLayout,QWidget
from PyQt5.QtCore import  Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.InitUI()

    def InitUI(self):
        self.centralWidget = QWidget()
        self.setWindowTitle("My App")
        self.button = QPushButton("Press me")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.theButtonWasClicked)
        self.button.clicked.connect(self.theButtonWasChecked)

        self.mainLayout = QHBoxLayout(self.centralWidget)
        self.mainLayout.addWidget(self.button)
        self.setCentralWidget(self.centralWidget)

    def theButtonWasClicked(self):
        print("clicked")

    def theButtonWasChecked(self,checked):
        print("Checked: ", checked)


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec_()