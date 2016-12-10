from maya import cmds
import os, platform, shutil
from PySide import QtCore, QtGui
import atomic_TFM_UI as atomicUI
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from xml.etree import ElementTree as ET
from functools import partial
import subprocess
reload(atomicUI)

__author__ = 'Adam Benson'
__version__ = '1.0.0'

'''
    This is the new and improve Texture File Manager!  Here are a list of features coming up in version 1.1.0
    1. *Set drag and drop actions !!!!  MOOT !!!!!! Old Format
    2. Add tools for changing the image type, resizing and other useful operations.
    3. Fix Progress Bars
    4. Need to add "TexturesOnly" function, but still have the ability to include system files as well; Alembic files, PTEX, and probably even xGen files.  Might actually want to include any project base settings.
    5. Also need to add columns to the XML sheet.  I might like to use the scene project structure to create a drop-down list of folder options for individual entries.  i.e. sourceimages/ or cache/alembic/.  Anything that the project settings might default to. 
    6. Auto build missing XML page
    7. Selection based processing.
'''


def atomicInterface():
    mainWin = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWin), QtGui.QWidget)


class atomicTextureFileManager(QtGui.QDialog):
    updateProgress = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(atomicTextureFileManager, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = atomicUI.Ui_atomicTextureFileManager()
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
                self.fileTypes[child.attrib['name']] = {'fileNameParam':child[0].text, 'defaultPath':child[1].text}
        else:
            print 'XML File cannot be found!'
        self.modes = {0: 'copy', 1: 'move', 2: 'missing', 3: 'consolidate'}
        self.preloadSystem()

    def removeThisNode(self, nodeType):
        print 'Remove %s' % nodeType
        xml = ET.parse(self.typeListFile)
        root_element = xml.getroot()
        for child in root_element.iter('nodeType'):
            if child.attrib['name'] == nodeType:
                root_element.remove(child)
        xml.write(self.typeListFile)
        self.fileTypes.clear()
        for child in root_element:
            self.fileTypes[child.attrib['name']] = {'fileNameParam':child[0].text, 'defaultPath':child[1].text}
        self.setFileTypesList()


    def buildDefaultXML(self):
        proceed = cmds.confirmDialg(m='No File Types XML file found.  Would you like to create one now?', button=['Yes', 'No'])
        if proceed:
            getFolder = cmds.fileDialog2(fm=3)
            print getFolder
    
    def cancel(self):
        # Close the window
        self.close()

    def getAllFiles(self):
        allFileTypes = {}
        for thisType in self.fileTypes:
            try:
                selectedType = cmds.ls(type=thisType)
                if len(selectedType) != 0:
                    allFileTypes[thisType] = selectedType
            except:
                pass
        return allFileTypes

    def getPathNames(self, allFileTypes):
        allPaths = {}
        for type in allFileTypes:
            shortList = allFileTypes[type]
            for thisNode in shortList:
                pathName = cmds.getAttr('%s.%s' % (thisNode, self.fileTypes[type]['fileNameParam']))
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
                inSourceSubs.append(testPath)
        for each in files:
            path = files[each]
            try:
                if sourcefolder in path:
                    pathNoFile = path.rsplit('/', 1)[0]
                    if pathNoFile in sourceImages or pathNoFile in inSourceSubs:
                        inSourceImages[each] = path

            except:
                pass
        return inSourceImages, sourceImages

    def populateTable(self, table, existingFiles, inSourceFiles, missingFiles, *args):
        allFiles = existingFiles.copy()
        allFiles.update(missingFiles)
        for nodeType, path in allFiles.items():
            rowCount = table.rowCount()
            table.insertRow(rowCount)
            if os.path.exists(path):
                thisImage = QtGui.QPixmap(path)
            else:
                thisImage = QtGui.QPixmap()
            thisImage.scaled(5, 5, QtCore.Qt.KeepAspectRatioByExpanding)
            imageLabel = QtGui.QLabel()
            imageLabel.setScaledContents(True)
            imageLabel.setFixedHeight(100)
            imageLabel.setFixedWidth(100)
            imageLabel.setPixmap(thisImage)
            imageLabel.setToolTip(path)
            col = 0
            table.setCellWidget(rowCount, col, imageLabel)
            table.setItem(rowCount, (col + 1), QtGui.QTableWidgetItem(nodeType))
            table.setItem(rowCount, (col + 3), QtGui.QTableWidgetItem(path))
            # Check to see if the file matches the 'sourceimages' folder.  This is a two way process.
            # If sourceimages is being iterated, then existingImages or missingImages will be compared.
            inSourceColor = False
            missingColor = False
            for inNodeType, inPath in inSourceFiles.items():
                if inPath in path:
                    thisColor = QtGui.QColor(0, 100, 0)
                    inSourceColor = True
                    break
                else:
                    inSourceColor = False
            for inNodeType, inPath in missingFiles.items():
                if inPath in path:
                    thisColor = QtGui.QColor(100, 0, 0)
                    missingColor = True
                    break
                else:
                    missingColor = False
            if inSourceColor or missingColor:
                thisList = table.item(rowCount, col + 1)
                thisList.setBackground(thisColor)
                thisList = table.item(rowCount, (col + 3))
                thisList.setBackground(thisColor)


    def preloadSystem(self):
        # get scene data
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
                
        self.ui.colorKeyCurrent.setAutoFillBackground(True)
        self.ui.colorKeyMissing.setAutoFillBackground(True)
        currentColor = QtGui.QColor(0, 100, 0)
        missingColor = QtGui.QColor(100, 0, 0)
        alpha = 255
        currentValues = "{r}, {g}, {b}, {a}".format(r=currentColor.red(), g=currentColor.green(), b=currentColor.blue(), a=alpha)
        missingValues = "{r}, {g}, {b}, {a}".format(r=missingColor.red(), g=missingColor.green(), b=missingColor.blue(), a=alpha)
        
        self.ui.colorKeyCurrent.setStyleSheet("QLabel { background-color: rgba(" + currentValues + "); }")
        self.ui.colorKeyMissing.setStyleSheet("QLabel { background-color: rgba(" + missingValues + "); }")

        # Populate Existing Files List
        self.populateTable(self.ui.existingTextureList, existingFiles, inSourceImagesFiles, missingFiles)
        
        # setup File Types List
        self.setFileTypesList()
        dropDown = self.foldersDropDown()[0]
        selectIndex = self.foldersDropDown()[1]
        for subFolder in dropDown:
            self.ui.defaultFolder.addItem(subFolder)
            if '/sourceimages' in subFolder:
                self.ui.defaultFolder.setCurrentIndex(selectIndex)
                #self.ui.defaultFolderTypes.set CurrentRow(selectIndex)
        for subFolder in dropDown:
            self.ui.defaultFolderTypes.addItem(subFolder)
        
        # Setup Channels
        self.setRunButton(existingFiles, inSourceImagesFiles, missingFiles)
        self.ui.cancel.clicked.connect(self.cancel)
        self.ui.sourceText.setText(sourceImagesFolder)
        self.ui.refresh.clicked.connect(self.resetFileTrees)
        self.ui.browseSourceBtn.clicked.connect(self.setSourceImagesFolder)
        #self.ui.browseOriginBtn.clicked.connect(self.setOriginFolder)
        self.ui.newNodeType.setPlaceholderText('Node Type')
        self.ui.newParameterName.setPlaceholderText('File Parameter')
        # self.show()

    def foldersDropDown(self):
        projectFolder = self.getSceneInfo()
        defaultFolder = projectFolder['project']
        allSubFolders = []
        for root, dirs, files in os.walk(defaultFolder):
            cutPath = root.split(defaultFolder)[1]
            shortPath = cutPath.replace('\\', '/')
            print 'Raw Short Path', shortPath
            if '/scenes' in shortPath or '/autosave' in shortPath:
                pass
            else:
                print '/scenes, /autosave CHECK:', shortPath
                allSubFolders.append(shortPath)
                if  '/sourceimages' in shortPath:
                    selectIndex = allSubFolders.index(shortPath)
        return allSubFolders, selectIndex
        
    
    
    def runMain(self, fileList, inSourceImages, missingFiles):
        # All of this is temporary until the UI is built.
        # autoManualMode = self.ui.autoManualButtons.itemAt(0).widget().isChecked()
        actionType = self.ui.actionTypeSelectionLayout
        keepOriginalSubfolders = self.ui.keepOriginalSubfolders.isChecked()
        updatePath = self.ui.updatePath.isChecked()
        count = actionType.count()
        for i in range(0, count):
            if actionType.itemAt(i).widget().isChecked():
                mode = self.modes[i]
                break
        sourceFolder = self.ui.sourceText.text()
        # I will most likely need to add something here for drag and drop verses button press actions.
        if mode == 'copy' or mode == 'move':
            try:
                copyAction = self.copyFiles(fileList, inSourceImages, sourceFolder, keepOriginalSubfolders, updatePath, mode)
            except:
                cmds.confirmDialog(m='These files cannot be copied.  It is possibly due to selection of a missing file.  Try running "Attempt Missing File Search" on this selection first.')
        elif mode == 'missing':
            if len(missingFiles) != 0:
                self.findFilesOnComputer(missingFiles)
                self.resetFileTrees()
            else:
                cmds.confirmDialog(m='No Missing Files!')
        else:
            pass
            
    def addNodeType(self):
        print 'Add Node Type'
        nodeType = self.ui.newNodeType.text()
        parameterName = self.ui.newParameterName.text()
        defaultFolderName = self.ui.defaultFolderName.text()
        xml = ET.parse(self.typeListFile)
        root_element = xml.getroot()
        newNode = ET.Element('nodeType', name=nodeType)
        newParam = ET.SubElement(newNode, 'fileNameParam')
        newParam.text = parameterName
        newDefault = ET.SubElement(newNode, 'defaultPath')
        newDefault.text = defaultFolderName
        root_element.append(newNode)
        xml.write(self.typeListFile)
        self.fileTypes[nodeType] = {'fileNameParam':parameterName, 'defaultPath':defaultFolderName}
        self.setFileTypesList()
        
    
    def setFileTypesList(self):
        # Populate NodeTypes List in Settings Tab
        self.ui.nodeTypesList.setRowCount(0)
        self.ui.newNodeType.setText('')
        self.ui.newParameterName.setText('')
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
            self.ui.nodeTypesList.setItem(rowCount, 2, QtGui.QTableWidgetItem(param['defaultPath']))
            self.ui.nodeTypesList.setItem(rowCount, 3, QtGui.QTableWidgetItem(param['fileNameParam']))
        self.ui.addNodeType.clicked.connect(partial(self.addNodeType))

    def findFilesOnComputer(self, fileList, *args):
        really = cmds.confirmDialog(m='A File search can take a very long time!  Are you sure you want to do this?', b=['Yes!', 'Nevermind'], db='Nevermind', cb='Nevermind')
        if really == 'Yes!':
            driveStr = subprocess.check_output("fsutil fsinfo drives")
            driveStr = driveStr.strip().lstrip('Drives: ')
            drives = driveStr.split()
            selectedFiles = self.getSelectedItems(fileList)
            for nodeType in selectedFiles:
                thisNodeType = cmds.nodeType(nodeType)
                fileParam = self.fileTypes[thisNodeType]['fileNameParam'] 
                fileDefaultPath = self.fileTypes[thisNodeType]['defaultPath']
                fileFound = False
                try:
                    slashPath = selectedFiles[nodeType].replace('\\', '/') # ['fileNameParam'] This "fileNameParam" and "Default Path" could be stuff that I threw in to tag the new all files system
                except:
                    slashPath = selectedFiles[nodeType]
                fileName = slashPath.rsplit('/', 1)[1]
                print 'Searching for %s..............................' % fileName
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
        self.resetFileTrees()

    def setSourceImagesFolder(self):
        getSourceImagesFolder = cmds.fileDialog2(fm=3)
        self.ui.sourceText.setText(getSourceImagesFolder[0])

    def setOriginFolder(self):
        getOriginFolder = cmds.fileDialog2(fm=3)
        self.ui.originText.setText(getOriginFolder[0])

    def getSelectedItems(self, fileList):
        getSelection = self.ui.existingTextureList.selectedItems()
        selectedFileList = {}
        if getSelection:
            total = len(getSelection)
            for selected in range(0, total, 2):
                selectedNode = getSelection[selected].text()
                selectedFileList[selectedNode] = getSelection[selected + 1].text()
        else:
            selectedFileList = fileList
        return selectedFileList

    def copyFiles(self, fileList, inSourceImages, sourceFolder, keepOriginalSubfolders, updatePath, mode, *args):
        total = len(fileList)
        update = 0
        selectedFileList = self.getSelectedItems(fileList)
        # I am temporarily disabling the Progress Bar until I get it working.  For version 1, I will use a print out of each file successfully copied.
        '''Dialog = QtGui.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()'''
        for nodeType, path in selectedFileList.items():
            # print total
            update += 1
            # Update progress bar here.
            # print update

            if '/' in path:
                splitPath = path.split('/')
            elif '\\' in path:
                splitPath = path.split('\\')
            if path not in inSourceImages.values():
                # Need to add some other conditions and actions here.
                if keepOriginalSubfolders == True:
                    if 'sourceimages' in splitPath:
                        pathFrom = splitPath.index('sourceimages')
                        pathLength = len(splitPath)
                        newPath = sourceFolder
                        for x in range((pathFrom + 1), (pathLength - 1)):
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
                    print '%s Moved Successfully!' % path
                # Progress Bar Call ---- SEE INITIAL CALL
                '''self.updateProgress.emit(update)
                time.sleep(0.1)'''

                updatedPath = newPath + '/' + splitPath[-1]
                thisNode = cmds.nodeType(nodeType)
                fileParam = self.fileTypes[thisNode]['fileNameParam']
                defaultPath = self.fileTypes[thisNode]['defaultPath']
                if updatePath == True:
                    cmds.setAttr('%s.%s' % (nodeType, fileParam), updatedPath, type='string')
                    print '%s Updated successfully!' % updatedPath
        # Dialog.close()
        self.resetFileTrees()
    
    def setRunButton(self, existingFiles, inSourceImagesFiles, missingFiles):
        self.ui.run.clicked.connect(partial(self.runMain, fileList=existingFiles, inSourceImages=inSourceImagesFiles, missingFiles=missingFiles))

    def flushTables(self):
        self.ui.existingTextureList.setRowCount(0)

    def resetFileTrees(self):
        allFileTypes = self.getAllFiles()
        pathNames = self.getPathNames(allFileTypes)
        fileExists = self.checkFileExistence(pathNames)
        existingFiles = fileExists[0]
        missingFiles = fileExists[1]
        getSourceImages = self.getSourceImagesFiles(pathNames)
        inSourceImagesFiles = getSourceImages[0]
        self.flushTables()
        self.setRunButton(existingFiles, inSourceImagesFiles, missingFiles)
        self.populateTable(self.ui.existingTextureList, existingFiles, inSourceImagesFiles, missingFiles)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 133)
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(20, 10, 361, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        # self.pushButton = QtGui.QPushButton(Dialog)
        # self.pushButton.setGeometry(QtCore.QRect(20, 40, 361, 61))
        # self.pushButton.setObjectName("pushButton")

        self.worker = atomicTextureFileManager()
        self.worker.updateProgress.connect(self.setProgress)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.progressBar.minimum = 1
        self.progressBar.maximum = 100

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        # self.pushButton.setText(QtGui.QApplication.translate("Dialog", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.progressBar.setValue(0)
        # self.pushButton.clicked.connect(self.worker.start)

    def setProgress(self, progress):
        self.progressBar.setValue(progress)



if __name__ == '__main__':
    run = atomicTextureFileManager(parent=atomicInterface())
    run.show()

