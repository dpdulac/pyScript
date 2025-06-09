#!/usr/bin/env python
# coding:utf-8
""":mod: displayGeoUI_v003
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: dulacd
   :date: 2025.06
   
"""
# --- START OF COMMENTED AND REFACTORED FILE displayGeoScript_v004.py ---

# This script defines a custom Katana Panel ('displayGeo') for advanced scene visibility management.
# It allows users to quickly find and control the visibility of scene graph locations using
# either a simplified form (by name, type, collection) or a full CEL (Collection Expression Language) editor.
# It leverages Katana's WorkingSet system for a standard, non-destructive workflow.
# Key features include an additive mode, saving/loading visibility presets, and integrated render visibility control.

from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QEvent, QCoreApplication, Qt

# Import necessary Katana API modules
from Katana import (
    NodegraphAPI, ScenegraphManager, Nodes3DAPI, Utils,
    WorkingSet, WorkingSetManager, UI4, QT4FormWidgets
)
import sys
import os
import yaml

# Explicitly import specific Qt Widgets for clarity
from PyQt5.QtWidgets import (
    QLineEdit, QMainWindow, QAction, QGridLayout, QWidget, QCheckBox, QLabel,
    QPushButton, QHBoxLayout, QComboBox, QSpacerItem, QSizePolicy, QFileDialog,
    QApplication, QScrollArea, QVBoxLayout
)

# Global variable to hold an instance of the UI, if run standalone (not used in Panel mode)
ex = None

# A predefined list of common location types for the dropdown menu.
typeList = [
    "None", "subdmesh", "polymesh", "pointcloud", "nurbspatch", "curves", "locator",
    "assembly", "component", "group", "light", "light filter", "light filter reference",
    "camera", "volume", "openvdbasset", "material", "instance", "instance source",
    "instance array", "level-of-detail group", "level-of-detail", "render procedural",
    "render procedural args"
]


class fileEdit(QLineEdit):
    """
    A custom QLineEdit widget that overrides drag-and-drop events.
    This allows a user to drag text (e.g., a scenegraph path from another Katana panel)
    and drop it directly into this line edit field.
    """

    def __init__(self, parent=None):
        super(fileEdit, self).__init__(parent)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        # Accept the event if the data being dropped is text.
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        # Accept the move event if the data is text.
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # When the text is dropped, set the line edit's text to the dropped data.
        if event.mimeData().hasText():
            filepath = event.mimeData().text()
            self.setText(filepath)


class CELPanel(QScrollArea):
    """
    A container widget that wraps Katana's native CEL (Collection Expression Language) editor.
    This provides a seamless way to integrate the powerful CEL widget into our custom UI.
    """

    def __init__(self, parent):
        super(CELPanel, self).__init__(parent)
        scrollParent = QWidget(self)
        self.setWidget(scrollParent)
        self.setWidgetResizable(True)
        self.setFrameStyle(self.NoFrame)
        self.HelpText = '\nUse this as a convenience for searching within your scenegraph with CEL.\n\n'
        scrollLayout = QVBoxLayout(scrollParent)
        scrollLayout.addStretch()
        scrollLayout.setSpacing(2)
        scrollLayout.setContentsMargins(2, 2, 2, 2)

        # Use Katana's form widget system to build the CEL editor.
        policyData = dict(CEL='')
        rootPolicy = QT4FormWidgets.PythonValuePolicy('cels', policyData)
        policy = rootPolicy.getChildByName('CEL')
        policy.getWidgetHints().update(widget='cel', help=self.HelpText, open='True')
        self.cellWidget = UI4.FormMaster.KatanaWidgetFactory.buildWidget(scrollParent, policy)
        scrollLayout.addWidget(self.cellWidget)
        scrollLayout.addStretch(2)

    def getCellWidgetValue(self):
        """Returns the current CEL expression from the embedded editor."""
        return self.cellWidget._CelEditorFormWidget__buildValueFromPanels()


