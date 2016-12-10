from maya import cmds
import os, platform, shutil
try:
    from PySide2 import QtCore as core
    from PySide2 import QtGui as gui
    from PySide2 import QtWidgets as widg
except:
    from PySide import QtCore as core
    from PySide import QtGui as gui
    widg = gui.QWidget

#import atomic_TFM_UI as atomicUI

try:
    from shiboken2 import wrapInstance
except:
    from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from xml.etree import ElementTree as ET
from functools import partial
import subprocess, glob, re

#reload(atomicUI)

__author__ = 'Adam Benson'
__version__ = '1.0.3'

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
    return wrapInstance(long(mainWin), widg)


class atomicTextureFileManager(widg.QDialog):
    updateProgress = core.Signal(int)

    def __init__(self, parent=None):
        super(atomicTextureFileManager, self).__init__(parent)
        self.setWindowFlags(core.Qt.Tool)
        self.ui = atomicUI()
        self.ui.setupUi(self)
        self.fileTypes = {}
        self.typeListFile = ''
        self.tagTypes = re.compile(r'(<UDIM>)|(U<U>_V<V>)|(u<U>_v<V>)|(<UVTILE>)|(u|U\d*_v|V\d*)')
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
                thisImage = gui.QPixmap(path)
            else:
                thisImage = gui.QPixmap()
            thisImage.scaled(5, 5, core.Qt.KeepAspectRatioByExpanding)
            imageLabel = gui.QLabel()
            imageLabel.setScaledContents(True)
            imageLabel.setFixedHeight(100)
            imageLabel.setFixedWidth(100)
            imageLabel.setPixmap(thisImage)
            imageLabel.setToolTip(path)
            col = 0
            table.setCellWidget(rowCount, col, imageLabel)
            table.setItem(rowCount, (col + 1), gui.QTableWidgetItem(nodeType))
            table.setItem(rowCount, (col + 3), gui.QTableWidgetItem(path))
            # Check to see if the file matches the 'sourceimages' folder.  This is a two way process.
            # If sourceimages is being iterated, then existingImages or missingImages will be compared.
            inSourceColor = False
            missingColor = False
            for inNodeType, inPath in inSourceFiles.items():
                if inPath in path:
                    thisColor = gui.QColor(0, 100, 0)
                    inSourceColor = True
                    break
                else:
                    inSourceColor = False
            for inNodeType, inPath in missingFiles.items():
                if inPath in path:
                    thisColor = gui.QColor(100, 0, 0)
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
        currentColor = gui.QColor(0, 100, 0)
        missingColor = gui.QColor(100, 0, 0)
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
            self.newButtons.append(gui.QPushButton(nodeType, self))
            self.newButtons[-1].setText('Remove')
            self.newButtons[-1].clicked.connect(partial(self.removeThisNode, nodeType=nodeType))
            self.ui.nodeTypesList.setCellWidget(rowCount, 0, self.newButtons[-1])
            self.ui.nodeTypesList.setItem(rowCount, 1, gui.QTableWidgetItem(nodeType))
            self.ui.nodeTypesList.setItem(rowCount, 2, gui.QTableWidgetItem(param['defaultPath']))
            self.ui.nodeTypesList.setItem(rowCount, 3, gui.QTableWidgetItem(param['fileNameParam']))
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

