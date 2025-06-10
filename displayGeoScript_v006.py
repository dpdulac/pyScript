
# --- START OF FILE displayGeoScript.py ---
"""
Katana Panel for Simplified Geometry Visibility Management.

This script provides a custom panel for the Katana user interface, designed to
streamline the process of showing, hiding, and selecting objects in the
viewer and for rendering. It acts as a user-friendly front-end for constructing
and applying CEL (Collection Expression Language) statements to Katana's
Working Sets.

Instead of manually writing complex CEL expressions, users can find and display
geometry based on simple criteria such as name, scenegraph type, scene collection,
or parent path. The tool also supports saving and loading visibility presets,
making it easy to switch between different display configurations.

Key Features:
    - Simple Search: Find locations by name, type, collection, or starting path.
    - Advanced CEL Mode: A dedicated CEL editor for complex, custom queries.
    - Additive Mode: Either replace the current visible set or add/remove
      from it.
    - Viewer & Render Control: Manages both the Viewer Visibility and Render
      Working Sets.
    - Include Children: Option to automatically include all descendants of
      matched locations.
    - Save/Load Presets: Save visibility configurations to text files and quickly
      load them from a dropdown menu.
    - Configurable Preset Directory: Set a custom directory for saving and
      loading preset files.
    - Select & Frame: Select the matched objects in the Scene Graph and frame
      them in the Viewer.
    - Expression Feedback: Displays the generated CEL expression used for the
      current operation.

Usage:
    1. Launch the panel from the Katana UI via 'Tabs > Custom > displayGeo'.
    2. Use the input fields to define your search criteria:
        - Name: A string to match in the object's name (e.g., "_hiShape").
        - Type: Select one or more geometry types from the dropdown.
        - Collection: Select a pre-existing scene collection.
        - Path: A space-separated list of scenegraph paths to search within.
          (You can drag and drop paths from the Scene Graph).
    3. Click 'Display' to make the matched objects visible or 'Hide' to hide them.
    4. Use the 'Add Mode' checkbox to accumulate selections.
    5. Check 'render' to apply the same visibility rules to the Render
       Working Set.
    6. Use 'Save' to store the current visible set and its expression to a .txt
       file. Use 'Load' or the preset dropdown to restore a saved state.

Configuration:
    The directory for preset files can be set via the 'Advanced > set file dir'
    menu action (Shortcut: Ctrl+T). This setting is stored in a `setting.yaml`
    file located in `~/displayGeo/`.

Dependencies:
    - PyQt5 / PySide2 (for Python 3+) or PyQt4 / PySide (for Python 2.7)
    - PyYAML
    - Katana API (version 3.0+ for current script structure with PyQt5/PySide2)

Note on Python 2.7 and Python 3.+ Compatibility:
This script uses PyQt5 and modern Katana API calls (e.g., UI4.FormMaster, WorkingSetManager).
Katana 3.0+ typically runs on Python 3+ and uses PyQt5 or PySide2.
Older Katana versions (e.g., 2.x) might use Python 2.7 and PyQt4 or PySide.
Directly making this *single* script compatible with both Python 2.7 and Python 3.+
while retaining its Katana UI integration is highly challenging due to fundamental
differences in the underlying Katana API versions and Qt bindings.
The following optimizations primarily address `print` statements and `super()`
calls for basic Python 2/3 compatibility, but extensive modifications (e.g.,
conditional imports for PyQt/PySide, potential API rewrites) would be
necessary for full cross-version Katana functionality.
For true compatibility, it's generally recommended to maintain separate versions
of the script for different major Katana environments or use a compatibility
layer if the API differences are minor.
"""

# Import necessary modules
# For Python 2.7, `from __future__ import print_function` would be needed for print() as a function.
# However, for broader compatibility, we'll explicitly use compatible print statements later.
from PyQt5.QtGui import QKeyEvent  # Imports QKeyEvent for simulating key presses (e.g., for framing in viewer).
from PyQt5.QtWidgets import QLineEdit, QMainWindow, QAction, QGridLayout, QWidget, QCheckBox, QLabel, QPushButton, \
    QHBoxLayout, QComboBox, QSpacerItem, QSizePolicy, QFileDialog, QApplication, QScrollArea, QVBoxLayout, \
    QDialog  # Explicitly import used widgets for clarity and to avoid potential conflicts with `*` if specific names are masked.
from PyQt5.QtCore import QEvent, QCoreApplication, \
    Qt  # Imports QEvent for event handling, QCoreApplication for event loop management, and Qt for various constants (e.g., alignment).

from Katana import NodegraphAPI, ScenegraphManager, Nodes3DAPI, Utils, WorkingSet, WorkingSetManager, \
    UI4  # Imports core Katana API modules.
# QT4FormWidgets and QtWidgets are specific to Katana's internal UI framework, and might vary across versions.
# For modern Katana (PyQt5/PySide2 based), UI4 is the primary entry point for custom UI.
# QT4FormWidgets is often an alias or legacy component for older Katana versions or specific internal needs.
# Keeping it for now as it's in the original.
from Katana import QT4FormWidgets, QtWidgets

import sys, os, \
    yaml  # Imports standard Python modules: sys for system-specific parameters, os for operating system interactions (e.g., file paths), and yaml for YAML parsing.

# Global variable to hold an instance of the main UI window, used for potential re-instantiation.
ex = None

# List of common scenegraph types used for filtering geometry.
typeList = ["None", "subdmesh", "polymesh", "pointcloud", "nurbspatch", "curves", "locator", "assembly", "component",
            "group", "light", "light filter", "light filter reference", "camera",
            "volume", "openvdbasset", "material", "instance", "instance source", "instance array",
            "level-of-detail group", "level-of-detail",
            "render procedural", "render procedural args"]


class fileEdit(QLineEdit):
    """
    A QLineEdit subclass that accepts drag-and-drop text events from Katana,
    typically used for dropping scene graph paths.
    """

    def __init__(self, parent=None):
        # Python 2.7 and 3.+ compatible super() call
        super(fileEdit, self).__init__(parent)

        self.setDragEnabled(True)  # Enables drag functionality for the widget.

    def dragEnterEvent(self, event):
        """
        Handles the drag enter event. Accepts the proposed action if the dragged data contains text.
        """
        data = event.mimeData()  # Gets the MIME data from the drag event.
        if data.hasText():  # Checks if the MIME data contains plain text.
            event.acceptProposedAction()  # Accepts the drag event, indicating that a drop is possible.

    def dragMoveEvent(self, event):
        """
        Handles the drag move event. Accepts the proposed action if the dragged data contains text.
        This allows visual feedback (e.g., showing a copy cursor) while dragging.
        """
        data = event.mimeData()  # Gets the MIME data from the drag event.
        if data.hasText():  # Checks if the MIME data contains plain text.
            event.acceptProposedAction()  # Accepts the drag move event.

    def dropEvent(self, event):
        """
        Handles the drop event. Extracts text data from the dropped item and sets it as the QLineEdit's text.
        """
        data = event.mimeData()  # Gets the MIME data from the drop event.
        if data.hasText():  # Checks if the MIME data contains plain text.
            filepath = data.text()  # Extracts the text content from the MIME data.
            self.setText(filepath)  # Sets the extracted text as the content of the QLineEdit.


