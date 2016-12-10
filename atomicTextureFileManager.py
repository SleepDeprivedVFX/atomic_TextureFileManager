from maya import cmds
import os, platform, shutil
from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from xml.etree import ElementTree as ET
from functools import partial
import subprocess, glob, re

__author__ = 'Adam Benson'
__version__ = '1.0.6'

'''
    This is the new and improved Texture File Manager!  Here are a list of features coming up in version 1.1.0
    1. File type selection settings
    2. Add tools for changing the image type, resizing and other useful operations.
    3. Fix Progress Bars
    4. Need to add "TexturesOnly" function, but still have the ability to include system files as well; Alembic files, PTEX, and probably even xGen files.  Might actually want to include any project base settings.
    5. Also need to add columns to the XML sheet.  I might like to use the scene project structure to create a drop-down list of folder options for individual entries.  i.e. sourceimages/ or cache/alembic/.  Anything that the project settings might default to.
    6. Ask before overwrite file
    7. Copy across network/permission issues.

    KNOWN ISSUES:
    1. An empty render layer, selected in the list, will throw an error  -  I feel like this note is accidentally in here from another tool.
    4. Image Planes have caused failures on the preload
    5. The file types system is currently not selecting file types automatically, and the system currently does not work.
    6. Selection mode fails copy/move if a missing file is selected.  vice verse.
    7. Currently blindly overwrites existing files.
    8. <UDIM> files and/or files with relative vs. absolute paths are showing up as missing.

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
    4. This version is getting a new UI.  I'm streamlining the user interface, swapping radio buttons for action
        buttons.  I'm also getting rid of the options roll down, and replacing it with

    This has now been added to the GitHub repository
'''


def atomicInterface():
    mainWin = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWin), QtGui.QMainWindow)


