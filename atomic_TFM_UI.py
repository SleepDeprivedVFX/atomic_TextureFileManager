# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Adam\Google Drive\Scripts\atomicTextureFileManager\UIs\atomic_TFM_UI.ui'
#
# Created: Sat Oct 08 17:02:53 2016
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_atomicTextureFileManager(object):
    def setupUi(self, atomicTextureFileManager):
        atomicTextureFileManager.setObjectName("atomicTextureFileManager")
        atomicTextureFileManager.resize(1289, 923)
        self.centralwidget = QtGui.QWidget(atomicTextureFileManager)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(896, 858))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setAutoFillBackground(True)
        self.tabWidget.setObjectName("tabWidget")
        self.filesTab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filesTab.sizePolicy().hasHeightForWidth())
        self.filesTab.setSizePolicy(sizePolicy)
        self.filesTab.setObjectName("filesTab")
        self.verticalLayout = QtGui.QVBoxLayout(self.filesTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TextureLists = QtGui.QFrame(self.filesTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TextureLists.sizePolicy().hasHeightForWidth())
        self.TextureLists.setSizePolicy(sizePolicy)
        self.TextureLists.setAutoFillBackground(False)
        self.TextureLists.setFrameShape(QtGui.QFrame.StyledPanel)
        self.TextureLists.setFrameShadow(QtGui.QFrame.Raised)
        self.TextureLists.setObjectName("TextureLists")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.TextureLists)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.frame = QtGui.QFrame(self.TextureLists)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFocusPolicy(QtCore.Qt.TabFocus)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.existingTextureGrid = QtGui.QGridLayout()
        self.existingTextureGrid.setObjectName("existingTextureGrid")
        self.existingTextureLabel = QtGui.QLabel(self.frame)
        self.existingTextureLabel.setObjectName("existingTextureLabel")
        self.existingTextureGrid.addWidget(self.existingTextureLabel, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.colorKeyCurrent = QtGui.QLabel(self.frame)
        self.colorKeyCurrent.setObjectName("colorKeyCurrent")
        self.horizontalLayout_4.addWidget(self.colorKeyCurrent)
        self.colorKeyMissing = QtGui.QLabel(self.frame)
        self.colorKeyMissing.setObjectName("colorKeyMissing")
        self.horizontalLayout_4.addWidget(self.colorKeyMissing)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.existingTextureGrid.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)
        self.existingTextureList = QtGui.QTableWidget(self.frame)
        self.existingTextureList.setDragEnabled(True)
        self.existingTextureList.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.existingTextureList.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.existingTextureList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.existingTextureList.setObjectName("existingTextureList")
        self.existingTextureList.setColumnCount(4)
        self.existingTextureList.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.existingTextureList.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.existingTextureList.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.existingTextureList.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.existingTextureList.setHorizontalHeaderItem(3, item)
        self.existingTextureList.horizontalHeader().setDefaultSectionSize(200)
        self.existingTextureList.horizontalHeader().setMinimumSectionSize(90)
        self.existingTextureList.horizontalHeader().setStretchLastSection(True)
        self.existingTextureList.verticalHeader().setCascadingSectionResizes(True)
        self.existingTextureList.verticalHeader().setDefaultSectionSize(30)
        self.existingTextureGrid.addWidget(self.existingTextureList, 0, 0, 1, 1)
        self.horizontalLayout.addLayout(self.existingTextureGrid)
        self.verticalLayout_4.addWidget(self.frame)
        self.TextureSettings = QtGui.QToolBox(self.TextureLists)
        self.TextureSettings.setObjectName("TextureSettings")
        self.operations = QtGui.QWidget()
        self.operations.setGeometry(QtCore.QRect(0, 0, 1203, 301))
        self.operations.setObjectName("operations")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.operations)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtGui.QLabel(self.operations)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.browseSourceBtn = QtGui.QPushButton(self.operations)
        self.browseSourceBtn.setObjectName("browseSourceBtn")
        self.horizontalLayout_3.addWidget(self.browseSourceBtn)
        self.sourceText = QtGui.QLineEdit(self.operations)
        self.sourceText.setText("")
        self.sourceText.setObjectName("sourceText")
        self.horizontalLayout_3.addWidget(self.sourceText)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.actionTypeSelectionLayout = QtGui.QHBoxLayout()
        self.actionTypeSelectionLayout.setObjectName("actionTypeSelectionLayout")
        self.copyToSrcImgs = QtGui.QRadioButton(self.operations)
        self.copyToSrcImgs.setChecked(True)
        self.copyToSrcImgs.setObjectName("copyToSrcImgs")
        self.actionTypeSelectionLayout.addWidget(self.copyToSrcImgs)
        self.moveToSrcImgs = QtGui.QRadioButton(self.operations)
        self.moveToSrcImgs.setObjectName("moveToSrcImgs")
        self.actionTypeSelectionLayout.addWidget(self.moveToSrcImgs)
        self.missingFileSearch = QtGui.QRadioButton(self.operations)
        self.missingFileSearch.setObjectName("missingFileSearch")
        self.actionTypeSelectionLayout.addWidget(self.missingFileSearch)
        self.verticalLayout_5.addLayout(self.actionTypeSelectionLayout)
        self.updatePath = QtGui.QCheckBox(self.operations)
        self.updatePath.setChecked(True)
        self.updatePath.setObjectName("updatePath")
        self.verticalLayout_5.addWidget(self.updatePath)
        self.keepOriginalSubfolders = QtGui.QCheckBox(self.operations)
        self.keepOriginalSubfolders.setChecked(True)
        self.keepOriginalSubfolders.setObjectName("keepOriginalSubfolders")
        self.verticalLayout_5.addWidget(self.keepOriginalSubfolders)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.TextureSettings.addItem(self.operations, "")
        self.options = QtGui.QWidget()
        self.options.setGeometry(QtCore.QRect(0, 0, 1203, 301))
        self.options.setObjectName("options")
        self.defaultFolderTypes = QtGui.QListWidget(self.options)
        self.defaultFolderTypes.setGeometry(QtCore.QRect(0, 60, 1121, 201))
        self.defaultFolderTypes.setAlternatingRowColors(True)
        self.defaultFolderTypes.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.defaultFolderTypes.setResizeMode(QtGui.QListView.Adjust)
        self.defaultFolderTypes.setLayoutMode(QtGui.QListView.Batched)
        self.defaultFolderTypes.setUniformItemSizes(True)
        self.defaultFolderTypes.setObjectName("defaultFolderTypes")
        self.checkBox = QtGui.QCheckBox(self.options)
        self.checkBox.setGeometry(QtCore.QRect(0, 30, 201, 25))
        self.checkBox.setChecked(False)
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtGui.QCheckBox(self.options)
        self.checkBox_2.setGeometry(QtCore.QRect(230, 30, 191, 25))
        self.checkBox_2.setChecked(True)
        self.checkBox_2.setObjectName("checkBox_2")
        self.label_9 = QtGui.QLabel(self.options)
        self.label_9.setGeometry(QtCore.QRect(1, 1, 327, 21))
        self.label_9.setObjectName("label_9")
        self.TextureSettings.addItem(self.options, "")
        self.verticalLayout_4.addWidget(self.TextureSettings)
        self.verticalLayout.addWidget(self.TextureLists)
        self.actionButtonsLayout = QtGui.QHBoxLayout()
        self.actionButtonsLayout.setObjectName("actionButtonsLayout")
        self.refresh = QtGui.QPushButton(self.filesTab)
        self.refresh.setObjectName("refresh")
        self.actionButtonsLayout.addWidget(self.refresh)
        self.cancel = QtGui.QPushButton(self.filesTab)
        self.cancel.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.cancel.setObjectName("cancel")
        self.actionButtonsLayout.addWidget(self.cancel)
        self.run = QtGui.QPushButton(self.filesTab)
        self.run.setObjectName("run")
        self.actionButtonsLayout.addWidget(self.run)
        self.verticalLayout.addLayout(self.actionButtonsLayout)
        self.tabWidget.addTab(self.filesTab, "")
        self.toolsTab = QtGui.QWidget()
        self.toolsTab.setObjectName("toolsTab")
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.toolsTab)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.toolBox = QtGui.QToolBox(self.toolsTab)
        self.toolBox.setObjectName("toolBox")
        self.imageResizeReformat = QtGui.QWidget()
        self.imageResizeReformat.setGeometry(QtCore.QRect(0, 0, 1231, 723))
        self.imageResizeReformat.setObjectName("imageResizeReformat")
        self.toolBox.addItem(self.imageResizeReformat, "")
        self.uvTilingSetup = QtGui.QWidget()
        self.uvTilingSetup.setGeometry(QtCore.QRect(0, 0, 100, 30))
        self.uvTilingSetup.setObjectName("uvTilingSetup")
        self.toolBox.addItem(self.uvTilingSetup, "")
        self.makePathsRelative = QtGui.QWidget()
        self.makePathsRelative.setGeometry(QtCore.QRect(0, 0, 100, 30))
        self.makePathsRelative.setObjectName("makePathsRelative")
        self.toolBox.addItem(self.makePathsRelative, "")
        self.verticalLayout_7.addWidget(self.toolBox)
        self.tabWidget.addTab(self.toolsTab, "")
        self.settingsTab = QtGui.QWidget()
        self.settingsTab.setObjectName("settingsTab")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.settingsTab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_4 = QtGui.QLabel(self.settingsTab)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_6.addWidget(self.label_4)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.xmlLabel = QtGui.QLabel(self.settingsTab)
        self.xmlLabel.setEnabled(True)
        self.xmlLabel.setInputMethodHints(QtCore.Qt.ImhNone)
        self.xmlLabel.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.xmlLabel.setObjectName("xmlLabel")
        self.verticalLayout_3.addWidget(self.xmlLabel)
        self.xmlLocation = QtGui.QLineEdit(self.settingsTab)
        self.xmlLocation.setEnabled(False)
        self.xmlLocation.setObjectName("xmlLocation")
        self.verticalLayout_3.addWidget(self.xmlLocation)
        self.verticalLayout_6.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.nodeTypesList = QtGui.QTableWidget(self.settingsTab)
        self.nodeTypesList.setMinimumSize(QtCore.QSize(0, 0))
        self.nodeTypesList.setSizeIncrement(QtCore.QSize(0, 0))
        self.nodeTypesList.setRowCount(0)
        self.nodeTypesList.setColumnCount(4)
        self.nodeTypesList.setObjectName("nodeTypesList")
        self.nodeTypesList.setColumnCount(4)
        self.nodeTypesList.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.nodeTypesList.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.nodeTypesList.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.nodeTypesList.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.nodeTypesList.setHorizontalHeaderItem(3, item)
        self.nodeTypesList.horizontalHeader().setCascadingSectionResizes(False)
        self.nodeTypesList.horizontalHeader().setDefaultSectionSize(200)
        self.nodeTypesList.horizontalHeader().setMinimumSectionSize(200)
        self.nodeTypesList.horizontalHeader().setSortIndicatorShown(False)
        self.nodeTypesList.horizontalHeader().setStretchLastSection(True)
        self.nodeTypesList.verticalHeader().setCascadingSectionResizes(False)
        self.nodeTypesList.verticalHeader().setHighlightSections(True)
        self.verticalLayout_2.addWidget(self.nodeTypesList)
        self.label_3 = QtGui.QLabel(self.settingsTab)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.label_7 = QtGui.QLabel(self.settingsTab)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_2.addWidget(self.label_7)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.newParameterName = QtGui.QLineEdit(self.settingsTab)
        self.newParameterName.setObjectName("newParameterName")
        self.gridLayout.addWidget(self.newParameterName, 1, 2, 1, 2)
        self.addNodeType = QtGui.QPushButton(self.settingsTab)
        self.addNodeType.setObjectName("addNodeType")
        self.gridLayout.addWidget(self.addNodeType, 2, 3, 1, 1)
        self.pushButton = QtGui.QPushButton(self.settingsTab)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 5, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 3, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(300, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 5, 2, 1, 1)
        self.label_5 = QtGui.QLabel(self.settingsTab)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.settingsTab)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 2, 1, 1)
        self.newNodeType = QtGui.QLineEdit(self.settingsTab)
        self.newNodeType.setObjectName("newNodeType")
        self.gridLayout.addWidget(self.newNodeType, 1, 0, 1, 1)
        self.label_8 = QtGui.QLabel(self.settingsTab)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 4, 0, 1, 1)
        self.defaultFolderLabel = QtGui.QLabel(self.settingsTab)
        self.defaultFolderLabel.setObjectName("defaultFolderLabel")
        self.gridLayout.addWidget(self.defaultFolderLabel, 0, 1, 1, 1)
        self.defaultFolder = QtGui.QComboBox(self.settingsTab)
        self.defaultFolder.setMinimumSize(QtCore.QSize(250, 0))
        self.defaultFolder.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.defaultFolder.setObjectName("defaultFolder")
        self.gridLayout.addWidget(self.defaultFolder, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout_6.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.settingsTab, "")
        self.verticalLayout_8.addWidget(self.tabWidget)
        #atomicTextureFileManager.setCentralWidget(self.centralwidget)
        self.actionCopy_Selected_To_Source = QtGui.QAction(atomicTextureFileManager)
        self.actionCopy_Selected_To_Source.setObjectName("actionCopy_Selected_To_Source")
        self.actionReset = QtGui.QAction(atomicTextureFileManager)
        self.actionReset.setObjectName("actionReset")
        self.actionMove_Selected_To_Source = QtGui.QAction(atomicTextureFileManager)
        self.actionMove_Selected_To_Source.setObjectName("actionMove_Selected_To_Source")
        self.actionDocumentation = QtGui.QAction(atomicTextureFileManager)
        self.actionDocumentation.setObjectName("actionDocumentation")
        self.label_2.setBuddy(self.browseSourceBtn)
        self.label_9.setBuddy(self.defaultFolderTypes)
        self.xmlLabel.setBuddy(self.xmlLocation)
        self.label_3.setBuddy(self.nodeTypesList)
        self.label_5.setBuddy(self.newNodeType)
        self.label_6.setBuddy(self.newParameterName)
        self.label_8.setBuddy(self.pushButton)

        self.retranslateUi(atomicTextureFileManager)
        self.tabWidget.setCurrentIndex(0)
        self.TextureSettings.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(0)
        QtCore.QObject.connect(self.checkBox, QtCore.SIGNAL("clicked(bool)"), self.checkBox_2.toggle)
        QtCore.QObject.connect(self.checkBox_2, QtCore.SIGNAL("clicked(bool)"), self.checkBox.toggle)
        QtCore.QMetaObject.connectSlotsByName(atomicTextureFileManager)
        atomicTextureFileManager.setTabOrder(self.copyToSrcImgs, self.moveToSrcImgs)
        atomicTextureFileManager.setTabOrder(self.moveToSrcImgs, self.missingFileSearch)
        atomicTextureFileManager.setTabOrder(self.missingFileSearch, self.browseSourceBtn)
        atomicTextureFileManager.setTabOrder(self.browseSourceBtn, self.sourceText)
        atomicTextureFileManager.setTabOrder(self.sourceText, self.run)
        atomicTextureFileManager.setTabOrder(self.run, self.cancel)
        atomicTextureFileManager.setTabOrder(self.cancel, self.keepOriginalSubfolders)

    def retranslateUi(self, atomicTextureFileManager):
        atomicTextureFileManager.setWindowTitle(QtGui.QApplication.translate("atomicTextureFileManager", "Atomic Texture File Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureLabel.setText(QtGui.QApplication.translate("atomicTextureFileManager", "<html><head/><body><p><span style=\" font-size:12pt;\">Scene Files</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.colorKeyCurrent.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Currently in Project   ", None, QtGui.QApplication.UnicodeUTF8))
        self.colorKeyMissing.setText(QtGui.QApplication.translate("atomicTextureFileManager", "   Missing Files   ", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("atomicTextureFileManager", "Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("atomicTextureFileManager", "Node Type", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("atomicTextureFileManager", "Default Folder", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("atomicTextureFileManager", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Source Images           ", None, QtGui.QApplication.UnicodeUTF8))
        self.browseSourceBtn.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.sourceText.setToolTip(QtGui.QApplication.translate("atomicTextureFileManager", "The existing sourceimages folder for the current Maya project, or a destination folder of your choice", None, QtGui.QApplication.UnicodeUTF8))
        self.sourceText.setStatusTip(QtGui.QApplication.translate("atomicTextureFileManager", "Current source images folder", None, QtGui.QApplication.UnicodeUTF8))
        self.sourceText.setPlaceholderText(QtGui.QApplication.translate("atomicTextureFileManager", "Source Images Folder", None, QtGui.QApplication.UnicodeUTF8))
        self.copyToSrcImgs.setToolTip(QtGui.QApplication.translate("atomicTextureFileManager", "This will copy files outside of sourceimages to the sourceimages folder", None, QtGui.QApplication.UnicodeUTF8))
        self.copyToSrcImgs.setStatusTip(QtGui.QApplication.translate("atomicTextureFileManager", "Copy files to sourceimages", None, QtGui.QApplication.UnicodeUTF8))
        self.copyToSrcImgs.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Copy to sourceimages", None, QtGui.QApplication.UnicodeUTF8))
        self.moveToSrcImgs.setToolTip(QtGui.QApplication.translate("atomicTextureFileManager", "This will move any files that are not yet in the sourceimages folder, to the sourceimages folder", None, QtGui.QApplication.UnicodeUTF8))
        self.moveToSrcImgs.setStatusTip(QtGui.QApplication.translate("atomicTextureFileManager", "Move files to the sourceimages folder", None, QtGui.QApplication.UnicodeUTF8))
        self.moveToSrcImgs.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Move to sourceimages", None, QtGui.QApplication.UnicodeUTF8))
        self.missingFileSearch.setToolTip(QtGui.QApplication.translate("atomicTextureFileManager", "This feature will search the computer for the filename of the missing files.  If found, the paths will be updated.", None, QtGui.QApplication.UnicodeUTF8))
        self.missingFileSearch.setStatusTip(QtGui.QApplication.translate("atomicTextureFileManager", "Attempt to find missing files on the computer", None, QtGui.QApplication.UnicodeUTF8))
        self.missingFileSearch.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Attempt Missing File Search", None, QtGui.QApplication.UnicodeUTF8))
        self.updatePath.setToolTip(QtGui.QApplication.translate("atomicTextureFileManager", "When this is checked, the nodes in the scene will be updated to the copied/moved path", None, QtGui.QApplication.UnicodeUTF8))
        self.updatePath.setStatusTip(QtGui.QApplication.translate("atomicTextureFileManager", "Uncheck if you want to copy the file to source images, but want to keep the original file location on the node.", None, QtGui.QApplication.UnicodeUTF8))
        self.updatePath.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Update Path on Run", None, QtGui.QApplication.UnicodeUTF8))
        self.keepOriginalSubfolders.setToolTip(QtGui.QApplication.translate("atomicTextureFileManager", "If the original file location is in a subfolder of a different sourceimages folder, and you want to keep that folder structure, make sure this is checked.", None, QtGui.QApplication.UnicodeUTF8))
        self.keepOriginalSubfolders.setStatusTip(QtGui.QApplication.translate("atomicTextureFileManager", "Check to keep original sub-folder structure", None, QtGui.QApplication.UnicodeUTF8))
        self.keepOriginalSubfolders.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Keep Original Subfolders", None, QtGui.QApplication.UnicodeUTF8))
        self.TextureSettings.setItemText(self.TextureSettings.indexOf(self.operations), QtGui.QApplication.translate("atomicTextureFileManager", "Operations", None, QtGui.QApplication.UnicodeUTF8))
        self.defaultFolderTypes.setSortingEnabled(True)
        self.checkBox.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Select All Node Types", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Texture Files Only", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("atomicTextureFileManager", "File Types by Default Project Folder Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.TextureSettings.setItemText(self.TextureSettings.indexOf(self.options), QtGui.QApplication.translate("atomicTextureFileManager", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.run.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Run Operation", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.filesTab), QtGui.QApplication.translate("atomicTextureFileManager", "Files", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.imageResizeReformat), QtGui.QApplication.translate("atomicTextureFileManager", "Image Resize/Reformat", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.uvTilingSetup), QtGui.QApplication.translate("atomicTextureFileManager", "UV Tiling Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.makePathsRelative), QtGui.QApplication.translate("atomicTextureFileManager", "Make All Paths Relative", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemToolTip(self.toolBox.indexOf(self.makePathsRelative), QtGui.QApplication.translate("atomicTextureFileManager", "Convert absolute paths to relative paths", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.toolsTab), QtGui.QApplication.translate("atomicTextureFileManager", "Tools", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("atomicTextureFileManager", "USE WITH CAUTION!!\n"
"\n"
"These settings will affect the way this tool runs!  It was designed to be expandable, and uses an xml document to keep a list of acceptable image types.  Some are inserted by default, but the list can be expanded upon by you.\n"
"It is important to understand that changing this list will directly affect this tool\'s ability to preform.  Make sure you understand what you are doing before you hit save!", None, QtGui.QApplication.UnicodeUTF8))
        self.xmlLabel.setText(QtGui.QApplication.translate("atomicTextureFileManager", "XML File Location", None, QtGui.QApplication.UnicodeUTF8))
        self.xmlLocation.setToolTip(QtGui.QApplication.translate("atomicTextureFileManager", "The XML file that maintains the list of texture file node types", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesList.setToolTip(QtGui.QApplication.translate("atomicTextureFileManager", "List of excepted file nodes", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("atomicTextureFileManager", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("atomicTextureFileManager", "nodeType", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("atomicTextureFileManager", "defaultFolder", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("atomicTextureFileManager", "parameterName", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Accepted Nodes", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Manually add new node", None, QtGui.QApplication.UnicodeUTF8))
        self.addNodeType.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setToolTip(QtGui.QApplication.translate("atomicTextureFileManager", "This will bring up a list of attribues from the existing node.  Pick the correct parameter from there", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("atomicTextureFileManager", "   Auto Add From Selection   ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("atomicTextureFileManager", "nodeType", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("atomicTextureFileManager", "parameterName", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Get the node type and attribute from the currently selected node", None, QtGui.QApplication.UnicodeUTF8))
        self.defaultFolderLabel.setText(QtGui.QApplication.translate("atomicTextureFileManager", "defaultFolder", None, QtGui.QApplication.UnicodeUTF8))
        self.defaultFolder.setToolTip(QtGui.QApplication.translate("atomicTextureFileManager", "Based on Project Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingsTab), QtGui.QApplication.translate("atomicTextureFileManager", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopy_Selected_To_Source.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Copy Selected To Source", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReset.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMove_Selected_To_Source.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Move Selected To Source", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDocumentation.setText(QtGui.QApplication.translate("atomicTextureFileManager", "Documentation", None, QtGui.QApplication.UnicodeUTF8))
