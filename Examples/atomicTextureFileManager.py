# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/Adam/Documents/maya/2016/scripts/UI/atomicTextureFileManager.ui'
#
# Created: Fri Sep 02 11:32:59 2016
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AtomicTextureFileManager(object):
    def setupUi(self, AtomicTextureFileManager):
        AtomicTextureFileManager.setObjectName("AtomicTextureFileManager")
        AtomicTextureFileManager.resize(896, 889)
        self.centralwidget = QtGui.QWidget(AtomicTextureFileManager)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.TextureLists = QtGui.QFrame(self.tab)
        self.TextureLists.setGeometry(QtCore.QRect(0, 0, 851, 731))
        self.TextureLists.setFrameShape(QtGui.QFrame.StyledPanel)
        self.TextureLists.setFrameShadow(QtGui.QFrame.Raised)
        self.TextureLists.setObjectName("TextureLists")
        self.layoutWidget = QtGui.QWidget(self.TextureLists)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 30, 391, 461))
        self.layoutWidget.setObjectName("layoutWidget")
        self.existingTextureGrid = QtGui.QGridLayout(self.layoutWidget)
        self.existingTextureGrid.setContentsMargins(0, 0, 0, 0)
        self.existingTextureGrid.setObjectName("existingTextureGrid")
        self.existingTextureLabel = QtGui.QLabel(self.layoutWidget)
        self.existingTextureLabel.setObjectName("existingTextureLabel")
        self.existingTextureGrid.addWidget(self.existingTextureLabel, 0, 0, 1, 1)
        self.graphicsView = QtGui.QGraphicsView(self.layoutWidget)
        self.graphicsView.setObjectName("graphicsView")
        self.existingTextureGrid.addWidget(self.graphicsView, 1, 0, 1, 1)
        self.layoutWidget1 = QtGui.QWidget(self.TextureLists)
        self.layoutWidget1.setGeometry(QtCore.QRect(430, 30, 401, 461))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.missingTexturesGrid = QtGui.QGridLayout(self.layoutWidget1)
        self.missingTexturesGrid.setContentsMargins(0, 0, 0, 0)
        self.missingTexturesGrid.setObjectName("missingTexturesGrid")
        self.missingTexturesLabel = QtGui.QLabel(self.layoutWidget1)
        self.missingTexturesLabel.setObjectName("missingTexturesLabel")
        self.missingTexturesGrid.addWidget(self.missingTexturesLabel, 0, 0, 1, 1)
        self.graphicsView_2 = QtGui.QGraphicsView(self.layoutWidget1)
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.missingTexturesGrid.addWidget(self.graphicsView_2, 1, 0, 1, 1)
        self.layoutWidget2 = QtGui.QWidget(self.TextureLists)
        self.layoutWidget2.setGeometry(QtCore.QRect(20, 500, 316, 27))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.automaticSourceRdoBtn = QtGui.QRadioButton(self.layoutWidget2)
        self.automaticSourceRdoBtn.setEnabled(True)
        self.automaticSourceRdoBtn.setChecked(True)
        self.automaticSourceRdoBtn.setObjectName("automaticSourceRdoBtn")
        self.horizontalLayout.addWidget(self.automaticSourceRdoBtn)
        self.manualSourceRdoBtn = QtGui.QRadioButton(self.layoutWidget2)
        self.manualSourceRdoBtn.setChecked(False)
        self.manualSourceRdoBtn.setObjectName("manualSourceRdoBtn")
        self.horizontalLayout.addWidget(self.manualSourceRdoBtn)
        self.checkBox = QtGui.QCheckBox(self.TextureLists)
        self.checkBox.setGeometry(QtCore.QRect(30, 700, 221, 25))
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.widget = QtGui.QWidget(self.TextureLists)
        self.widget.setGeometry(QtCore.QRect(30, 550, 811, 36))
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.browseDestinationBtn = QtGui.QPushButton(self.widget)
        self.browseDestinationBtn.setEnabled(False)
        self.browseDestinationBtn.setObjectName("browseDestinationBtn")
        self.horizontalLayout_2.addWidget(self.browseDestinationBtn)
        self.destinationText = QtGui.QLineEdit(self.widget)
        self.destinationText.setEnabled(False)
        self.destinationText.setObjectName("destinationText")
        self.horizontalLayout_2.addWidget(self.destinationText)
        self.widget1 = QtGui.QWidget(self.TextureLists)
        self.widget1.setGeometry(QtCore.QRect(30, 610, 811, 36))
        self.widget1.setObjectName("widget1")
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget1)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.browseSourceBtn = QtGui.QPushButton(self.widget1)
        self.browseSourceBtn.setObjectName("browseSourceBtn")
        self.horizontalLayout_3.addWidget(self.browseSourceBtn)
        self.sourceText = QtGui.QLineEdit(self.widget1)
        self.sourceText.setObjectName("sourceText")
        self.horizontalLayout_3.addWidget(self.sourceText)
        self.widget2 = QtGui.QWidget(self.TextureLists)
        self.widget2.setGeometry(QtCore.QRect(30, 660, 807, 27))
        self.widget2.setObjectName("widget2")
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.widget2)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.radioButton = QtGui.QRadioButton(self.widget2)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.horizontalLayout_4.addWidget(self.radioButton)
        self.radioButton_2 = QtGui.QRadioButton(self.widget2)
        self.radioButton_2.setObjectName("radioButton_2")
        self.horizontalLayout_4.addWidget(self.radioButton_2)
        self.radioButton_3 = QtGui.QRadioButton(self.widget2)
        self.radioButton_3.setObjectName("radioButton_3")
        self.horizontalLayout_4.addWidget(self.radioButton_3)
        self.radioButton_4 = QtGui.QRadioButton(self.widget2)
        self.radioButton_4.setObjectName("radioButton_4")
        self.horizontalLayout_4.addWidget(self.radioButton_4)
        self.widget3 = QtGui.QWidget(self.tab)
        self.widget3.setGeometry(QtCore.QRect(510, 740, 331, 36))
        self.widget3.setObjectName("widget3")
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.widget3)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pushButton_2 = QtGui.QPushButton(self.widget3)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_5.addWidget(self.pushButton_2)
        self.pushButton = QtGui.QPushButton(self.widget3)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_5.addWidget(self.pushButton)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        AtomicTextureFileManager.setCentralWidget(self.centralwidget)
        self.menuBar = QtGui.QMenuBar(AtomicTextureFileManager)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 896, 31))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menu_Edit = QtGui.QMenu(self.menuBar)
        self.menu_Edit.setObjectName("menu_Edit")
        self.menu_Help = QtGui.QMenu(self.menuBar)
        self.menu_Help.setObjectName("menu_Help")
        AtomicTextureFileManager.setMenuBar(self.menuBar)
        self.actionCopy_Selected_To_Source = QtGui.QAction(AtomicTextureFileManager)
        self.actionCopy_Selected_To_Source.setObjectName("actionCopy_Selected_To_Source")
        self.actionReset = QtGui.QAction(AtomicTextureFileManager)
        self.actionReset.setObjectName("actionReset")
        self.actionMove_Selected_To_Source = QtGui.QAction(AtomicTextureFileManager)
        self.actionMove_Selected_To_Source.setObjectName("actionMove_Selected_To_Source")
        self.actionDocumentation = QtGui.QAction(AtomicTextureFileManager)
        self.actionDocumentation.setObjectName("actionDocumentation")
        self.menuFile.addAction(self.actionCopy_Selected_To_Source)
        self.menuFile.addAction(self.actionMove_Selected_To_Source)
        self.menu_Edit.addAction(self.actionReset)
        self.menu_Help.addAction(self.actionDocumentation)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menu_Edit.menuAction())
        self.menuBar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(AtomicTextureFileManager)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.manualSourceRdoBtn, QtCore.SIGNAL("clicked(bool)"), self.browseDestinationBtn.setEnabled)
        QtCore.QObject.connect(self.manualSourceRdoBtn, QtCore.SIGNAL("clicked(bool)"), self.destinationText.setEnabled)
        QtCore.QObject.connect(self.automaticSourceRdoBtn, QtCore.SIGNAL("clicked(bool)"), self.browseDestinationBtn.setDisabled)
        QtCore.QObject.connect(self.automaticSourceRdoBtn, QtCore.SIGNAL("clicked(bool)"), self.destinationText.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(AtomicTextureFileManager)

    def retranslateUi(self, AtomicTextureFileManager):
        AtomicTextureFileManager.setWindowTitle(QtGui.QApplication.translate("AtomicTextureFileManager", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureLabel.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "<html><head/><body><p><span style=\" font-size:12pt;\">Existing Textures</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.missingTexturesLabel.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "<html><head/><body><p><span style=\" font-size:12pt;\">Missing Textures</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.automaticSourceRdoBtn.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Automatic Source", None, QtGui.QApplication.UnicodeUTF8))
        self.manualSourceRdoBtn.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Manual Source", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Keep Original Subfolders", None, QtGui.QApplication.UnicodeUTF8))
        self.browseDestinationBtn.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.destinationText.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Destination", None, QtGui.QApplication.UnicodeUTF8))
        self.browseSourceBtn.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.sourceText.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Source", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Copy to sourceimages", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_2.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Move to sourceimages", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_3.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Attempt Missing File Search", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_4.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Consolidate All", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Run Operation", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("AtomicTextureFileManager", "Files", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("AtomicTextureFileManager", "Tools", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("AtomicTextureFileManager", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Edit.setTitle(QtGui.QApplication.translate("AtomicTextureFileManager", "&Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Help.setTitle(QtGui.QApplication.translate("AtomicTextureFileManager", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopy_Selected_To_Source.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Copy Selected To Source", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReset.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMove_Selected_To_Source.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Move Selected To Source", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDocumentation.setText(QtGui.QApplication.translate("AtomicTextureFileManager", "Documentation", None, QtGui.QApplication.UnicodeUTF8))