class atomicTextureFileManager(QtGui.QMainWindow):
    updateProgress = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(atomicTextureFileManager, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = atomicUI()
        self.ui.setupUi(self)
        self.fileTypes = {}
        self.typeListFile = ''
        self.checkBoxList = []
        self.tagTypes = re.compile(r'((_u|_U)\d*(_v|_V)\d*)|(<UDIM>)|(<UVTILE>)|(_(u|U)<U>_(v|V)<V>)')
        self.modes = {0: 'copy', 1: 'move', 2: 'missing'}
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
            try:
                for child in root_element:
                    self.fileTypes[child.attrib['name']] = {'fileNameParam': child[0].text, 'defaultPath': child[1].text}
                self.preloadSystem()
            except (RuntimeError, TypeError, NameError, ValueError):
                print 'This system is unable to run due to a problem configuring the "atfm_TypeList.xml" file.'
        else:
            print 'No File Types XML file can be found or created!'

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
            xmlString += '<nodeType name="file"><fileNameParam>fileTextureName</fileNameParam><defaultPath>/publish/textures</defaultPath></nodeType>'
            xmlString += '<nodeType name="mentalrayTexture"><fileNameParam>fileTextureName</fileNameParam><defaultPath>/publish/textures</defaultPath></nodeType>'
            xmlString += '<nodeType name="mentalrayIblShape"> <fileNameParam>texture</fileNameParam>	<defaultPath>/publish/textures</defaultPath></nodeType>'
            xmlString += '<nodeType name="aiImage">	<fileNameParam>filename</fileNameParam>	<defaultPath>/publish/textures</defaultPath></nodeType>'
            xmlString += '<nodeType name="rmanImageFile">	<fileNameParam>File</fileNameParam>	<defaultPath>/publish/textures</defaultPath></nodeType>'
            xmlString += '<nodeType name="imagePlane"><fileNameParam>imagePlane</fileNameParam><defaultPath>/publish/textures</defaultPath></nodeType>'
            xmlString += '<nodeType name="AlembicNode"><fileNameParam>abc_File</fileNameParam><defaultPath>/publish/caches/alembic</defaultPath></nodeType>'
            xmlString += '</atfm_TypeList>'

            newFile = (getFolder + '/atfm_TypeList.xml')
            newXML = open(newFile, 'w')
            newXML.write(xmlString)
            newXML.close()
        else:
            # Setup an alert with instructions and options to proceed without a working XML file.
            # Perhaps, have a "Find file manually" feature, and if that fails, then the tool just doesn't run.
            print 'Wah wah!'
        return newFile

    def cancel(self):
        # Close the window
        self.close()

    def getAllFiles(self):
        # This method searches through all the nodes in the Maya scenes, looking for node types listed in the XML file.
        # If nodes are found, then node type and the name of each node or nodes is saved into a dictionary and returned.
        allFileTypes = {}
        for thisType in self.fileTypes:
            try:
                selectedType = cmds.ls(type=thisType)
                if len(selectedType) != 0:
                    allFileTypes[thisType] = selectedType
            except (RuntimeError, TypeError, NameError, ValueError):
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
        sceneInfo['alembicCache'] = cmds.workspace(fre='alembicCache')
        # subcatagories
        sceneInfo['offlineEdits'] = cmds.workspace(fre='offlineEdits')
        sceneInfo['3dPaintTextures'] = cmds.workspace(fre='3dPaintTextures')
        sceneInfo['depth'] = cmds.workspace(fre='depth')
        sceneInfo['iprImages'] = cmds.workspace(fre='iprImages')
        sceneInfo['shaders'] = cmds.workspace(fre='shaders')
        sceneInfo['furFiles'] = cmds.workspace(fre='furFiles')
        sceneInfo['furImages'] = cmds.workspace(fre='furImages')
        sceneInfo['furEqualMap'] = cmds.workspace(fre='furEqualMap')
        sceneInfo['furAttrMap'] = cmds.workspace(fre='furAttrMap')
        sceneInfo['furShadowMap'] = cmds.workspace(fre='furShadowMap')
        sceneInfo['particleCache'] = cmds.workspace(fre='particleCache')
        sceneInfo['fileCache'] = cmds.workspace(fre='fileCache')
        sceneInfo['bifrostCache'] = cmds.workspace(fre='bifrostCache')
        sceneInfo['mayaAscii'] = cmds.workspace(fre='mayaAscii')
        sceneInfo['mayaBinary'] = cmds.workspace(fre='mayaBinary')
        sceneInfo['mel'] = cmds.workspace(fre='mel')
        sceneInfo['OBJ'] = cmds.workspace(fre='OBJ')
        sceneInfo['audio'] = cmds.workspace(fre='audio')
        sceneInfo['move'] = cmds.workspace(fre='move')
        sceneInfo['EPS'] = cmds.workspace(fre='EPS')
        sceneInfo['adobeIllustrator'] = cmds.workspace(fre='adobeIllustrator')
        sceneInfo['FBX'] = cmds.workspace(fre='FBX')
        return sceneInfo

    def getSystemInfo(self):
        systemInfo = {}
        systemInfo['OS-System'] = platform.system()
        systemInfo['OS-Release'] = platform.release()
        systemInfo['OS-User'] = os.getenv('USER')
        systemInfo['OS-Version'] = platform.version()

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
                except (RuntimeError, TypeError, NameError, ValueError):
                    pass
        return existingFiles, missingFiles

    def getSourceImagesFiles(self, files):
        sceneInfo = self.getSceneInfo()
        root = sceneInfo['project']
        # Here is where I most likely need to add an iteration through the options panel, and the selected nodes there.
        # Which is going to complicate how this thing goes through images.  The sourceFolder below might be replaced
        # with a "For each category:" loop.
        getCategories = []
        optionNames = self.optionsList()
        for thisOption in optionNames:
            getCategories.append(self.fileTypes[thisOption]['defaultPath'])
        # Need to convert getCategories from the nodeName to the DefaultPath
        inSourceImages = {}
        inSourceSubs = []
        for category in getCategories:
            sourcefolder = category.strip('/')
            sourceImages = os.path.join(root, sourcefolder)
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
                except (RuntimeError, TypeError, NameError, ValueError):
                    pass
        return inSourceImages, sourceImages

    def sourceFoldersList(self):
        # This method is used to get the folders of the acceptable nodeTypes and save them into a minimal path list.
        # Several nodeTypes share the same default folder path, so to keep duplicates from showing up in places like
        # the defaultFolderTypes list, this reduces the complete list, down the basic list of actual paths.
        defaultParams = []
        acceptedTypes = self.fileTypes
        for name, params in acceptedTypes.items():
            path = params['defaultPath']
            # path = path.strip('/')
            if path not in defaultParams:
                defaultParams.append(path)
        return defaultParams

    def getParamNameFromParam(self, param):
        acceptedTypes = self.fileTypes
        paramName = ''
        for name, params in acceptedTypes.items():
            if params['defaultPath'] == param:
                paramName = name
                break
        return paramName

    def populateDefaultFolderTypes(self):
        table = self.ui.defaultFolderTypes
        # Get list of actual folders from the XML file.  No duplicate entries.
        defaultParams = self.sourceFoldersList()
        # Get options check list
        texturesOnly = self.ui.selectTextureNodesOnly.isChecked()
        sourceImages = self.getSceneInfo()['sourceImages']
        # Iterate through default folder paths, and add them to the defaultFolderTypes list
        for param in defaultParams:
            rowCount = table.rowCount()
            table.insertRow(rowCount)
            col = 0
            # checkName = param
            # checkName should probably work like this:
            checkName = self.getParamNameFromParam(param)
            # where the parameter name, like "file" or "AlembicNode" is returned as the checkBox Name
            # HOWEVER... This means that the Options DEF will return the wrong information, and thus break everything
            # Create a checkBox
            newCheck = QtGui.QCheckBox(checkName)
            if newCheck not in self.checkBoxList:
                self.checkBoxList.append(newCheck)
            header = table.horizontalHeader()
            header.setResizeMode(QtGui.QHeaderView.ResizeToContents)
            header.setStretchLastSection(True)
            table.setCellWidget(rowCount, col, newCheck)
            newCheck.stateChanged.connect(partial(self.checkBoxSettings, checkName))
            if texturesOnly:
                if sourceImages in param:
                    newCheck.setChecked(True)
            # If sourceImages default Folder IN defaultParams:
            #   Check the sourceImages checkbox

            # I need to figure out what data goes here.
            # Also, this will need to check if the "Textures Only" check, or all file types, is checked
            # first one should be a check box
            table.setItem(rowCount, (col + 1), QtGui.QTableWidgetItem(param))

    def getDefaultPath(self, nodeType):
        thisNode = cmds.nodeType(nodeType)
        for key, value in self.fileTypes.items():
                if thisNode == key:
                    defaultPath = value['defaultPath']
                    break
        return defaultPath

    def populateTable(self, table, existingFiles, inSourceFiles, missingFiles, *args):
        allFiles = existingFiles.copy()
        allFiles.update(missingFiles)
        options = []
        optionNames = self.optionsList()
        for thisOption in optionNames:
            options.append(self.fileTypes[thisOption]['defaultPath'])
        for nodeType, path in allFiles.items():
            checkNode = self.getDefaultPath(nodeType)
            if checkNode in options:
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
                defaultType = self.getDefaultPath(nodeType)
                header = table.horizontalHeader()
                header.setResizeMode(QtGui.QHeaderView.ResizeToContents)
                header.setStretchLastSection(True)
                table.setCellWidget(rowCount, col, imageLabel)
                table.setItem(rowCount, (col + 1), QtGui.QTableWidgetItem(nodeType))
                table.setItem(rowCount, (col + 2), QtGui.QTableWidgetItem(defaultType))
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
                    thisList = table.item(rowCount, col + 2)
                    thisList.setBackground(thisColor)
                    thisList = table.item(rowCount, (col + 3))
                    thisList.setBackground(thisColor)

    def preloadSystem(self):
        # get scene data
        self.flushTables()
        self.populateDefaultFolderTypes()
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
            # self.ui.defaultFolderTypes.addItem(subFolder)  # This isn't working because the list changed to table

            # This is a patch for what was in the if statement: if '/sourceimages' in subFolder:
            # That won't work in the future, so I'm starting to patch it in now. The dynamic call to getSceneInfo is
            # the patch.
            sourceImages = self.getSceneInfo()['sourceImages']
            if sourceImages in subFolder:
                self.ui.defaultFolder.setCurrentIndex(selectIndex)
                # self.ui.defaultFolderTypes.setCurrentRow(selectIndex)

        # Setup button actions and connections
        self.setActionButtons(existingFiles, inSourceImagesFiles, missingFiles)
        self.ui.cancel.clicked.connect(self.cancel)
        # self.ui.sourceText.setText(sourceImagesFolder)
        self.ui.refresh.clicked.connect(self.resetFileTrees)
        # self.ui.browseSourceBtn.clicked.connect(self.setSourceImagesFolder)
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
                allSubFolders.append(shortPath)
                # This needs to be replaced with a dynamic link to sourceImages
                if 'sourceimages' in shortPath:
                    selectIndex = allSubFolders.index(shortPath)
        return allSubFolders, selectIndex

    def runMain(self, fileList, inSourceImages, missingFiles, mode):
        # actionType = self.ui.actionTypeSelectionLayout
        keepOriginalSubfolders = self.ui.keepOriginalSubfolders.isChecked()
        updatePath = self.ui.updatePath.isChecked()
        # count = actionType.count()
        '''for i in range(0, count):
            if actionType.itemAt(i).widget().isChecked():
                mode = self.modes[i]
                break'''
        sourceFolder = self.sourceFoldersList()
        if mode == 'copy' or mode == 'move':
            try:
                self.copyFiles(fileList, inSourceImages, sourceFolder, keepOriginalSubfolders, updatePath, mode)
            except (RuntimeError):
                print 'RuntimeError occurred.  Cannot copy this specific file or folder.'
            except (TypeError):
                print 'TypeError occurred.  Cannot copy this specific file or folder.'
            except (NameError):
                print 'NameError occurred.  Cannot copy this specific file or folder.'
            except (ValueError):
                print 'ValueError occurred. Cannot copy this specific file or folder.'
        elif mode == 'search':
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
            fileFound = False
            selectedFiles = self.getSelectedItems(fileList)
            for nodeType, path in selectedFiles.items():
                thisNodeType = cmds.nodeType(nodeType)
                fileParam = self.fileTypes[thisNodeType]['fileNameParam']
                fileFound = False
                try:
                    slashPath = path.replace('\\', '/')
                except (RuntimeError, TypeError, NameError, ValueError):
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
                                foundFiles[nodeType] = path
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
        print 'FileList:', fileList
        getSelection = self.ui.existingTextureList.selectedItems()
        print 'getSelection:', getSelection[0]
        selectedFileList = {}
        if getSelection:
            total = len(getSelection)
            for selected in range(0, total, 3):
                selectedNode = getSelection[selected].text()
                print 'selectedNode:', selectedNode
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

    def optionsList(self):
        options = []
        for check in self.checkBoxList:
            if check.isChecked():
                options.append(check.text())
        return options

    def copyFiles(self, fileList, inSourceImages, sourceFolder, keepOriginalSubfolders, updatePath, mode, *args):
        # I think I need to change the parameters above to the **kwargs in order to take more limited suggestions
        # Although, I know I'm still going to need some of this info, so it might be better to pass it to the
        # findFilesOnComputer.
        update = 0
        selectedFileList = self.getSelectedItems(fileList)
        # I am temporarily disabling the Progress Bar until I get it working.  For version 1, I will use a print out of
        # each file successfully copied.
        for nodeType, path in selectedFileList.items():
            update += 1
            # Update progress bar here.
            # print update
            for folder in sourceFolder:
                print 'for folder in sourceFolder:', folder
                # If I'm not mistaken, then folder in sourceFolders should loop AND compare with the options list of
                # selected folder types.  BUT where does that hook in below?
                optionsList = []
                optionNames = self.optionsList()
                for thisOption in optionNames:
                    optionsList.append(self.fileTypes[thisOption]['defaultPath'])
                print optionsList
                print folder
                # This breaks BECAUSE we need to see if the object's default folder is in the options list,
                # Currently, it's looking to see if the list of folder types available are in the checked options list
                # Duh, of course they are.  So, I need to get the object default folder.
                if folder in optionsList:
                    if '/' in path:
                        splitPath = path.split('/')
                        print 'forward slash split path found'
                    elif '\\' in path:
                        splitPath = path.split('\\')
                        print 'back slash split path found'
                    if path not in inSourceImages.values():
                        print 'Path not in InSourceImages.values()', path
                        print 'This is important, because if it\'s already in sourceImages, then there\'s no need to copy'
                        # Need to add some other conditions and actions here.
                        # ALERT!! This method will most likely fail alembic copies, or any other non-sourceimages files.
                        # This is just for the subfolder search. I think I just need to replace 'sourceimages' with a
                        # bona-fide variable from one of the folder type lists.
                        # It needs to reflect both the getSceneInfo list, but also the catagories list
                        sourceImages = self.getSceneInfo()['sourceImages']
                        root = self.getSceneInfo()['project']
                        print root
                        sourceImagesPath = root + '/' + sourceImages
                        print 'sourceImages folder:', sourceImagesPath
                        if keepOriginalSubfolders:
                            print 'Keep Original Folders is Checked'
                            # the 'sourceImages' string needs to be replaced with a loop that searches through the fileTypes
                            print 'SourceImages = %s | splitPath = %s' % (sourceImages, splitPath)
                            if sourceImages in splitPath:
                                print 'sourceImages in splitPath =', sourceImages, splitPath
                                # I think source images needs to be the full path
                                pathFrom = splitPath.index(sourceImages)
                                print 'pathFrom', pathFrom
                                pathLength = len(splitPath)
                                print 'pathLength', pathLength
                                newPath = sourceImagesPath
                                for x in range((pathFrom + 1), (pathLength - 1)):
                                    print 'pathFrom to pathLength x =', x
                                    newPath = newPath + '/' + splitPath[x]
                                    if not os.path.isdir(newPath):
                                        print 'newPath not found, making directory', newPath
                                        os.mkdir(newPath)
                            else:
                                newPath = sourceImagesPath
                                print 'newPath is the same as sourceFolder', newPath
                        else:
                            newPath = sourceImagesPath
                            print 'Keep Original Folders is NOT Checked and newPath =', newPath
                        print 'Begin Tag Check'

                        tagFound = self.lookForTags(newPath)
                        print 'Tag check successful'

                        if tagFound:
                            print 'tag was found'
                            pathList = self.getImageCollection(path, tagFound)
                            print 'Copy path list =', pathList
                        else:
                            print 'No Tag found'
                            pathList = [path]
                            print 'Copy path list =', pathList

                        for thisPath in pathList:
                            fileName = thisPath.rsplit('/', 1)[1]
                            checkPath = os.path.join(newPath, fileName)
                            if os.path.isfile(checkPath):
                                originalSize = os.path.getsize(thisPath)
                                newSize = os.path.getsize(checkPath)
                                originalDate = os.path.getmtime(thisPath)
                                newDate = os.path.getmtime(checkPath)
                                if newSize == originalSize and newDate == originalDate:
                                    print 'The files are the same'
                                    conflictResolution = cmds.confirmDialog(m='The file %s already exists and appears '
                                                                              'to be the same in both locations.  How '
                                                                              'would you like to proceed?' % fileName,
                                                                            button=['Overwrite', 'Skip'],
                                                                            db='Overwrite', cb='Skip')
                                    if conflictResolution == 'Overwrite':
                                        self.copyAction(mode, thisPath, os.path.join(newPath, fileName), path)
                                    else:
                                        pass
                                elif newSize != originalSize or newDate != originalDate:
                                    print 'The files are different'
                                    conflictResolution = cmds.confirmDialog(m='There is already a file with the name %s'
                                                                              ' in the source images folder. How would'
                                                                              ' you like to proceed?' % fileName,
                                                                            button=['Overwrite', 'Use Latest',
                                                                                    'Use Largest', 'Skip'],
                                                                            db='Overwrite', cb='Skip')
                                    if conflictResolution == 'Overwrite':
                                       self.copyAction(mode, thisPath, os.path.join(newPath, fileName), path)
                                    elif conflictResolution == 'Use Latest':
                                        if originalDate > newDate:
                                            print 'Copy the Original File'
                                            self.copyAction(mode, thisPath, os.path.join(newPath, fileName), path)
                                        else:
                                            print 'Use New Path instead'
                                    elif conflictResolution == 'Use Largest':
                                        if originalSize > newSize:
                                            print 'Copy the Original File'
                                            self.copyAction(mode, thisPath, os.path.join(newPath, fileName), path)
                                        else:
                                            print 'Use the New File'
                                    else:
                                        pass
                            else:
                                self.copyAction(mode, thisPath, os.path.join(newPath, fileName), path)

                    # Progress Bar Call ---- SEE INITIAL CALL
                    '''self.updateProgress.emit(update)
                    time.sleep(0.1)'''

                    updatedPath = newPath + '/' + splitPath[-1]
                    thisNode = cmds.nodeType(nodeType)
                    fileParam = self.fileTypes[thisNode]['fileNameParam']
                    defaultPath = self.fileTypes[thisNode]['defaultPath']
                    if updatePath:
                        cmds.setAttr('%s.%s' % (nodeType, fileParam), updatedPath, type='string')
                        print '%s Updated successfully!' % updatedPath
        # Dialog.close()
        self.resetFileTrees()

    def copyAction(self, mode, src, dest, path):
        if mode == 'copy':
            shutil.copy2(src, dest)
            print '%s copied successfully!' % path
        elif mode == 'move':
            shutil.move(src, dest)
            print '%s moved successfully!' % path

    def lookForTags(self, path):
        tagFound = ''
        tag = self.tagTypes.search(path)
        if tag:
            tagFound = tag.group()
        else:
            tagFound = ''
        return tagFound

    def setActionButtons(self, existingFiles, inSourceImagesFiles, missingFiles):
        # These actually needs to set multiple buttons
        self.ui.copy.clicked.connect(partial(self.runMain, fileList=existingFiles, inSourceImages=inSourceImagesFiles,
                                            missingFiles=missingFiles, mode='copy'))
        self.ui.move.clicked.connect(partial(self.runMain, fileList=existingFiles, inSourceImages=inSourceImagesFiles,
                                            missingFiles=missingFiles, mode='move'))
        self.ui.search.clicked.connect(partial(self.runMain, fileList=existingFiles, inSourceImages=inSourceImagesFiles,
                                            missingFiles=missingFiles, mode='search'))
        self.ui.selectAllNodeTypes.stateChanged.connect(partial(self.checkBoxSettings, 'selectAll'))
        self.ui.selectTextureNodesOnly.stateChanged.connect(partial(self.checkBoxSettings, 'texturesOnly'))

    def checkBoxSettings(self, *args):
        # This currently ain't working.  HOWEVER... This is a critical part of getting the options box to work.
        boxName = args[0]
        clickState = args[1]
        sourceImages = self.getSceneInfo()['sourceImages']
        if boxName == 'selectAll' and clickState > 1:
            self.ui.selectTextureNodesOnly.setChecked(False)
            for thisCheck in self.checkBoxList:
                thisCheck.setChecked(True)
                self.ui.selectAllNodeTypes.setChecked(True)
            self.resetFileTrees()
        elif boxName == 'texturesOnly' and clickState > 1:
            self.ui.selectAllNodeTypes.setChecked(False)
            for thisCheck in self.checkBoxList:
                thisCheck.setChecked(False)
                checkName = thisCheck.text()
                checkName = self.fileTypes[checkName]['defaultPath']
                if sourceImages in checkName:
                    thisCheck.setChecked(True)
                self.ui.selectTextureNodesOnly.setChecked(True)
            self.resetFileTrees()
        else:
            dynamicChecksCount = len(self.checkBoxList)
            counted = 0
            for check in self.checkBoxList:
                isChecked = check.isChecked()
                if isChecked:
                    counted += 1
            if counted < dynamicChecksCount:
                self.ui.selectAllNodeTypes.setChecked(False)
                self.ui.selectTextureNodesOnly.setChecked(False)


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
        self.setActionButtons(existingFiles, inSourceImagesFiles, missingFiles)
        self.populateTable(self.ui.existingTextureList, existingFiles, inSourceImagesFiles, missingFiles)


class atomicUI(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1293, 1012)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.filesTab = QtGui.QWidget()
        self.filesTab.setObjectName("filesTab")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.filesTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.existingTextureLabel = QtGui.QLabel(self.filesTab)
        self.existingTextureLabel.setObjectName("existingTextureLabel")
        self.verticalLayout.addWidget(self.existingTextureLabel)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.colorKeyCurrent = QtGui.QLabel(self.filesTab)
        self.colorKeyCurrent.setObjectName("colorKeyCurrent")
        self.horizontalLayout.addWidget(self.colorKeyCurrent)
        self.colorKeyMissing = QtGui.QLabel(self.filesTab)
        self.colorKeyMissing.setObjectName("colorKeyMissing")
        self.horizontalLayout.addWidget(self.colorKeyMissing)
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.existingTextureList = QtGui.QTableWidget(self.filesTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.existingTextureList.sizePolicy().hasHeightForWidth())
        self.existingTextureList.setSizePolicy(sizePolicy)
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
        self.verticalLayout.addWidget(self.existingTextureList)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.nodeTypesLabel = QtGui.QLabel(self.filesTab)
        self.nodeTypesLabel.setObjectName("nodeTypesLabel")
        self.horizontalLayout_4.addWidget(self.nodeTypesLabel)
        self.selectAllNodeTypes = QtGui.QCheckBox(self.filesTab)
        self.selectAllNodeTypes.setChecked(False)
        self.selectAllNodeTypes.setObjectName("selectAllNodeTypes")
        self.horizontalLayout_4.addWidget(self.selectAllNodeTypes)
        self.selectTextureNodesOnly = QtGui.QCheckBox(self.filesTab)
        self.selectTextureNodesOnly.setChecked(True)
        self.selectTextureNodesOnly.setObjectName("selectTextureNodesOnly")
        self.horizontalLayout_4.addWidget(self.selectTextureNodesOnly)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.defaultFolderTypes = QtGui.QTableWidget(self.filesTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.defaultFolderTypes.sizePolicy().hasHeightForWidth())
        self.defaultFolderTypes.setSizePolicy(sizePolicy)
        self.defaultFolderTypes.setAutoFillBackground(False)
        self.defaultFolderTypes.setObjectName("defaultFolderTypes")
        self.defaultFolderTypes.setColumnCount(2)
        self.defaultFolderTypes.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.defaultFolderTypes.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.defaultFolderTypes.setHorizontalHeaderItem(1, item)
        self.defaultFolderTypes.horizontalHeader().setCascadingSectionResizes(False)
        self.defaultFolderTypes.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.defaultFolderTypes)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.keepOriginalSubfolders = QtGui.QCheckBox(self.filesTab)
        self.keepOriginalSubfolders.setChecked(True)
        self.keepOriginalSubfolders.setObjectName("keepOriginalSubfolders")
        self.horizontalLayout_2.addWidget(self.keepOriginalSubfolders)
        self.updatePath = QtGui.QCheckBox(self.filesTab)
        self.updatePath.setChecked(True)
        self.updatePath.setObjectName("updatePath")
        self.horizontalLayout_2.addWidget(self.updatePath)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.actionButtonsLayout = QtGui.QHBoxLayout()
        self.actionButtonsLayout.setObjectName("actionButtonsLayout")
        self.copy = QtGui.QPushButton(self.filesTab)
        self.copy.setObjectName("copy")
        self.actionButtonsLayout.addWidget(self.copy)
        self.move = QtGui.QPushButton(self.filesTab)
        self.move.setObjectName("move")
        self.actionButtonsLayout.addWidget(self.move)
        self.search = QtGui.QPushButton(self.filesTab)
        self.search.setObjectName("search")
        self.actionButtonsLayout.addWidget(self.search)
        self.refresh = QtGui.QPushButton(self.filesTab)
        self.refresh.setObjectName("refresh")
        self.actionButtonsLayout.addWidget(self.refresh)
        self.cancel = QtGui.QPushButton(self.filesTab)
        self.cancel.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.cancel.setObjectName("cancel")
        self.actionButtonsLayout.addWidget(self.cancel)
        self.verticalLayout.addLayout(self.actionButtonsLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.tabWidget.addTab(self.filesTab, "")
        self.toolsTab = QtGui.QWidget()
        self.toolsTab.setObjectName("toolsTab")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.toolsTab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.toolBox = QtGui.QToolBox(self.toolsTab)
        self.toolBox.setObjectName("toolBox")
        self.imageResizeReformat = QtGui.QWidget()
        self.imageResizeReformat.setGeometry(QtCore.QRect(0, 0, 1235, 812))
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
        self.verticalLayout_4.addWidget(self.toolBox)
        self.tabWidget.addTab(self.toolsTab, "")
        self.settingsTab = QtGui.QWidget()
        self.settingsTab.setObjectName("settingsTab")
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.settingsTab)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.settingsLabel = QtGui.QLabel(self.settingsTab)
        self.settingsLabel.setWordWrap(True)
        self.settingsLabel.setObjectName("settingsLabel")
        self.verticalLayout_7.addWidget(self.settingsLabel)
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.xmlLabel = QtGui.QLabel(self.settingsTab)
        self.xmlLabel.setEnabled(True)
        self.xmlLabel.setInputMethodHints(QtCore.Qt.ImhNone)
        self.xmlLabel.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.xmlLabel.setObjectName("xmlLabel")
        self.verticalLayout_6.addWidget(self.xmlLabel)
        self.xmlLocation = QtGui.QLineEdit(self.settingsTab)
        self.xmlLocation.setEnabled(False)
        self.xmlLocation.setObjectName("xmlLocation")
        self.verticalLayout_6.addWidget(self.xmlLocation)
        self.verticalLayout_7.addLayout(self.verticalLayout_6)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
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
        self.verticalLayout_5.addWidget(self.nodeTypesList)
        self.acceptedNodesLabel = QtGui.QLabel(self.settingsTab)
        self.acceptedNodesLabel.setObjectName("acceptedNodesLabel")
        self.verticalLayout_5.addWidget(self.acceptedNodesLabel)
        self.manualAddNodesLabel = QtGui.QLabel(self.settingsTab)
        self.manualAddNodesLabel.setObjectName("manualAddNodesLabel")
        self.verticalLayout_5.addWidget(self.manualAddNodesLabel)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.newParameterName = QtGui.QLineEdit(self.settingsTab)
        self.newParameterName.setObjectName("newParameterName")
        self.gridLayout.addWidget(self.newParameterName, 1, 2, 1, 2)
        self.addNodeType = QtGui.QPushButton(self.settingsTab)
        self.addNodeType.setObjectName("addNodeType")
        self.gridLayout.addWidget(self.addNodeType, 2, 3, 1, 1)
        self.autoAddNodeButton = QtGui.QPushButton(self.settingsTab)
        self.autoAddNodeButton.setObjectName("autoAddNodeButton")
        self.gridLayout.addWidget(self.autoAddNodeButton, 5, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 3, 3, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(300, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 5, 2, 1, 1)
        self.nodeTypeLabel = QtGui.QLabel(self.settingsTab)
        self.nodeTypeLabel.setObjectName("nodeTypeLabel")
        self.gridLayout.addWidget(self.nodeTypeLabel, 0, 0, 1, 1)
        self.parameterNameLabel = QtGui.QLabel(self.settingsTab)
        self.parameterNameLabel.setObjectName("parameterNameLabel")
        self.gridLayout.addWidget(self.parameterNameLabel, 0, 2, 1, 1)
        self.newNodeType = QtGui.QLineEdit(self.settingsTab)
        self.newNodeType.setObjectName("newNodeType")
        self.gridLayout.addWidget(self.newNodeType, 1, 0, 1, 1)
        self.autoAddNodeLabel = QtGui.QLabel(self.settingsTab)
        self.autoAddNodeLabel.setObjectName("autoAddNodeLabel")
        self.gridLayout.addWidget(self.autoAddNodeLabel, 4, 0, 1, 1)
        self.defaultFolderLabel = QtGui.QLabel(self.settingsTab)
        self.defaultFolderLabel.setObjectName("defaultFolderLabel")
        self.gridLayout.addWidget(self.defaultFolderLabel, 0, 1, 1, 1)
        self.defaultFolder = QtGui.QComboBox(self.settingsTab)
        self.defaultFolder.setMinimumSize(QtCore.QSize(250, 0))
        self.defaultFolder.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.defaultFolder.setObjectName("defaultFolder")
        self.gridLayout.addWidget(self.defaultFolder, 1, 1, 1, 1)
        self.verticalLayout_5.addLayout(self.gridLayout)
        self.verticalLayout_7.addLayout(self.verticalLayout_5)
        self.tabWidget.addTab(self.settingsTab, "")
        self.verticalLayout_3.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.xmlLabel.setBuddy(self.xmlLocation)
        self.acceptedNodesLabel.setBuddy(self.nodeTypesList)
        self.nodeTypeLabel.setBuddy(self.newNodeType)
        self.parameterNameLabel.setBuddy(self.newParameterName)
        self.autoAddNodeLabel.setBuddy(self.autoAddNodeButton)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureLabel.setText(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">Scene Files</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.colorKeyCurrent.setText(QtGui.QApplication.translate("MainWindow", "Currently in Project   ", None, QtGui.QApplication.UnicodeUTF8))
        self.colorKeyMissing.setText(QtGui.QApplication.translate("MainWindow", "   Missing Files   ", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("MainWindow", "Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("MainWindow", "Node Type", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("MainWindow", "Default Folder", None, QtGui.QApplication.UnicodeUTF8))
        self.existingTextureList.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("MainWindow", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesLabel.setText(QtGui.QApplication.translate("MainWindow", "File Types by Default Project Folder Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAllNodeTypes.setText(QtGui.QApplication.translate("MainWindow", "Select All Node Types", None, QtGui.QApplication.UnicodeUTF8))
        self.selectTextureNodesOnly.setText(QtGui.QApplication.translate("MainWindow", "Texture Files Only", None, QtGui.QApplication.UnicodeUTF8))
        self.defaultFolderTypes.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.defaultFolderTypes.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("MainWindow", "Folder", None, QtGui.QApplication.UnicodeUTF8))
        self.keepOriginalSubfolders.setToolTip(QtGui.QApplication.translate("MainWindow", "If the original file location is in a subfolder of a different sourceimages folder, and you want to keep that folder structure, make sure this is checked.", None, QtGui.QApplication.UnicodeUTF8))
        self.keepOriginalSubfolders.setStatusTip(QtGui.QApplication.translate("MainWindow", "Check to keep original sub-folder structure", None, QtGui.QApplication.UnicodeUTF8))
        self.keepOriginalSubfolders.setText(QtGui.QApplication.translate("MainWindow", "Keep Original Subfolders", None, QtGui.QApplication.UnicodeUTF8))
        self.updatePath.setToolTip(QtGui.QApplication.translate("MainWindow", "When this is checked, the nodes in the scene will be updated to the copied/moved path", None, QtGui.QApplication.UnicodeUTF8))
        self.updatePath.setStatusTip(QtGui.QApplication.translate("MainWindow", "Uncheck if you want to copy the file to source images, but want to keep the original file location on the node.", None, QtGui.QApplication.UnicodeUTF8))
        self.updatePath.setText(QtGui.QApplication.translate("MainWindow", "Update Path on Run", None, QtGui.QApplication.UnicodeUTF8))
        self.copy.setText(QtGui.QApplication.translate("MainWindow", "Copy Misplaced Files", None, QtGui.QApplication.UnicodeUTF8))
        self.move.setText(QtGui.QApplication.translate("MainWindow", "Move Misplaced Files", None, QtGui.QApplication.UnicodeUTF8))
        self.search.setText(QtGui.QApplication.translate("MainWindow", "Attempt File Search", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh.setText(QtGui.QApplication.translate("MainWindow", "Refresh Scene Files List", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel.setText(QtGui.QApplication.translate("MainWindow", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.filesTab), QtGui.QApplication.translate("MainWindow", "Files", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.imageResizeReformat), QtGui.QApplication.translate("MainWindow", "Image Resize/Reformat", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.uvTilingSetup), QtGui.QApplication.translate("MainWindow", "UV Tiling Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.makePathsRelative), QtGui.QApplication.translate("MainWindow", "Make All Paths Relative", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemToolTip(self.toolBox.indexOf(self.makePathsRelative), QtGui.QApplication.translate("MainWindow", "Convert absolute paths to relative paths", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.toolsTab), QtGui.QApplication.translate("MainWindow", "Tools", None, QtGui.QApplication.UnicodeUTF8))
        self.settingsLabel.setText(QtGui.QApplication.translate("MainWindow", "USE WITH CAUTION!!\n"
"\n"
"These settings will affect the way this tool runs!  It was designed to be expandable, and uses an xml document to keep a list of acceptable image types.  Some are inserted by default, but the list can be expanded upon by you.\n"
"It is important to understand that changing this list will directly affect this tool\'s ability to preform.  Make sure you understand what you are doing before you hit save!", None, QtGui.QApplication.UnicodeUTF8))
        self.xmlLabel.setText(QtGui.QApplication.translate("MainWindow", "XML File Location", None, QtGui.QApplication.UnicodeUTF8))
        self.xmlLocation.setToolTip(QtGui.QApplication.translate("MainWindow", "The XML file that maintains the list of texture file node types", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesList.setToolTip(QtGui.QApplication.translate("MainWindow", "List of excepted file nodes", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("MainWindow", "nodeType", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("MainWindow", "defaultFolder", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypesList.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("MainWindow", "parameterName", None, QtGui.QApplication.UnicodeUTF8))
        self.acceptedNodesLabel.setText(QtGui.QApplication.translate("MainWindow", "Accepted Nodes", None, QtGui.QApplication.UnicodeUTF8))
        self.manualAddNodesLabel.setText(QtGui.QApplication.translate("MainWindow", "Manually add new node", None, QtGui.QApplication.UnicodeUTF8))
        self.addNodeType.setText(QtGui.QApplication.translate("MainWindow", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.autoAddNodeButton.setToolTip(QtGui.QApplication.translate("MainWindow", "This will bring up a list of attribues from the existing node.  Pick the correct parameter from there", None, QtGui.QApplication.UnicodeUTF8))
        self.autoAddNodeButton.setText(QtGui.QApplication.translate("MainWindow", "   Auto Add From Selection   ", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeTypeLabel.setText(QtGui.QApplication.translate("MainWindow", "nodeType", None, QtGui.QApplication.UnicodeUTF8))
        self.parameterNameLabel.setText(QtGui.QApplication.translate("MainWindow", "parameterName", None, QtGui.QApplication.UnicodeUTF8))
        self.autoAddNodeLabel.setText(QtGui.QApplication.translate("MainWindow", "Get the node type and attribute from the currently selected node", None, QtGui.QApplication.UnicodeUTF8))
        self.defaultFolderLabel.setText(QtGui.QApplication.translate("MainWindow", "defaultFolder", None, QtGui.QApplication.UnicodeUTF8))
        self.defaultFolder.setToolTip(QtGui.QApplication.translate("MainWindow", "Based on Project Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingsTab), QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == '__main__':
    # wrap atomicInterface() in a instance wrapper and call
    run = atomicTextureFileManager(parent=atomicInterface())
    run.show()
