from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from Katana import  NodegraphAPI, ScenegraphManager, Nodes3DAPI, Utils, WorkingSet, WorkingSetManager, UI4, QT4FormWidgets, QtWidgets
import sys, os

ex = None

typeList = ["None", "subdmesh", "polymesh", "pointcloud", "nurbspatch", "curves", "locator", "assembly", "component", "group", "light", "light filter", "light filter reference", "camera",
			"volume", "openvdbasset", "material", "instance", "instance source", "instance array", "level-of-detail group", "level-of-detail",
			"render procedural", "render procedural args"]
# @LineEdit class to accept drop of path from katana
class fileEdit(QLineEdit):
    def __init__(self, parent=None):
        super(fileEdit, self).__init__(parent)

        self.setDragEnabled(True)

    def dragEnterEvent( self, event ):
            data = event.mimeData()
            # urls = data.urls()
            if data.hasText():
                event.acceptProposedAction()

    def dragMoveEvent( self, event ):
        data = event.mimeData()
        # urls = data.urls()
        if data.hasText():
            event.acceptProposedAction()

    def dropEvent( self, event ):
        data = event.mimeData()
        # urls = data.urls()
        if data.hasText():
            filepath = data.text()
            self.setText(filepath)

class CELPanel(QtWidgets.QScrollArea):

    def __init__(self, parent):
        QtWidgets.QScrollArea.__init__(self, parent)
        scrollParent = QtWidgets.QWidget(self)
        self.setWidget(scrollParent)
        self.setWidgetResizable(True)
        self.setFrameStyle(self.NoFrame)
        self.HelpText = '\nUse this as a convenience for searching within your scenegraph with CEL.\n\n'
        scrollLayout = QtWidgets.QVBoxLayout(scrollParent)
        scrollLayout.addStretch()
        scrollLayout.setSpacing(2)
        scrollLayout.setContentsMargins(2, 2, 2, 2)
        policyData = dict(CEL='')
        rootPolicy = QT4FormWidgets.PythonValuePolicy('cels', policyData)
        policy = rootPolicy.getChildByName('CEL')
        policy.getWidgetHints().update(widget='cel', help=self.HelpText, open='True')
        self.cellWidget = UI4.FormMaster.KatanaWidgetFactory.buildWidget(scrollParent, policy)
        scrollLayout.addWidget(self.cellWidget)
        scrollLayout.addStretch(2)

    def getCellWidgetValue(self):
        return self.cellWidget._CelEditorFormWidget__buildValueFromPanels()


