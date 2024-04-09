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
class FileContentDialog2(QDialog):
    def __init__(self, name,attribute, size, create_date, last_updated, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Infomation")
        
        self.name = name
        self.attribute = attribute
        self.size = size
        self.create_date = create_date
        self.last_updated = last_updated
        
        name = QLabel("Name: " + str(name))
        attri=QLabel(str(attribute))
        size_label = QLabel("Size: " + str(size))
        create_date_label = QLabel("Create Date: " + str(create_date))
        last_updated_label = QLabel("Last Updated: " + str(last_updated))
        
        layout = QVBoxLayout()
        layout.addWidget(name)
        layout.addWidget(attri)
        layout.addWidget(size_label)
        layout.addWidget(create_date_label)
        layout.addWidget(last_updated_label)
        
        self.setLayout(layout)
class FileExplorerApp(QMainWindow):
    def __init__(self,drive):
        super().__init__()
        self.setWindowTitle("File Explorer")
        self.setGeometry(50, 50, 1400, 1000)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Name", "Size"])
        
        self.treeWidget.setColumnWidth(0, 600)  # Cột "Name" có kích thước 300 pixels
        self.treeWidget.setColumnWidth(1, 50)

        
        self.setCentralWidget(self.treeWidget)
        self.set_selected_drive(drive)
        self.treeWidget.itemDoubleClicked.connect(self.on_item_clicked)
        # self.treeWidget.itemClicked.connect(self.print_info)
    def print_info(self,item):
        
        file=item.text(0)
        full_path = self.get_full_path(item)
        direc_path=os.path.dirname(full_path)
        sub_dir_info = self.fat32.retrieve_path(direc_path)
        sub_entries = sub_dir_info.get_active_entries()
        for entry in sub_entries:
            
            if entry.entry_name.upper()==file.upper():
                try:
                    dialog = FileContentDialog2(entry.entry_name ,entry.attr, entry.size,entry.create_date,entry.last_updated)
                    dialog.exec()
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e))
    
    def set_selected_drive(self, drive):
    
        self.fat32 = FAT32(drive)
        self.populate_tree()
    
    def populate_tree(self):
        header_labels = ["Name", "Size", "Date Created", "Last Modified","Attribute"] 
        self.treeWidget.setHeaderLabels(header_labels)
        self.treeWidget.setColumnWidth(2, 300)
        self.treeWidget.setColumnWidth(3, 300)
        self.treeWidget.setColumnWidth(4, 200)
        root = QTreeWidgetItem(self.treeWidget, [self.fat32.name])
        self.treeWidget.addTopLevelItem(root)
        self.populate_children(root, self.fat32.RDET.get_active_entries())
        

    def populate_children(self, parent, entries):
        for entry in entries:
            if entry.entry_name not in [".", ".."]:  # Skip entries "." and ".."
                child = QTreeWidgetItem(parent, [entry.entry_name, str(entry.size), str(entry.create_date), str(entry.last_updated),str(entry.attr)])
                parent.addChild(child)
               
                if entry.is_direct():
                    try:
                        # Lấy thông tin về thư mục con
                        
                        path=self.get_full_path(child)
                       
                        sub_dir_info = self.fat32.retrieve_path(path)
                     
                        sub_entries = sub_dir_info.get_active_entries()  # Thông tin về các thư mục con
                        # Đệ quy để thêm các mục con vào cây thư mục
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
   