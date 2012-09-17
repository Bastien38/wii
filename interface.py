# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 21:45:26 2012

@author: bastien
"""
import random
import sys, time, bluetooth
import wiiboard

from PyQt4 import QtCore, QtGui, uic

class MyWidget(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        #somewhere in constructor:
        self.ui = uic.loadUi("interface.ui")
        self.ui.show()
        #change color of frame
        self.ui.frame.setStyleSheet("QWidget { background-color: %s }" %  
            "Red")
        self.timer = QtCore.QBasicTimer()
        self.render_widget = RenderWidget()
        self.ui.horizontalLayout_4.addWidget(self.render_widget)
        #connect slots
        QtCore.QObject.connect(self.ui.pushButton,
                               QtCore.SIGNAL('clicked()'), 
                               self.connect_board)
        QtCore.QObject.connect(self.ui.pushButton_2,
                               QtCore.SIGNAL('clicked()'), 
                               self.launch_acquisition)
        
    def connect_board(self):
        board = wiiboard.Wiiboard()
        try:        
            board.connect("00:22:4C:55:A2:32") #The wii board must be in sync mode at this time
            time.sleep(0.1)
            board.setLight(True)
            self.ui.frame.setStyleSheet("QWidget { background-color: %s }" %  
            "Green")
            self.board = board
            self.ui.textEdit.append(time.ctime() + " Connection successful")
            
        except bluetooth.btcommon.BluetoothError:
            self.ui.textEdit.append(time.ctime() + " Connection failed")
            
    def launch_acquisition(self):
        self.ui.textEdit.append(time.ctime() + " Starting acquisition")
        self.ui.textEdit.append(time.ctime() + " " + str(self.board.lastEvent.totalWeight))
        self.render_widget.update()
        self.timer.start(1, self)
        
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.render_widget.points.append(self.get_current_position())
        else:
            QtGui.QFrame.timerEvent(self, event)    
    
    def get_current_position(self):
        self.board.lastEvent
        #TODO
        M=event.mass.totalWeight
                    TR=event.mass.topRight
                    TL=event.mass.topLeft
                    BR=event.mass.bottomRight
                    BL=event.mass.bottomLeft
                    R=TR+BR
                    L=TL+BL
                    T=TR+TL
                    B=BR+BL
class RenderWidget(QtGui.QWidget):
    def __init__(self):
        super(RenderWidget, self).__init__()
        
        self.initUI()
        
        self.points = [(150, 150)]        
        
    def initUI(self):      

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Points')
        self.show()
        
    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()
        
    def drawPoints(self, qp):
      
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)

        qp.setPen(pen)

        size = self.size()
        
        for point in self.points:
            #x = random.randint(1, size.width()-1)
            #y = random.randint(1, size.height()-1)
            x,y = point
            qp.drawPoint(x, y)         
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyWidget()
    sys.exit(app.exec_())