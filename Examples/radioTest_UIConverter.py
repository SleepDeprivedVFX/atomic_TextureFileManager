import sys, pprint
from pysideuic import compileUi
pyfile = open('C:\\Users\\Adam\\OneDrive\\Documents\\maya\\2016\\scripts\\atomic_TFM_UI.py', 'w')
compileUi('C:\\Users\\Adam\\Google Drive\\Scripts\\atomicTextureFileManager\\UIs\\atomic_TFM_UI.ui', pyfile, False, 4,False)
pyfile.close()