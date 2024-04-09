from PyQt6.QtWidgets import QMainWindow, QTreeWidget, QMenu, QAction, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class FileExplorerApp(QMainWindow):
    def __init__(self, drive):
        super().__init__()
        self.setWindowTitle("File Explorer")
        self.setGeometry(50, 50, 800, 600)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Name", "Size"])

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.treeWidget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.set_selected_drive(drive)

    def show_context_menu(self, position):
        # Tạo menu tùy chỉnh
        menu = QMenu(self)

        # Thêm các action vào menu
        open_action = QAction("Open", self)
        menu.addAction(open_action)

        # Hiển thị menu tại vị trí con chuột
        menu.exec_(self.treeWidget.viewport().mapToGlobal(position))

    # Các phương thức khác

if __name__ == "__main__":
    app = QApplication([])
    window = FileExplorerApp("E:")
    window.show()
    app.exec()