# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/adamb/Documents/maya/2015-x64/scripts/radioTest.ui'
#
# Created: Fri Sep 02 15:11:59 2016
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.run = QtGui.QPushButton(self.centralwidget)
        self.run.setGeometry(QtCore.QRect(270, 180, 75, 23))
        self.run.setCheckable(False)
        self.run.setChecked(False)
        self.run.setObjectName("run")
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(210, 160, 132, 19))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sin = QtGui.QRadioButton(self.widget)
        self.sin.setChecked(True)
        self.sin.setObjectName("sin")
        self.horizontalLayout.addWidget(self.sin)
        self.cos = QtGui.QRadioButton(self.widget)
        self.cos.setObjectName("cos")
        self.horizontalLayout.addWidget(self.cos)
        self.tan = QtGui.QRadioButton(self.widget)
        self.tan.setObjectName("tan")
        self.horizontalLayout.addWidget(self.tan)
        #MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        #MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        #MainWindow.setStatusBar(self.statusbar)
        self.action_Reset = QtGui.QAction(MainWindow)
        self.action_Reset.setObjectName("action_Reset")
        self.menu_File.addAction(self.action_Reset)
        self.menubar.addAction(self.menu_File.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.run.setText(QtGui.QApplication.translate("MainWindow", "Run", None, QtGui.QApplication.UnicodeUTF8))
        self.sin.setText(QtGui.QApplication.translate("MainWindow", "Sin", None, QtGui.QApplication.UnicodeUTF8))
        self.cos.setText(QtGui.QApplication.translate("MainWindow", "Cos", None, QtGui.QApplication.UnicodeUTF8))
        self.tan.setText(QtGui.QApplication.translate("MainWindow", "Tan", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_File.setTitle(QtGui.QApplication.translate("MainWindow", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Reset.setText(QtGui.QApplication.translate("MainWindow", "&Reset", None, QtGui.QApplication.UnicodeUTF8))

