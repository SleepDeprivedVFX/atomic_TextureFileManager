from maya import cmds
import os, platform, shutil
from PySide import QtCore, QtGui
import atomic_TFM_UI as atomicUI
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from xml.etree import ElementTree as ET
from functools import partial
import subprocess, glob, re

reload(atomicUI)

__author__ = 'Adam Benson'
__version__ = '1.0.2'

'''
    This is the new and improve Texture File Manager!  Here are a list of features coming up in version 1.1.0
    1. *Set drag and drop actions !!!!  MOOT !!!!!! Old Format
    2. Add tools for changing the image type, resizing and other useful operations.
    3. Fix Progress Bars
    4. Need to add "TexturesOnly" function, but still have the ability to include system files as well; Alembic files, PTEX, and probably even xGen files.  Might actually want to include any project base settings.
    5. Also need to add columns to the XML sheet.  I might like to use the scene project structure to create a drop-down list of folder options for individual entries.  i.e. sourceimages/ or cache/alembic/.  Anything that the project settings might default to. 
    6. Auto build missing XML page
    7. Selection based processing.

    KNOWN ISSUES:
    1. An empty render layer, selected in the list, will throw an error
    2. UDIMM style file formatting currently does not work
    3. There are currently name restrictions, forcing objects to have the same name.  Very difficult when importing objects
        into the base level.
    4. Image Planes have caused failures on the preload
    5. The file types system is currently not selecting file types automatically, and the system currently does not work.
    6. Selection mode fails copy/move if a missing file is selected.  vice verse.

    NOTES:
    1. The File Types List system on the front page should be populated by the custom list, setup on the last page.
        It should have everything selected by default, but it should have two radio buttons: one for "Select All" and the
        other for "Textures Only".  Textures Only should only search for objects in the /sourceimages folder, while option
        one would select everything in the XML file type list.
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
        self.tagTypes = re.compile(r'(<UDIM>)' r'|(U<U>_V<V>)' r'|(u<U>_v<V>)' r'|(<UVTILE>)' r'|(u|U\d*_v|V\d*)')
        scriptsFolders = os.environ['MAYA_SCRIPT_PATH'].split(';')
        for folder in scriptsFolders:
            if os.path.exists(folder + '/atfm_TypeList.xml'):
                self.typeListFile = folder + '/atfm_TypeList.xml'
                break
        if self.typeListFile == '':
            self.typeListFile = self.buildDefaultXML()
        if self.typeListFile != '':
            xml = ET.parse(self.typeListFile)
            root_element = xml.getroot()
            for child in root_element:
                self.fileTypes[child.attrib['name']] = {'fileNameParam': child[0].text, 'defaultPath': child[1].text}
        else:
            print 'No XML file can be found or created!'

        self.modes = {0: 'copy', 1: 'move', 2: 'missing'}
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
            self.fileTypes[child.attrib['name']] = {'fileNameParam': child[0].text, 'defaultPath': child[1].text}
        self.setFileTypesList()

    def buildDefaultXML(self):
        proceed = cmds.confirmDialog(m='No File Types XML file found.  Would you like to create one now?', button=['Yes', 'No'])
        newFile = ''
        if proceed:
            getFolder = cmds.fileDialog2(fm=3)[0]
            xmlString = '<atfm_TypeList>'
            xmlString += '<nodeType name="file"><fileNameParam>fileTextureName</fileNameParam><defaultPath>/sourceimages</defaultPath></nodeType>'
            xmlString += '<nodeType name="mentalrayTexture"><fileNameParam>fileTextureName</fileNameParam><defaultPath>/sourceimages</defaultPath></nodeType>'
            xmlString += '<nodeType name="mentalrayIblShape"> <fileNameParam>texture</fileNameParam>	<defaultPath>/sourceimages</defaultPath></nodeType>'
            xmlString += '<nodeType name="aiImage">	<fileNameParam>filename</fileNameParam>	<defaultPath>/sourceimages</defaultPath></nodeType>'
            xmlString += '<nodeType name="rmanImageFile">	<fileNameParam>File</fileNameParam>	<defaultPath>/sourceimages</defaultPath></nodeType>'
            xmlString += '<nodeType name="imagePlane"><fileNameParam>imagePlane</fileNameParam><defaultPath>/sourceimages</defaultPath></nodeType>'
            xmlString += '<nodeType name="AlembicNode"><fileNameParam>abc_File</fileNameParam><defaultPath>/cache/alembic</defaultPath></nodeType>'
            xmlString += '</atfm_TypeList>'

            newFile = (getFolder + '/atfm_TypeList.xml')
            newXML = open(newFile, 'w')
            newXML.write(xmlString)
            newXML.close()
        else:
            print 'Wah wah!'
        return newFile

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
        # PathNames contains all of the files in the search parameters
        pathNames = self.getPathNames(allFileTypes)
        # fileExists helps create existingFiles and missingFiles.  These two separate pathNames into either an existing,
        # or missing file list.
        fileExists = self.checkFileExistence(pathNames)
        existingFiles = fileExists[0]
        missingFiles = fileExists[1]
        # ATTENTION!!  getSourceImages, inSourceImages and sourceImagesFolder are really misnomers.  It should really be
        # called something like getProperFileStructure or something like that. inProperFileStructure. Think of it that
        # way.
        getSourceImages = self.getSourceImagesFiles(pathNames)
        inSourceImagesFiles = getSourceImages[0]
        sourceImagesFolder = getSourceImages[1]

        self.ui.existingTextureList.verticalHeader().setDefaultSectionSize(100);

        self.ui.colorKeyCurrent.setAutoFillBackground(True)
        self.ui.colorKeyMissing.setAutoFillBackground(True)
        currentColor = QtGui.QColor(0, 100, 0)
        missingColor = QtGui.QColor(100, 0, 0)
        alpha = 255
        currentValues = "{r}, {g}, {b}, {a}".format(r=currentColor.red(), g=currentColor.green(), b=currentColor.blue(),
                                                    a=alpha)
        missingValues = "{r}, {g}, {b}, {a}".format(r=missingColor.red(), g=missingColor.green(), b=missingColor.blue(),
                                                    a=alpha)

        self.ui.colorKeyCurrent.setStyleSheet("QLabel { background-color: rgba(" + currentValues + "); }")
        self.ui.colorKeyMissing.setStyleSheet("QLabel { background-color: rgba(" + missingValues + "); }")

        # Populate Files List
        self.populateTable(self.ui.existingTextureList, existingFiles, inSourceImagesFiles, missingFiles)

        # setup File Types List in the settings tab
        self.setFileTypesList()

        # This dropDown, selectIndex system is not currently working as promised.  dropDown is populating with the
        # setCurrentIndex() call in the if statement below.
        dropDown = self.foldersDropDown()[0]
        selectIndex = self.foldersDropDown()[1]
        for subFolder in dropDown:
            self.ui.defaultFolder.addItem(subFolder)
            self.ui.defaultFolderTypes.addItem(subFolder)
            if '/sourceimages' in subFolder:
                self.ui.defaultFolder.setCurrentIndex(selectIndex)
                # self.ui.defaultFolderTypes.set CurrentRow(selectIndex)

        # Setup button actions and connections
        self.setRunButton(existingFiles, inSourceImagesFiles, missingFiles)
        self.ui.cancel.clicked.connect(self.cancel)
        self.ui.sourceText.setText(sourceImagesFolder)
        self.ui.refresh.clicked.connect(self.resetFileTrees)
        self.ui.browseSourceBtn.clicked.connect(self.setSourceImagesFolder)
        # self.ui.browseOriginBtn.clicked.connect(self.setOriginFolder)
        self.ui.newNodeType.setPlaceholderText('Node Type')
        self.ui.newParameterName.setPlaceholderText('File Parameter')

    def foldersDropDown(self):
        projectFolder = self.getSceneInfo()
        defaultFolder = projectFolder['project']
        allSubFolders = []
        selectIndex = ''
        for root in os.listdir(defaultFolder):
            shortPath = '/' + root
            checkPath = defaultFolder + shortPath
            if os.path.isdir(checkPath):
                if '/scenes' in shortPath or '/autosave' in shortPath:
                    pass
                else:
                    allSubFolders.append(shortPath)
                    if '/sourceimages' in shortPath:
                        selectIndex = allSubFolders.index(shortPath)
        return allSubFolders, selectIndex

    def runMain(self, fileList, inSourceImages, missingFiles):
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
                self.copyFiles(fileList, inSourceImages, sourceFolder, keepOriginalSubfolders, updatePath, mode)
            except:
                cmds.confirmDialog(
                    m='These files cannot be copied.  It is possibly due to selection of a missing file.  Try running "Attempt Missing File Search" on this selection first.')
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
        self.fileTypes[nodeType] = {'fileNameParam': parameterName, 'defaultPath': defaultFolderName}
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
                fileFound = False
                try:
                    slashPath = selectedFiles[nodeType].replace('\\', '/')  # ['fileNameParam'] This "fileNameParam" and "Default Path" could be stuff that I threw in to tag the new all files system
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

    def getImageCollection(self, path, tag):
        splitPath = path.rsplit('/')
        basePath = splitPath[0]
        fileName = splitPath[1]
        splitFile = fileName.split(tag)
        pre = splitFile[0]
        post = splitFile[1]
        print tag
        print basePath
        print fileName
        print pre
        print post


    def copyFiles(self, fileList, inSourceImages, sourceFolder, keepOriginalSubfolders, updatePath, mode, *args):
        update = 0
        selectedFileList = self.getSelectedItems(fileList)
        # I am temporarily disabling the Progress Bar until I get it working.  For version 1, I will use a print out of
        # each file successfully copied.
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
                # ALERT!!  This method will most likely fail alembic copies, or any other non-sourceimages files.
                # This is also just for the subfolder search.  I think I just need to replace 'sourceimages' with a
                # bona-fide variable from one of the folder type lists.
                if keepOriginalSubfolders:
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
                tagFound = ''
                tag = self.tagTypes.search(path)
                if tag:
                    tagFound = tag.group()
                else:
                    tagFound = ''

                if tagFound:
                    # Here I will have to get a list of all the filenames that fit into the correct image sequence.
                    pathList = self.getImageCollection(path, tagFound)
                    print 'TAG FOUND: %s' % tagFound
                    # This should probably be a list of file paths.  That way, the other path could be put into a list
                    # by itself, and both could be iterated through the copy/move commands
                else:
                    pathList = [path]
                    print 'NO TAG FOUND!!!'
                    
                if mode == 'copy':
                    for thisPath in pathList:
                        shutil.copy2(thisPath, newPath)
                        print '%s Copied Successfully!' % path
                elif mode == 'move':
                    for thisPath in pathList:
                        shutil.move(thisPath, newPath)
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
        self.ui.run.clicked.connect(partial(self.runMain, fileList=existingFiles, inSourceImages=inSourceImagesFiles,
                                            missingFiles=missingFiles))

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


if __name__ == '__main__':
    run = atomicTextureFileManager(parent=atomicInterface())
    run.show()
