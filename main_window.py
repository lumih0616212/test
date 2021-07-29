from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtGui,QtCore
import numpy as np
import time
from utils import cal_reproject_error, sliding_window_calibrate, scatter_hist
import cv2

LabelPictureSize = (1500, 900)
ButtonHeight = 40
img=None

class calithread(QThread):
    print_error=Signal(str)
    finish_cali=Signal()
    def __init__(self):
        super().__init__()
        
    def run(self):
       
       self.objpoints = []
       self.imgpoints = []
       self.counter=0
       #self.frame_count=20
       self.frame_count=1
       self.slide_threshold=10
       self.corner_x = 7
       self.corner_y = 7
       self.objp = np.zeros((self.corner_x*self.corner_y, 3), np.float32)
       self.objp[:, :2] = np.mgrid[0:self.corner_x, 0:self.corner_y].T.reshape(-1, 2)
       self._width=0
       self._height=0
       t=time.time()
       while(True):
          t2=time.time()
          if(t2-t>3):
             t=t2
             self.calibrate()
             
          if(self.counter==self.frame_count):
             self.finish_cali.emit()
             break
           
    def calibrate(self):
       global img
       calibrate_img=img
       gray = cv2.cvtColor(calibrate_img, cv2.COLOR_BGR2GRAY)
       r, corners = cv2.findChessboardCorners(gray, (self.corner_x, self.corner_y), None)
       t=""
       if(r==True):
            self.counter += 1
            t+=("capture success and chessboard \nis founded, {}/{}\n".format(self.counter,self.frame_count))
            self.objpoints.append(self.objp)
            self.imgpoints.append(corners)
            #above part for finding chessboard
            self._width=calibrate_img.shape[1]
            self._height=calibrate_img.shape[0]
            img_size = (self._width, self._height)
            if self.counter>self.slide_threshold:  #choosing when to do the sliding window
                ret, mtx, dist, rvecs, tvecs, self.imgpoints, self.objpoints, err = sliding_window_calibrate(self.objpoints, self.imgpoints, img_size, self.counter, self.frame_count)
            else:
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, img_size, None, None)
                err = cal_reproject_error(self.imgpoints,self.objpoints,rvecs,tvecs,mtx,dist)
            t+=("error:{}".format(err))
       else:
           t+=("No chessboard is found in this frame")
       self.print_error.emit(t)
       print("a frame will be captured in three seconds")
   
    def stop(self):
        self.wait()
class VideoThread(QThread):
    change_pixmap_signal = Signal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = False
        self.exit=True
    def run(self):
        # capture from web cam
        while(self.exit):
          self.cap = cv2.VideoCapture(0)
          while self._run_flag:
              ret, cv_img = self.cap.read()
              if ret:
                  self.change_pixmap_signal.emit(cv_img)
          # shut down capture system
        self.cap.release()

    def stop(self):
        #Sets run flag to False and waits for thread to finish
        self._run_flag = False
        self.exit=False
        self.wait()
    def sstop(self):
        self._run_flag = False
    def sstart(self):
        self._run_flag = True

