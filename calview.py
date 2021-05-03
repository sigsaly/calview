import sys, random, copy
from PyQt5.QtWidgets import QWidget, QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem
from PyQt5.QtCore import QMutex, pyqtSlot, QObject, Qt, QTime, QTimer,QDateTime, QDir, QSize, QRectF, QLineF, QThread
from PyQt5.QtGui import QBrush, QPen, QFont, QImage, QPixmap, QPainter, QPalette, QColor
import cv2
from camitem import CamCapture
from clkitem import ClockItem, CalendarItem, monthString, dowString

import datetime, calendar
import threading, time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

CLOCK_INIT_X = 40
CLOCK_INIT_Y = 40
CLOCK_WIDTH = 230
CLOCK_HEIGHT = 150

CAL_INIT_X = 380
CAL_INIT_Y = 40
CAL_WIDTH = 380
CAL_HEIGHT = 380

CAL2_IMG_INIT_X = 0
CAL2_IMG_INIT_Y = 0
CAL2_MON_INIT_X = 30
CAL2_MON_INIT_Y = 20
CAL2_YEAR_INIT_X = 700
CAL2_YEAR_INIT_Y = 30
CAL2_DATE_INIT_X = 40
CAL2_DATE_INIT_Y = 160
CAL2_DATE_BAR_OFFSET_Y = 38

MOVE_MIN_X = -16
MOVE_MAX_X = 16
MOVE_MIN_Y = -16
MOVE_MAX_Y = 16