class CELPanel(QScrollArea):
    """
    A QScrollArea that embeds and manages a Katana CEL editor widget,
    providing a dedicated area for advanced CEL expressions.
    """

    def __init__(self, parent):
        # Python 2.7 and 3.+ compatible super() call
        super(CELPanel, self).__init__(parent)  # Initializes the QScrollArea base class.
        scrollParent = QWidget(self)  # Creates a QWidget as the container for the CEL editor.
        self.setWidget(scrollParent)  # Sets the scrollParent widget as the scroll area's child widget.
        self.setWidgetResizable(True)  # Makes the widget inside the scroll area resizable.
        self.setFrameStyle(self.NoFrame)  # Removes the frame around the scroll area.
        self.HelpText = '\nUse this as a convenience for searching within your scenegraph with CEL.\n\n'  # Help text for the CEL editor.
        scrollLayout = QVBoxLayout(scrollParent)  # Creates a vertical layout for the scrollParent.
        scrollLayout.addStretch()  # Adds a stretch to push content to the top.
        scrollLayout.setSpacing(2)  # Sets spacing between widgets in the layout.
        scrollLayout.setContentsMargins(2, 2, 2, 2)  # Sets margins around the layout's contents.
        policyData = dict(CEL='')  # Initializes a dictionary for the policy data, containing an empty CEL string.
        rootPolicy = QT4FormWidgets.PythonValuePolicy('cels',
                                                      policyData)  # Creates a PythonValuePolicy, which is used by Katana's FormMaster to build widgets from data.
        policy = rootPolicy.getChildByName('CEL')  # Gets the child policy specifically for the 'CEL' key.
        policy.getWidgetHints().update(widget='cel', help=self.HelpText,
                                       open='True')  # Updates widget hints to specify it's a 'cel' widget, provide help text, and indicate it should be open.
        self.cellWidget = UI4.FormMaster.KatanaWidgetFactory.buildWidget(scrollParent,
                                                                         policy)  # Builds the Katana CEL editor widget using the FormMaster.
        scrollLayout.addWidget(self.cellWidget)  # Adds the CEL editor widget to the layout.
        scrollLayout.addStretch(2)  # Adds another stretch to push content to the bottom.

    def getCellWidgetValue(self):
        """
        Retrieves the current CEL expression from the embedded CEL editor widget.
        """
        # This accesses a private method `_CelEditorFormWidget__buildValueFromPanels()`.
        # While it works, relying on private methods can make code brittle if the Katana API changes.
        return self.cellWidget._CelEditorFormWidget__buildValueFromPanels()


class expressionWindowUI(QMainWindow):
    """
    A simple QMainWindow to display the CEL expression from a saved preset file.
    It allows users to inspect the expression that generated a saved selection.
    """

    def __init__(self, parent=None, listCombo=None):
        # Python 2.7 and 3.+ compatible super() call
        super(expressionWindowUI, self).__init__(parent)  # Initializes the QMainWindow base class.
        self.parent = parent  # Stores a reference to the parent widget.
        # Ensure listCombo is not None to prevent errors
        if listCombo is None:
            listCombo = []
        if self.parent is not None:
            self.pathFile = self.parent.dirTxtName  # Gets the directory for preset files from the parent.
            self.listCombo = listCombo  # Gets the list of preset file names from the parent.
        else:  # Handle case where parent is None
            self.pathFile = "/tmp"  # Default path
            self.listCombo = listCombo
        self.initUI()  # Calls the method to initialize the UI.

    def initUI(self):
        """
        Initializes the user interface for the expression reader window.
        """
        self.centralWidget = QWidget()  # Creates a central widget for the main window.
        self.mainGridLayout = QGridLayout(self.centralWidget)  # Creates a grid layout for the central widget.
        self.setCentralWidget(self.centralWidget)  # Sets the central widget.
        self.comboBox = QComboBox()  # Creates a QComboBox to select preset files.
        self.comboBox.addItems(self.listCombo)  # Populates the combo box with preset file names.
        self.lineEdit = QLineEdit()  # Creates a QLineEdit to display the expression.
        self.exitButton = QPushButton("Exit")  # Creates an Exit button.
        self.mainGridLayout.addWidget(self.comboBox, 0, 0, Qt.AlignLeft)  # Adds the combo box to the grid.
        self.mainGridLayout.addWidget(self.lineEdit, 1, 0)  # Adds the line edit to the grid.
        self.mainGridLayout.addWidget(self.exitButton, 2, 0, Qt.AlignRight)  # Adds the exit button to the grid.
        self.exitButton.clicked.connect(self.exitFunc)  # Connects the exit button to the exit function.
        self.comboBox.currentTextChanged.connect(
            self.typeChanged)  # Connects combo box text changes to update the expression.
        self.setMinimumWidth(700)  # Sets the minimum width of the window.
        self.setMinimumHeight(100)  # Sets the minimum height of the window.
        self.setWindowTitle("expression reader")  # Sets the window title.

    # display the expression in the lineEdit widget
    def typeChanged(self):
        """
        Displays the CEL expression from the selected preset file in the QLineEdit.
        """
        self.lineEdit.clear()  # Clears the current text in the line edit.
        selected_text = self.comboBox.currentText()  # Get selected text from combo box
        if selected_text != "None" and selected_text != "":  # Checks if a valid preset is selected.
            file_name = os.path.join(self.pathFile,
                                     selected_text)  # Constructs the full path to the preset file using os.path.join for better path handling.
            try:
                with open(file_name, "r") as f:  # Use 'with' statement for proper file closing.
                    # Reads the first line (which contains the expression) from the file.
                    # .strip() removes leading/trailing whitespace including newlines.
                    asset_path = f.readline().strip()
                # Displays the expression, removing '#' characters.
                # Optimized to use replace() once and strip() for whitespace.
                self.lineEdit.setText(asset_path.replace("#", "").strip())
            except IOError:  # Catch file I/O errors.
                self.lineEdit.setText("Error: Could not read file or file not found.")
            except Exception as e:  # Catch any other unexpected errors.
                self.lineEdit.setText("Error: {}".format(e))
        else:
            self.lineEdit.setText("")  # Clear if "None" or empty selected.

    def exitFunc(self):
        """
        Closes the expression reader window.
        """
        # Checks if the parent's expressionWindow attribute exists and is not None before trying to close it.
        if self.parent and self.parent.expressionWindow:
            self.parent.expressionWindow.close()  # Closes the window via the parent's reference.
            self.parent.expressionWindow = None  # Clears the reference in the parent.


