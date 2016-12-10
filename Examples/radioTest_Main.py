from maya import cmds
from PySide import QtCore, QtGui
import radioTest as rt
reload(rt)
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
 
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
class ControlMainWindow(QtGui.QDialog):
 
    def __init__(self, parent=None):
 
        super(ControlMainWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui =  rt.Ui_MainWindow()
        self.ui.setupUi(self)
 
        self.ui.run.clicked.connect(self.someFunc)
 
    def someFunc(self):
        print 'Hello {0} !'
 
myWin = ControlMainWindow(parent=maya_main_window())
myWin.show()