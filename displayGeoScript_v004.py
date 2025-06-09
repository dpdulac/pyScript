from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QEvent, QCoreApplication, Qt

from Katana import  NodegraphAPI, ScenegraphManager, Nodes3DAPI, Utils, WorkingSet, WorkingSetManager, UI4, QT4FormWidgets, QtWidgets
import sys, os, yaml

from PyQt5.QtWidgets import QLineEdit, QMainWindow, QAction, QGridLayout, QWidget,QCheckBox,QLabel, QPushButton, QHBoxLayout, QComboBox, QSpacerItem, QSizePolicy, QFileDialog, QApplication, QScrollArea, QVBoxLayout, QDialog

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

class CELPanel(QScrollArea):

    def __init__(self, parent):
        QScrollArea.__init__(self, parent)
        scrollParent = QWidget(self)
        self.setWidget(scrollParent)
        self.setWidgetResizable(True)
        self.setFrameStyle(self.NoFrame)
        self.HelpText = '\nUse this as a convenience for searching within your scenegraph with CEL.\n\n'
        scrollLayout = QVBoxLayout(scrollParent)
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

class expressionWindowUI(QMainWindow):
    def __init__(self, parent=None, listCombo=[]):
        super(expressionWindowUI, self).__init__(parent)
        self.parent = parent
        if self.parent is not None:
            self.pathFile = self.parent.dirTxtName
            self.listCombo = listCombo
        self.initUI()

    def initUI(self):
        self.centralWidget = QWidget()
        self.mainGridLayout = QGridLayout(self.centralWidget)
        self.setCentralWidget(self.centralWidget)
        self.comboBox = QComboBox()
        self.comboBox.addItems(self.listCombo)
        self.lineEdit = QLineEdit()
        self.exitButton = QPushButton("Exit")
        self.mainGridLayout.addWidget(self.comboBox, 0, 0, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.lineEdit, 1, 0)
        self.mainGridLayout.addWidget(self.exitButton, 2, 0, Qt.AlignRight)
        self.exitButton.clicked.connect(self.exitFunc)
        self.comboBox.currentTextChanged.connect(self.typeChanged)
        # self.setLayout(self.mainLayout)
        self.setMinimumWidth(700)
        self.setMinimumHeight(100)
        self.setWindowTitle("expression reader")

    # display the expression in the lineEdit widget
    def typeChanged(self):
        self.lineEdit.clear()
        if self.comboBox.currentText != "None" or self.comboBox.currentText != "":
            fileName = self.pathFile + "/" + self.comboBox.currentText()
            f = open(fileName, "r")
            try:
                assetPath = f.read().splitlines()[0]
            except:
                self.lineEdit.setText("No expression found")
            else:
                self.lineEdit.setText(assetPath.replace("#", ""))
            f.close()

    def exitFunc(self):
        self.parent.expressionWindow.close()
        self.parent.expressionWindow = None

class Dialog(QDialog):
    def __init__(self):
        super(Dialog, self).__init__()

        self.setWindowTitle("ERROR")
        self.mainLayout = QVBoxLayout()
        self.message = QLabel("Please Graphe a node")
        self.button = QPushButton("Close")
        self.mainLayout.addWidget(self.message)
        self.mainLayout.addWidget(self.button)
        self.setLayout(self.mainLayout)
        self.button.clicked.connect(self.close_clicked)

    def close_clicked(self):
        self.close()

