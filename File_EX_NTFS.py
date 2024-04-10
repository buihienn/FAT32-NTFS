import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem,QPushButton
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QDialog, QLabel, QVBoxLayout, QMessageBox
from NTFS import NTFS
from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QTextEdit
from functools import partial
class FileContentDialog(QDialog):
    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Content")
        
        self.textEdit = QTextEdit()
        self.textEdit.setPlainText(content)
        
        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)
        
        self.setLayout(layout)

class FileContentDialog2(QDialog):

    def __init__(self, name,attribute,createDate, lastUpdated, size, parent = None):
        super().__init__(parent)
        self.setWindowTitle("File Infomation")
        
        self.name = name
        self.atribute = attribute
        self.size = size
        self.create_date = createDate
        self.last_updated = lastUpdated
        
        name = QLabel("Name file: " + name)
        attri = QLabel("Attributes: " + ", ".join(attribute))
        create_date_label = QLabel("Create Date: " + str(createDate))
        last_updated_label = QLabel("Last Updated: " + str(lastUpdated))
        size_label = QLabel("Size: " + str(size) + " bytes")
        
        layout = QVBoxLayout()
        layout.addWidget(name)
        layout.addWidget(attri)
        layout.addWidget(create_date_label)
        layout.addWidget(last_updated_label)
        layout.addWidget(size_label)
        
        self.setLayout(layout)
class FileContentDialog3(QDialog):

    def __init__(self, name,attribute,createDate, lastUpdated, size,content, parent = None):
        super().__init__(parent)
        self.setWindowTitle("File Infomation")
        
        self.name = name
        self.atribute = attribute
        self.size = size
        self.create_date = createDate
        self.last_updated = lastUpdated
        
        name = QLabel("Name file: " + name)
        attri = QLabel("Attributes: " + ", ".join(attribute))
        create_date_label = QLabel("Create Date: " + str(createDate))
        last_updated_label = QLabel("Last Updated: " + str(lastUpdated))
        size_label = QLabel("Size: " + str(size) + " bytes")
        self.open_button=QPushButton("OPEN")
        layout = QVBoxLayout()
        layout.addWidget(name)
        layout.addWidget(attri)
        layout.addWidget(create_date_label)
        layout.addWidget(last_updated_label)
        layout.addWidget(size_label)
        layout.addWidget(self.open_button)
        self.open_button.clicked.connect(partial(self.open_item, content))
        
        self.setLayout(layout)
    def open_item(self,content):
        dialog = FileContentDialog(content, self)
        dialog.exec() 
class NTFS_FileExplorerApp(QMainWindow):
    def __init__(self,drive):
        super().__init__()
        self.setWindowTitle("File Explorer")
        self.setGeometry(100, 100, 800, 600)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Name", "Size", "Date Created", "Date Modified", "ID"])
        self.setCentralWidget(self.treeWidget)

        self.set_selected_drive(drive)

        #self.treeWidget.itemDoubleClicked.connect(self.on_item_clicked)
        self.treeWidget.itemClicked.connect(self.printInfo)
    def set_selected_drive(self, drive):
    
        self.ntfs =NTFS(drive)
        self.populate_tree()

    def populate_tree(self):
        root_node = QTreeWidgetItem(self.treeWidget, [self.ntfs.name])  # Create root node
        self.treeWidget.addTopLevelItem(root_node)
        self.populate_children(root_node, self.ntfs.tree.root.children)  # Populate children recursively

    def populate_children(self, parent_item, children):
        for name, node in children.items():
            item = QTreeWidgetItem(parent_item, [name, str(node.fileSize) + " bytes", str(node.dateCreated), str(node.dateModified), str(node.id)]) # Create tree item with node name
            parent_item.addChild(item)
            self.populate_children(item, node.children)  # Recursively populate children

    def printInfo(self, item):
        idFile = int(item.text(4))
        
        for mftEntry in self.ntfs.MFTList:
            if mftEntry.EntryID == idFile:
                totalSize =mftEntry.getFileSize()
                if mftEntry.isDirectory() == True:
                    totalSize = self.ntfs.calSizeFolder(mftEntry.EntryID)
                if not self.ntfs.isFileTXT(mftEntry.EntryID):
                    try:
                        dialog = FileContentDialog2(mftEntry.getFileName(),mftEntry.getAttribute(),mftEntry.getCreatedTime(), mftEntry.getModified(), totalSize)
                        dialog.exec()
                    except Exception as e:
                        QMessageBox.warning(self, "Error", str(e))
                else:
                    try:
                        content = self.ntfs.dataFileText(mftEntry.EntryID)
                        dialog = FileContentDialog3(mftEntry.getFileName(),mftEntry.getAttribute(),mftEntry.getCreatedTime(), mftEntry.getModified(), totalSize,content)
                        dialog.exec()
                    except Exception as e:
                        QMessageBox.warning(self, "Error", str(e))
        return 

