from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from ui import main, tbrowser, filename
import sys, os
import threading
import base64
import traceback

class FileName(filename.Ui_Dialog, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(FileName, self).__init__(parent)
        self.setupUi(self)
    
class TextBrowser(tbrowser.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(TextBrowser, self).__init__(parent)
        self.setupUi(self)


class ListFiles(main.Ui_MainWindow, QtWidgets.QMainWindow):
    def enableButtons(self):
        self.edit.setEnabled(True)
        self.rename.setEnabled(True)
        self.deleteFile.setEnabled(True)

    def disableButtons(self):
        self.edit.setEnabled(False)
        self.rename.setEnabled(False)
        self.deleteFile.setEnabled(False)

    def createFile(self, filename='New File'):
        item = QtWidgets.QListWidgetItem()
        item.setText(filename)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/file-icon-doodle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon)
        self.files.addItem(item)
        
    
    def appendFiles(self):
        try:
            files = os.listdir(self.filesDir)
            for file in files:
                fname = os.path.splitext(file)[0]
                self.createFile(filename=fname)
            
        except Exception as e:
            # traceback.print_exc()
            pass
                
    def __init__(self):
        super(ListFiles, self).__init__()
        self.filesDir = os.path.join(os.getcwd(), "files")
        if not os.path.exists(self.filesDir):
            os.mkdir(self.filesDir)

        self.dataDir = os.path.join(os.getcwd(), "data")
        if not os.path.exists(self.dataDir):
            os.mkdir(self.dataDir)

        self.setupUi(self)
        icon = QtGui.QIcon('icons/icon_small.png')
        self.setWindowIcon(icon)
        self.setWindowTitle('Note Editor')
        self.fontSize = 8
        self.font = ''
        self.fontColor = "#000"
        self.background = '#fff'
        self.seperator = '©¼½¾®'
        self.currentFile = ''
        self.files.clear()
        self.appendFiles()
        self.edit.setEnabled(False)
        self.rename.setEnabled(False)
        self.deleteFile.setEnabled(False)
        if self.files.count()>0:
            self.enableButtons()
        self.files.itemClicked.connect(self.onItemClicked)
        self.newFile.setIcon(QtGui.QIcon('icons/new-file-icon.png'))
        self.edit.setIcon(QtGui.QIcon('icons/edit-file-icon.png'))
        #self.newFile.clicked.connect(self.addFile)
        newFileThread = threading.Thread(target=self.newFile.clicked.connect, args=(self.addFile,))
        newFileThread.start()
        editFileThread = threading.Thread(target=self.edit.clicked.connect, args=(self.editFile,))
        editFileThread.start()
        editFileThread2 = threading.Thread(target=self.files.itemDoubleClicked.connect, args=(self.editFile,))
        editFileThread2.start()
        deleteFileThread = threading.Thread(target=self.deleteFile.clicked.connect, args=(self.delete_file,))
        deleteFileThread.start()
        renameFileThread = threading.Thread(target=self.rename.clicked.connect, args=(self.renameFile,))
        renameFileThread.start()
        self.menuClose.setTitle('Window')
        self.menuClose.addAction("Minimize", self.actionClicked)
        self.menuClose.addAction("Maximize", self.actionClicked)
        self.menuClose.addAction("Close", self.actionClicked)

    @QtCore.pyqtSlot()
    def actionClicked(self):
        action = self.sender()
        text = action.text()
        if text == 'Close':
            self.close()

        if text == 'Minimize':
            self.showMinimized()

        if text == 'Maximize':
            self.showMaximized()
        #self.close()

    def setStatusBarText(statusBar, message, time=2):
        def clearStatusBarTimer(statusBar, time):
            statusBar.clearMessage()
        statusBar.showMessage(message)
        threading.Thread(target=clearStatusBarTimer, args=(statusBar, time))

    def renameFile(self):
        def rename():
            newName = dialog.filename.text()
            rnew_file = os.path.join(self.filesDir, f'{newName}.du')
            os.rename(rfile, rnew_file)
            self.files.clear()
            self.appendFiles()
            dialog.close()
        
        def close():
            dialog.close()

        if len(self.files.selectedItems())!=0:
            dialog = FileName(parent=self)
            dialog.show()
            dialog.ok.clicked.connect(rename)
            dialog.cancel.clicked.connect(close)

            index = self.files.currentRow()
            filename = self.files.item(index).text()
            rfile = os.path.join(self.filesDir, f'{self.files.item(index).text()}.du')
            # path =  os.path.join(os.getcwd(), 'files\\')

            dialog.filename.setText(filename)
            dialog.filename.selectAll()
            
        else:
            self.statusbar.showMessage('Please select file before rename !')

    def delete_file(self):
        if len(self.files.selectedItems())!=0:
            index = self.files.currentRow()
            dfile = os.path.join(self.filesDir,f'{self.files.item(index).text()}.du')
            self.files.takeItem(index)
            items =  [str(self.files.item(i).text()) for i in range(self.files.count())]
            filename = os.path.join(self.dataDir, 'files.dat')
            file = open(filename, 'w')
            for i in items:
                file.write(i+'\n')

            # remove file from system    
            os.remove(dfile)
            

            if len(items) == 0:
                self.disableButtons()
        else:
            self.statusbar.showMessage('Please select file before delete !')
        
    def onItemClicked(self):
        self.statusbar.showMessage('')

    def editFile(self):
        def changeFontColor():
            color = QtWidgets.QColorDialog.getColor()
            if color.isValid():
                self.fontColor = color.name()
                self.tb.color.setStyleSheet(f"background:{self.fontColor};border:1px solid black;")
                self.tb.editor.setStyleSheet(f'color:{self.fontColor};background:{self.background}')

        def changeBackground():
            color = QtWidgets.QColorDialog.getColor()

            if color.isValid():
                self.background = color.name()
                self.tb.bg_color.setStyleSheet(f"background:{self.background};border:1px solid black;")
                self.tb.editor.setStyleSheet(f'color:{self.fontColor};background:{self.background}')

        def setFont():
            index = self.tb.font.currentIndex()
            font = self.tb.font.itemText(index)
            self.font = QtGui.QFont(font)
            self.font.setPointSize(self.fontSize)
            self.tb.editor.setFont(self.font)

        def changeFontSize():
            self.fontSize = self.tb.fsize.value()
            setFont()

        def editFileAddData():
            self.writeToFile(self.currentFile+'.du')
            self.tb.statusBar().showMessage("File Saved !")
            # self.setStatusBarText(self.tb.statusBar(), "File Saved", time=5)

        def addDataToFile():
            try:
                file_path = os.path.join(self.filesDir, f'{self.currentFile}.du')
                file = open(file_path, 'rb')
                data = file.read()
                decoded_data = base64.urlsafe_b64decode(data).decode()
                data_split = [x for x in decoded_data.split(self.seperator) if x!=""]
                font = data_split[0]
                self.fontSize = int(data_split[1])
                self.fontColor = data_split[2]
                self.background = data_split[3]
                self.tb.color.setStyleSheet(f"background:{self.fontColor};border:1px solid black;")
                self.tb.bg_color.setStyleSheet(f"background:{self.background};border:1px solid black;")

                self.font = QtGui.QFont(font)
                self.font.setPointSize(self.fontSize)
                self.tb.editor.setFont(self.font)
                self.tb.editor.setStyleSheet(f'color:{self.fontColor};background:{self.background};')
                self.tb.fsize.setProperty("value", self.fontSize)
                new_data = data_split[4]
                self.tb.editor.setPlainText(new_data)
            except Exception as e:
                # traceback.print_exc()
                pass
            

        if len(self.files.selectedItems())!=0:
            self.tb = TextBrowser(parent=self)
            
            index = self.files.currentRow()
            self.currentFile = self.files.item(index).text()
            self.tb.font.currentIndexChanged.connect(setFont)
            self.tb.fsize.valueChanged.connect(changeFontSize)
            self.tb.foreground.clicked.connect(changeFontColor)
            self.tb.background.clicked.connect(changeBackground)
            
            self.tb.editor.textChanged.connect(editFileAddData)
            self.tb.save.clicked.connect(editFileAddData)
            self.tb.show()
            addDataToFile()
        else:
            self.statusbar.showMessage('Please select file before edit!')


    def closeEvent(self, event):
            self.newFile.setEnabled(True)
    def addFile(self):
        all_files = [str(self.files.item(i).text()) for i in range(self.files.count())]
        self.newFile.setEnabled(False)
        dialog = FileName(parent=self)
        
        def accept():
            text = dialog.filename.text()
            if text == "":
                dialog.filename.setStyleSheet('border:1px solid red;')
                dialog.log.append('Filename Required !')
            else:
                if text in all_files:
                    dialog.log.clear()
                    dialog.filename.setStyleSheet('border:1px solid red;')
                    dialog.log.append('File with this name already exists !')
                else:
                    self.createFile(filename=text)
                    dialog.close()
                    self.enableButtons()
                    self.newFile.setEnabled(True)
                    self.saveFiles(text)
        def reject():
            dialog.close()
            self.newFile.setEnabled(True)
        def changeColor():
            dialog.filename.setStyleSheet('border:1px solid black;')
        
        dialog.show()
        dialog.closeEvent = self.closeEvent
        dialog.filename.textEdited.connect(changeColor)
        dialog.ok.clicked.connect(accept)
        dialog.cancel.clicked.connect(reject)

    def saveFiles(self, data):
        filename = os.path.join(self.dataDir, 'files.dat')
        file = open(filename, 'a')
        file.write(data+'\n')
        self.createNewFile(data)

    def createNewFile(self, name):
        filename = os.path.join(self.filesDir, f'{name}.du')
        file = open(filename, 'w').write('')
        
    def writeToFile(self, filename):
        self.seperator = '©¼½¾®'
        file_path = os.path.join(self.filesDir, f'{filename}')
        file = open(file_path, 'wb')
        data = self.tb.editor.toPlainText()
        new_data = f'{self.font}{self.seperator}{self.fontSize}{self.seperator}{self.fontColor}{self.seperator}{self.background}{self.seperator}{data}'
        encoded_data = base64.urlsafe_b64encode(new_data.encode())
        file.write(encoded_data)
        #file.write()
        
        
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ListFiles()
    window.show()
    sys.exit(app.exec_())