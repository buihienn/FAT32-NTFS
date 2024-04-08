from FAT32 import FAT32

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtGui,QtWidgets,QtCore
from choose import Ui_MainWindow
from file_explorer import FileExplorerApp
from NTFS import NTFS
from File_EX_NTFS import NTFS_FileExplorerApp
ui=''
app =QApplication(sys.argv)
Main_Window=QMainWindow()
def main_window():
    global ui
    ui=Ui_MainWindow()#choose.py
    ui.setupUi(Main_Window)
    
    ui.pushButton.clicked.connect(open_file_explorer)#nut hoan tat

    Main_Window.show()

def open_file_explorer():
    
    selected_drive = ui.volumeC.currentText()#E:...
    
    if FAT32.is_FAT32(selected_drive):
        file_explorer_FAT32(selected_drive)
    else:
        file_explorer_NTFS(selected_drive)#xay cay cac thu
def file_explorer_NTFS(drive):
    global ui
    ui = NTFS_FileExplorerApp(drive)
    
    ui.show()  
def file_explorer_FAT32(drive):
    global ui
    ui = FileExplorerApp(drive)
    
    ui.show()  


if __name__ == "__main__":
    main_window()
    
    sys.exit(app.exec())
