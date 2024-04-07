import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtCore import QDir
from FAT32 import FAT32
import os
class FileInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Information")
        
        self.create_date_label = QLabel()
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Create Date:"))
        layout.addWidget(self.create_date_label)
        
        self.setLayout(layout)
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
        root = QTreeWidgetItem(self.treeWidget, [self.fat32.name])
        self.treeWidget.addTopLevelItem(root)
        self.populate_children(root, self.fat32.RDET.get_active_entries())

    def populate_children(self, parent, entries):
        for entry in entries:
            if entry.entry_name not in [".", ".."]:  # Skip entries "." and ".."
                # Create a list of strings to represent the item's columns
                item_data = [entry.entry_name, str(entry.size), str(entry.create_date), str(entry.last_accessed)]
                # Add more information to the item's data list
                item_data.append("Flags: " + str(entry.attr.value))
                # Create the child item with the extended data
                child = QTreeWidgetItem(parent, item_data)
                parent.addChild(child)
                if entry.is_direct():
                    try:
                        sub_entries = self.fat32.retrieve_path(entry.entry_name).get_active_entries()
                        self.populate_children(child, sub_entries)
                    except Exception as e:
                        print(f"Error: {e}")

    # def populate_children(self, parent, entries):
    #     for entry in entries:
    #         if entry.entry_name not in [".", ".."]:  # Skip entries "." and ".."
    #             child = QTreeWidgetItem(parent, [entry.entry_name, str(entry.size)])
    #             parent.addChild(child)
    #             if entry.is_direct():
    #                 try:
    #                     sub_entries = self.fat32.retrieve_path(entry.entry_name).get_active_entries()
    #                     self.populate_children(child, sub_entries)
    #                 except Exception as e:
    #                     print(f"Error: {e}")


    def on_item_clicked(self, item, column):
        item_path = self.get_item_full_path(item)
        entry_info = self.get_directory_info(item_path)
        self.show_file_info_dialog(entry_info)

    def get_item_full_path(self, item):
        path = []
        while item is not None:
            path.insert(0, item.text(0))
            item = item.parent()
        return QDir.cleanPath('/'.join(path))

    def get_directory_info(self, path):
        try:
            return self.fat32.get_directory_info(path)
        except Exception as error:
            print(f"Error: {error}")

    def show_file_info_dialog(self, entry_info):
        dialog = FileInfoDialog(self)
        dialog.create_date_label.setText(entry_info["Date Created"].strftime("%Y-%m-%d %H:%M:%S"))
        dialog.exec()