class atomicUI(object):
    def setupUi(self, atomicTextureFileManager):
        atomicTextureFileManager.setObjectName("atomicTextureFileManager")
        atomicTextureFileManager.resize(1289, 923)
        self.centralwidget = gui.QWidget(atomicTextureFileManager)
        sizePolicy = gui.QSizePolicy(gui.QSizePolicy.Expanding, gui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(core.QSize(896, 858))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_8 = gui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.tabWidget = gui.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)
        sizePolicy = gui.QSizePolicy(gui.QSizePolicy.Expanding, gui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setAutoFillBackground(True)
        self.tabWidget.setObjectName("tabWidget")
        self.filesTab = gui.QWidget()
        sizePolicy = gui.QSizePolicy(gui.QSizePolicy.Expanding, gui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filesTab.sizePolicy().hasHeightForWidth())
        self.filesTab.setSizePolicy(sizePolicy)
        self.filesTab.setObjectName("filesTab")
        self.verticalLayout = gui.QVBoxLayout(self.filesTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TextureLists = gui.QFrame(self.filesTab)
        sizePolicy = gui.QSizePolicy(gui.QSizePolicy.Expanding, gui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TextureLists.sizePolicy().hasHeightForWidth())
        self.TextureLists.setSizePolicy(sizePolicy)
        self.TextureLists.setAutoFillBackground(False)
        self.TextureLists.setFrameShape(gui.QFrame.StyledPanel)
        self.TextureLists.setFrameShadow(gui.QFrame.Raised)
        self.TextureLists.setObjectName("TextureLists")
        self.verticalLayout_4 = gui.QVBoxLayout(self.TextureLists)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.frame = gui.QFrame(self.TextureLists)
        sizePolicy = gui.QSizePolicy(gui.QSizePolicy.Expanding, gui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFocusPolicy(core.Qt.TabFocus)
        self.frame.setObjectName("frame")
        self.horizontalLayout = gui.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.existingTextureGrid = gui.QGridLayout()
        self.existingTextureGrid.setObjectName("existingTextureGrid")
        self.existingTextureLabel = gui.QLabel(self.frame)
        self.existingTextureLabel.setObjectName("existingTextureLabel")
        self.existingTextureGrid.addWidget(self.existingTextureLabel, 1, 0, 1, 1)
        self.horizontalLayout_4 = gui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.colorKeyCurrent = gui.QLabel(self.frame)
        self.colorKeyCurrent.setObjectName("colorKeyCurrent")
        self.horizontalLayout_4.addWidget(self.colorKeyCurrent)
        self.colorKeyMissing = gui.QLabel(self.frame)
        self.colorKeyMissing.setObjectName("colorKeyMissing")
        self.horizontalLayout_4.addWidget(self.colorKeyMissing)
        spacerItem = gui.QSpacerItem(40, 20, gui.QSizePolicy.Expanding, gui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.existingTextureGrid.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)
        self.existingTextureList = gui.QTableWidget(self.frame)
        self.existingTextureList.setDragEnabled(True)
        self.existingTextureList.setDragDropMode(gui.QAbstractItemView.DragOnly)
        self.existingTextureList.setSelectionMode(gui.QAbstractItemView.MultiSelection)
        self.existingTextureList.setSelectionBehavior(gui.QAbstractItemView.SelectRows)
        self.existingTextureList.setObjectName("existingTextureList")
        self.existingTextureList.setColumnCount(4)
        self.existingTextureList.setRowCount(0)
        item = gui.QTableWidgetItem()
        self.existingTextureList.setHorizontalHeaderItem(0, item)
        item = gui.QTableWidgetItem()
        self.existingTextureList.setHorizontalHeaderItem(1, item)
        item = gui.QTableWidgetItem()
        self.existingTextureList.setHorizontalHeaderItem(2, item)
        item = gui.QTableWidgetItem()
        self.existingTextureList.setHorizontalHeaderItem(3, item)
        self.existingTextureList.horizontalHeader().setDefaultSectionSize(200)
        self.existingTextureList.horizontalHeader().setMinimumSectionSize(90)
        self.existingTextureList.horizontalHeader().setStretchLastSection(True)
        self.existingTextureList.verticalHeader().setCascadingSectionResizes(True)
        self.existingTextureList.verticalHeader().setDefaultSectionSize(30)
        self.existingTextureGrid.addWidget(self.existingTextureList, 0, 0, 1, 1)
        self.horizontalLayout.addLayout(self.existingTextureGrid)
        self.verticalLayout_4.addWidget(self.frame)
        self.TextureSettings = gui.QToolBox(self.TextureLists)
        self.TextureSettings.setObjectName("TextureSettings")
        self.operations = gui.QWidget()
        self.operations.setGeometry(core.QRect(0, 0, 1203, 301))
        self.operations.setObjectName("operations")
        self.verticalLayout_5 = gui.QVBoxLayout(self.operations)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_3 = gui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = gui.QLabel(self.operations)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.browseSourceBtn = gui.QPushButton(self.operations)
        self.browseSourceBtn.setObjectName("browseSourceBtn")
        self.horizontalLayout_3.addWidget(self.browseSourceBtn)
        self.sourceText = gui.QLineEdit(self.operations)
        self.sourceText.setText("")
        self.sourceText.setObjectName("sourceText")
        self.horizontalLayout_3.addWidget(self.sourceText)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.actionTypeSelectionLayout = gui.QHBoxLayout()
        self.actionTypeSelectionLayout.setObjectName("actionTypeSelectionLayout")
        self.copyToSrcImgs = gui.QRadioButton(self.operations)
        self.copyToSrcImgs.setChecked(True)
        self.copyToSrcImgs.setObjectName("copyToSrcImgs")
        self.actionTypeSelectionLayout.addWidget(self.copyToSrcImgs)
        self.moveToSrcImgs = gui.QRadioButton(self.operations)
        self.moveToSrcImgs.setObjectName("moveToSrcImgs")
        self.actionTypeSelectionLayout.addWidget(self.moveToSrcImgs)
        self.missingFileSearch = gui.QRadioButton(self.operations)
        self.missingFileSearch.setObjectName("missingFileSearch")
        self.actionTypeSelectionLayout.addWidget(self.missingFileSearch)
        self.verticalLayout_5.addLayout(self.actionTypeSelectionLayout)
        self.updatePath = gui.QCheckBox(self.operations)
        self.updatePath.setChecked(True)
        self.updatePath.setObjectName("updatePath")
        self.verticalLayout_5.addWidget(self.updatePath)
        self.keepOriginalSubfolders = gui.QCheckBox(self.operations)
        self.keepOriginalSubfolders.setChecked(True)
        self.keepOriginalSubfolders.setObjectName("keepOriginalSubfolders")
        self.verticalLayout_5.addWidget(self.keepOriginalSubfolders)
        spacerItem1 = gui.QSpacerItem(20, 40, gui.QSizePolicy.Minimum, gui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.TextureSettings.addItem(self.operations, "")
        self.options = gui.QWidget()
        self.options.setGeometry(core.QRect(0, 0, 1203, 301))
        self.options.setObjectName("options")
        self.defaultFolderTypes = gui.QListWidget(self.options)
        self.defaultFolderTypes.setGeometry(core.QRect(0, 60, 1121, 201))
        self.defaultFolderTypes.setAlternatingRowColors(True)
        self.defaultFolderTypes.setSelectionMode(gui.QAbstractItemView.MultiSelection)
        self.defaultFolderTypes.setResizeMode(gui.QListView.Adjust)
        self.defaultFolderTypes.setLayoutMode(gui.QListView.Batched)
        self.defaultFolderTypes.setUniformItemSizes(True)
        self.defaultFolderTypes.setObjectName("defaultFolderTypes")
        self.checkBox = gui.QCheckBox(self.options)
        self.checkBox.setGeometry(core.QRect(0, 30, 201, 25))
        self.checkBox.setChecked(False)
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = gui.QCheckBox(self.options)
        self.checkBox_2.setGeometry(core.QRect(230, 30, 191, 25))
        self.checkBox_2.setChecked(True)
        self.checkBox_2.setObjectName("checkBox_2")
        self.label_9 = gui.QLabel(self.options)
        self.label_9.setGeometry(core.QRect(1, 1, 327, 21))
        self.label_9.setObjectName("label_9")
        self.TextureSettings.addItem(self.options, "")
        self.verticalLayout_4.addWidget(self.TextureSettings)
        self.verticalLayout.addWidget(self.TextureLists)
        self.actionButtonsLayout = gui.QHBoxLayout()
        self.actionButtonsLayout.setObjectName("actionButtonsLayout")
        self.refresh = gui.QPushButton(self.filesTab)
        self.refresh.setObjectName("refresh")
        self.actionButtonsLayout.addWidget(self.refresh)
        self.cancel = gui.QPushButton(self.filesTab)
        self.cancel.setContextMenuPolicy(core.Qt.DefaultContextMenu)
        self.cancel.setObjectName("cancel")
        self.actionButtonsLayout.addWidget(self.cancel)
        self.run = gui.QPushButton(self.filesTab)
        self.run.setObjectName("run")
        self.actionButtonsLayout.addWidget(self.run)
        self.verticalLayout.addLayout(self.actionButtonsLayout)
        self.tabWidget.addTab(self.filesTab, "")
        self.toolsTab = gui.QWidget()
        self.toolsTab.setObjectName("toolsTab")
        self.verticalLayout_7 = gui.QVBoxLayout(self.toolsTab)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.toolBox = gui.QToolBox(self.toolsTab)
        self.toolBox.setObjectName("toolBox")
        self.imageResizeReformat = gui.QWidget()
        self.imageResizeReformat.setGeometry(core.QRect(0, 0, 1231, 723))
        self.imageResizeReformat.setObjectName("imageResizeReformat")
        self.toolBox.addItem(self.imageResizeReformat, "")
        self.uvTilingSetup = gui.QWidget()
        self.uvTilingSetup.setGeometry(core.QRect(0, 0, 100, 30))
        self.uvTilingSetup.setObjectName("uvTilingSetup")
        self.toolBox.addItem(self.uvTilingSetup, "")
        self.makePathsRelative = gui.QWidget()
        self.makePathsRelative.setGeometry(core.QRect(0, 0, 100, 30))
        self.makePathsRelative.setObjectName("makePathsRelative")
        self.toolBox.addItem(self.makePathsRelative, "")
        self.verticalLayout_7.addWidget(self.toolBox)
        self.tabWidget.addTab(self.toolsTab, "")
        self.settingsTab = gui.QWidget()
        self.settingsTab.setObjectName("settingsTab")
        self.verticalLayout_6 = gui.QVBoxLayout(self.settingsTab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_4 = gui.QLabel(self.settingsTab)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_6.addWidget(self.label_4)
        self.verticalLayout_3 = gui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.xmlLabel = gui.QLabel(self.settingsTab)
        self.xmlLabel.setEnabled(True)
        self.xmlLabel.setInputMethodHints(core.Qt.ImhNone)
        self.xmlLabel.setTextInteractionFlags(core.Qt.NoTextInteraction)
        self.xmlLabel.setObjectName("xmlLabel")
        self.verticalLayout_3.addWidget(self.xmlLabel)
        self.xmlLocation = gui.QLineEdit(self.settingsTab)
        self.xmlLocation.setEnabled(False)
        self.xmlLocation.setObjectName("xmlLocation")
        self.verticalLayout_3.addWidget(self.xmlLocation)
        self.verticalLayout_6.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = gui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.nodeTypesList = gui.QTableWidget(self.settingsTab)
        self.nodeTypesList.setMinimumSize(core.QSize(0, 0))
        self.nodeTypesList.setSizeIncrement(core.QSize(0, 0))
        self.nodeTypesList.setRowCount(0)
        self.nodeTypesList.setColumnCount(4)
        self.nodeTypesList.setObjectName("nodeTypesList")
        self.nodeTypesList.setColumnCount(4)
        self.nodeTypesList.setRowCount(0)
        item = gui.QTableWidgetItem()
        self.nodeTypesList.setHorizontalHeaderItem(0, item)
        item = gui.QTableWidgetItem()
        self.nodeTypesList.setHorizontalHeaderItem(1, item)
        item = gui.QTableWidgetItem()
        self.nodeTypesList.setHorizontalHeaderItem(2, item)
        item = gui.QTableWidgetItem()
        self.nodeTypesList.setHorizontalHeaderItem(3, item)
        self.nodeTypesList.horizontalHeader().setCascadingSectionResizes(False)
        self.nodeTypesList.horizontalHeader().setDefaultSectionSize(200)
        self.nodeTypesList.horizontalHeader().setMinimumSectionSize(200)
        self.nodeTypesList.horizontalHeader().setSortIndicatorShown(False)
        self.nodeTypesList.horizontalHeader().setStretchLastSection(True)
        self.nodeTypesList.verticalHeader().setCascadingSectionResizes(False)
        self.nodeTypesList.verticalHeader().setHighlightSections(True)
        self.verticalLayout_2.addWidget(self.nodeTypesList)
        self.label_3 = gui.QLabel(self.settingsTab)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.label_7 = gui.QLabel(self.settingsTab)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_2.addWidget(self.label_7)
        self.gridLayout = gui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.newParameterName = gui.QLineEdit(self.settingsTab)
        self.newParameterName.setObjectName("newParameterName")
        self.gridLayout.addWidget(self.newParameterName, 1, 2, 1, 2)
        self.addNodeType = gui.QPushButton(self.settingsTab)
        self.addNodeType.setObjectName("addNodeType")
        self.gridLayout.addWidget(self.addNodeType, 2, 3, 1, 1)
        self.pushButton = gui.QPushButton(self.settingsTab)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 5, 0, 1, 1)
        spacerItem2 = gui.QSpacerItem(20, 10, gui.QSizePolicy.Minimum, gui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 3, 1, 1)
        spacerItem3 = gui.QSpacerItem(300, 20, gui.QSizePolicy.Fixed, gui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 5, 2, 1, 1)
        self.label_5 = gui.QLabel(self.settingsTab)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)
        self.label_6 = gui.QLabel(self.settingsTab)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 2, 1, 1)
        self.newNodeType = gui.QLineEdit(self.settingsTab)
        self.newNodeType.setObjectName("newNodeType")
        self.gridLayout.addWidget(self.newNodeType, 1, 0, 1, 1)
        self.label_8 = gui.QLabel(self.settingsTab)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 4, 0, 1, 1)
        self.defaultFolderLabel = gui.QLabel(self.settingsTab)
        self.defaultFolderLabel.setObjectName("defaultFolderLabel")
        self.gridLayout.addWidget(self.defaultFolderLabel, 0, 1, 1, 1)
        self.defaultFolder = gui.QComboBox(self.settingsTab)
        self.defaultFolder.setMinimumSize(core.QSize(250, 0))
        self.defaultFolder.setInsertPolicy(gui.QComboBox.InsertAlphabetically)
        self.defaultFolder.setObjectName("defaultFolder")
        self.gridLayout.addWidget(self.defaultFolder, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout_6.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.settingsTab, "")
        self.verticalLayout_8.addWidget(self.tabWidget)
        #atomicTextureFileManager.setCentralWidget(self.centralwidget)
        self.actionCopy_Selected_To_Source = gui.QAction(atomicTextureFileManager)
        self.actionCopy_Selected_To_Source.setObjectName("actionCopy_Selected_To_Source")
        self.actionReset = gui.QAction(atomicTextureFileManager)
        self.actionReset.setObjectName("actionReset")
        self.actionMove_Selected_To_Source = gui.QAction(atomicTextureFileManager)
        self.actionMove_Selected_To_Source.setObjectName("actionMove_Selected_To_Source")
        self.actionDocumentation = gui.QAction(atomicTextureFileManager)
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
        core.QObject.connect(self.checkBox, core.SIGNAL("clicked(bool)"), self.checkBox_2.toggle)
        core.QObject.connect(self.checkBox_2, core.SIGNAL("clicked(bool)"), self.checkBox.toggle)
        core.QMetaObject.connectSlotsByName(atomicTextureFileManager)
        atomicTextureFileManager.setTabOrder(self.copyToSrcImgs, self.moveToSrcImgs)
        atomicTextureFileManager.setTabOrder(self.moveToSrcImgs, self.missingFileSearch)
        atomicTextureFileManager.setTabOrder(self.missingFileSearch, self.browseSourceBtn)
        atomicTextureFileManager.setTabOrder(self.browseSourceBtn, self.sourceText)
        atomicTextureFileManager.setTabOrder(self.sourceText, self.run)
        atomicTextureFileManager.setTabOrder(self.run, self.cancel)
        atomicTextureFileManager.setTabOrder(self.cancel, self.keepOriginalSubfolders)

    def retranslateUi(self, atomicTextureFileManager):
        atomicTextureFileManager.setWindowTitle(gui.QApplication.translate("atomicTextureFileManager", "Atomic Texture File Manager", None, gui.QApplication.UnicodeUTF8))
        self.existingTextureLabel.setText(gui.QApplication.translate("atomicTextureFileManager", "<html><head/><body><p><span style=\" font-size:12pt;\">Scene Files</span></p></body></html>", None, gui.QApplication.UnicodeUTF8))
        self.colorKeyCurrent.setText(gui.QApplication.translate("atomicTextureFileManager", "Currently in Project   ", None, gui.QApplication.UnicodeUTF8))
        self.colorKeyMissing.setText(gui.QApplication.translate("atomicTextureFileManager", "   Missing Files   ", None, gui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(0).setText(gui.QApplication.translate("atomicTextureFileManager", "Preview", None, gui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(1).setText(gui.QApplication.translate("atomicTextureFileManager", "Node Type", None, gui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(2).setText(gui.QApplication.translate("atomicTextureFileManager", "Default Folder", None, gui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(3).setText(gui.QApplication.translate("atomicTextureFileManager", "Path", None, gui.QApplication.UnicodeUTF8))
        self.label_2.setText(gui.QApplication.translate("atomicTextureFileManager", "Source Images           ", None, gui.QApplication.UnicodeUTF8))
        self.browseSourceBtn.setText(gui.QApplication.translate("atomicTextureFileManager", "Browse...", None, gui.QApplication.UnicodeUTF8))
        self.sourceText.setToolTip(gui.QApplication.translate("atomicTextureFileManager", "The existing sourceimages folder for the current Maya project, or a destination folder of your choice", None, gui.QApplication.UnicodeUTF8))
        self.sourceText.setStatusTip(gui.QApplication.translate("atomicTextureFileManager", "Current source images folder", None, gui.QApplication.UnicodeUTF8))
        self.sourceText.setPlaceholderText(gui.QApplication.translate("atomicTextureFileManager", "Source Images Folder", None, gui.QApplication.UnicodeUTF8))
        self.copyToSrcImgs.setToolTip(gui.QApplication.translate("atomicTextureFileManager", "This will copy files outside of sourceimages to the sourceimages folder", None, gui.QApplication.UnicodeUTF8))
        self.copyToSrcImgs.setStatusTip(gui.QApplication.translate("atomicTextureFileManager", "Copy files to sourceimages", None, gui.QApplication.UnicodeUTF8))
        self.copyToSrcImgs.setText(gui.QApplication.translate("atomicTextureFileManager", "Copy to sourceimages", None, gui.QApplication.UnicodeUTF8))
        self.moveToSrcImgs.setToolTip(gui.QApplication.translate("atomicTextureFileManager", "This will move any files that are not yet in the sourceimages folder, to the sourceimages folder", None, gui.QApplication.UnicodeUTF8))
        self.moveToSrcImgs.setStatusTip(gui.QApplication.translate("atomicTextureFileManager", "Move files to the sourceimages folder", None, gui.QApplication.UnicodeUTF8))
        self.moveToSrcImgs.setText(gui.QApplication.translate("atomicTextureFileManager", "Move to sourceimages", None, gui.QApplication.UnicodeUTF8))
        self.missingFileSearch.setToolTip(gui.QApplication.translate("atomicTextureFileManager", "This feature will search the computer for the filename of the missing files.  If found, the paths will be updated.", None, gui.QApplication.UnicodeUTF8))
        self.missingFileSearch.setStatusTip(gui.QApplication.translate("atomicTextureFileManager", "Attempt to find missing files on the computer", None, gui.QApplication.UnicodeUTF8))
        self.missingFileSearch.setText(gui.QApplication.translate("atomicTextureFileManager", "Attempt Missing File Search", None, gui.QApplication.UnicodeUTF8))
        self.updatePath.setToolTip(gui.QApplication.translate("atomicTextureFileManager", "When this is checked, the nodes in the scene will be updated to the copied/moved path", None, gui.QApplication.UnicodeUTF8))
        self.updatePath.setStatusTip(gui.QApplication.translate("atomicTextureFileManager", "Uncheck if you want to copy the file to source images, but want to keep the original file location on the node.", None, gui.QApplication.UnicodeUTF8))
        self.updatePath.setText(gui.QApplication.translate("atomicTextureFileManager", "Update Path on Run", None, gui.QApplication.UnicodeUTF8))
        self.keepOriginalSubfolders.setToolTip(gui.QApplication.translate("atomicTextureFileManager", "If the original file location is in a subfolder of a different sourceimages folder, and you want to keep that folder structure, make sure this is checked.", None, gui.QApplication.UnicodeUTF8))
        self.keepOriginalSubfolders.setStatusTip(gui.QApplication.translate("atomicTextureFileManager", "Check to keep original sub-folder structure", None, gui.QApplication.UnicodeUTF8))
        self.keepOriginalSubfolders.setText(gui.QApplication.translate("atomicTextureFileManager", "Keep Original Subfolders", None, gui.QApplication.UnicodeUTF8))
        self.TextureSettings.setItemText(self.TextureSettings.indexOf(self.operations), gui.QApplication.translate("atomicTextureFileManager", "Operations", None, gui.QApplication.UnicodeUTF8))
        self.defaultFolderTypes.setSortingEnabled(True)
        self.checkBox.setText(gui.QApplication.translate("atomicTextureFileManager", "Select All Node Types", None, gui.QApplication.UnicodeUTF8))
        self.checkBox_2.setText(gui.QApplication.translate("atomicTextureFileManager", "Texture Files Only", None, gui.QApplication.UnicodeUTF8))
        self.label_9.setText(gui.QApplication.translate("atomicTextureFileManager", "File Types by Default Project Folder Settings", None, gui.QApplication.UnicodeUTF8))
        self.TextureSettings.setItemText(self.TextureSettings.indexOf(self.options), gui.QApplication.translate("atomicTextureFileManager", "Options", None, gui.QApplication.UnicodeUTF8))
        self.refresh.setText(gui.QApplication.translate("atomicTextureFileManager", "Refresh", None, gui.QApplication.UnicodeUTF8))
        self.cancel.setText(gui.QApplication.translate("atomicTextureFileManager", "Close", None, gui.QApplication.UnicodeUTF8))
        self.run.setText(gui.QApplication.translate("atomicTextureFileManager", "Run Operation", None, gui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.filesTab), gui.QApplication.translate("atomicTextureFileManager", "Files", None, gui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.imageResizeReformat), gui.QApplication.translate("atomicTextureFileManager", "Image Resize/Reformat", None, gui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.uvTilingSetup), gui.QApplication.translate("atomicTextureFileManager", "UV Tiling Setup", None, gui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.makePathsRelative), gui.QApplication.translate("atomicTextureFileManager", "Make All Paths Relative", None, gui.QApplication.UnicodeUTF8))
        self.toolBox.setItemToolTip(self.toolBox.indexOf(self.makePathsRelative), gui.QApplication.translate("atomicTextureFileManager", "Convert absolute paths to relative paths", None, gui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.toolsTab), gui.QApplication.translate("atomicTextureFileManager", "Tools", None, gui.QApplication.UnicodeUTF8))
        self.label_4.setText(gui.QApplication.translate("atomicTextureFileManager", "USE WITH CAUTION!!\n"
"\n"
"These settings will affect the way this tool runs!  It was designed to be expandable, and uses an xml document to keep a list of acceptable image types.  Some are inserted by default, but the list can be expanded upon by you.\n"
"It is important to understand that changing this list will directly affect this tool\'s ability to preform.  Make sure you understand what you are doing before you hit save!", None, gui.QApplication.UnicodeUTF8))
        self.xmlLabel.setText(gui.QApplication.translate("atomicTextureFileManager", "XML File Location", None, gui.QApplication.UnicodeUTF8))
        self.xmlLocation.setToolTip(gui.QApplication.translate("atomicTextureFileManager", "The XML file that maintains the list of texture file node types", None, gui.QApplication.UnicodeUTF8))
        self.nodeTypesList.setToolTip(gui.QApplication.translate("atomicTextureFileManager", "List of excepted file nodes", None, gui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(0).setText(gui.QApplication.translate("atomicTextureFileManager", "-", None, gui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(1).setText(gui.QApplication.translate("atomicTextureFileManager", "nodeType", None, gui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(2).setText(gui.QApplication.translate("atomicTextureFileManager", "defaultFolder", None, gui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(3).setText(gui.QApplication.translate("atomicTextureFileManager", "parameterName", None, gui.QApplication.UnicodeUTF8))
        self.label_3.setText(gui.QApplication.translate("atomicTextureFileManager", "Accepted Nodes", None, gui.QApplication.UnicodeUTF8))
        self.label_7.setText(gui.QApplication.translate("atomicTextureFileManager", "Manually add new node", None, gui.QApplication.UnicodeUTF8))
        self.addNodeType.setText(gui.QApplication.translate("atomicTextureFileManager", "Add", None, gui.QApplication.UnicodeUTF8))
        self.pushButton.setToolTip(gui.QApplication.translate("atomicTextureFileManager", "This will bring up a list of attribues from the existing node.  Pick the correct parameter from there", None, gui.QApplication.UnicodeUTF8))
        self.pushButton.setText(gui.QApplication.translate("atomicTextureFileManager", "   Auto Add From Selection   ", None, gui.QApplication.UnicodeUTF8))
        self.label_5.setText(gui.QApplication.translate("atomicTextureFileManager", "nodeType", None, gui.QApplication.UnicodeUTF8))
        self.label_6.setText(gui.QApplication.translate("atomicTextureFileManager", "parameterName", None, gui.QApplication.UnicodeUTF8))
        self.label_8.setText(gui.QApplication.translate("atomicTextureFileManager", "Get the node type and attribute from the currently selected node", None, gui.QApplication.UnicodeUTF8))
        self.defaultFolderLabel.setText(gui.QApplication.translate("atomicTextureFileManager", "defaultFolder", None, gui.QApplication.UnicodeUTF8))
        self.defaultFolder.setToolTip(gui.QApplication.translate("atomicTextureFileManager", "Based on Project Settings", None, gui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingsTab), gui.QApplication.translate("atomicTextureFileManager", "Settings", None, gui.QApplication.UnicodeUTF8))
        self.actionCopy_Selected_To_Source.setText(gui.QApplication.translate("atomicTextureFileManager", "Copy Selected To Source", None, gui.QApplication.UnicodeUTF8))
        self.actionReset.setText(gui.QApplication.translate("atomicTextureFileManager", "Reset", None, gui.QApplication.UnicodeUTF8))
        self.actionMove_Selected_To_Source.setText(gui.QApplication.translate("atomicTextureFileManager", "Move Selected To Source", None, gui.QApplication.UnicodeUTF8))
        self.actionDocumentation.setText(gui.QApplication.translate("atomicTextureFileManager", "Documentation", None, gui.QApplication.UnicodeUTF8))



if __name__ == '__main__':
    run = atomicTextureFileManager(parent=atomicInterface())
    run.show()
