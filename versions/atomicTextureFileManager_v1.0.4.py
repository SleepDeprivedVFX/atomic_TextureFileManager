from maya import cmds
import os, platform, shutil
from PySide import QtCore, QtGui
#import atomic_TFM_UI as atomicUI
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from xml.etree import ElementTree as ET
from functools import partial
import subprocess, glob, re

#reload(atomicUI)

__author__ = 'Adam Benson'
__version__ = '1.0.4'

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
    2. Autodesk has decided to upgrade from PyQt4 to PyQt5.  It is not backward compatible, so I was originally attempting
        to make a cross compatible version of my code, and I may still be able to achieve it... However, there do seem to be
        some complex differences, and for the moment I'm going to make two versions.  One for 2016 prior, and another for 2017
        forward.
    3. In these versions I am going to be integrating the UI into the main file.  This will make distribution easier.
'''


def atomicInterface():
    mainWin = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWin), QtGui.QWidget)


class atomicTextureFileManager(QtGui.QDialog):
    updateProgress = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(atomicTextureFileManager, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = atomicUI()
        self.ui.setupUi(self)
        self.fileTypes = {}
        self.typeListFile = ''
        self.tagTypes = re.compile(r'((_u|_U)\d*(_v|_V)\d*)|(<UDIM>)|(<UVTILE>)|(_(u|U)<U>_(v|V)<V>)')
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
        sceneInfo['sourceImages'] = cmds.workspace(fre='sourceImages')
        sceneInfo['scripts'] = cmds.workspace(fre='scripts')
        sceneInfo['templates'] = cmds.workspace(fre='templates')
        sceneInfo['images'] = cmds.workspace(fre='images')
        sceneInfo['renderData'] = cmds.workspace(fre='renderData')
        sceneInfo['clips'] = cmds.workspace(fre='clips')
        sceneInfo['sound'] = cmds.workspace(fre='sound')
        sceneInfo['diskCache'] = cmds.workspace(fre='diskCache')
        sceneInfo['movies'] = cmds.workspace(fre='movies')
        sceneInfo['translatorData'] = cmds.workspace(fre='translatorData')
        sceneInfo['autoSave'] = cmds.workspace(fre='autoSave')
        # Add subcategories later
        sceneInfo['OS-System'] = platform.system()
        sceneInfo['OS-Release'] = platform.release()
        sceneInfo['OS-User'] = os.getenv('USER')
        sceneInfo['OS-Version'] = platform.version()
        return sceneInfo

    def checkFileExistence(self, filePaths):
        existingFiles = {}
        missingFiles = {}
        for thisFile, path in filePaths.items():
            if path:
                tagFound = self.lookForTags(path)
                if tagFound:
                    pathList = self.getImageCollection(path, tagFound)
                    if not pathList:
                        pathList = [path]
                else:
                    pathList = [path]

                try:
                    for thisPath in pathList:
                        if os.path.exists(thisPath):
                            existingFiles[thisFile] = thisPath
                        else:
                            missingFiles[thisFile] = thisPath
                except:
                    pass
        return existingFiles, missingFiles

    def getSourceImagesFiles(self, files):
        sceneInfo = self.getSceneInfo()
        root = sceneInfo['project']
        # Here is where I most likely need to add an iteration through the options panel, and the selected nodes there.
        # Which is going to complicate how this thing goes through images.  The sourceFolder below might be replaced
        # with a "For each category:" loop.
        getCategories = self.ui.defaultFolderTypes.selectedItems()
        print getCategories
        sourcefolder = sceneInfo['sourceImages']
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
            # This is a patch for what was in the if statement: if '/sourceimages' in subFolder:
            # That won't work in the future, so I'm starting to patch it in now. The dynamic call to getSceneInfo is
            # the patch.
            sourceImages = self.getSceneInfo()['sourceImages']
            if sourceImages in subFolder:
                self.ui.defaultFolder.setCurrentIndex(selectIndex)
                self.ui.defaultFolderTypes.setCurrentRow(selectIndex)

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
                self.findFilesOnComputer(missingFiles, inSourceImages, sourceFolder, keepOriginalSubfolders, updatePath, mode)
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

    def findFilesOnComputer(self, fileList, inSourceImages, sourceFolder, keepOriginalSubfolders, updatePath, mode, *args):
        really = cmds.confirmDialog(m='A File search can take a very long time!  Are you sure you want to do this?', b=['Yes!', 'Nevermind'], db='Nevermind', cb='Nevermind')
        if really == 'Yes!':
            foundFiles = {}
            driveStr = subprocess.check_output("fsutil fsinfo drives")
            driveStr = driveStr.strip().lstrip('Drives: ')
            drives = driveStr.split()
            selectedFiles = self.getSelectedItems(fileList)
            for nodeType, path in selectedFiles.items():
                thisNodeType = cmds.nodeType(nodeType)
                fileParam = self.fileTypes[thisNodeType]['fileNameParam']
                fileFound = False
                try:
                    slashPath = path.replace('\\', '/')  # ['fileNameParam'] This "fileNameParam" and "Default Path" could be stuff that I threw in to tag the new all files system
                except:
                    slashPath = path
                fileName = slashPath.rsplit('/', 1)[1]

                tagFound = self.lookForTags(fileName)

                print 'Searching for %s..............................' % fileName
                for drive in drives:
                    print 'searching on drive', drive
                    for root, dirs, files in os.walk(drive):
                        if tagFound:
                            for thisFile in files:
                                compoundFileName = self.tagTypes.search(thisFile)
                                if compoundFileName:
                                    compoundTag = compoundFileName.group()
                                    splitCompound = thisFile.split(compoundTag)
                                    compoundBaseName = splitCompound[0]
                                    compoundExt = splitCompound[1]
                                    splitFileName = fileName.split(tagFound)
                                    fileNameBase = splitFileName[0]
                                    fileNameExt = splitFileName[1]
                                    if compoundBaseName == fileNameBase and compoundExt == fileNameExt:
                                        newPath = os.path.join(root, fileName)
                                        path = newPath.replace('\\', '/')
                                        cmds.setAttr('%s.%s' % (nodeType, fileParam), path, type='string')
                                        fileFound = True
                                        foundFiles[nodeType] = path
                                        break
                        else:
                            if fileName in files:
                                newPath = os.path.join(root, fileName)
                                path = newPath.replace('\\', '/')
                                cmds.setAttr('%s.%s' % (nodeType, fileParam), path, type='string')
                                fileFound = True
                                break
                    if fileFound:
                        print '%s Found!!' % path
                        print '%s file path updated!' % nodeType
                        break
            print 'Search finished ------------------------------------------------------------------------------------'
        self.resetFileTrees()
        print 'File Tree Reset'
        print 'Found Files pre-test:', foundFiles
        if foundFiles:
            print 'Found Files post-test:', foundFiles
            continueToCopy = cmds.confirmDialog(m='All found files have been updated in the scene.  Would you like to copy or move the files to the correct folder?', b=['Copy', 'Move', 'No Thanks'], cb='No Thanks', db='Copy')
            if continueToCopy == 'Copy' or continueToCopy == 'Move':
                # the foundFIles variable probably needs to be crammed into a dictionary that matches the original call
                if continueToCopy == 'Copy':
                    mode = 'copy'
                else:
                    mode = 'move'
                self.copyFiles(foundFiles, inSourceImages, sourceFolder, keepOriginalSubfolders, updatePath, mode, *args)

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
        fileCollection = []
        splitPath = path.rsplit('/', 1)
        basePath = splitPath[0]
        fileName = splitPath[1]
        splitFile = path.split(tag)
        pre = splitFile[0]
        post = splitFile[1]
        checkDirectory = os.path.isdir(basePath)
        if checkDirectory:
            dirList = os.listdir(basePath)
            for dirObj in dirList:
                checkPath = basePath + '/' + dirObj
                if os.path.isfile(checkPath):
                    if self.tagTypes.search(checkPath):
                        foundFileTag = self.tagTypes.search(checkPath).group()
                        matchBase = checkPath.split(foundFileTag)[0]
                        matchExt = checkPath.split(foundFileTag)[1]
                        if matchBase == pre and matchExt == post:
                            fileCollection.append(checkPath)
        return fileCollection

    def copyFiles(self, fileList, inSourceImages, sourceFolder, keepOriginalSubfolders, updatePath, mode, *args):
        # I think I need to change the parameters above to the **kwargs in order to take more limited suggestions
        # Although, I know I'm still going to need some of this info, so it might be better to pass it to the
        # findFilesOnComputer.
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
                # It needs to reflect both the getSceneInfo list, but also the catagories list
                sourceImages = self.getSceneInfo()['sourceimages']
                if keepOriginalSubfolders:
                    # the 'sourceImages' string needs to be replaced with a loop that searches through the fileTpes
                    if sourceImages in splitPath:
                        pathFrom = splitPath.index(sourceImages)
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

                tagFound = self.lookForTags()

                if tagFound:
                    pathList = self.getImageCollection(path, tagFound)
                else:
                    pathList = [path]

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

    def lookForTags(self, path):
        tagFound = ''
        tag = self.tagTypes.search(path)
        if tag:
            tagFound = tag.group()
        else:
            tagFound = ''
        return tagFound

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
        atomicTextureFileManager.resize(1241, 986)
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
        self.operations.setGeometry(QtCore.QRect(0, 0, 1155, 333))
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
        self.options.setGeometry(QtCore.QRect(0, 0, 98, 28))
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
        self.imageResizeReformat.setGeometry(QtCore.QRect(0, 0, 98, 28))
        self.imageResizeReformat.setObjectName("imageResizeReformat")
        self.toolBox.addItem(self.imageResizeReformat, "")
        self.uvTilingSetup = QtGui.QWidget()
        self.uvTilingSetup.setGeometry(QtCore.QRect(0, 0, 98, 28))
        self.uvTilingSetup.setObjectName("uvTilingSetup")
        self.toolBox.addItem(self.uvTilingSetup, "")
        self.makePathsRelative = QtGui.QWidget()
        self.makePathsRelative.setGeometry(QtCore.QRect(0, 0, 98, 28))
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


if __name__ == '__main__':
    run = atomicTextureFileManager(parent=atomicInterface())
    run.show()