class expressionWindowUI(UI4.Tabs.BaseTab):
    """
    A small utility window to display the saved CEL expression from a loaded preset file.
    This is useful for quickly inspecting the query behind a saved preset.
    """

    def __init__(self, parent=None, listCombo=[]):
        super(expressionWindowUI, self).__init__(parent)
        self.parent = parent
        if self.parent:
            self.pathFile = self.parent.dirTxtName
            self.listCombo = listCombo
        self.initUI()

    def initUI(self):
        """Sets up the UI for the expression reader window."""
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

        self.setMinimumWidth(700)
        self.setMinimumHeight(100)
        self.setWindowTitle("Expression Reader")

    def typeChanged(self):
        """Called when the user selects a different preset from the dropdown."""
        self.lineEdit.clear()
        if self.comboBox.currentText() not in ("None", ""):
            fileName = os.path.join(self.pathFile, self.comboBox.currentText())
            try:
                with open(fileName, "r") as f:
                    # Safely read the first line, which contains the expression.
                    first_line = f.readline()
                    # Clean up the line by removing '#' and whitespace.
                    assetPath = first_line.replace("#", "").strip()
                    if assetPath:
                        self.lineEdit.setText(assetPath)
                    else:
                        self.lineEdit.setText("No expression found in file.")
            # REFACTOR: Catch specific exceptions instead of a generic 'except'.
            except IOError as e:
                self.lineEdit.setText("Error reading file: {}".format(e))

    def exitFunc(self):
        """Closes the window and clears the reference in the parent."""
        self.parent.expressionWindow.close()
        self.parent.expressionWindow = None


