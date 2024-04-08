from FAT32 import FAT32
from UI import UI
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QPushButton, QWidget
from PyQt6 import QtGui,QtWidgets,QtCore
from choose import Ui_MainWindow
from file_explorer import FileExplorerApp

ui=''
app =QApplication(sys.argv)
Main_Window=QMainWindow()
def main_window():
    global ui
    ui=Ui_MainWindow()
    ui.setupUi(Main_Window)
    
    ui.pushButton.clicked.connect(open_file_explorer)
    Main_Window.show()

def open_file_explorer():
    
    selected_drive = ui.volumeC.currentText()
    
    file_explorer(selected_drive)

def file_explorer(drive):
    global ui
    ui = FileExplorerApp(drive)
    
    ui.show()  


if __name__ == "__main__":
    main_window()
    
    sys.exit(app.exec())