class CalendarView(QGraphicsView):
    imgPaths = []
    days = []
    def __init__(self):
        QGraphicsView.__init__(self)

        self.scene1 = QGraphicsScene(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scene2 = QGraphicsScene(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        self.showFullScreen()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: black; border: 0px")

        self.ImageHorizFull = True
        self.front_mode = 0
        self.back_mode = 0
        self.ImageFromCam = False

        self.setupScene1()
        self.setupScene2()        

        self.cam = CamCapture()
        self.cam.sig.connect(self.loadCapImage)
        self.cam.start()

        self.setScene(self.scene1)

        self.tmCnt = 0
        timer = QTimer(self)  
        timer.timeout.connect(self.timerWork)  
        timer.start(1000) 

    def setupScene1(self):
        self.curIndex = 0
        self.maxIndex = 0

        dir = QDir("images")
        files = dir.entryList(QDir.Files|QDir.Readable|QDir.Name)

        for filename in files:
            self.imgPaths.append(dir.absoluteFilePath(filename))
        self.maxIndex = len(self.imgPaths)

        if self.maxIndex == 0:
            print('No image')
            return

        image = QImage(self.imgPaths[self.curIndex])
        pixmap = self.scale(QPixmap.fromImage(image))

        self.curImage = self.scene1.addPixmap(pixmap)

        # set image center 
        w = pixmap.size().width()
        h = pixmap.size().height()

        if w == SCREEN_WIDTH:
            dif = int((SCREEN_HEIGHT - h)/2)
            self.curImage.setPos(0,dif)
        else :
            dif = int((SCREEN_WIDTH - w)/2)
            self.curImage.setPos(dif,0)

        self.curIndex += 1
        if self.curIndex > self.maxIndex:
            self.curIndex = 0

        self.clk_item = ClockItem(self, QRectF(CLOCK_INIT_X,CLOCK_INIT_Y,CLOCK_WIDTH,CLOCK_HEIGHT))
        self.scene1.addItem(self.clk_item)

        self.curClkX = 0
        self.curClkY = 0

        self.cal_item = CalendarItem(self, QRectF(CAL_INIT_X,CAL_INIT_Y,CAL_WIDTH,CAL_HEIGHT))
        self.scene1.addItem(self.cal_item)
        self.curCalX = 0
        self.curCalY = 0

    def scale(self, pixmap):
        size = pixmap.size()
        scaledSize = QSize(min(SCREEN_WIDTH, size.width()), min(SCREEN_HEIGHT, size.height()) )

        if size != scaledSize:
            if self.ImageHorizFull and size.width() > size.height():
                pixmap = pixmap.scaled(scaledSize, Qt.KeepAspectRatioByExpanding)
            else:
                pixmap = pixmap.scaled(scaledSize, Qt.KeepAspectRatio)
        return pixmap

    def timerWork(self):
        self.clk_item.showTime()
        self.tmCnt += 1000

        if self.tmCnt == 300000:
            self.tmCnt = 0
            if self.ImageFromCam == False:
                self.loadImage()

        now = datetime.datetime.now()
        if now.hour==0 and now.minute==0 and now.second==0:
            self.updateCalendar()

        if self.tmCnt % 10000 == 0:
            dr1 = random.randrange(0,4)
            dr2 = random.randrange(0,4)

            if dr1 == 0: # to top
                if self.curClkY > MOVE_MIN_Y:
                    self.curClkY -= 1
                    self.curCal2Y -= 1
            elif dr1 == 1: # to bottom
                if self.curClkY < MOVE_MAX_Y:
                    self.curClkY += 1
                    self.curCal2Y += 1
            elif dr1 == 2: # to left
                if self.curClkX > MOVE_MIN_X:
                    self.curClkX -= 1
                    self.curCal2X -= 1
            else :  #to right
                if self.curClkX < MOVE_MAX_X:
                    self.curClkX += 1
                    self.curCal2X += 1

            if dr2 == 0: # to top
                if self.curCalY > MOVE_MIN_Y:
                    self.curCalY -= 1
            elif dr2 == 1: # to bottom
                if self.curCalY < MOVE_MAX_Y:
                    self.curCalY += 1
            elif dr2 == 2: # to left
                if self.curCalX > MOVE_MIN_X:
                    self.curCalX -= 1
            else :  #to right
                if self.curCalX < MOVE_MAX_X:
                    self.curCalX += 1

            self.clk_item.setPos(self.curClkX, self.curClkY)
            self.cal_item.setPos(self.curCalX, self.curCalY)
            self.updateCalPos()

    def loadImage(self):
        if self.ImageFromCam == False:
            image = QImage(self.imgPaths[random.randrange(0, self.maxIndex-1)])
            pixmap = self.scale(QPixmap.fromImage(image))
            self.curImage.setPixmap(pixmap)

            w = pixmap.size().width()
            h = pixmap.size().height()

            if w == SCREEN_WIDTH:
                dif = int((SCREEN_HEIGHT - h)/2)
                self.curImage.setPos(0,dif)
            else :
                dif = int((SCREEN_WIDTH - w)/2)
                self.curImage.setPos(dif,0)

            self.curIndex += 1
            if self.curIndex >= self.maxIndex:
                self.curIndex = 0

    def setupScene2(self):
        image = QImage("calendar.png")
        self.calImg = self.scene2.addPixmap(QPixmap.fromImage(image))
        self.calImg.setPos(CAL2_IMG_INIT_X,CAL2_IMG_INIT_Y)

        monthFont = QFont("Arial", 26, QFont.Normal)
        monthFont.setStyle(QFont.StyleItalic)
        self.monthTxt = self.scene2.addText("month", monthFont)
        self.monthTxt.setDefaultTextColor(QColor(210,240,255))
        self.monthTxt.setPos(CAL2_MON_INIT_X, CAL2_MON_INIT_Y)

        yearFont = QFont("Comic Sans", 20, QFont.Normal)
        yearFont.setStyle(QFont.StyleItalic)
        self.yearTxt = self.scene2.addText("year", yearFont)
        self.yearTxt.setDefaultTextColor(QColor(97,147,255))
        self.yearTxt.setPos(CAL2_YEAR_INIT_X, CAL2_YEAR_INIT_Y)

        pen = QPen(QColor(35,200,220))
        pen.setWidth(3)
        self.todayLine = self.scene2.addLine(QLineF(0,0,36,0), pen)

        for y in range(6):
            for x in range(7):
                dateFont = QFont("Verdana", 18, QFont.Normal)
                date = self.scene2.addText("00", dateFont)
                date.setDefaultTextColor(Qt.white)
                date.setPos(CAL2_DATE_INIT_X+114*x, CAL2_DATE_INIT_Y+50*y)
                self.days.insert(y*7+x, date)

        self.curCal2X = 0
        self.curCal2Y = 0
        self.updateCalendar()

    def updateCalPos(self):
        self.calImg.setPos(CAL2_IMG_INIT_X + self.curCal2X, CAL2_IMG_INIT_Y + self.curCal2Y)
        self.monthTxt.setPos(CAL2_MON_INIT_X + self.curCal2X, CAL2_MON_INIT_Y + self.curCal2Y)
        self.yearTxt.setPos(CAL2_YEAR_INIT_X + self.curCal2X, CAL2_YEAR_INIT_Y + self.curCal2Y)
        for y in range(6):
            for x in range(7):
                self.days[y*7+x].setPos(CAL2_DATE_INIT_X + self.curCal2X + 114*x, 
                    CAL2_DATE_INIT_Y + self.curCalY + 50*y)
                if self.todayX == x and self.todayY == y:
                    self.todayLine.setPos(CAL2_DATE_INIT_X + + self.curCal2X + 114*x, 
                        CAL2_DATE_INIT_Y + CAL2_DATE_BAR_OFFSET_Y + self.curCalY + 50*y)

    def updateCalendar(self): 
        now = datetime.datetime.now()
        calendar.setfirstweekday(6)
        cal = calendar.monthcalendar(now.year, now.month)

        self.monthTxt.setPlainText(monthString[now.month-1]) 
        self.yearTxt.setPlainText(str(now.year)) 

        for y in range(6):
            if y < len(cal):
                week = cal[y]  # get a week data
            else:
                week = [0,0,0,0,0,0,0]
            for x in range(0,7):
                if(week[x] == 0): # not this month
                    self.days[y*7+x].setPlainText("")
                else:
                    self.days[y*7+x].setPlainText(str(week[x]))

                if(week[x]==now.day):
                    self.days[y*7+x].setDefaultTextColor(QColor(55,255,255))
                    self.todayX = x
                    self.todayY = y
                    self.todayLine.setPos(40+114*x, 198+50*y)

                elif(x==0):
                    self.days[y*7+x].setDefaultTextColor(Qt.red)
                else:
                    self.days[y*7+x].setDefaultTextColor(QColor(159,201,255))

    @pyqtSlot()
    def loadCapImage(self):
        if self.ImageFromCam == True:
            pixmap = QPixmap.fromImage(self.cam.qImg)
            self.curImage.setPixmap(pixmap)
 
            w = pixmap.size().width()
            h = pixmap.size().height()

            if w == SCREEN_WIDTH:
                dif = int((SCREEN_HEIGHT - h)/2)
                self.curImage.setPos(0,dif)
            else :
                dif = int((SCREEN_WIDTH - w)/2)
                self.curImage.setPos(dif,0)


    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_M:
            self.front_mode += 1
            if self.front_mode > 2:
                self.front_mode = 0
            if self.front_mode == 0:
                self.setScene(self.scene1)
                self.cal_item.show()
                self.clk_item.show()
            elif self.front_mode == 1:
                self.cal_item.hide()
            elif self.front_mode == 2:
                self.clk_item.hide()

        elif e.key() == Qt.Key_N:
            self.back_mode += 1            
            if self.back_mode > 1:
                self.back_mode = 0

            if self.back_mode == 0:
                self.ImageFromCam = False
                self.setScene(self.scene1)
                self.loadImage()
            elif self.back_mode == 1:
                self.ImageFromCam = True

        elif e.key() == Qt.Key_1:
            self.front_mode = 0
            self.back_mode = 0
            self.ImageFromCam = False
            self.setScene(self.scene1)
            self.cal_item.show()
            self.clk_item.show()
        elif e.key() == Qt.Key_2:
            self.ImageFromCam = False
            self.setScene(self.scene2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CalendarView()
    w.show()
    sys.exit(app.exec_())