class displayGeoUI(QMainWindow):
    def __init__(self,parent=None):
        super(displayGeoUI, self).__init__(parent)
        # working set for visibility
        self.workingSet = WorkingSetManager.WorkingSetManager.getOrCreateWorkingSet(WorkingSetManager.WorkingSetManager.ViewerVisibilityWorkingSetName)
        # working set for render
        self.workingSetRender = WorkingSetManager.WorkingSetManager.getOrCreateWorkingSet(WorkingSetManager.WorkingSetManager.RenderWorkingSetName)
        self.sg = ScenegraphManager.getActiveScenegraph()
        # collection list
        self.collectionNameList = ["None"]
        self.rootNode = NodegraphAPI.GetNode( 'root' )
        self.time = NodegraphAPI.GetCurrentTime()
        # create producer
        self.producer = Nodes3DAPI.GetGeometryProducer(self.rootNode, self.time)
        if self.producer is None:
            dialogbox = Dialog()  # we subclasses QDialog into Dialog
            dialogbox.exec_()
            self.close()
            return
        # get the collections names from the scene
        self.getCollections()
        # expression created
        self.expression = ""
        # expression to write on file or in the lineEdit widget
        self.expressionToWrite = ""
        # expression for all the light
        self.expressionAllLight = "((/root//*{attr(\"type\") == \"light\"}))"
        self.dirTxtName = "/tmp"
        self.listOfTxtFiles = ["None"]
        self.expressionWindow = None
        # check if there is path already checked
        currentPaths = self.workingSet.getLocationsByState(WorkingSet.WorkingSet.State.Included)
        if len(currentPaths) == 0:
            self.allPath = []
        else:
            self.allPath = currentPaths
        self.renderPaths = []
        # dir to put the setting.yaml file
        self.settingFilePath = '/homes/' + os.environ['USER'] + '/displayGeo/'
        self.settingFileName = self.settingFilePath + "setting.yaml"
        # check if the file/path exist if not create it
        if not os.path.isfile(self.settingFileName):
            if not os.path.isdir(self.settingFilePath):
                os.makedirs(self.settingFilePath)
            with open(self.settingFileName, 'w') as fp:
                pass
            os.utime(self.settingFileName, None)
            os.chmod(self.settingFileName, 0o0775)
            dictToWrite = { "dirFiles":{"dirOfTxtFile": self.dirTxtName}}
            with open(self.settingFileName, 'w') as yamlFile:
                yaml.dump(dictToWrite, yamlFile)
            yamlFile.close()
        self.dirTxtName = self.yamlReadFile(file = self.settingFileName)[0]
        if self.dirTxtName == "":
            self.dirTxtName = "/tmp"

        self.initUI()

    def initUI(self):
        # menubar
        self.bar = self.menuBar()
        self.fileBar = self.bar.addMenu("&Advanced")
        self.setDirAction = QAction('&set file dir', self)
        self.setDirAction.setShortcut("Ctrl+T")
        self.setDirAction.setStatusTip('set the dir to find the .txt files')
        self.setDirAction.triggered.connect(self.setDirTxtFiles)
        self.fileBar.addAction(self.setDirAction)
        self.expressionAction = QAction("&read expression", self)
        self.expressionAction.setShortcut("Ctrl+W")
        self.expressionAction.setToolTip("display the expression of the choosen file")
        self.expressionAction.triggered.connect(self.displayExpressionWindow)
        self.fileBar.addAction(self.expressionAction)

        self.centralWidget = QWidget()
        self.mainVBoxLayout = QVBoxLayout(self.centralWidget)
        self.setCentralWidget(self.centralWidget)

        self.mainGridLayout = QGridLayout()
        self.mainVBoxLayout.addLayout(self.mainGridLayout)
        # CEl check Box
        self.celCheckBox = QCheckBox("Use CEL")
        self.celCheckBox.setChecked(False)
        self.celCheckBox.setToolTip("check to use CEL statement")
        # child check Box
        self.childCheckBox = QCheckBox("include child")
        self.childCheckBox.setChecked(True)
        self.childCheckBox.setToolTip("will add the child of all locations wanted")
        # additive mode
        self.addCheckBox = QCheckBox("Add Mode")
        self.addCheckBox.setChecked(False)
        self.addCheckBox.setToolTip("Set additive mode")
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
        # display
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
        self.presetComboBox.addItems(self.listOfTxtFiles)
        self.createPresetList()
        # select button
        self.selectButton = QPushButton("Select")
        self.selectButton.setMaximumWidth(200)
        self.selectButton.setToolTip("select the asset(s) in the scene viewer and focus on it/them")
        self.selectButton.setObjectName("selectButton")
        # cell widget
        self.cellWidget = CELPanel(self)
        self.cellWidget.setMinimumWidth(600)
        self.cellWidget.setVisible(False)

        self.expressionLineEdit = QLineEdit()
        self.mainVBoxLayout.addWidget(self.expressionLineEdit)

        # widget layout
        self.mainGridLayout.addWidget(self.celCheckBox, 0, 0, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.addCheckBox, 0, 1, Qt.AlignLeft)
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
        self.mainGridLayout.addWidget(self.resetButton, 7, 2)
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
        self.presetComboBox.currentTextChanged.connect(self.displayChosenFile)

        self.setWindowTitle("display geo")

        Utils.EventModule.ProcessAllEvents()

    def __del__(self):
        pass

    def displayExpressionWindow(self):
        if self.expressionWindow is None:
            self.expressionWindow = expressionWindowUI(self, listCombo=self.listOfTxtFiles)
            self.expressionWindow.move(700,300)
            self.expressionWindow.setWindowFlags(Qt.Tool)
            self.expressionWindow.show()

        else:
            self.expressionWindow.close()
            self.expressionWindow = None

    def getCollections(self):
        collectionsAttr = self.producer.getAttribute("collections")
        if collectionsAttr is not None:
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
        self.renderPaths = []
        if self.renderCheck.isChecked():
            if len(self.allPath) == 0:
                pass
            else:
                wid = UI4.Widgets.CollectAndSelectInScenegraph(self.expressionAllLight, "/root")
                self.renderPaths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
                self.renderPaths += self.workingSet.getLocationsByState(WorkingSet.WorkingSet.State.Included)
                if self.childCheckBox.isChecked() and self.collectionComboBox.currentText() != "None":
                    self.recursiveFindPath(self.producer, self.renderPaths)
                self.workingSetRender.setLocationStates(self.renderPaths, WorkingSet.WorkingSet.State.Included)
        else:
            self.workingSetRender.clear()
            self.renderPaths = []

    # set the dir for textFile
    def setDirTxtFiles(self):
        self.dirTxtName = str(QFileDialog.getExistingDirectory(self, 'Open Directory', self.dirTxtName, QFileDialog.ShowDirsOnly))
        self.createPresetList(True)

    def createPresetList(self, newPath=False):
        if newPath:
            dictToWrite = { "dirFiles":{"dirOfTxtFile": self.dirTxtName}}
            with open(self.settingFileName, 'w') as yamlFile:
                yaml.dump(dictToWrite, yamlFile)
            yamlFile.close()
        fileInDir = os.listdir(self.dirTxtName)
        self.listOfTxtFiles = ["None"]
        self.listOfTxtFiles += [i for i in fileInDir if i.endswith(".txt")]
        self.presetComboBox.clear()
        self.presetComboBox.addItems(self.listOfTxtFiles)

    # save the pinned asset path to a file
    def saveDisplayFile(self):
        allLoc = self.workingSet.getLocationsByState(WorkingSet.WorkingSet.State.Included)
        fileName = str(QFileDialog.getSaveFileName(self, 'Open file', self.dirTxtName, "text files ( *.txt)")[0])
        if not fileName.endswith(".txt"):
            fileName += ".txt"
        if os.path.isfile(fileName):
            os.remove(fileName)
        f = open(fileName, "w")
        if self.expressionToWrite != "":
            f.write("# " + self.expressionToWrite + " #\n")
        else:
            f.write("# no expression found #\n")
        if len(allLoc) != 0:
            for loc in allLoc:
                f.write(loc + "\n")
            f.close()
        else:
            os.remove(fileName)
        self.createPresetList()
        self.presetComboBox.setCurrentText(fileName[fileName.rfind("/") + 1:])

    #load the saved path for display
    def loadDisplayFile(self):
        self.displayViewer(False)
        self.resetDisplay(self.renderCheck.isChecked(), self.addCheckBox.isChecked())
        inputFileName = str(QFileDialog.getOpenFileName(self, 'Open file', self.dirTxtName,"text files ( *.txt)")[0])
        f = open(inputFileName, "r")
        # don't load the first line
        assetPath = f.read().splitlines()[1:]
        if self.addCheckBox.isChecked():
                self.allPath += assetPath
        else:
            self.allPath = assetPath
        f.close()
        self.workingSet.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.Included)
        if self.renderCheck.isChecked():
            self.setRender()
        self.displayViewer(True)

    # display the chosen file
    def displayChosenFile(self):
        if str(self.presetComboBox.currentText()) != "None":
            self.resetDisplay(self.renderCheck.isChecked(), self.addCheckBox.isChecked())
            inputFileName = self.dirTxtName + "/" + str(self.presetComboBox.currentText())
            f = open(inputFileName, "r")
            assetPath = f.read().splitlines()[1:]
            if self.addCheckBox.isChecked():
                self.allPath += assetPath
            else:
                self.allPath = assetPath
            f.close()
            f = open(inputFileName, "r")
            expressionLine = f.read().splitlines()[0]
            self.expressionLineEdit.setText(str(expressionLine.replace("#", "")))
            f.close()
            self.workingSet.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.Included)
            if self.renderCheck.isChecked():
                self.setRender()
            self.displayViewer(True)
        else:
            self.resetDisplay()

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
    def resetDisplay(self, excludeRender=False, deleteAllPath=False):
        self.workingSet.clear()
        self.workingSetRender.clear()
        self.displayViewer(False)
        self.nameLineEdit.setText("")
        self.pathLineEdit.setText('')
        self.typeBox.setCurrentText('None')
        self.typeLineEdit.setText("")
        self.collectionComboBox.setCurrentText("None")
        # need the oposite to del allPath data
        if not deleteAllPath:
            self.allPath = []
            self.renderPaths = []
            self.expression = ""
            self.expressionToWrite = ""
            self.expressionLineEdit.clear()
        # self.presetComboBox.setCurrentText("None")
        if not excludeRender:
            self.renderCheck.setChecked(False)

    def resetTheName(self):
        self.nameLineEdit.setText("")

    def resetThePath(self):
        self.pathLineEdit.setText("")

    # recursively get the producer path if it contain the nameIn Node string
    def recursiveFindPath(self, producer, listPath=[], nameInNode='_hiShape'):
        for path in listPath:
            producerPath = producer.getProducerByPath(path)
            self.recursiveFromPath(producerPath, listPath)
        return listPath

    def recursiveFromPath(self, producer, listPath=[]):
        if producer is not None:
            if producer.getFullName() not in listPath:
                listPath.append(producer.getFullName())
            for child in producer.iterChildren():
                self.recursiveFromPath(child, listPath)

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

    # return a dict from a .yalm file
    def yamlReadFile(self, file="/tmp/donuts.yaml", module='dirFiles', dictMode=False):
        with open(file) as f:
            dictionary = yaml.load(f, Loader=yaml.FullLoader)
            if dictMode:
                # logger.debug('dictionary: {res}'.format(res=dictionary[module]))
                return dictionary[module]
            else:
                itemList = []
                for key in sorted(dictionary[module].keys()):
                    itemList.append(dictionary[module][key])
                # logger.debug('list form: {res}'.format(res=itemList))
                return itemList

    # main function to display/hide the asset
    def displayModel(self,node=NodegraphAPI.GetRootNode(), nameInNode='_hiShape'):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        nameSender = str(self.sender().objectName())
        self.paths = []
        if not self.addCheckBox.isChecked() :
            if nameSender != "selectButton":
                self.workingSet.clear()
            self.allPath = []
        nameInNode = self.nameLineEdit.text()
        splitText = str(self.pathLineEdit.text()).split(' ')
        # Enable Visibility Working Set.
        self.sg.setViewerVisibilityFollowingWorkingSet(True)
        # check the CEL widget
        if self.celCheckBox.isChecked():
            self.expression = self.cellWidget.getCellWidgetValue()
            # if there is an expression
            if self.expression != "":
                wid = UI4.Widgets.CollectAndSelectInScenegraph(self.expression, "/root")
                self.paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
                if self.addCheckBox.isChecked():
                    self.allPath += self.paths
                else:
                    self.allPath = self.paths
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
                self.paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
                if self.addCheckBox.isChecked():
                    self.allPath += self.paths
                else:
                    self.allPath = self.paths
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
                self.paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
                if self.addCheckBox.isChecked():
                    self.allPath += self.paths
                else:
                    self.allPath = self.paths
            if self.collectionComboBox.currentText() != "None":
                self.expression = ""
                for key in self.collectionNameList:
                    if key == self.collectionComboBox.currentText():
                        self.expression = "(/$" + key +")"
                        wid = UI4.Widgets.CollectAndSelectInScenegraph(self.expression, "/root")
                        self.paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
                        if self.addCheckBox.isChecked():
                            self.allPath += self.paths
                        else:
                            self.allPath = self.paths
            if self.renderCheck.isChecked():
                    self.setRender()
        self.expressionLineEdit.clear()
        # hide the asset
        if nameSender == 'Hide' :
            self.producer = Nodes3DAPI.GetGeometryProducer(self.rootNode, self.time)
            if self.childCheckBox.isChecked() and self.collectionComboBox.currentText() != "None" :
                self.recursiveFindPath(self.producer, self.paths)
            self.workingSet.setLocationStates(self.paths, WorkingSet.WorkingSet.State.Empty)
            if self.addCheckBox.isChecked() and self.expressionToWrite != "":
                if self.expressionToWrite.find(" + " + self.expression) > -1:
                    self.expressionToWrite = self.expressionToWrite.replace(" + " + self.expression, "")
                    self.expressionToWrite += " - " + self.expression
                elif self.expressionToWrite.find("- " + self.expression) > -1:
                    pass
                elif self.expressionToWrite.find(self.expression) > -1:
                    pass
                else:
                    self.expressionToWrite += " - " + self.expression
            else:
                self.expressionToWrite = self.expression
            self.expressionLineEdit.setText(self.expressionToWrite)
            if self.renderCheck.isChecked():
                self.setRender()

        #select
        elif nameSender == 'selectButton':
            self.sg.clearSelection()
            self.sg.addSelectedLocations(self.paths, False)
            # zoom in the viewer
            tab = UI4.App.Tabs.FindTopTab('Viewer')
            viewport = tab.getViewportWidgetByIndex(viewportIndex=0, viewerDelegate=tab.getViewerDelegateByIndex(0))

            keyEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_F, Qt.NoModifier)
            QCoreApplication.postEvent(viewport, keyEvent)
            del keyEvent  # Clear local variable as Qt takes ownership of the underlying C++ object
            self.expressionLineEdit.setText(self.expressionToWrite)
        # show the asset   
        else:
            if self.childCheckBox.isChecked() and self.collectionComboBox.currentText() != "None":
                self.recursiveFindPath(self.producer, self.allPath)

            self.workingSet.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.Included)
            if self.addCheckBox.isChecked() and self.expressionToWrite != "":
                if self.expressionToWrite.find(" - " + self.expression) > -1:
                    self.expressionToWrite = self.expressionToWrite.replace(" - " + self.expression, "")
                    self.expressionToWrite += " + " + self.expression
                elif self.expressionToWrite.find(self.expression) > -1:
                    pass
                else:
                    self.expressionToWrite += " + " + self.expression
            else:
                self.expressionToWrite = self.expression
            self.expressionLineEdit.setText(self.expressionToWrite)
            if self.renderCheck.isChecked():
                self.setRender()

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

# def BuildisplayGeoUI():
#     global ex
#     if ex is not None:
#         ex.close()
#     ex= displayGeoUI()
#     ex.setWindowFlags(Qt.Tool)
#     ex.move(700, 500)
#     ex.show()
PluginRegistry = [
    ('KatanaPanel', 2.0, 'displayGeo', displayGeoUI),
    ('KatanaPanel', 2.0, 'Custom/displayGeo', displayGeoUI),
]
# BuildisplayGeoUI()
