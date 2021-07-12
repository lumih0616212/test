from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QRadioButton, QButtonGroup
from PySide2.QtGui import QFont, QIcon


class MainWindow(object):
    
    def __init__(self, parent=None):
        """Main window, holding all user interface including.
        Args:
          parent: parent class of main window
        Returns:
          None
        Raises:
          None
        """
        self._window = None
        self.sum=""
        self.tag=1
        self.setup_ui()

    @property
    def window(self):
        """The main window object"""
        return self._window

    def setup_ui(self):
        loader = QUiLoader()
        file = QFile('./media/calculus.ui')
        file.open(QFile.ReadOnly)
        self._window = loader.load(file)
        file.close()
         
        self._window.b0.clicked.connect(lambda:self.addNumber(0))
        self._window.b1.clicked.connect(lambda:self.addNumber(1))
        self._window.b2.clicked.connect(lambda:self.addNumber(2))
        self._window.b3.clicked.connect(lambda:self.addNumber(3))
        self._window.b4.clicked.connect(lambda:self.addNumber(4))
        self._window.b5.clicked.connect(lambda:self.addNumber(5))
        self._window.b6.clicked.connect(lambda:self.addNumber(6))
        self._window.b7.clicked.connect(lambda:self.addNumber(7))
        self._window.b8.clicked.connect(lambda:self.addNumber(8))
        self._window.b9.clicked.connect(lambda:self.addNumber(9))
        self._window.bplus.clicked.connect(lambda:self.addNumber("+"))
        self._window.beql.clicked.connect(lambda:self.addNumber("="))
        self._window.bmul.clicked.connect(lambda:self.addNumber("*"))
        self._window.bdiv.clicked.connect(lambda:self.addNumber("/"))
        self._window.bclean.clicked.connect(lambda:self.addNumber("@"))
    def addNumber(self, number):
        if(number=="@"):
            self.sum=""
            self._window.lineEdit_2.setText("")
            self._window.lineEdit.setText("")
            self.tag=1
            return
        if (self.tag):
          
          if(number==0 and (self.sum=="" or self.sum=="0")):
             return
          self._window.lineEdit_2.insert(str(number))
          if(number=="="):
            self._window.lineEdit.setText(str(eval(self.sum)))
            self.tag=0
            
          self.sum+=str(number)
        else:
            self.sum= self._window.lineEdit.text()
            self._window.lineEdit_2.setText(self.sum+number)
            self.sum+=number
            self.tag=1