class CameraWidget(QWidget):
    def __init__(self, centralwidget):
        super().__init__()
        self.centralwidget = centralwidget
        self.image = None
    
    def setupUi(self, MainWindow):
        self.setObjectName(u"camerawidget")
        self.setFont(QFont(u"Arial", 16)) # 修改字體大小(07/)

        self.LabelCamera = QLabel('Label to show Camera', self)
        self.LabelCamera.setObjectName(u"LabelCamera")
        self.LabelCamera.setStyleSheet("background-color: lightgreen")
        # self.LabelCamera.setGeometry(QRect(20, 20, *LabelPictureSize))  # updated

        self.frame = QFrame(self)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        # self.frame.setGeometry(QRect(1550, 30, 350, 1000))  # updated

        font_Arial18 = QFont("Arial", 18)

        # updated 新增 label
        self.groupBox_2 = QGroupBox('Info', self.frame)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setFont(font_Arial18) # 修改字體大小(07/)
        # self.groupBox_2.setGeometry(QRect(10, 10, 300, 70)) # updated

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")
        #self.label.setText("THIS IS A TEST.\n HAHAHAH")
        self.label.move(20, 30)
        # resize for testing
        self.label.resize(300,240)
        # self.label.setGeometry(QRect(20, 30, 80, 30)) # 修改寬度 高度(07/)

        self.groupBox = QGroupBox('Functions', self.frame)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setFont(font_Arial18)
        # self.groupBox.setGeometry(QRect(40, 500, 240, 300)) # x, y, x_len, y_len updated

        # Buttons: Connect Camera | Correction | Play Pause | ... | Skip
        self.ButtonConnectCamera = QPushButton('Connect Camera', self.groupBox)
        self.ButtonConnectCamera.setObjectName(u"ButtonConnectCamera")
        self.ButtonConnectCamera.setFont(font_Arial18)
        # self.ButtonConnectCamera.setGeometry(QRect(20, 40+(ButtonHeight+10)*0, 200, ButtonHeight))
        '''
        self.ButtonCalibration = QPushButton('Calibration', self.groupBox)
        self.ButtonCalibration.setObjectName(u"ButtonCalibration")
        self.ButtonCalibration.setFont(font_Arial18)
        # self.ButtonCalibration.setGeometry(QRect(20, 40+(ButtonHeight+10)*1, 200, ButtonHeight))

        self.ButtonPlayPause = QPushButton('Play / Pause', self.groupBox)
        self.ButtonPlayPause.setObjectName(u"ButtonPlayPause")
        self.ButtonPlayPause.setFont(font_Arial18)
        # self.ButtonPlayPause.setGeometry(QRect(20, 40+(ButtonHeight+10)*2, 200, ButtonHeight))
        '''
        self.ButtonChangeQWidget = QPushButton('Skip', self.groupBox)
        self.ButtonChangeQWidget.setObjectName(u"ButtonChangeQWidget")
        self.ButtonChangeQWidget.setFont(font_Arial18)
        # self.ButtonChangeQWidget.setGeometry(QRect(20, 40+(ButtonHeight+10)*4, 200, ButtonHeight))

        # layout
        #---------- updated begin--------- 
        self.main_layout = QHBoxLayout(self)  # updated
        self.main_layout.setObjectName(u"main_layout")  # updated
        self.main_layout.addWidget(self.LabelCamera, 8)  # updated
        self.main_layout.addWidget(self.frame, 2)  # updated

        self.layout_frame = QVBoxLayout(self.frame) # updated
        self.layout_frame.setObjectName(u"layout_frame")
        self.layout_frame.addWidget(self.groupBox_2, 4) # updated
        self.layout_frame.addWidget(self.groupBox, 5) # updated

        self.layout_button = QVBoxLayout(self.groupBox) # updated
        self.layout_button.setObjectName(u"layout_button")
        self.layout_button.addWidget(self.ButtonConnectCamera, 1)
        '''
        self.layout_button.addWidget(self.ButtonCalibration, 1)
        self.layout_button.addWidget(self.ButtonPlayPause, 1)
        '''
        self.layout_button.addStretch(1)
        self.layout_button.addWidget(self.ButtonChangeQWidget, 1)
        #---------- updated end --------- 

        self.ButtonConnectCamera.clicked.connect(self.ConnectCamera)
        #self.ButtonPlayPause.clicked.connect(self.PlayPause)
        self.MainWindow=MainWindow
        self.ButtonChangeQWidget.clicked.connect(self.skip)
        self.CameraOpening=False
        self.timer = QTimer()
        self.timer.timeout.connect(self.ii)
        self.status="Connect"
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()
        
    def ii(self):
        self.timer.stop()
        self.label.setText("a frame will be captured in three seconds")
        
        self.cali_thread=calithread()
        self.cali_thread.start()
        self.cali_thread.print_error.connect(self.change_word)
        self.cali_thread.finish_cali.connect(self.button_change)
    def button_change(self):
        self.ButtonConnectCamera.setText("Play / Pause")
        self.status="PlayPause"
    def change_word(self,word):
        self.label.setText(word)
    def ConnectCamera(self):
        if(self.status=="Connect"):
           if(not self.CameraOpening):
               self.thread.sstart()
               self.CameraOpening=True
           self.label.setText("Start Calibrating...")
           self.timer.start(3000)
        elif(self.status=="PlayPause"):
           self.PlayPause()
    def PlayPause(self):
        if(self.CameraOpening):
             self.thread.sstop()
             self.CameraOpening=False
        else:
             self.thread.sstart()
             self.CameraOpening=True
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        global img
        self.qt_img = self.convert_cv_qt(cv_img)
        self.LabelCamera.setPixmap(self.qt_img)
        self.image=cv_img
        img=cv_img
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        global LabelPictureSize # updated
        LabelPictureSize = self.LabelCamera.size().toTuple() # updated

        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(*LabelPictureSize, Qt.KeepAspectRatio) # updated
        return QPixmap.fromImage(p)

    def skip(self):
        self.MainWindow.setCentralWidget(self.centralwidget)  
        self.thread.stop() 
        print('LabelPictureSize:', self.LabelCamera.size())  # updated