class displayGeoUI(QMainWindow):
    """
    The main class for the 'displayGeo' Katana Panel.
    It constructs the UI and contains all the logic for interacting with the scene.
    """

    def __init__(self, parent=None):
        super(displayGeoUI, self).__init__(parent)

        # --- State and Katana Integration ---
        # Get a handle to the standard viewer visibility and render working sets.
        self.workingSet = WorkingSetManager.WorkingSetManager.getOrCreateWorkingSet(
            WorkingSetManager.WorkingSetManager.ViewerVisibilityWorkingSetName)
        self.workingSetRender = WorkingSetManager.WorkingSetManager.getOrCreateWorkingSet(
            WorkingSetManager.WorkingSetManager.RenderWorkingSetName)
        self.sg = ScenegraphManager.getActiveScenegraph()

        # --- UI and Data State ---
        self.collectionNameList = ["None"]

        # REFACTOR: Use a set to manage active expressions for robust addition/removal in "Additive Mode".
        # This is far more reliable than string manipulation.
        self.active_expressions = set()
        self.expressionToWrite = ""  # The final, combined string for display/saving.

        self.expressionAllLight = "((/root//*{attr(\"type\") == \"light\"}))"
        self.dirTxtName = "/tmp"  # Default directory for presets.
        self.listOfTxtFiles = ["None"]
        self.expressionWindow = None

        # Initialize the list of visible paths with what's currently in the working set.
        currentPaths = self.workingSet.getLocationsByState(WorkingSet.WorkingSet.State.Included)
        self.allPath = list(currentPaths)  # The master list of all paths to make visible.
        self.renderPaths = []

        # --- Settings File Management ---
        self.settingFilePath = os.path.join('/homes', os.environ.get('USER', 'defaultuser'), 'displayGeo')
        self.settingFileName = os.path.join(self.settingFilePath, "setting.yaml")

        # --- Initialization ---
        self._initialize_settings()
        self.initUI()
        self.getCollections()  # Populate dynamic UI elements after the UI is built.

    def _initialize_settings(self):
        """Handles the creation and reading of the YAML settings file for the preset directory."""
        if not os.path.isfile(self.settingFileName):
            try:
                if not os.path.isdir(self.settingFilePath):
                    os.makedirs(self.settingFilePath)
                with open(self.settingFileName, 'w') as fp:
                    dictToWrite = {"dirFiles": {"dirOfTxtFile": self.dirTxtName}}
                    yaml.dump(dictToWrite, fp)
                os.chmod(self.settingFileName, 0o0775)
            except (IOError, OSError) as e:
                print("Warning: Could not create settings file at " + str(self.settingFileName) + ": " + str(e))

        try:
            # Safely read the setting file.
            self.dirTxtName = self.yamlReadFile(file=self.settingFileName)[0]
            if not self.dirTxtName:
                self.dirTxtName = "/tmp"
        except (IOError, IndexError, yaml.YAMLError) as e:
            print("Warning: Could not read settings from" + str(self.settingFileName) + ", defaulting to /tmp. Error: " + str(e))
            self.dirTxtName = "/tmp"

    def initUI(self):
        """Constructs all the widgets and layouts for the main panel."""
        # Menubar setup
        self.bar = self.menuBar()
        self.fileBar = self.bar.addMenu("&Advanced")
        self.setDirAction = QAction('&Set Preset Directory', self)
        self.setDirAction.setShortcut("Ctrl+T")
        self.setDirAction.triggered.connect(self.setDirTxtFiles)
        self.fileBar.addAction(self.setDirAction)
        self.expressionAction = QAction('&Read Expression', self)
        self.expressionAction.setShortcut("Ctrl+W")
        self.expressionAction.triggered.connect(self.displayExpressionWindow)
        self.fileBar.addAction(self.expressionAction)

        # Main layout
        self.centralWidget = QWidget()
        self.mainVBoxLayout = QVBoxLayout(self.centralWidget)
        self.setCentralWidget(self.centralWidget)
        self.mainGridLayout = QGridLayout()
        self.mainVBoxLayout.addLayout(self.mainGridLayout)

        # --- Widget Creation ---
        self.celCheckBox = QCheckBox("Use CEL")
        self.childCheckBox = QCheckBox("Include Children")
        self.childCheckBox.setToolTip(
            "Finds all children of matched locations using CEL '//*'. This is much faster than Python recursion.")
        self.addCheckBox = QCheckBox("Additive Mode")

        self.nameLabel = QLabel('Name')
        self.nameLineEdit = QLineEdit()
        self.resetName = QPushButton('Reset')

        self.typeLabel = QLabel("Type")
        self.typeLayout = QHBoxLayout()
        self.typeBox = QComboBox()
        self.typeBox.addItems(typeList)
        self.typeLineEdit = QLineEdit()
        self.typeLineEdit.setReadOnly(True)
        self.typeLayout.addWidget(self.typeBox)
        self.typeLayout.addWidget(self.typeLineEdit)
        self.typeReset = QPushButton("Reset")

        self.collectionNameLabel = QLabel("Collection")
        self.collectionComboBox = QComboBox()

        self.pathLabel = QLabel('Path')
        self.pathLineEdit = fileEdit(self)
        self.resetPath = QPushButton('Reset')

        self.renderCheck = QCheckBox("Set Render Visibility")

        self.displayButton = QPushButton('Display')
        self.unDisplayButton = QPushButton('Hide')
        self.resetButton = QPushButton('Reset All')

        self.saveFileButton = QPushButton("Save Preset")
        self.loadFileButton = QPushButton("Load Preset")

        self.presetComboBox = QComboBox()
        self.createPresetList()  # Populate with initial presets

        self.selectButton = QPushButton("Select & Frame")
        self.selectButton.setToolTip(
            "Selects the currently displayed items in the scenegraph and frames them in the viewer.")

        self.cellWidget = CELPanel(self)
        self.cellWidget.setVisible(False)

        self.expressionLineEdit = QLineEdit()
        self.expressionLineEdit.setReadOnly(True)
        self.expressionLineEdit.setToolTip("Shows the final combined CEL expression being used.")
        self.mainVBoxLayout.addWidget(self.expressionLineEdit)

        # --- Layout ---
        self.displayOnOffGridLayout = QGridLayout()
        self.displayOnOffGridLayout.setContentsMargins(0, 0, 0, 0)
        self.displayOnOffGridLayout.addWidget(self.displayButton, 0, 0)
        self.displayOnOffGridLayout.addWidget(self.unDisplayButton, 0, 1)

        self.saveLoadGridLayout = QGridLayout()
        self.saveLoadGridLayout.setContentsMargins(0, 0, 0, 0)
        self.saveLoadGridLayout.addWidget(self.saveFileButton, 0, 0)
        self.saveLoadGridLayout.addWidget(self.loadFileButton, 0, 1)

        # Add all widgets to the main grid layout
        self.mainGridLayout.addWidget(self.celCheckBox, 0, 0, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.addCheckBox, 0, 1, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.childCheckBox, 0, 2, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.nameLabel, 1, 0)
        self.mainGridLayout.addWidget(self.nameLineEdit, 1, 1)
        self.mainGridLayout.addWidget(self.resetName, 1, 2)
        self.mainGridLayout.addWidget(self.typeLabel, 2, 0)
        self.mainGridLayout.addLayout(self.typeLayout, 2, 1)
        self.mainGridLayout.addWidget(self.typeReset, 2, 2)
        self.mainGridLayout.addWidget(self.collectionNameLabel, 3, 0)
        self.mainGridLayout.addWidget(self.collectionComboBox, 3, 1)
        self.mainGridLayout.addWidget(self.pathLabel, 4, 0)
        self.mainGridLayout.addWidget(self.pathLineEdit, 4, 1)
        self.mainGridLayout.addWidget(self.resetPath, 4, 2)
        self.mainGridLayout.addWidget(self.cellWidget, 5, 0, 1, 3)
        self.mainGridLayout.addWidget(self.renderCheck, 6, 0)
        self.mainGridLayout.addLayout(self.displayOnOffGridLayout, 7, 0)
        self.mainGridLayout.addItem(QSpacerItem(40, 10, QSizePolicy.Minimum, QSizePolicy.Expanding), 7, 1)
        self.mainGridLayout.addWidget(self.resetButton, 7, 2)
        self.mainGridLayout.addLayout(self.saveLoadGridLayout, 8, 0)
        self.mainGridLayout.addWidget(self.presetComboBox, 8, 1)
        self.mainGridLayout.addWidget(self.selectButton, 8, 2)

        # --- Connections ---
        self.displayButton.clicked.connect(self.displayModel)
        self.unDisplayButton.clicked.connect(self.displayModel)
        self.resetButton.clicked.connect(self.resetDisplay)
        self.resetName.clicked.connect(self.resetTheName)
        self.resetPath.clicked.connect(self.resetThePath)
        self.typeBox.currentTextChanged.connect(self.typeChanged)
        self.typeReset.clicked.connect(self.typeReseted)
        self.saveFileButton.clicked.connect(self.saveDisplayFile)
        self.loadFileButton.clicked.connect(self.loadDisplayFile)
        # REFACTOR: Connect 'Select' to its own dedicated, faster function.
        self.selectButton.clicked.connect(self.selectCurrentPaths)
        self.celCheckBox.toggled.connect(self.celCheckBoxToggled)
        self.renderCheck.toggled.connect(self.setRender)
        self.presetComboBox.currentTextChanged.connect(self.displayChosenFile)
        self.collectionComboBox.addItems(self.collectionNameList)  # Populate after init

        self.setWindowTitle("Display Geo")
        Utils.EventModule.ProcessAllEvents()  # Ensure UI updates

    def displayExpressionWindow(self):
        """Shows or hides the helper window for reading expressions."""
        if self.expressionWindow is None:
            self.expressionWindow = expressionWindowUI(self, listCombo=self.listOfTxtFiles)
            self.expressionWindow.move(700, 300)
            self.expressionWindow.setWindowFlags(Qt.Tool)
            self.expressionWindow.show()
        else:
            self.expressionWindow.close()

    def getCollections(self):
        """
        Fetches the list of collections from the current scene graph state.
        REFACTOR: Gets a fresh scenegraph producer on-demand to avoid using stale data
        if the Katana recipe changes.
        """
        self.collectionNameList = ["None"]
        time = NodegraphAPI.GetCurrentTime()
        rootNode = NodegraphAPI.GetNode('root')
        producer = Nodes3DAPI.GetGeometryProducer(rootNode, time)

        if producer:
            collectionsAttr = producer.getAttribute("collections")
            if collectionsAttr:
                for i in range(collectionsAttr.getNumberOfChildren()):
                    self.collectionNameList.append(collectionsAttr.getChildName(i))

        # Update the combobox if it has already been created.
        if hasattr(self, 'collectionComboBox'):
            current_selection = self.collectionComboBox.currentText()
            self.collectionComboBox.clear()
            self.collectionComboBox.addItems(self.collectionNameList)
            # Try to restore previous selection
            index = self.collectionComboBox.findText(current_selection)
            if index != -1:
                self.collectionComboBox.setCurrentIndex(index)

    def celCheckBoxToggled(self, is_checked):
        """Switches the UI between the simplified form and the advanced CEL editor."""
        self.cellWidget.setVisible(is_checked)
        is_form_visible = not is_checked
        # Toggle visibility of all form-related widgets.
        for widget in [self.childCheckBox, self.nameLabel, self.nameLineEdit, self.resetName,
                       self.typeLabel, self.typeLayout, self.typeReset, self.collectionNameLabel,
                       self.collectionComboBox, self.pathLabel, self.pathLineEdit, self.resetPath]:
            widget.setVisible(is_form_visible)

    def setRender(self):
        """Updates the render working set based on the currently visible paths in `self.allPath`."""
        self.workingSetRender.clear()
        self.renderPaths = []
        if self.renderCheck.isChecked() and self.allPath:
            # Add all lights to the render set for context.
            light_collector = UI4.Widgets.CollectAndSelectInScenegraph(self.expressionAllLight, "/root")
            light_paths = light_collector.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())

            self.renderPaths.extend(light_paths)
            self.renderPaths.extend(self.allPath)

            # The 'include child' logic is already handled by the CEL query that produced self.allPath.
            # No need for manual recursion.
            self.workingSetRender.setLocationStates(self.renderPaths, WorkingSet.WorkingSet.State.Included)

    def setDirTxtFiles(self):
        """Opens a file dialog to allow the user to select a new directory for presets."""
        new_dir = QFileDialog.getExistingDirectory(self, 'Select Preset Directory', self.dirTxtName,
                                                   QFileDialog.ShowDirsOnly)
        if new_dir:  # Proceed only if a directory was chosen.
            self.dirTxtName = str(new_dir)
            self.createPresetList(newPath=True)

    def createPresetList(self, newPath=False):
        """
        Updates the preset dropdown list. If `newPath` is True, it also saves the new
        directory path to the settings file.
        """
        if newPath:
            dictToWrite = {"dirFiles": {"dirOfTxtFile": self.dirTxtName}}
            try:
                with open(self.settingFileName, 'w') as yamlFile:
                    yaml.dump(dictToWrite, yamlFile)
            except IOError as e:
                print("Error saving settings file: " + str(e))

        self.listOfTxtFiles = ["None"]
        if os.path.isdir(self.dirTxtName):
            try:
                fileInDir = os.listdir(self.dirTxtName)
                self.listOfTxtFiles += sorted([f for f in fileInDir if f.endswith(".txt")])
            except OSError as e:
                print("Error reading directory " +str(self.dirTxtName) +": " + str(e))

        self.presetComboBox.clear()
        self.presetComboBox.addItems(self.listOfTxtFiles)

    def saveDisplayFile(self):
        """Saves the current visible set and its corresponding CEL expression to a preset file."""
        fileName, _ = QFileDialog.getSaveFileName(self, 'Save Preset File', self.dirTxtName, "Text files (*.txt)")
        if not fileName:  # User cancelled the dialog.
            return

        if not fileName.endswith(".txt"):
            fileName += ".txt"

        try:
            with open(fileName, "w") as f:
                # First line is always the master expression, commented out.
                f.write("# {} #\n".format(self.expressionToWrite))

                # REFACTOR: Do not delete the file if `self.allPath` is empty.
                # Saving an empty set is a valid user action.
                if self.allPath:
                    f.write("\n".join(self.allPath))
                    f.write("\n")  # Ensure trailing newline for cleanliness.
        except IOError as e:
            print("Error writing to file " + fileName + ": " + str(e))
            return

        self.createPresetList()
        # Automatically select the newly saved file in the combobox.
        self.presetComboBox.setCurrentText(os.path.basename(fileName))

    def loadDisplayFile(self):
        """Opens a file dialog to load a preset file."""
        inputFileName, _ = QFileDialog.getOpenFileName(self, 'Load Preset File', self.dirTxtName, "Text files (*.txt)")
        if not inputFileName:
            return

        self._load_paths_from_file(inputFileName)
        self.presetComboBox.setCurrentText(os.path.basename(inputFileName))

    def displayChosenFile(self):
        """Loads a preset that the user selected from the dropdown menu."""
        current_file = self.presetComboBox.currentText()
        if current_file and current_file != "None":
            inputFileName = os.path.join(self.dirTxtName, current_file)
            self._load_paths_from_file(inputFileName)
        else:
            self.resetDisplay()

    def _load_paths_from_file(self, filepath):
        """Helper function containing the core logic for parsing and applying a preset file."""
        self.resetDisplay(keep_render_checked=self.renderCheck.isChecked(),
                          keep_additive_checked=self.addCheckBox.isChecked())

        try:
            with open(filepath, "r") as f:
                lines = f.readlines()
        except IOError as e:
            print("Error reading file " + filepath + ": " + str(e))
            return

        if not lines:
            return

        # Parse the expression from the first line.
        expression_line = lines[0].replace("#", "").strip()
        self.expressionToWrite = expression_line
        self.expressionLineEdit.setText(expression_line)
        # Re-populate the active expression set for consistency in additive mode.
        self.active_expressions = {part.strip() for part in expression_line.split('+') if part.strip()}

        # Subsequent lines are scenegraph paths.
        assetPaths = [line.strip() for line in lines[1:] if line.strip()]

        if self.addCheckBox.isChecked():
            # In additive mode, add new paths to any existing ones.
            self.allPath.extend(assetPaths)
            self.allPath = sorted(list(set(self.allPath)))  # Ensure uniqueness
        else:
            self.allPath = assetPaths

        self._update_visibility_state()

    # --- Simple UI Helper Methods ---
    def typeReseted(self):
        """Resets the type selection controls."""
        self.typeBox.setCurrentText('None')
        self.typeLineEdit.setText("")

    def typeChanged(self):
        """Appends the selected type from the dropdown to the read-only line edit."""
        current_type = self.typeBox.currentText()
        if current_type != "None":
            existing_text = self.typeLineEdit.text()
            if existing_text:
                if current_type not in existing_text.split(';'):
                    self.typeLineEdit.setText(existing_text + ";" + current_type)
            else:
                self.typeLineEdit.setText(current_type)

    def resetDisplay(self, keep_render_checked=False, keep_additive_checked=False):
        """Resets the UI and clears all visibility states."""
        self.workingSet.clear()
        self.workingSetRender.clear()
        self.displayViewer(False)
        self.nameLineEdit.setText("")
        self.pathLineEdit.setText('')
        self.typeBox.setCurrentText('None')
        self.typeLineEdit.setText("")
        self.collectionComboBox.setCurrentText("None")

        if not keep_additive_checked:
            self.allPath = []
            self.renderPaths = []
            self.active_expressions.clear()
            self.expressionToWrite = ""
            self.expressionLineEdit.clear()

        if not keep_render_checked:
            self.renderCheck.setChecked(False)

    def resetTheName(self):
        self.nameLineEdit.setText("")

    def resetThePath(self):
        self.pathLineEdit.setText("")


    def yamlReadFile(self, file, module='dirFiles', dictMode=False):
        """Utility to read data from the YAML settings file."""
        with open(file) as f:
            dictionary = yaml.load(f, Loader=yaml.FullLoader)
            if dictMode:
                return dictionary[module]
            else:
                return [dictionary[module][key] for key in sorted(dictionary[module].keys())]


    # --- Core Logic Methods ---

    def selectCurrentPaths(self):
        """
        REFACTOR: New dedicated function for selection and framing.
        This is much faster than re-running the query, as it acts on the already-found paths.
        """
        if not self.allPath:
            print("No paths to select.")
            return

        self.sg.clearSelection()
        self.sg.addSelectedLocations(self.allPath, extend=False)

        # Frame the new selection in the primary viewer.
        tab = UI4.App.Tabs.FindTopTab('Viewer')
        if tab:
            viewport = tab.getViewportWidgetByIndex(viewportIndex=0, viewerDelegate=tab.getViewerDelegateByIndex(0))
            if viewport:
                # Simulating a key press is a robust way to trigger Katana's internal framing logic.
                keyEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_F, Qt.NoModifier)
                QCoreApplication.postEvent(viewport, keyEvent)


    def _build_expression_from_form(self):
        """
        REFACTOR: New helper function to construct a CEL expression from the UI form fields.
        This greatly simplifies the main `displayModel` function and centralizes query logic.
        """
        parts = []
        nameInNode = self.nameLineEdit.text()
        search_paths = self.pathLineEdit.text().split()
        type_list = [t for t in self.typeLineEdit.text().split(";") if t]
        collection = self.collectionComboBox.currentText()

        # Build expression for Name
        if nameInNode:
            # Python 2.7: Replaced f-string with str.format()
            base_expr = "//*[contains(name(), '{}')]".format(nameInNode)
            if search_paths:
                # Python 2.7: Replaced f-string in list comprehension with str.format()
                parts.extend(["(({}{}))".format(p, base_expr) for p in search_paths])
            else:
                # Python 2.7: Replaced f-string with str.format()
                parts.append("(/root{})".format(base_expr))

        # Build expression for Type
        if type_list:
            # Python 2.7: This is a special case for str.format(). To get literal curly braces { }
            # in the output, you must double them {{ }} in the template string.
            type_queries = ["{{attr(\"type\") == \"{}\"}}".format(t) for t in type_list]
            type_expr = " or ".join(type_queries)

            # Python 2.7: Replaced f-string with str.format()
            base_expr = "//*[{}]".format(type_expr)
            if search_paths:
                # Python 2.7: Replaced f-string in list comprehension with str.format()
                parts.extend(["(({}{}))".format(p, base_expr) for p in search_paths])
            else:
                # Python 2.7: Replaced f-string with str.format()
                parts.append("(/root{})".format(base_expr))

        # Build expression for Collection
        if collection != "None":
            # Python 2.7: Replaced f-string with str.format()
            # The dollar sign '$' is treated as a literal character.
            parts.append("(/${})".format(collection))

        # Combine all parts of the query
        final_query = " + ".join(parts)

        # REFACTOR: Centralized 'include child' logic. Let CEL do the heavy lifting.
        # This is massively more performant than Python recursion.
        if self.childCheckBox.isChecked() and final_query:
            # Wrap the existing query and add the recursive 'all children' selector.
            # Python 2.7: Replaced f-string with str.format()
            return "({})//*".format(final_query)

        return final_query


    def _update_visibility_state(self):
        """Helper to apply the `self.allPath` list to the working sets and update the viewer."""
        # Set the viewer visibility working set.
        self.workingSet.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.Included)

        # Update the render working set if the checkbox is active.
        if self.renderCheck.isChecked():
            self.setRender()

        # Tell the viewer to respect the working set.
        self.displayViewer(True)


    def displayModel(self):
        """
        The primary logic function, triggered by 'Display' and 'Hide'.
        REFACTOR: This function now acts as a high-level coordinator.
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            nameSender = self.sender().objectName()

            # Step 1: Determine the expression for this single action from the UI state.
            current_expression = ""
            if self.celCheckBox.isChecked():
                current_expression = self.cellWidget.getCellWidgetValue()
            else:
                current_expression = self._build_expression_from_form()

            if not current_expression:
                print("No query specified. Please fill the form or use CEL.")
                return

            # Step 2: Update the master set of active expressions based on the mode.
            if self.addCheckBox.isChecked():
                if nameSender == 'Hide':
                    self.active_expressions.discard(current_expression)
                else:  # 'Display'
                    self.active_expressions.add(current_expression)
            else:  # Not in additive mode, so replace the current set.
                if nameSender == 'Hide':
                    self.active_expressions.clear()
                else:  # 'Display'
                    self.active_expressions = {current_expression}

            # Step 3: Build the final, combined query and update the display string.
            final_query = " + ".join(sorted(list(self.active_expressions)))
            self.expressionToWrite = final_query
            self.expressionLineEdit.setText(final_query)

            # Step 4: Execute the final query to get all required scene paths.
            if final_query:
                collector = UI4.Widgets.CollectAndSelectInScenegraph(final_query, "/root")
                self.allPath = collector.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
            else:
                self.allPath = []

            # Step 5: Update the working sets and viewer visibility with the results.
            self.workingSet.clear()
            self._update_visibility_state()

        finally:
            # Always restore the cursor, even if an error occurs.
            QApplication.restoreOverrideCursor()


    def displayViewer(self, state=False):
        """Toggles the viewer's working set visibility mode on or off."""
        self.sg.setViewerVisibilityFollowingWorkingSet(state)


# --- Katana Plugin Registration ---
# This is the standard mechanism for telling Katana about the new panel.
# It can be launched from the 'Tabs' menu as 'displayGeo' or 'Custom/displayGeo'.
PluginRegistry = [
    ('KatanaPanel', 2.0, 'displayGeo', displayGeoUI),
    ('KatanaPanel', 2.0, 'Custom/displayGeo', displayGeoUI),
]
