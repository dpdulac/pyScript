#!/usr/bin/env python
# coding:utf-8
""":mod: pyqtArrow --- Module Title
=================================

   2018.08
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

class FrameLayout(QWidget):
    def __init__(self, parent=None, title=None):
        QFrame.__init__(self, parent=parent)
        self._is_collasped = True
        self._title_frame = None
        self._content, self._content_layout = (None, None)
        self._main_v_layout = QVBoxLayout(self)
        self._main_v_layout.addWidget(self.initTitleFrame(title, self._is_collasped))
        self._main_v_layout.addWidget(self.initContent(self._is_collasped))
        self.initCollapsable()

    def initTitleFrame(self, title, collapsed):
        self._title_frame = self.TitleFrame(title=title, collapsed=collapsed)
        return self._title_frame

    def initContent(self, collapsed):
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content.setLayout(self._content_layout)
        self._content.setVisible(not collapsed)
        return self._content

    def addWidget(self, widget):
        self._content_layout.addWidget(widget)

    def initCollapsable(self):
        QObject.connect(self._title_frame, SIGNAL('clicked()'), self.toggleCollapsed)

    def toggleCollapsed(self):
        self._content.setVisible(self._is_collasped)
        self._is_collasped = not self._is_collasped
        self._title_frame._arrow.setArrow(int(self._is_collasped))
     ############################
    #           TITLE          #
    ############################
    class TitleFrame(QFrame):
        def __init__(self, parent=None, title="", collapsed=False):
            QFrame.__init__(self, parent=parent)
            self.setMinimumHeight(24)
            self.move(QPoint(24, 0))
            #self.setStyleSheet("border:1px solid rgb(41, 41, 41); ")
            self.mainQvboxLayout = QVBoxLayout()
            self.fileGroup = QGroupBox('atom')
            self._hlayout = QHBoxLayout(self)
            self._hlayout.setContentsMargins(0, 0, 0, 0)
            self._hlayout.setSpacing(0)
            self._arrow = None
            self._title = None
            self.inCheckbox = QCheckBox("in")
            self.midCheckbox = QCheckBox("mid")
            self.outCheckbox = QCheckBox("out")
            self._hlayout.addWidget(self.initArrow(collapsed))
            self._hlayout.addWidget(self.initTitle(title))
            self._hlayout.addWidget(self.inCheckbox)
            self._hlayout.addWidget(self.midCheckbox)
            self._hlayout.addWidget(self.outCheckbox)

        def initArrow(self, collapsed):
            self._arrow = FrameLayout.Arrow(collapsed=collapsed)
            self._arrow.setStyleSheet("border:0px")
            return self._arrow

        def initTitle(self, title=None):
            self._title = QLabel(title)
            self._title.setMinimumHeight(24)
            self._title.move(QPoint(24, 0))
            self._title.setStyleSheet("border:0px")
            return self._title

        def mousePressEvent(self, event):
            self.emit(SIGNAL('clicked()'))
            return super(FrameLayout.TitleFrame, self).mousePressEvent(event)
     #############################
    #           ARROW           #
    #############################
    class Arrow(QFrame):
        def __init__(self, parent=None, collapsed=False):
            QFrame.__init__(self, parent=parent)
            self.setMaximumSize(24, 24)
             # horizontal == 0
            self._arrow_horizontal = (QPointF(7.0, 8.0), QPointF(17.0, 8.0), QPointF(12.0, 13.0))
            # vertical == 1
            self._arrow_vertical = (QPointF(8.0, 7.0), QPointF(13.0, 12.0), QPointF(8.0, 17.0))
            # arrow
            self._arrow = None
            self.setArrow(int(collapsed))

        def setArrow(self, arrow_dir):
            if arrow_dir:
                self._arrow = self._arrow_vertical
            else:
                self._arrow = self._arrow_horizontal

        def paintEvent(self, event):
            painter = QPainter()
            painter.begin(self)
            painter.setBrush(QColor(192, 192, 192))
            painter.setPen(QColor(64, 64, 64))
            painter.drawPolygon(*self._arrow)
            painter.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = QMainWindow()
    w = QWidget()
    w.setMinimumWidth(350)
    win.setCentralWidget(w)
    l = QVBoxLayout()
    l.setSpacing(0)
    l.setAlignment(Qt.AlignTop)
    w.setLayout(l)
    t = FrameLayout(title="Buttons")
    t.addWidget(QPushButton('a'))
    t.addWidget(QPushButton('b'))
    t.addWidget(QPushButton('c'))
    f = FrameLayout(title="TableWidget")
    rows, cols = (6, 3)
    data = {'col1': ['1', '2', '3', '4', '5', '6'],
            'col2': ['7', '8', '9', '10', '11', '12'],
            'col3': ['13', '14', '15', '16', '17', '18']}
    table = QTableWidget(rows, cols)
    headers = []
    for n, key in enumerate(sorted(data.keys())):
        headers.append(key)
        for m, item in enumerate(data[key]):
            newitem = QTableWidgetItem(item)
            table.setItem(m, n, newitem)
    table.setHorizontalHeaderLabels(headers)
    f.addWidget(table)
    l.addWidget(t)
    l.addWidget(f)
    win.show()
    win.raise_()
    print "Finish"
    sys.exit(app.exec_())