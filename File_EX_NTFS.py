import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QDialog, QLabel, QVBoxLayout, QMessageBox
from NTFS import NTFS
from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QTextEdit
class NTFS_FileExplorerApp(QMainWindow):
    def __init__(self,drive):
        super().__init__()
        self.setWindowTitle("File Explorer")
        self.setGeometry(10, 10, 1600, 1000)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Name", "Size"])
        self.treeWidget.setColumnWidth(0, 600)  # Cột "Name" có kích thước 300 pixels
        self.treeWidget.setColumnWidth(1, 50) 
        self.setCentralWidget(self.treeWidget)

        self.set_selected_drive(drive)
    def set_selected_drive(self, drive):
    
        self.ntfs =NTFS(drive)
        self.populate_tree()
    def populate_tree(self):
        root_node = QTreeWidgetItem(self.treeWidget, [self.ntfs.name])  # Create root node
        self.treeWidget.addTopLevelItem(root_node)
        self.populate_children(root_node, self.ntfs.tree.root.children)  # Populate children recursively

    def populate_children(self, parent_item, children):
        for name, node in children.items():
            item = QTreeWidgetItem(parent_item, [name])  # Create tree item with node name
            parent_item.addChild(item)
            self.populate_children(item, node.children)  # Recursively populate children
    
