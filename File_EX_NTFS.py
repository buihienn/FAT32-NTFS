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
        self.setGeometry(100, 100, 800, 600)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Name", "Size", "Date Created", "Date Modified"])
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
            item = QTreeWidgetItem(parent_item, [name, str(node.fileSize), str(node.dateCreated), str(node.dateModified)])  # Create tree item with node name
            parent_item.addChild(item)
            self.populate_children(item, node.children)  # Recursively populate children
    

# if __name__ == "__main__":
#     app = QApplication(sys.argv)  # Create the application instance

#     # Provide the drive information (replace 'drive' with the actual drive information)
#     drive_info = "C:"  

#     # Create an instance of the FileExplorerApp class
#     file_explorer_app = FileExplorerApp(drive_info)

#     # Show the main window
#     file_explorer_app.show()

#     # Execute the application
#     sys.exit(app.exec())