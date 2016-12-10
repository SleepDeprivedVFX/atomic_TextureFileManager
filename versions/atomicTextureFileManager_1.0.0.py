from maya import cmds
import os, platform, sys, shutil, time
from PySide import QtCore, QtGui
import atomic_TFM_UI as atomicUI
reload(atomicUI)
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from xml.etree import ElementTree as ET
from functools import partial
import subprocess

__author__ = 'Adam Benson'
__version__ = '1.0.0'

'''
    This is the new and improve Texture File Manager!  Here are a list of features coming up in version 1.1.0
    1. Set drag and drop actions
    2. Add tools for changing the image type, resizing and other useful operations.
    3. Fix Progress Bars
'''

def atomicInterface():
    mainWin = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWin), QtGui.QWidget)
    
class atomicTextureFileManager(QtGui.QDialog):
    
    updateProgress = QtCore.Signal(int)
     
    def __init__(self, parent=None):
        super(atomicTextureFileManager, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui =  atomicUI.Ui_atomicTextureFileManager()
        self.ui.setupUi(self)
        self.fileTypes = {} 
        self.typeListFile = ''
        scriptsFolders = os.environ['MAYA_SCRIPT_PATH'].split(';')
        for folder in scriptsFolders:
            if os.path.exists(folder + '/atfm_TypeList.xml'):
                self.typeListFile = folder + '/atfm_TypeList.xml'
                break
        if self.typeListFile != '':
            xml = ET.parse(self.typeListFile)
            root_element = xml.getroot()
            for child in root_element:
                self.fileTypes[child.attrib['name']] = child[0].text
        else:
            print 'XML File cannot be found!'
        self.modes = {0:'copy', 1:'move', 2:'missing', 3:'consolodate'}
        self.preloadSystem()

    def cancel(self):
        #Close the window
        self.close()
 
    def getAllFiles(self):
        allFileTypes = {}
        for thisType in self.fileTypes:
            try:
                selectedType = cmds.ls(type=thisType)
                if len(selectedType) != 0:
                    allFileTypes[thisType]=selectedType
            except:
                pass
        return allFileTypes
        
    def getPathNames(self, allFileTypes):
        allPaths = {}
        for type in allFileTypes:
            shortList = allFileTypes[type]
            for thisNode in shortList:
                pathName = cmds.getAttr('%s.%s' % (thisNode, self.fileTypes[type]))
                allPaths[thisNode] = pathName
        return allPaths
    
    def getSceneInfo(self):
        sceneInfo = {}
        sceneInfo['project'] = cmds.workspace(q=True, act=True)
        sceneInfo['sourceFolder'] = cmds.workspace(fre='sourceImages')
        sceneInfo['scripts'] = cmds.workspace(fre='scripts')
        sceneInfo['OS-System'] = platform.system()
        sceneInfo['OS-Release'] = platform.release()
        sceneInfo['OS-User'] = os.getenv('USER')
        sceneInfo['OS-Version'] = platform.version()
        return sceneInfo
        
    def checkFileExistence(self, filePaths):
        existingFiles = {}
        missingFiles = {}
        for thisFile in filePaths:
            try:
                if os.path.exists(filePaths[thisFile]):
                    existingFiles[thisFile] = filePaths[thisFile]
                else:
                    missingFiles[thisFile] = filePaths[thisFile]
            except:
                pass
        return existingFiles, missingFiles

    def getSourceImagesFiles(self, files):
        sceneInfo = self.getSceneInfo()
        root = sceneInfo['project']
        sourcefolder = sceneInfo['sourceFolder']
        sourceImages = root + '/' + sourcefolder
        inSourceImages = {}
        inSourceSubs = []
        allSubdirectories = os.walk(sourceImages)
        for eachSubdir in allSubdirectories:
            subdir = eachSubdir[0]
            testPath = subdir.replace('\\', '/')
            if os.path.isdir(testPath):
                print '+++++++++++++++++++++++++++++++++++++++++++++++ TEST PATH'
                print testPath
                inSourceSubs.append(testPath)
        for each in files:
            path = files[each]
            try:
                if sourcefolder in path:
                    pathNoFile = path.rsplit('/', 1)[0]
                    print '--------------------------------------------- PATH NO FILE'
                    print pathNoFile
                    if pathNoFile in sourceImages or pathNoFile in inSourceSubs:
                        inSourceImages[each] = path
                        
            except:
                pass
        return inSourceImages, sourceImages

    def populateTable(self, table, pathList, compareList, image, isMissing, *args):
        for nodeType, path in pathList.items():
            rowCount = table.rowCount()
            thisRow = table.insertRow(rowCount)
            col = 0
            if image:     
                thisImage = QtGui.QPixmap(path)
                thisImage.scaled(5, 5, QtCore.Qt.KeepAspectRatioByExpanding)
                imageLabel = QtGui.QLabel()
                imageLabel.setScaledContents(True)
                imageLabel.setFixedHeight(100)
                imageLabel.setFixedWidth(100)
                imageLabel.setPixmap(thisImage)
                imageLabel.setToolTip(path)
                thisList = table.setCellWidget(rowCount, col, imageLabel)
                thisList = table.setItem(rowCount, (col+1), QtGui.QTableWidgetItem(nodeType))
                thisList = table.setItem(rowCount, (col+2), QtGui.QTableWidgetItem(path))
                col += 1
            else:
                thisList = table.setItem(rowCount, col, QtGui.QTableWidgetItem(nodeType))
                thisList = table.setItem(rowCount, (col+1), QtGui.QTableWidgetItem(path))
            colorize = False
            #Check to see if the file matches the 'sourceimages' folder.  This is a two way process.  If sourceimages is being iterated, then existingImages or missingImages will be compared.
            for inNodeType, inPath in compareList.items():
                if inPath in path:
                    if isMissing == True:
                        thisColor = QtGui.QColor(100, 0, 0)
                    else:
                        thisColor = QtGui.QColor(0,100,0)
                    colorize = True
                    break
                else:
                    colorize = False
            if colorize == True:
                thisList = table.item(rowCount, col)
                thisList.setBackground(thisColor)
                thisList = table.item(rowCount, (col+1))
                thisList.setBackground(thisColor)
            else:
                if isMissing or args:
                    pass
                else:
                    #thisList = table.selectRow(rowCount)
                    #This will eventually be used for drag and drop perhaps
                    pass
            if args:
                for inNodeType, inPath in args[0].items():
                    if inPath in path:
                        try:
                            thisList = table.item(rowCount, col)
                            thisList.setBackground(QtGui.QColor(100,0,0))
                            thisList = table.item(rowCount, (col+1))
                            thisList.setBackground(QtGui.QColor(100,0,0))
                        except:
                            pass
                


    def preloadSystem(self):
        #get scene data
        self.flushTables()
        allFileTypes = self.getAllFiles()
        pathNames = self.getPathNames(allFileTypes)
        sceneInfo = self.getSceneInfo()
        fileExists = self.checkFileExistence(pathNames)
        existingFiles = fileExists[0]
        missingFiles = fileExists[1]
        getSourceImages = self.getSourceImagesFiles(pathNames)
        inSourceImagesFiles = getSourceImages[0]
        sourceImagesFolder = getSourceImages[1]
        self.ui.existingTextureList.verticalHeader().setDefaultSectionSize(100);
        self.ui.inSourceImagesList.verticalHeader().setDefaultSectionSize(100);
        self.ui.missingTexturesList.verticalHeader().setDefaultSectionSize(100);        
        #Populate Existing Files List
        existingFilesPop = self.populateTable(self.ui.existingTextureList, existingFiles, inSourceImagesFiles, True, False)
        existingFilesDropAction = self.ui.existingTextureList
        existingFilesDropAction.installEventFilter(inSourceDropEvent(self))
        #Populate In Source Images List
        inSourceImagesPop = self.populateTable(self.ui.inSourceImagesList, inSourceImagesFiles, existingFiles, True, False, missingFiles) 
        inSourceImagesDropAction = self.ui.inSourceImagesList
        inSourceImagesDropAction.installEventFilter(inSourceDropEvent(self))           
        #Populate Missing Files List
        missingFilesPop = self.populateTable(self.ui.missingTexturesList, missingFiles, inSourceImagesFiles, False, True)
        missingFilesDropAction = self.ui.missingTexturesList
        missingFilesDropAction.installEventFilter(inSourceDropEvent(self))
        #Populate NodeTypes List
        self.newButtons = []
        self.ui.xmlLocation.setText(self.typeListFile)
        for nodeType, param in self.fileTypes.items():
            rowCount = self.ui.nodeTypesList.rowCount()
            self.ui.nodeTypesList.insertRow(rowCount)
            self.newButtons.append(QtGui.QPushButton(nodeType, self))
            self.newButtons[-1].setText('Remove')
            self.newButtons[-1].clicked.connect(partial(self.removeThisNode, nodeType=nodeType))
            self.ui.nodeTypesList.setCellWidget(rowCount, 0, self.newButtons[-1])
            self.ui.nodeTypesList.setItem(rowCount, 1, QtGui.QTableWidgetItem(nodeType))
            self.ui.nodeTypesList.setItem(rowCount, 2, QtGui.QTableWidgetItem(param))        
        #Setup Channels
        self.ui.run.clicked.connect(partial(self.runMain, fileList=existingFiles, inSourceImages=inSourceImagesFiles, missingFiles=missingFiles))
        self.ui.cancel.clicked.connect(self.cancel)
        self.ui.sourceText.setText(sourceImagesFolder)
        self.ui.refresh.clicked.connect(self.resetFileTrees)
        self.ui.browseSourceBtn.clicked.connect(self.setSourceImagesFolder)
        self.ui.browseOriginBtn.clicked.connect(self.setOriginFolder)
        #self.show()
        

    def runMain(self, fileList, inSourceImages, missingFiles):
        #All of this is temporary until the UI is built.
        autoManualMode = self.ui.autoManualButtons.itemAt(0).widget().isChecked()
        actionType = self.ui.actionTypeSelectionLayout
        keepOriginalSubfolders = self.ui.keepOriginalSubfolders.isChecked()
        updatePath = self.ui.updatePath.isChecked()
        count = actionType.count()
        for i in range(0, count):
            if actionType.itemAt(i).widget().isChecked():
                mode = self.modes[i]
                break
        if not autoManualMode:
            originFolder = self.ui.originText.text()
        else:
            originFolder = ''
        sourceFolder = self.ui.sourceText.text()
        #I will most likely need to add something here for drag and drop verses button press actions.
        if mode == 'copy' or mode == 'move':
            copyAction = self.copyFiles(fileList, inSourceImages, sourceFolder, originFolder, autoManualMode, keepOriginalSubfolders, updatePath, mode)
        elif mode == 'missing':
            if len(missingFiles) != 0:
                missingAction = self.findFilesOnComputer(missingFiles)
                self.resetFileTrees()
            else:
                cmds.confirmDialog(m='No Missing Files!')
        else:
            pass
        
    def findFilesOnComputer(self, fileList, *args):
        really = cmds.confirmDialog(m='A File search can take a very long time!  Are you sure you want to do this?', b=['Yes!', 'Nevermind'], db='Nevermind', cb='Nevermind')
        if really == 'Yes!':
            driveStr = subprocess.check_output("fsutil fsinfo drives")
            driveStr = driveStr.strip().lstrip('Drives: ')
            drives = driveStr.split()
            for nodeType in fileList:
                thisNodeType = cmds.nodeType(nodeType)
                fileParam = self.fileTypes[thisNodeType]
                fileFound = False
                try:
                    slashPath = fileList[nodeType].replace('\\', '/')
                except:
                    slashPath = fileList[nodeType]
                fileName = slashPath.rsplit('/', 1)[1]
                print 'Searching for %s..............................' %fileName
                for drive in drives:
                    print 'searching on drive', drive
                    for root, dirs, files in os.walk(drive):
                        if fileName in files:
                            newPath = os.path.join(root, fileName)
                            path = newPath.replace('\\', '/')
                            cmds.setAttr('%s.%s' % (nodeType, fileParam), path, type='string')
                            fileFound = True
                            break
                    if fileFound == True:
                        print '%s Found!!' % path
                        print '%s file path updated!' % nodeType
                        break
            print 'Search finished --------------------------------------------------------------------------------------------------'
            
        
    def setSourceImagesFolder(self):
        getSourceImagesFolder = cmds.fileDialog2(fm=3)
        self.ui.sourceText.setText(getSourceImagesFolder[0])
        
    
    def setOriginFolder(self):
        getOriginFolder = cmds.fileDialog2(fm=3)
        self.ui.originText.setText(getOriginFolder[0])
        
        
    def removeThisNode(self, nodeType):
        print 'Remove %s' % nodeType
        pass
        
        
    def copyFiles(self, fileList, inSourceImages, sourceFolder, originFolder, autoManualMode, keepOriginalSubfolders, updatePath, mode, *args):
        total = len(fileList)
        update = 0
        #I am temporarily disabling the Progress Bar until I get it working.  For version 1, I will use a print out of each file successfully copied.
        '''Dialog = QtGui.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()'''
        for nodeType, path in fileList.items():
            #print total
            update += 1
            #Update progress bar here.
            #print update

            if '/' in path:
                splitPath = path.split('/')
            elif '\\' in path:
                splitPath = path.split('\\')
            if path not in inSourceImages.values():
                #Need to add some other conditions and actions here.
                if keepOriginalSubfolders == True:
                    if 'sourceimages' in splitPath:
                        pathFrom = splitPath.index('sourceimages')
                        pathLength = len(splitPath)
                        newPath = sourceFolder
                        for x in range((pathFrom + 1), (pathLength-1)):
                            newPath = newPath + '/' + splitPath[x]
                            if not os.path.isdir(newPath):
                                os.mkdir(newPath)
                    else:
                        newPath = sourceFolder
                else:
                    newPath = sourceFolder
                if mode == 'copy':
                    shutil.copy2(path, newPath)
                    print '%s Copied Successfully!' % path
                elif mode == 'move':
                    shutil.move(path, newPath)
                    print '%s Copied Successfully!' % path
                #Progress Bar Call ---- SEE INITIAL CALL
                '''self.updateProgress.emit(update)
                time.sleep(0.1)'''
                
                updatedPath = newPath + '/' + splitPath[-1]
                thisNode = cmds.nodeType(nodeType)
                fileParam = self.fileTypes[thisNode]
                if updatePath == True:
                    cmds.setAttr('%s.%s' % (nodeType, fileParam), updatedPath, type='string')
                    print '%s Updated successfully!' % updatedPath
        #Dialog.close()        
        self.resetFileTrees()

        
    def flushTables(self):
        self.ui.existingTextureList.setRowCount(0)
        self.ui.inSourceImagesList.setRowCount(0)
        self.ui.missingTexturesList.setRowCount(0)
        

    def resetFileTrees(self):
        allFileTypes = self.getAllFiles()
        pathNames = self.getPathNames(allFileTypes)
        sceneInfo = self.getSceneInfo()
        fileExists = self.checkFileExistence(pathNames)
        existingFiles = fileExists[0]
        missingFiles = fileExists[1]
        getSourceImages = self.getSourceImagesFiles(pathNames)
        inSourceImagesFiles = getSourceImages[0]
        sourceImagesFolder = getSourceImages[1]
        self.flushTables()
        existingFilesPop = self.populateTable(self.ui.existingTextureList, existingFiles, inSourceImagesFiles, True, False)
        inSourceImagesPop = self.populateTable(self.ui.inSourceImagesList, inSourceImagesFiles, existingFiles, True, False, missingFiles)
        missingFilesPop = self.populateTable(self.ui.missingTexturesList, missingFiles, inSourceImagesFiles, False, True)
        
        


        


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 133)
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(20, 10, 361, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        #self.pushButton = QtGui.QPushButton(Dialog)
        #self.pushButton.setGeometry(QtCore.QRect(20, 40, 361, 61))
        #self.pushButton.setObjectName("pushButton")

        self.worker = atomicTextureFileManager()
        self.worker.updateProgress.connect(self.setProgress)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.progressBar.minimum = 1
        self.progressBar.maximum = 100

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        #self.pushButton.setText(QtGui.QApplication.translate("Dialog", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.progressBar.setValue(0)
        #self.pushButton.clicked.connect(self.worker.start)

    def setProgress(self, progress):
        self.progressBar.setValue(progress)


class inSourceDropEvent(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)

    def eventFilter(self, obj, event):
        #print event.type()
        if event.type() == QtCore.QEvent.DragEnter:
            #print 'Dragging'
            # we need to accept this event explicitly to be able to receive QDropEvents!
            event.accept()
        if event.type() == QtCore.QEvent.ChildRemoved:
            #print 'Dropping'
            #md = event.MimeData()
            #print event.data()
            #if md.hasUrls():
                #for url in md.urls():
                    #obj.setText(url.path())
                    #break
            event.accept()
        return QtCore.QObject.eventFilter(self, obj, event)



if __name__ == '__main__':
    run = atomicTextureFileManager(parent=atomicInterface())
    run.show()

'''  TESTING BELOW '''
'''__________________________________________________________________________________________________________________________________________'''

'''class FileEdit(QLineEdit):
        def __init__( self, parent ):
            super(FileEdit, self).__init__(parent)

            self.setDragEnabled(True)

        def dragEnterEvent( self, event ):
            data = event.mimeData()
            urls = data.urls()
            if ( urls and urls[0].scheme() == 'file' ):
                event.acceptProposedAction()

        def dragMoveEvent( self, event ):
            data = event.mimeData()
            urls = data.urls()
            if ( urls and urls[0].scheme() == 'file' ):
                event.acceptProposedAction()

        def dropEvent( self, event ):
            data = event.mimeData()
            urls = data.urls()
            if ( urls and urls[0].scheme() == 'file' ):
                # for some reason, this doubles up the intro slash
                filepath = str(urls[0].path())[1:]
                self.setText(filepath)


from PyQt4.QtCore import QObject, QEvent


class QLineEditDropHandler(QObject):
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.DragEnter:
            # we need to accept this event explicitly to be able to receive QDropEvents!
            event.accept()
        if event.type() == QEvent.Drop:
            md = event.mimeData()
            if md.hasUrls():
                for url in md.urls():
                    obj.setText(url.path())
                    break
            event.accept()
        return QObject.eventFilter(self, obj, event)


lineEdit.installEventFilter(QLineEditDropHandler(self))'''