class Dialog(QDialog):
    """A basic QDialog for displaying simple error messages."""

    def __init__(self):
        # Python 2.7 and 3.+ compatible super() call
        super(Dialog, self).__init__()  # Initializes the QDialog base class.

        self.setWindowTitle("ERROR")  # Sets the window title to "ERROR".
        self.mainLayout = QVBoxLayout()  # Creates a vertical layout.
        self.message = QLabel("Please Graph a node")  # Creates a label with an error message. (Typo: Graphe -> Grab)
        self.button = QPushButton("Close")  # Creates a close button.
        self.mainLayout.addWidget(self.message)  # Adds the message label to the layout.
        self.mainLayout.addWidget(self.button)  # Adds the button to the layout.
        self.setLayout(self.mainLayout)  # Sets the layout for the dialog.
        self.button.clicked.connect(self.close_clicked)  # Connects the button to the close function.

    def close_clicked(self):
        """
        Closes the dialog when the "Close" button is clicked.
        """
        self.close()  # Closes the dialog.


class displayGeoUI(QMainWindow):
    """
    The main application window for the displayGeo tool. It builds the UI,
    manages user input, and interacts with the Katana scene and Working Sets.
    """

    def __init__(self, parent=None):
        # Python 2.7 and 3.+ compatible super() call
        super(displayGeoUI, self).__init__(parent)  # Initializes the QMainWindow base class.

        # Working Set for Viewer Visibility
        self.workingSet = WorkingSetManager.WorkingSetManager.getOrCreateWorkingSet(
            WorkingSetManager.WorkingSetManager.ViewerVisibilityWorkingSetName)
        # Working Set for Render Visibility
        self.workingSetRender = WorkingSetManager.WorkingSetManager.getOrCreateWorkingSet(
            WorkingSetManager.WorkingSetManager.RenderWorkingSetName)

        self.sg = ScenegraphManager.getActiveScenegraph()  # Gets the active ScenegraphManager.

        # Collection list (initialized with "None")
        self.collectionNameList = ["None"]
        self.rootNode = NodegraphAPI.GetNode('root')  # Gets the root node of the Katana node graph.
        self.time = NodegraphAPI.GetCurrentTime()  # Gets the current time for scene evaluation.

        # Create producer
        self.producer = Nodes3DAPI.GetGeometryProducer(self.rootNode, self.time)
        if self.producer is None:
            dialogbox = Dialog()  # we subclasses QDialog into Dialog
            dialogbox.exec_()  # Shows an error dialog if no producer is available.
            self.close()  # Closes the main window.
            return

        # Get the collections names from the scene
        self.getCollections()  # Populates the collectionNameList.

        # Expression variables
        self.expression = ""  # Stores the currently generated CEL expression.
        self.expressionToWrite = ""  # Stores the expression to be written to file or in the lineEdit widget.
        self.expressionAllLight = "((/root//*{attr(\"type\") == \"light\"}))"  # A CEL expression to find all lights.

        self.dirTxtName = "/tmp"  # Default directory for text files (presets).
        self.listOfTxtFiles = ["None"]  # List of saved preset files.
        self.expressionWindow = None  # Reference to the expression reader window.

        # Check if there are paths already checked in the viewer working set
        currentPaths = self.workingSet.getLocationsByState(WorkingSet.WorkingSet.State.Included)
        if len(currentPaths) == 0:
            self.allPath = []  # Initializes allPath if no paths are currently included.
        else:
            self.allPath = list(currentPaths)  # Convert set-like object to list for consistent operations.
        self.renderPaths = []  # List to store paths for render working set.

        # Directory to put the setting.yaml file
        # Using `os.path.expanduser('~')` for cross-platform compatibility for home directory.
        self.settingFilePath = os.path.join(os.path.expanduser('~'),
                                            'displayGeo') + os.sep  # Ensure trailing separator.
        self.settingFileName = os.path.join(self.settingFilePath,
                                            "setting.yaml")  # Full path to the settings YAML file.

        # Check if the file/path exist; if not, create it
        if not os.path.isfile(self.settingFileName):
            if not os.path.isdir(self.settingFilePath):
                os.makedirs(self.settingFilePath)  # Creates the settings directory if it doesn't exist.
            try:
                # Use 'with' statement for file creation/writing for proper closing.
                with open(self.settingFileName, 'w') as fp:
                    pass  # Create an empty file.
                os.utime(self.settingFileName, None)  # Updates access and modification times.
                os.chmod(self.settingFileName,
                         0o0775)  # Sets file permissions (octal literal for Python 3, compatible with Python 2).

                # Default content for the settings file.
                dictToWrite = {"dirFiles": {"dirOfTxtFile": self.dirTxtName}}
                with open(self.settingFileName, 'w') as yamlFile:
                    yaml.dump(dictToWrite, yamlFile,
                              default_flow_style=False)  # Use default_flow_style=False for more readable YAML.
            except Exception as e:
                # print("Error creating settings file:", e) # For debugging
                pass  # Silently fail or log error

        # Read the preset directory from the settings file.
        # Ensure file exists before reading.
        if os.path.isfile(self.settingFileName):
            try:
                self.dirTxtName = self.yamlReadFile(file=self.settingFileName)[0]
            except Exception:
                # Handle cases where YAML might be malformed or empty, default to /tmp.
                self.dirTxtName = "/tmp"

        if not self.dirTxtName:  # Fallback to /tmp if the directory read is empty or None.
            self.dirTxtName = "/tmp"

        self.initUI()  # Calls the method to initialize the UI.

    def initUI(self):
        """
        Initializes the main user interface components of the displayGeo tool.
        """
        # Menubar
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

        self.mainGridLayout = QGridLayout()  # Creates the main grid layout for the UI controls.
        self.mainVBoxLayout.addLayout(self.mainGridLayout)

        # CEL check Box
        self.celCheckBox = QCheckBox("Use CEL")
        self.celCheckBox.setChecked(False)
        self.celCheckBox.setToolTip("check to use CEL statement")

        # Child check Box
        self.childCheckBox = QCheckBox("include child")
        self.childCheckBox.setChecked(True)
        self.childCheckBox.setToolTip("will add the child of all locations wanted")

        # Additive mode
        self.addCheckBox = QCheckBox("Add Mode")
        self.addCheckBox.setChecked(False)
        self.addCheckBox.setToolTip("Set additive mode")

        # Name input
        self.nameLabel = QLabel('Name')
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setToolTip('name or part of name to look for')
        self.nameLineEdit.setText("")
        self.resetName = QPushButton('ResetName')
        self.resetName.setToolTip("reset the name field")  # Updated tooltip for clarity

        # Type selection
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

        # Collections
        self.collectionNameLabel = QLabel("Collection")
        self.collectionComboBox = QComboBox()
        self.collectionComboBox.addItems(self.collectionNameList)
        self.collectionComboBox.setMaximumWidth(220)
        self.collectionComboBox.setObjectName("collectionComboBox")
        self.collectionComboBox.setToolTip("select a collection to add the displayed asset")

        # Path input (using custom fileEdit for drag and drop)
        self.pathLabel = QLabel('Path')
        self.pathLineEdit = fileEdit(self)
        self.pathLineEdit.setText("")
        self.pathLineEdit.setToolTip('path(s) from the sceneGraph where to match the name')
        self.resetPath = QPushButton('ResetPath')
        self.resetPath.setToolTip('empty the path')
        self.resetPath.setObjectName('resetPath')

        # Render control
        self.renderCheck = QCheckBox("render")
        self.renderCheck.setChecked(False)
        self.renderCheck.setToolTip("check to set render Included objects columns")

        # Display/Hide buttons
        self.displayOnOffGridLayout = QGridLayout()
        self.displayButton = QPushButton('Display')
        self.displayButton.setToolTip('Display the object containing the name in selected path')
        self.displayButton.setMaximumWidth(100)
        self.displayButton.setObjectName('Display')
        self.unDisplayButton = QPushButton('Hide')
        self.unDisplayButton.setToolTip('Hide the object(s) containing the name in selected path')
        self.unDisplayButton.setMaximumWidth(100)
        self.unDisplayButton.setObjectName('Hide')
        self.displayOnOffGridLayout.setContentsMargins(0, 0, 0, 0)
        self.displayOnOffGridLayout.addWidget(self.displayButton, 0, 0)
        self.displayOnOffGridLayout.addWidget(self.unDisplayButton, 0, 1)

        # Reset All button
        self.resetButton = QPushButton('Reset')
        self.resetButton.setMaximumWidth(200)
        self.resetButton.setToolTip('reset the name, path and undisplay all the displayed objects')

        # Save and Load Presets
        self.saveLoadGridLayout = QGridLayout()
        self.saveFileButton = QPushButton("Save")
        self.saveFileButton.setMaximumWidth(100)
        self.saveFileButton.setToolTip("save the asset display path to a file")
        self.loadFileButton = QPushButton("Load")
        self.loadFileButton.setMaximumWidth(100)
        self.loadFileButton.setToolTip("load the asset display path from a file")
        self.saveLoadGridLayout.setContentsMargins(0, 0, 0, 0)
        self.saveLoadGridLayout.addWidget(self.saveFileButton, 0, 0)
        self.saveLoadGridLayout.addWidget(self.loadFileButton, 0, 1)

        # Combobox for .txt file presets
        self.presetComboBox = QComboBox()
        self.presetComboBox.addItems(self.listOfTxtFiles)
        self.createPresetList()  # Initial population of preset list.

        # Select & Frame button
        self.selectButton = QPushButton("Select")
        self.selectButton.setMaximumWidth(200)
        self.selectButton.setToolTip("select the asset(s) in the scene viewer and focus on it/them")
        self.selectButton.setObjectName("selectButton")

        # CEL editor widget
        self.cellWidget = CELPanel(self)
        self.cellWidget.setMinimumWidth(600)
        self.cellWidget.setVisible(False)  # Initially hides the CEL panel.

        # Line edit to display the generated CEL expression
        self.expressionLineEdit = QLineEdit()
        self.expressionLineEdit.setReadOnly(True)  # Make it read-only
        self.expressionLineEdit.setPlaceholderText("Generated CEL Expression will appear here...")
        self.mainVBoxLayout.addWidget(self.expressionLineEdit)

        # Widget layout - Arranging all widgets in the main grid layout.
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
        # CEL widget spans multiple columns.
        self.mainGridLayout.addWidget(self.cellWidget, 4, 0, 1, 3)
        self.mainGridLayout.addWidget(self.pathLabel, 5, 0)
        self.mainGridLayout.addWidget(self.pathLineEdit, 5, 1)
        self.mainGridLayout.addWidget(self.resetPath, 5, 2)
        self.mainGridLayout.addWidget(self.renderCheck, 6, 0)
        self.mainGridLayout.addLayout(self.displayOnOffGridLayout, 7, 0)
        self.mainGridLayout.addItem(QSpacerItem(40, 10, QSizePolicy.Minimum, QSizePolicy.Expanding), 7,
                                    1)  # Spacer item.
        self.mainGridLayout.addWidget(self.resetButton, 7, 2)
        self.mainGridLayout.addLayout(self.saveLoadGridLayout, 8, 0)
        self.mainGridLayout.addWidget(self.presetComboBox, 8, 1)
        self.mainGridLayout.addWidget(self.selectButton, 8, 2)

        # Connections - Connecting signals to slots.
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

        self.setWindowTitle("display geo")  # Sets the main window title.

        # Processes any pending Katana events. This is important for UI responsiveness on startup.
        Utils.EventModule.ProcessAllEvents()

    def __del__(self):
        """
        Destructor for the class.
        This method is called when the object is about to be destroyed.
        It's generally not used for explicit cleanup of Qt widgets as their parent-child
        ownership model handles destruction, but could be used for other resource release.
        """
        pass

    def displayExpressionWindow(self):
        """
        Opens or closes the expression reader window.
        """
        if self.expressionWindow is None:  # If the window is not open.
            self.expressionWindow = expressionWindowUI(self, listCombo=self.listOfTxtFiles)  # Creates a new instance.
            self.expressionWindow.move(700, 300)  # Moves the window to a specific position.
            self.expressionWindow.setWindowFlags(Qt.Tool)  # Sets the window as a tool window.
            self.expressionWindow.show()  # Shows the window.
        else:
            self.expressionWindow.close()  # Closes the existing window.
            self.expressionWindow = None  # Clears the reference.

    def getCollections(self):
        """
        Populates the `collectionNameList` with names of collections found in the scene.
        """
        collectionsAttr = self.producer.getAttribute(
            "collections")  # Gets the "collections" attribute from the producer.
        if collectionsAttr is not None:  # Checks if the attribute exists.
            # Using list comprehension for conciseness.
            # getNumberOfChildren() and getChildName(i) are Katana API specific.
            self.collectionNameList.extend(
                [collectionsAttr.getChildName(i) for i in range(collectionsAttr.getNumberOfChildren())])

    def celCheckBoxToggled(self, s):
        """
        Toggles the visibility of standard search fields and the CEL editor based on the CEL checkbox state.
        """
        self.allPath = []  # Clears all selected paths.
        self.expression = ""  # Clears the current expression.
        self.expressionLineEdit.clear()  # Clear displayed expression

        # Determine visibility state based on checkbox 's' (True/False)
        cel_mode_active = bool(s)

        # Hide/show elements based on CEL mode
        self.cellWidget.setVisible(cel_mode_active)
        self.childCheckBox.setVisible(not cel_mode_active)
        self.nameLabel.setVisible(not cel_mode_active)
        self.nameLineEdit.setVisible(not cel_mode_active)
        self.resetName.setVisible(not cel_mode_active)
        self.typeLabel.setVisible(not cel_mode_active)
        self.typeBox.setVisible(not cel_mode_active)
        self.typeLineEdit.setVisible(not cel_mode_active)
        self.typeReset.setVisible(not cel_mode_active)
        self.collectionNameLabel.setVisible(not cel_mode_active)
        self.collectionComboBox.setVisible(not cel_mode_active)
        self.pathLabel.setVisible(not cel_mode_active)
        self.pathLineEdit.setVisible(not cel_mode_active)
        self.resetPath.setVisible(not cel_mode_active)

    def setRender(self):
        """
        Manages the Render Working Set based on the `renderCheck` checkbox state.
        If checked, includes current viewer visible paths and all lights.
        If unchecked, clears the Render Working Set.
        """
        self.renderPaths = []  # Clears the render paths.
        if self.renderCheck.isChecked():  # If render checkbox is checked.
            # Collect all lights in the scene using the predefined expression.
            wid = UI4.Widgets.CollectAndSelectInScenegraph(self.expressionAllLight, "/root")
            # `select=False` means it collects paths without immediately selecting them in the Scenegraph tab.
            lights_paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())
            self.renderPaths.extend(lights_paths)  # Use extend for efficiency.

            # Add currently included viewer paths to render paths.
            viewer_included_paths = self.workingSet.getLocationsByState(WorkingSet.WorkingSet.State.Included)
            self.renderPaths.extend(viewer_included_paths)  # Use extend.

            # If 'include child' is checked AND a collection is selected, recursively add children.
            # The original condition `self.collectionComboBox.currentText() != "None"` might be redundant here
            # as `recursiveFindPath` operates on the `self.renderPaths` which already contains specific paths.
            # However, keeping the original logic's intent.
            if self.childCheckBox.isChecked() and self.collectionComboBox.currentText() != "None":
                # This call modifies self.renderPaths in place.
                self.recursiveFindPath(self.producer, self.renderPaths)

            # Set the collected paths as included in the Render Working Set.
            # Convert to set first to remove duplicates, then back to list if order matters (WorkingSet expects iterable).
            self.workingSetRender.setLocationStates(list(set(self.renderPaths)), WorkingSet.WorkingSet.State.Included)
        else:
            self.workingSetRender.clear()  # Clears the Render Working Set.
            self.renderPaths = []  # Clears the local render paths list.

    def setDirTxtFiles(self):
        """
        Allows the user to select a directory for saving and loading preset text files.
        Updates the settings YAML file and recreates the preset list.
        """
        # QFileDialog.getExistingDirectory returns a string (Python 3) or QString (Python 2).
        # str() conversion for Python 2 compatibility (or implicit conversion in Python 3).
        selected_dir = str(
            QFileDialog.getExistingDirectory(self, 'Open Directory', self.dirTxtName, QFileDialog.ShowDirsOnly))

        if selected_dir:  # Ensure a directory was actually selected (not cancelled).
            self.dirTxtName = selected_dir
            self.createPresetList(newPath=True)  # Recreates the preset list, indicating a new path was set.

    def createPresetList(self, newPath=False):
        """
        Populates the preset combo box with .txt files from the `dirTxtName`.
        Optionally updates the settings YAML file if a new path is provided.
        """
        if newPath:  # If a new directory path was set.
            dictToWrite = {"dirFiles": {"dirOfTxtFile": self.dirTxtName}}  # Creates a dictionary for YAML output.
            try:
                # Use 'with' statement for proper file closing.
                with open(self.settingFileName, 'w') as yamlFile:
                    yaml.dump(dictToWrite, yamlFile,
                              default_flow_style=False)  # Use default_flow_style=False for more readable YAML.
            except Exception as e:
                # print("Error writing settings file:", e) # For debugging
                pass  # Silently fail or log error

        # Ensure the directory exists before trying to list its contents.
        if os.path.isdir(self.dirTxtName):
            fileInDir = os.listdir(self.dirTxtName)  # Gets all files in the preset directory.
            # Filter for .txt files and sort them.
            self.listOfTxtFiles = sorted([f for f in fileInDir if f.endswith(".txt")])
        else:
            self.listOfTxtFiles = []  # If directory doesn't exist, list is empty.

        # Always add "None" as the first option.
        self.listOfTxtFiles.insert(0, "None")

        self.presetComboBox.clear()  # Clears the combo box.
        self.presetComboBox.addItems(self.listOfTxtFiles)  # Adds the updated list of files.

    def saveDisplayFile(self):
        """
        Saves the currently included paths in the viewer working set and their generating expression to a .txt file.
        """
        allLoc = self.workingSet.getLocationsByState(
            WorkingSet.WorkingSet.State.Included)  # Gets all currently included locations.

        # QFileDialog.getSaveFileName returns a tuple; [0] gets the selected path string.
        # Ensure it's converted to a Python string from QString if in Python 2.
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save file', self.dirTxtName, "text files (*.txt)")
        file_path = str(file_path)  # Ensure it's a string for Python 2/3 compatibility.

        if not file_path:  # If the user cancelled the dialog.
            return

        if not file_path.endswith(".txt"):  # Ensures the file has a .txt extension.
            file_path += ".txt"

        # No need to check and remove if file exists; 'w' mode truncates/creates.
        try:
            with open(file_path, "w") as f:  # Use 'with' statement for proper file closing.
                if self.expressionToWrite:  # Writes the expression if available.
                    # Add a marker to easily identify and strip later.
                    f.write("#EXPRESSION#: " + self.expressionToWrite + "\n")
                else:
                    f.write("#EXPRESSION#: No expression found\n")  # Writes a placeholder if no expression.

                if allLoc:  # If there are locations to save.
                    for loc in allLoc:  # Writes each location to a new line.
                        f.write(loc + "\n")
        except Exception as e:
            # print("Error saving file:", e) # For debugging
            return  # Exit on error

        # If no locations were written and the file was just created with only expression, it's fine.
        # The original code would remove the file if `len(allLoc) == 0`.
        # Decided to keep the file with just the expression as it might still be useful.

        self.createPresetList()  # Refreshes the preset list in the UI.

        # Set the newly saved file as selected in the combo box.
        # Use os.path.basename to get just the filename.
        self.presetComboBox.setCurrentText(os.path.basename(file_path))

    def loadDisplayFile(self):
        """
        Loads display settings from a selected preset file, applies them to the viewer
        and render working sets (if applicable), and updates the UI.
        """
        # Temporarily disables viewer visibility following working set to avoid flickering.
        self.displayViewer(False)
        # Resets current display, preserving render and additive mode flags.
        # Pass current state of checkboxes directly.
        self.resetDisplay(excludeRender=self.renderCheck.isChecked(), deleteAllPath=not self.addCheckBox.isChecked())

        # Get file path from QFileDialog.getOpenFileName; [0] gets the path string.
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open file', self.dirTxtName, "text files (*.txt)")
        file_path = str(file_path)  # Convert to Python string.

        if not file_path:  # If the user cancelled.
            self.displayViewer(True)  # Re-enable viewer visibility.
            return

        try:
            with open(file_path, "r") as f:  # Use 'with' statement for proper file closing.
                lines = f.read().splitlines()
                # Skip the first line (expression) and take the rest as asset paths.
                asset_paths = lines[1:] if len(lines) > 1 else []

            if self.addCheckBox.isChecked():  # If in additive mode.
                self.allPath.extend(asset_paths)  # Use extend for efficiency.
            else:
                self.allPath = asset_paths  # Replaces existing paths with loaded ones.

            # Remove duplicates from `self.allPath` while preserving order (if important, otherwise use set).
            # For preserving order, one common pattern is:
            # seen = set()
            # self.allPath = [x for x in self.allPath if x not in seen and not seen.add(x)]
            # For simplicity, for now, just convert to set and back to list for uniqueness.
            self.allPath = list(set(self.allPath))

            self.workingSet.setLocationStates(self.allPath,
                                              WorkingSet.WorkingSet.State.Included)  # Sets the loaded paths as included in the viewer working set.

            if self.renderCheck.isChecked():  # If render is checked.
                self.setRender()  # Updates the render working set.

            self.displayViewer(True)  # Re-enables viewer visibility following working set.

            # Update the preset combo box to reflect the loaded file.
            self.presetComboBox.setCurrentText(os.path.basename(file_path))

        except IOError:
            # print("Error: Could not read file or file not found:", file_path) # For debugging
            self.expressionLineEdit.setText("Error: Could not load file.")
            self.displayViewer(True)  # Ensure viewer is re-enabled even on error.
        except Exception as e:
            # print("An unexpected error occurred:", e) # For debugging
            self.expressionLineEdit.setText("Error loading file: {}".format(e))
            self.displayViewer(True)  # Ensure viewer is re-enabled even on error.

    def displayChosenFile(self):
        """
        Loads and applies a display preset selected from the `presetComboBox`.
        Updates the viewer and render working sets, and displays the expression.
        """
        selected_text = str(self.presetComboBox.currentText())
        if selected_text != "None" and selected_text != "":  # Ensures a valid preset is selected.
            # Reset current display, preserving render and additive mode flags.
            self.resetDisplay(excludeRender=self.renderCheck.isChecked(),
                              deleteAllPath=not self.addCheckBox.isChecked())

            input_file_name = os.path.join(self.dirTxtName, selected_text)  # Constructs the full path.

            try:
                with open(input_file_name, "r") as f:  # Use 'with' statement for proper file closing.
                    lines = f.read().splitlines()
                    expression_line = lines[0] if lines else ""
                    asset_paths = lines[1:] if len(lines) > 1 else []

                if self.addCheckBox.isChecked():  # If in additive mode.
                    self.allPath.extend(asset_paths)  # Use extend.
                else:
                    self.allPath = asset_paths  # Replaces paths.

                self.allPath = list(set(self.allPath))  # Remove duplicates.

                # Display the expression, removing '#EXPRESSION#:' marker and '#' characters.
                # Use .replace() and .strip() for cleaner output.
                display_expr = expression_line.replace("#EXPRESSION#:", "").replace("#", "").strip()
                self.expressionLineEdit.setText(display_expr)

                self.workingSet.setLocationStates(self.allPath,
                                                  WorkingSet.WorkingSet.State.Included)  # Applies to viewer working set.

                if self.renderCheck.isChecked():  # If render is checked.
                    self.setRender()  # Updates render working set.

                self.displayViewer(True)  # Re-enables viewer visibility.

            except IOError:
                self.expressionLineEdit.setText("Error: Could not read selected file.")
                self.resetDisplay()  # Reset everything on error.
            except Exception as e:
                self.expressionLineEdit.setText("Error loading preset: {}".format(e))
                self.resetDisplay()  # Reset everything on error.
        else:
            self.resetDisplay()  # If "None" is selected, reset everything.

    def typeReseted(self):
        """
        Resets the type selection to "None" and clears the type line edit.
        """
        if self.typeLineEdit.text():  # Checks if there's text to clear (empty string is falsy).
            self.typeBox.setCurrentText('None')  # Sets combo box to "None".
            self.typeLineEdit.setText("")  # Clears line edit.

    def typeChanged(self):
        """
        Appends the currently selected type from `typeBox` to `typeLineEdit`,
        separated by a semicolon if `typeLineEdit` already has content.
        """
        current_type = str(self.typeBox.currentText())  # Ensure string type for Python 2/3 compatibility.
        if current_type != "None":  # Only act if a specific type is selected.
            current_line_edit_text = str(self.typeLineEdit.text())  # Ensure string type.
            if current_line_edit_text:  # If text already exists.
                self.typeLineEdit.setText(current_line_edit_text + ";" + current_type)  # Append with semicolon.
            else:
                self.typeLineEdit.setText(current_type)  # Set directly if empty.

    def resetDisplay(self, excludeRender=False, deleteAllPath=False):
        """
        Resets the display settings, clearing working sets, input fields, and expressions.
        `excludeRender`: If True, the render checkbox state is not changed.
        `deleteAllPath`: If True, `self.allPath` and `self.renderPaths` are always cleared.
        """
        self.workingSet.clear()  # Clears the viewer working set.
        self.workingSetRender.clear()  # Clears the render working set.
        self.displayViewer(False)  # Disables viewer visibility.
        self.nameLineEdit.setText("")  # Clears name field.
        self.pathLineEdit.setText('')  # Clears path field.
        self.typeBox.setCurrentText('None')  # Resets type combo box.
        self.typeLineEdit.setText("")  # Clears type line edit.
        self.collectionComboBox.setCurrentText("None")  # Resets collection combo box.

        if deleteAllPath:  # If forced to delete all paths (e.g., when not in additive mode).
            self.allPath = []  # Clears viewer paths.
            self.renderPaths = []  # Clears render paths.

        self.expression = ""  # Clears expression.
        self.expressionToWrite = ""  # Clears expression to write.
        self.expressionLineEdit.clear()  # Clears expression display.

        if not excludeRender:  # If not excluding render reset.
            self.renderCheck.setChecked(False)  # Unchecks render.

    def resetTheName(self):
        """
        Clears the text in the name input field.
        """
        self.nameLineEdit.setText("")

    def resetThePath(self):
        """
        Clears the text in the path input field.
        """
        self.pathLineEdit.setText("")

    def recursiveFindPath(self, producer, path_list):
        """
        Recursively finds all descendant paths for each given `path` in `path_list`
        and adds them to `path_list`. This is used to include children of selected items.

        Modifies `path_list` in place.
        """
        # Create a copy of the list to iterate over, as it will be modified during iteration.
        paths_to_process = list(path_list)

        for path in paths_to_process:
            prod = producer.getProducerByPath(path)
            if prod:  # Ensure producer exists for the path.
                self.recursiveFromPath(prod, path_list)  # Recursively adds children of that producer.
        # `path_list` is modified in place, so no return is strictly necessary for the caller,
        # but returning it can be clearer.
        return path_list

    def recursiveFromPath(self, producer, path_list):
        """
        Helper for `recursiveFindPath`. Recursively adds the current producer's full name
        and all its children's full names to `path_list`.

        Modifies `path_list` in place.
        """
        if producer is not None:
            full_name = producer.getFullName()
            if full_name not in path_list:  # Avoids duplicates.
                path_list.append(full_name)  # Adds the current producer's full name.

            for child in producer.iterChildren():  # Iterates through children.
                self.recursiveFromPath(child, path_list)  # Recursively calls for each child.

    def recursiveFindType(self, producer, path_list, type_name_list):
        """
        Recursively finds producers whose type matches any in `type_name_list`
        and adds their full names to `path_list`.

        (Note: This function is defined but not directly called in the `displayModel` logic for current types).
        """
        if producer is not None and type_name_list and type_name_list[0] != "":
            producer_type_attr = producer.getAttribute("type")
            if producer_type_attr:  # Check if 'type' attribute exists.
                producer_type = producer_type_attr.getValue()  # Gets the 'type' attribute value.
                if producer_type in type_name_list:  # Checks if the type is in the desired list.
                    path_list.append(producer.getFullName())  # Adds the full name.

            for child in producer.iterChildren():  # Iterates through children.
                self.recursiveFindType(child, path_list, type_name_list)  # Recursively calls for each child.
        # else:
        # print('no producer for :', producer) # Debug print if no producer.
        return path_list

    def yamlReadFile(self, file, module='dirFiles', dictMode=False):
        """
        Reads a YAML file and returns its content.
        `module`: The top-level key to extract data from.
        `dictMode`: If True, returns the dictionary under `module`.
                    Otherwise, returns a sorted list of values from the `module` dictionary.
        """
        try:
            with open(file, 'r') as f:  # Use 'with' statement for proper file closing.
                # Use yaml.SafeLoader for security, or yaml.FullLoader if full YAML features are needed.
                # Current code uses FullLoader, keeping it for consistency.
                dictionary = yaml.load(f, Loader=yaml.FullLoader)

                if dictMode:
                    return dictionary.get(module)  # Use .get() for safer dictionary access.
                else:
                    item_list = []
                    # Check if 'module' exists and is a dictionary before iterating keys.
                    module_data = dictionary.get(module)
                    if isinstance(module_data, dict):
                        for key in sorted(module_data.keys()):
                            item_list.append(module_data[key])
                    return item_list
        except IOError as e:
            # print("Error reading YAML file {}: {}".format(file, e)) # For debugging
            return [] if not dictMode else {}  # Return empty list or dict on error.
        except yaml.YAMLError as e:
            # print("Error parsing YAML file {}: {}".format(file, e)) # For debugging
            return [] if not dictMode else {}  # Return empty list or dict on parsing error.
        except Exception as e:
            # print("An unexpected error occurred in yamlReadFile: {}".format(e)) # For debugging
            return [] if not dictMode else {}

    def displayModel(self, node=None, nameInNode='_hiShape'):
        """
        The core function for displaying, hiding, or selecting scene graph locations.
        It constructs CEL expressions based on user input (name, type, collection, path, or raw CEL),
        applies them to Katana Working Sets, and provides visual feedback.
        """
        # Ensure node is properly initialized if not provided (default behavior is rootNode)
        if node is None:
            node = NodegraphAPI.GetRootNode()

        QApplication.setOverrideCursor(Qt.WaitCursor)  # Changes cursor to busy indicator.

        # Get the object name of the button that triggered this function.
        # sender() returns QObject.objectName().
        name_sender = str(self.sender().objectName())  # Ensure string conversion for Python 2/3 compatibility.

        self.paths = []  # Initializes paths for the current operation.

        # If not in additive mode, clear current selections before proceeding.
        if not self.addCheckBox.isChecked():
            if name_sender != "selectButton":  # If not specifically selecting.
                self.workingSet.clear()  # Clears the viewer working set.
            self.allPath = []  # Clears all accumulated paths.

        nameInNode = str(self.nameLineEdit.text()).strip()  # Get text from name input, strip whitespace.
        # Split path input by space and filter out empty strings.
        splitText = [p.strip() for p in str(self.pathLineEdit.text()).split(' ') if p.strip()]

        # Ensure viewer visibility follows the working set.
        self.sg.setViewerVisibilityFollowingWorkingSet(True)

        # Check the CEL widget
        if self.celCheckBox.isChecked():  # If CEL mode is enabled.
            self.expression = str(self.cellWidget.getCellWidgetValue()).strip()  # Get CEL expression, strip whitespace.
            # If there is an expression.
            if self.expression:  # If a CEL expression is provided (not empty).
                wid = UI4.Widgets.CollectAndSelectInScenegraph(self.expression, "/root")
                self.paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())

                if self.addCheckBox.isChecked():
                    self.allPath.extend(self.paths)  # Use extend for efficiency.
                else:
                    self.allPath = list(self.paths)  # Ensure it's a list.
            else:
                self.expression = ""  # Reset if CEL editor is empty.

        else:  # If standard search mode (not CEL).
            current_expression_parts = []

            # Find producers which contain the input name.
            if nameInNode:  # If a name is provided.
                if splitText:  # If specific paths are given.
                    # Build CEL for name match within specified paths.
                    # Using format strings for readability (compatible with Python 2.7 with .format).
                    current_expression_parts.extend(
                        ["(({}//*{}*))".format(prodpath, nameInNode) for prodpath in splitText])
                else:
                    # Build CEL for name match globally.
                    current_expression_parts.append("/root//*{}*".format(nameInNode))

            # Get the path with the help of asset type.
            type_line_edit_text = str(self.typeLineEdit.text()).strip()
            if type_line_edit_text:  # If asset types are specified.
                splitTypeText = [t.strip() for t in type_line_edit_text.split(";") if t.strip()]

                if splitText:  # If specific paths are given.
                    # Build CEL for type match within specified paths.
                    current_expression_parts.extend(["(({}//*{{attr(\"type\") == \"{}\"}}))".format(prodpath, splitType)
                                                     for prodpath in splitText for splitType in splitTypeText])
                else:
                    # Build CEL for type match globally.
                    current_expression_parts.extend(["((/root//*{{attr(\"type\") == \"{}\"}}))".format(splitType)
                                                     for splitType in splitTypeText])

            # If a collection is selected.
            selected_collection = str(self.collectionComboBox.currentText())
            if selected_collection != "None":
                # Build CEL for the selected collection.
                current_expression_parts.append("(/${})".format(selected_collection))

            # Combine all parts into a single expression.
            if current_expression_parts:
                self.expression = " + ".join(current_expression_parts)
                # Collect paths based on the constructed expression.
                wid = UI4.Widgets.CollectAndSelectInScenegraph(self.expression, "/root")
                self.paths = wid.collectAndSelect(select=False, node=NodegraphAPI.GetViewNode())

                if self.addCheckBox.isChecked():
                    self.allPath.extend(self.paths)
                else:
                    self.allPath = list(self.paths)
            else:
                self.expression = ""  # No criteria, so no expression.

            # Handle render check if not in CEL mode directly.
            # This logic is also in setRender(), but it might be needed here if conditions change.
            # Keeping it separated as setRender() is more comprehensive for render updates.
            # if self.renderCheck.isChecked():
            #    self.setRender()

        # Remove duplicates from `self.allPath` (important if multiple criteria overlapped).
        self.allPath = list(set(self.allPath))

        # Clear the expression display before updating.
        self.expressionLineEdit.clear()

        # Hide the asset.
        if name_sender == 'Hide':
            # The producer is initialized in __init__; re-getting it here is often redundant unless scene changes.
            # self.producer = Nodes3DAPI.GetGeometryProducer(self.rootNode, self.time)

            # If including children AND a collection was selected, recursively add children to paths to hide.
            # The condition `self.collectionComboBox.currentText() != "None"` applies to the paths *already in self.paths*
            # or implicitly derived.
            if self.childCheckBox.isChecked() and self.collectionComboBox.currentText() != "None":
                self.recursiveFindPath(self.producer, self.paths)  # Recursively adds children to paths to hide.

            # Set paths to "Empty" (hidden) in viewer.
            self.workingSet.setLocationStates(self.paths, WorkingSet.WorkingSet.State.Empty)

            # Update the expression for writing/display based on additive mode.
            if self.addCheckBox.isChecked() and self.expressionToWrite:
                if " + " + self.expression in self.expressionToWrite:
                    self.expressionToWrite = self.expressionToWrite.replace(" + " + self.expression, "")
                    self.expressionToWrite += " - " + self.expression
                elif " - " + self.expression in self.expressionToWrite:
                    pass  # Already explicitly subtracted.
                elif self.expression in self.expressionToWrite:
                    # If just present (e.g., from initial additive), add a negative subtraction.
                    self.expressionToWrite += " - " + self.expression
                else:
                    self.expressionToWrite += " - " + self.expression
            else:
                self.expressionToWrite = self.expression

            self.expressionLineEdit.setText(self.expressionToWrite)  # Display the expression to write.

            if self.renderCheck.isChecked():  # If render is checked.
                self.setRender()  # Update render working set.

        # Select and frame assets.
        elif name_sender == 'selectButton':
            self.sg.clearSelection()  # Clears current scenegraph selection.
            # Add collected paths to selection (False for non-exclusive).
            self.sg.addSelectedLocations(self.paths, False)

            # Zoom in the viewer (frame selected).
            tab = UI4.App.Tabs.FindTopTab('Viewer')
            if tab:  # Ensure Viewer tab exists.
                # Get the viewport widget. Assumes first viewport (index 0).
                viewport = tab.getViewportWidgetByIndex(viewportIndex=0, viewerDelegate=tab.getViewerDelegateByIndex(0))
                if viewport:
                    # Creates a simulated 'F' key press event (for framing).
                    # `Qt.Key_F` and `Qt.NoModifier` are compatible.
                    keyEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_F, Qt.NoModifier)
                    QCoreApplication.postEvent(viewport, keyEvent)
                    # In PyQt, QKeyEvent objects are typically managed by the event loop,
                    # so `del keyEvent` might not be strictly necessary to prevent memory leaks
                    # if the C++ object ownership is transferred, but it's harmless.

            self.expressionLineEdit.setText(self.expressionToWrite)  # Display the expression to write.

        # Show the asset.
        else:  # If "Display" button was clicked.
            # If including children AND a collection was selected, recursively add children to paths to display.
            if self.childCheckBox.isChecked() and self.collectionComboBox.currentText() != "None":
                self.recursiveFindPath(self.producer, self.allPath)  # Recursively adds children to paths to display.

            # Remove duplicates again after adding children.
            self.allPath = list(set(self.allPath))

            # Set paths to "Included" (visible) in viewer.
            self.workingSet.setLocationStates(self.allPath, WorkingSet.WorkingSet.State.Included)

            # Update the expression for writing/display based on additive mode.
            if self.addCheckBox.isChecked() and self.expressionToWrite:
                if " - " + self.expression in self.expressionToWrite:
                    self.expressionToWrite = self.expressionToWrite.replace(" - " + self.expression, "")
                    self.expressionToWrite += " + " + self.expression
                elif " + " + self.expression in self.expressionToWrite:
                    pass  # Already explicitly added.
                elif self.expression in self.expressionToWrite:
                    pass  # If just present (e.g., from initial additive), assume it's already part of the positive set.
                else:
                    self.expressionToWrite += " + " + self.expression
            else:
                self.expressionToWrite = self.expression

            self.expressionLineEdit.setText(self.expressionToWrite)  # Display the expression to write.

            if self.renderCheck.isChecked():  # If render is checked.
                self.setRender()  # Update render working set.

        # Ensure viewer visibility is on after any display operation.
        self.displayViewer(True)
        QApplication.restoreOverrideCursor()  # Restores the original cursor.

    def displayViewer(self, state=False):
        """
        Enables or disables Katana's viewer visibility following the working set.
        """
        # Toggles the core viewer visibility setting.
        # This controls whether the 3D Viewer respects the Working Set (True) or shows everything (False).
        self.sg.setViewerVisibilityFollowingWorkingSet(state)


# Katana Plugin Registry entry point.
# This registers the `displayGeoUI` class as a Katana panel.
# The tuple format is ('Category', Version, 'Name', Class).
PluginRegistry = [
    ('KatanaPanel', 2.0, 'displayGeo', displayGeoUI),
    ('KatanaPanel', 2.0, 'Custom/displayGeo', displayGeoUI),
    # Registers it again under 'Custom/displayGeo' for menu structure.
]