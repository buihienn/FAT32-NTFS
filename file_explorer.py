import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QDialog, QLabel, QVBoxLayout, QMessageBox

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QTextEdit
from FAT32 import FAT32
import os
class FileContentDialog(QDialog):
    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Content")
        
        self.textEdit = QTextEdit()
        self.textEdit.setPlainText(content)
        
        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)
        
        self.setLayout(layout)
def get_full_path_to_file(fat32, file_name, current_path=""):
    if current_path == "":
        current_path = fat32.name
    
    # Check if the current directory contains the file
    cur_det = fat32.retrieve_path(current_path)
    entry = cur_det.find_entry(file_name)
    if entry is not None and not entry.is_direct():
        return current_path
    
    # Recursively search in subdirectories
    entries = cur_det.get_active_entries()
    for entry in entries:
        if entry.is_direct():
            sub_path = os.path.join(current_path, entry.entry_name)
            full_path = get_full_path_to_file(fat32, file_name, sub_path)
            if full_path:
                return full_path
    
    return None
class FileExplorerApp(QMainWindow):
    def __init__(self,drive):
        super().__init__()
        self.setWindowTitle("File Explorer")
        self.setGeometry(100, 100, 800, 600)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Name", "Size"])
        self.setCentralWidget(self.treeWidget)

        self.set_selected_drive(drive)
        self.treeWidget.itemDoubleClicked.connect(self.on_item_clicked)
    def set_selected_drive(self, drive):
        self.fat32 = FAT32(drive)
        self.populate_tree()
    def populate_tree(self):
        header_labels = ["Name", "Size", "Date Created", "Last Modified"]  # Update header labels
        self.treeWidget.setHeaderLabels(header_labels)

        root = QTreeWidgetItem(self.treeWidget, [self.fat32.name])
        self.treeWidget.addTopLevelItem(root)
        self.populate_children(root, self.fat32.RDET.get_active_entries())
        for i in range(len(header_labels)):
            self.treeWidget.resizeColumnToContents(i)

    def populate_children(self, parent, entries):
        for entry in entries:
            if entry.entry_name not in [".", ".."]:  # Skip entries "." and ".."
                child = QTreeWidgetItem(parent, [entry.entry_name, str(entry.size), str(entry.create_date), str(entry.last_updated)])
                parent.addChild(child)
                if entry.is_direct():
                    try:
                        sub_entries = self.fat32.retrieve_path(entry.entry_name).get_active_entries()
                        self.populate_children(child, sub_entries)
                    except Exception as e:
                        print(f"Error: {e}")
   

    def on_item_clicked(self, item):
        # Get the full path of the clicked item
        file=item.text(0)
        full_path = self.get_full_path(item)
        direc_path=os.path.dirname(full_path)
        print(direc_path)
        
        try:
            self.fat32.move_to_directory(direc_path)
            content = self.fat32.get_File_content(file)
        
            # Create a dialog to display the file content
            dialog = FileContentDialog(content, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def get_full_path(self, item):
        # Get the full path of the clicked item by traversing its ancestors
        path = [item.text(0)]
        parent = item.parent()
        while parent:
            path.insert(0, parent.text(0))
            parent = parent.parent()
        full_path = QDir.fromNativeSeparators("/".join(path))
        return full_path
   
