import cv2
from PyQt5.QtCore import pyqtSlot, QEventLoop, QThread, pyqtSignal, QTimer, QMutex
from PyQt5.QtGui import QImage

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

class CamCapture(QThread):
    sig = pyqtSignal()

    def __init__(self):
        super(CamCapture,self).__init__()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, SCREEN_WIDTH)
        self.cap.set(4, SCREEN_HEIGHT)

    def run(self):
        while True:
            success, img = self.cap.read()
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            self.qImg = QImage(imgRGB.data, SCREEN_WIDTH, SCREEN_HEIGHT,
                            img.strides[0], # byte size of a line
                            QImage.Format_RGB888)
            self.sig.emit()

            loop = QEventLoop()
            QTimer.singleShot(30, loop.quit)
            loop.exec_()      



