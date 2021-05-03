from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtCore import Qt, QTime, QDateTime, QRectF
from PyQt5.QtGui import QBrush, QFont, QColor
import datetime, calendar
import copy

monthString = ["January", "February", "March", "April","May",
 "June", "July", "August", "September", "October", "November", "December"]
dowString = ["SUN", "MON", "TUE","WED", "THU", "FRI", "SAT"]

class ClockItem(QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        QGraphicsRectItem.__init__(self, parent)
        self.showTime()

    def paint(self, painter, option, widget=None):
        painter.setPen(QColor(12,12,12,150))
        painter.setBrush(QBrush(QColor(12,12,12,150)))
        rect = self.boundingRect()
        painter.drawRoundedRect(rect,10,10)

        rect.setX(rect.x() + 10)
        rect.setY(rect.y() + 10)
        painter.setPen(QColor(230,240,255))
        painter.setFont(QFont("Arial", 60, QFont.Normal))
        painter.drawText(rect, Qt.AlignLeft, self.current_time.toString('hh:mm'))
        rect.setX(rect.x() + 30)
        rect.setY(rect.y() + 90)

        painter.setPen(QColor(200,225,245))
        painter.setFont(QFont("Arial", 20, QFont.Normal))
        painter.drawText(rect, Qt.AlignLeft, self.now.toString('M.d  dddd'))

    def showTime(self): 
        self.current_time = QTime.currentTime()   
        self.now = QDateTime.currentDateTime()
        self.update()

class CalendarItem(QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        QGraphicsRectItem.__init__(self, parent)
        self.update()

    def paint(self, painter, option, widget=None):
        now = datetime.datetime.now()
        calendar.setfirstweekday(6)
        cal = calendar.monthcalendar(now.year, now.month)

        painter.setPen(QColor(12,12,12,150))
        painter.setBrush(QBrush(QColor(12,12,12,150)))
        rect = self.boundingRect()
        rect1 = copy.deepcopy(rect)
        painter.drawRoundedRect(rect,10,10)

        painter.setPen(QColor(210,240,255))
        painter.setFont(QFont("Arial", 18, italic = True))
        rect1.setX(rect.x() + 20)
        rect1.setY(rect.y() + 18)
        painter.drawText(rect1, Qt.AlignLeft, monthString[now.month-1])

        rect1.setX(rect.x() + 314)
        rect1.setY(rect.y() + 20)
        painter.setPen(QColor(97,147,255))
        painter.setFont(QFont("Comic Sans", 13, italic = True))
        painter.drawText(rect1, Qt.AlignLeft, str(now.year))

        painter.setFont(QFont("Verdana", 13, QFont.Normal))
        for i in range(7):
            rect1.setX(rect.x() + 20 + 50*i)
            rect1.setY(rect.y() + 68)
            if(i==0):
                painter.setPen(QColor(240,10,10))
            else:
                painter.setPen(Qt.white)
            painter.drawText(rect1, Qt.AlignLeft, dowString[i])

        painter.setFont(QFont("Verdana", 13, QFont.Normal))
        for y in range(6):
            if y < len(cal):
                week = cal[y]
            else:
                week = [0,0,0,0,0,0,0]
            for x in range(7):

                rect1.setX(rect.x() + 30 + 50*x)
                rect1.setY(rect.y() + 120 + 44*y)
                if(x==0):
                    painter.setPen(QColor(240,10,10))
                else:
                    painter.setPen(Qt.white)
                if(week[x] == 0): # not this month    
                    painter.drawText(rect1, Qt.AlignLeft, "")
                else:
                    painter.drawText(rect1, Qt.AlignLeft, str(week[x]))

                if week[x] == now.day:
                    rect2 = QRectF()
                    rect2.setX(rect1.x()-4)
                    rect2.setY(rect1.y()-4)
                    rect2.setWidth(30)
                    rect2.setHeight(34)
                    painter.setPen(QColor(97,147,255))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawRect(rect2)


    def updateCalendar(self): 
        self.update()    