class displayGeoUI(QMainWindow):
    def __init__(self,parent=None):
        super(displayGeoUI, self).__init__(parent)
        self.workingSet = WorkingSetManager.WorkingSetManager.getOrCreateWorkingSet(WorkingSetManager.WorkingSetManager.ViewerVisibilityWorkingSetName)
        self.workingSetRender = WorkingSetManager.WorkingSetManager.getOrCreateWorkingSet(WorkingSetManager.WorkingSetManager.RenderWorkingSetName)
        self.sg = ScenegraphManager.getActiveScenegraph()
        self.collectionNameList = ["None"]
        self.rootNode = NodegraphAPI.GetNode( 'root' )
        self.time = NodegraphAPI.GetCurrentTime()
        self.producer = Nodes3DAPI.GetGeometryProducer(self.rootNode, self.time)
        self.getCollections()
        self.expression = ""
        # check if there is path already checked
        currentPaths = self.workingSet.getLocationsByState(WorkingSet.WorkingSet.State.Included)
        if len(currentPaths) == 0:
            self.allPath = []
        else:
            self.allPath = currentPaths
        self.initUI()

    def initUI(self):
        self.centralWidget = QWidget()
        self.mainGridLayout = QGridLayout(self.centralWidget)
        self.setCentralWidget(self.centralWidget)

        # CEl check Box
        self.celCheckBox = QCheckBox("Use CEL")
        self.celCheckBox.setChecked(False)
        self.celCheckBox.setToolTip("check to use CEL statement")
        # child check Box
        self.childCheckBox = QCheckBox("include child")
        self.childCheckBox.setChecked(True)
        self.childCheckBox.setToolTip("will add the child of all locations wanted")
        # name
        self.nameLabel = QLabel('Name')
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setToolTip('name or part of name to look for')
        self.nameLineEdit.setText("")
        self.resetName = QPushButton('ResetName')
        self.resetName.setToolTip("reset the name to '_hiShape'")
        # type
        self.typeLabel = QLabel("Type")
        self.typeLayout = QHBoxLayout()
        self.typeBox = QComboBox()
        self.typeBox.addItems(typeList)
        self.typeBox.setToolTip("type of the asset to display")
        self.typeLineEdit = QLineEdit()
        self.typeLineEdit.setText("")
        self.typeLineEdit.setReadOnly(True)
        self.typeLineEdit.setToolTip("list of asset type")
        self.typeLayout.addWidget(self.typeBox)
        self.typeLayout.addWidget(self.typeLineEdit)
        self.typeReset = QPushButton("ResetType")
        self.typeReset.setToolTip("reset the asset type")
        # collections
        self.collectionNameLabel = QLabel("Collection")
        self.collectionComboBox = QComboBox()
        self.collectionComboBox.addItems(self.collectionNameList)
        self.collectionComboBox.setMaximumWidth(220)
        self.collectionComboBox.setObjectName("collectionComboBox")
        self.collectionComboBox.setToolTip("select a collection to add the displayed asset")
        # path
        self.pathLabel = QLabel('Path')
        self.pathLineEdit = fileEdit(self)
        self.pathLineEdit.setText("")
        self.pathLineEdit.setToolTip('path(s) from the sceneGraph where to match the name')
        self.resetPath = QPushButton('ResetPath')
        self.resetPath.setToolTip('empty the path')
        self.resetPath.setObjectName('resetPath')
        #render part
        self.renderCheck = QCheckBox("render")
        self.renderCheck.setChecked(False)
        self.renderCheck.setToolTip("check to set render Included objects columns")
        # 
        # diplay
        self.displayOnOffGridLayout = QGridLayout()
        self.displayButton = QPushButton('Display')
        self.displayButton.setToolTip('Display the object containing the name in selected path')
        self.displayButton.setMaximumWidth(100)
        self.displayButton.setObjectName('Display')
        self.unDisplayButton = QPushButton('Hide')
        self.unDisplayButton.setToolTip('Hide the objectS containing the name in selected path')
        self.unDisplayButton.setMaximumWidth(100)
        self.unDisplayButton.setObjectName('Hide')
        self.resetButton = QPushButton('Reset')
        self.displayOnOffGridLayout.setContentsMargins(0, 0, 0, 0)
        self.displayOnOffGridLayout.addWidget(self.displayButton, 0, 0)
        self.displayOnOffGridLayout.addWidget(self.unDisplayButton, 0, 1)
        # reset all
        self.resetButton.setMaximumWidth(200)
        self.resetButton.setToolTip('reset the name, path and undisplay all the displayed objects')
        # save and load
        self.saveLoadGridLayout = QGridLayout()
        self.saveFileButton = QPushButton("Save")
        self.saveFileButton.setMaximumWidth(100)
        self.saveFileButton.setToolTip("save the asset display path to a file")
        self.loadFileButton = QPushButton("Load")
        self.loadFileButton.setMaximumWidth(100)
        self.loadFileButton.setToolTip("load the asset display path from a file")
        self.saveLoadGridLayout.setContentsMargins(0,0,0,0)
        self.saveLoadGridLayout.addWidget(self.saveFileButton, 0, 0)
        self.saveLoadGridLayout.addWidget(self.loadFileButton, 0, 1)
        # combobox for .txt file
        self.presetComboBox = QComboBox()
        self.presetComboBox.addItems(self.collectionNameList)
        # select button
        self.selectButton = QPushButton("Select")
        self.selectButton.setMaximumWidth(200)
        self.selectButton.setToolTip("select the asset(s) in the scene viewer and focus on it/them")
        self.selectButton.setObjectName("selectButton")
        # cell widget
        self.cellWidget = CELPanel(self)
        self.cellWidget.setMinimumWidth(600)
        self.cellWidget.setVisible(False)

        # widget layout
        self.mainGridLayout.addWidget(self.celCheckBox, 0, 0, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.nameLabel, 1, 0)
        self.mainGridLayout.addWidget(self.nameLineEdit, 1, 1)
        self.mainGridLayout.addWidget(self.resetName, 1, 2)
        self.mainGridLayout.addWidget(self.typeLabel, 2, 0)
        self.mainGridLayout.addLayout(self.typeLayout, 2, 1)
        self.mainGridLayout.addWidget(self.typeReset, 2, 2)
        self.mainGridLayout.addWidget(self.collectionNameLabel, 3, 0)
        self.mainGridLayout.addWidget(self.collectionComboBox, 3, 1)
        self.mainGridLayout.addWidget(self.childCheckBox, 3, 2, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.cellWidget, 4, 0, 1, 3)
        self.mainGridLayout.addWidget(self.pathLabel,5 , 0)
        self.mainGridLayout.addWidget(self.pathLineEdit, 5, 1)
        self.mainGridLayout.addWidget(self.resetPath, 5, 2)
        self.mainGridLayout.addWidget(self.renderCheck, 6, 0)
        self.mainGridLayout.addLayout(self.displayOnOffGridLayout, 7, 0)
        self.mainGridLayout.addItem(QSpacerItem(40, 10, QSizePolicy.Minimum, QSizePolicy.Expanding), 7, 1)
        # self.mainGridLayout.addWidget(self.displayButton, 7, 0)
        self.mainGridLayout.addWidget(self.resetButton, 7, 2)
        # self.mainGridLayout.addWidget(self.unDisplayButton, 7, 1, Qt.AlignLeft)
        self.mainGridLayout.addLayout(self.saveLoadGridLayout, 8, 0)
        self.mainGridLayout.addWidget(self.presetComboBox, 8, 1)
        self.mainGridLayout.addWidget(self.selectButton, 8, 2)

        # connections
        self.displayButton.clicked.connect(self.displayModel)
        self.unDisplayButton.clicked.connect(self.displayModel)
        self.resetButton.clicked.connect(self.resetDisplay)
        self.resetName.clicked.connect(self.resetTheName)
        self.resetPath.clicked.connect(self.resetThePath)
        self.typeBox.currentTextChanged.connect(self.typeChanged)
        self.typeReset.clicked.connect(self.typeReseted)
        self.saveFileButton.clicked.connect(self.saveDisplayFile)
        self.loadFileButton.clicked.connect(self.loadDisplayFile)
        self.selectButton.clicked.connect(self.displayModel)
        self.celCheckBox.toggled.connect(self.celCheckBoxToggled)
        self.renderCheck.toggled.connect(self.setRender)

        self.setWindowTitle("display geo")

        Utils.EventModule.ProcessAllEvents()

    def __del__(self):
        pass

    def getCollections(self):
        collectionsAttr = self.producer.getAttribute("collections")
        for i in range(collectionsAttr.getNumberOfChildren()):
            self.collectionNameList.append(collectionsAttr.getChildName(i))


    def celCheckBoxToggled(self, s):
        self.allPath = []
        self.expression = ""
        if s:
            self.cellWidget.setVisible(True)
            self.childCheckBox.setVisible(False)
            self.nameLabel.setVisible(False)
            self.nameLineEdit.setVisible(False)
            self.resetName.setVisible(False)
            self.typeLabel.setVisible(False)
            self.typeBox.setVisible(False)
            self.typeLineEdit.setVisible(False)
            self.typeReset.setVisible(False)
            self.collectionNameLabel.setVisible(False)
            self.collectionComboBox.setVisible(False)
            self.pathLabel.setVisible(False)
            self.pathLineEdit.setVisible(False)
            self.resetPath.setVisible(False)
        else:
            self.cellWidget.setVisible(False)
            self.childCheckBox.setVisible(True)
            self.nameLabel.setVisible(True)
            self.nameLineEdit.setVisible(True)
            self.resetName.setVisible(True)
            self.typeLabel.setVisible(True)
            self.typeBox.setVisible(True)
            self.typeLineEdit.setVisible(True)
            self.typeReset.setVisible(True)
            self.collectionNameLabel.setVisible(True)
            self.collectionComboBox.setVisible(True)
            self.pathLabel.setVisible(True)
            self.pathLineEdit.setVisible(True)
            self.resetPath.setVisible(True)

    # add the objects to the render column
    def setRender(self):
        if self.renderCheck.isChecked():
            self.expression = ""
            if len(self.allPath) == 0:
                pass
            else:
                self.expression = "((/root//*{attr(\"type\") == \"light\"}))"
                wid = UI4.Widgets.CollectAndSelectInScenegraph(self.expression, "/root")
                paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
                self.allPath  += paths
                if self.childCheckBox.isChecked() and self.collectionComboBox.currentText() != "None":
                    self.workingSetRender.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.IncludedWithChildren)
                else:
                    self.workingSetRender.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.IncludedWithChildren)

    # save the pinned asset path to a file
    def saveDisplayFile(self):
        allLoc = self.workingSet.getLocationsByState(WorkingSet.WorkingSet.State.Included)
        fileName = str(QFileDialog.getSaveFileName(self, 'Open file', "/tmp", "text files ( *.txt)")[0])
        if not fileName.endswith(".txt"):
        	fileName += ".txt"
        if os.path.isfile(fileName):
        	os.remove(fileName)
        f = open(fileName, "w")
        if len(allLoc) != 0:
        	for loc in allLoc:
        		f.write(loc + "\n")
        	f.close()
        else:
        	os.remove(fileName)

    #load the saved path for display
    def loadDisplayFile(self):
        self.displayViewer(False)
        allLoc = []
        inputFileName = str(QFileDialog.getOpenFileName(self, 'Open file', "/tmp","text files ( *.txt)")[0])
        f = open(inputFileName, "r")
        allLoc = f.read().splitlines()
        f.close()
        self.workingSet.setLocationStates(allLoc, WorkingSet.WorkingSet.State.Included)
        self.displayViewer(True)


    # reset the type go back to None and get rid of the text
    def typeReseted(self):
        if self.typeLineEdit.text() != None or self.typeLineEdit.text() != "":
            self.typeBox.setCurrentText('None')
            self.typeLineEdit.setText("")

    # add a text with multiple input
    def typeChanged(self):
        if self.typeBox.currentText() != "None":
            if str(self.typeLineEdit.text()) != "":
                self.typeLineEdit.setText(self.typeLineEdit.text() + ";" + self.typeBox.currentText())
            else:
                self.typeLineEdit.setText(self.typeBox.currentText())

    # reset the display
    def resetDisplay(self):
        self.workingSet.clear()
        self.workingSetRender.clear()
        self.displayViewer(False)
        self.nameLineEdit.setText("")
        self.pathLineEdit.setText('')
        self.typeBox.setCurrentText('None')
        self.typeLineEdit.setText("")
        self.collectionComboBox.setCurrentText("None")
        self.renderCheck.setChecked(False)

    def resetTheName(self):
        self.nameLineEdit.setText("")

    def resetThePath(self):
        self.pathLineEdit.setText("")

    # recursively get the producer path if it contain the nameIn Node string
    def recursiveFindPath(self, producer, listPath=[], nameInNode='_hiShape'):
        if producer is not None:
            path = producer.getFullName()
            if path.find(nameInNode) >= 0:
                listPath.append(path)
            for child in producer.iterChildren():
                self.recursiveFindPath(child, listPath, nameInNode)
        else:
            print('no producer for :',producer)
        return listPath

    def recursiveFromPath(self, producer):
        if producer is not None:
            if producer.getFullName() not in self.allPath:
                self.allPath.append(producer.getFullName())
            for child in producer.iterChildren():
                self.recursiveFromPath(child)

    # recursively get the producer path it the asset type is in the list
    def recursiveFindType(self, producer, listPath=[], typeNameList=[]):
        if producer is not None and len(typeNameList) != 0 and typeNameList[0] != "":
            producerType = producer.getAttribute("type").getValue()
            if producerType in typeNameList:
                listPath.append(producer.getFullName())
            for child in producer.iterChildren():
                self.recursiveFindType(child, listPath, typeNameList)
        else:
            print('no producer for :',producer)
        return listPath

    # main function to display/hide the asset
    def displayModel(self,node=NodegraphAPI.GetRootNode(), nameInNode='_hiShape'):
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        nameSender = str(self.sender().objectName())
        self.allPath =[]
        nameInNode = self.nameLineEdit.text()
        node = NodegraphAPI.GetNode( 'root' )
        time = NodegraphAPI.GetCurrentTime()
        producer = Nodes3DAPI.GetGeometryProducer(node, time)
        splitText = str(self.pathLineEdit.text()).split(' ')
        # Enable Visibility Working Set.
        self.sg.setViewerVisibilityFollowingWorkingSet(True)
        # check the CEL widget
        if self.celCheckBox.isChecked():
            self.expression = self.cellWidget.getCellWidgetValue()
            if self.expression != "":
                wid = UI4.Widgets.CollectAndSelectInScenegraph(self.expression, "/root")
                paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
                self.allPath += paths
        else:
            # find the producer which contain the input name
            if nameInNode != "" and nameInNode is not None:
                self.expression = ""
                # only look for the producers which path is wanted
                if len(splitText) > 0 and splitText[0] != '' :
                    for prodpath in splitText:
                        self.expression += "((" + prodpath + "//*" + nameInNode + "*)) + "
                    self.expression = self.expression[:self.expression.rfind("+")]
                # over the entire scene
                else :
                    self.expression = "/root//*" + nameInNode + "*"
                wid = UI4.Widgets.CollectAndSelectInScenegraph(self.expression, "/root")
                paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
                self.allPath += paths
            # get the path with the help of asset type
            if self.typeLineEdit.text() != "":
                splitTypeText = str(self.typeLineEdit.text()).split(";")
                self.expression = ""
                # only look for the producers which path is wanted
                if len(splitText) > 0 and splitText[0] != '' :
                    for prodpath in splitText:
                        for splitType in splitTypeText:
                            self.expression += "((" + prodpath + "//*{attr(\"type\") == \"" + splitType + "\"})) + "
                else:
                    for splitType in splitTypeText:
                        self.expression += "((/root//*{attr(\"type\") == \"" + splitType + "\"})) + "
                self.expression = self.expression[:self.expression.rfind("+")]
                wid = UI4.Widgets.CollectAndSelectInScenegraph(self.expression, "/root")
                paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
                self.allPath += paths
                    # producer = Nodes3DAPI.GetGeometryProducer(node, time)
            if self.collectionComboBox.currentText() != "None":
                for key in self.collectionNameList:
                    if key == self.collectionComboBox.currentText():
                        nodeValue = "(/$" + key +")"
                        wid = UI4.Widgets.CollectAndSelectInScenegraph(nodeValue, "/root")
                        paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
                        self.allPath += paths
            # if render column need to be checked
            if self.renderCheck.isChecked():
                    self.setRender()
            # if self.childCheckBox.isChecked():
            #     for prod in self.allPath:
            #         producer = self.producer.getProducerByPath(prod)
            #         self.recursiveFromPath(producer)
            #         self.producer = Nodes3DAPI.GetGeometryProducer(self.rootNode, self.time)
        # hide the asset
        if nameSender == 'Hide' :
            self.workingSet.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.Empty)
        #select
        elif nameSender == 'selectButton':
            self.sg.clearSelection()
            self.sg.addSelectedLocations(self.allPath, False)
            # zoom in the viewer
            tab = UI4.App.Tabs.FindTopTab('Viewer')
            viewport = tab.getViewportWidgetByIndex(viewportIndex=0, viewerDelegate=tab.getViewerDelegateByIndex(0))

            keyEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_F, Qt.NoModifier)
            QCoreApplication.postEvent(viewport, keyEvent)
            del keyEvent  # Clear local variable as Qt takes ownership of the underlying C++ object
        # show the asset   
        else:
            if self.childCheckBox.isChecked() and self.collectionComboBox.currentText() != "None":
                self.workingSet.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.IncludedWithChildren)
                # self.workingSetRender.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.IncludedWithChildren)

            else:
                self.workingSet.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.Included)
                # self.workingSetRender.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.IncludedWithChildren)
        #display the asset
        self.displayViewer(True)
        QApplication.restoreOverrideCursor()

    def displayViewer(self, state=False):
        # if self.renderCheck.isChecked():
        #     scenegraphTab = UI4.App.Tabs.FindTopTab('Scene Graph')
        #     sceneGraphview = scenegraphTab.getSceneGraphView()
        #     widget = sceneGraphview.getColumnByName('render')
        #     widget.setTitleToggledOn(state)
        # turn on the object display column
        self.sg.setViewerVisibilityFollowingWorkingSet(state)

def BuildisplayGeoUI():
    global ex
    if ex is not None:
        ex.close()
    ex= displayGeoUI()
    ex.setWindowFlags(Qt.Tool)
    ex.move(700, 500)
    ex.show()

# BuildisplayGeoUI()
