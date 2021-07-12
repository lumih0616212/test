import sys

from PySide2.QtWidgets import QApplication

from main_window_2 import MainWindow

if '__main__' == __name__:
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.window.show()

    ret = app.exec_()
    sys.exit(ret)
