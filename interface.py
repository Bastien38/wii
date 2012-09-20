# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 21:45:26 2012

@author: bastien
"""

import sys, time, bluetooth
import wiiboard
import numpy as np

from PyQt4 import QtCore, QtGui, uic

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # load the UI
        self.ui = uic.loadUi("interface.ui", self)
        
        # customize the UI
        self.initUI()
        
        #connect slots
        self.connectSlots()
        
    def connectSlots(self):
        QtCore.QObject.connect(self.ui.pushButton,
                               QtCore.SIGNAL('clicked()'), 
                               self.connectWiiBoard)
        QtCore.QObject.connect(self.ui.pushButton_2,
                               QtCore.SIGNAL('clicked()'), 
                               self.startAcquisition)

    def initUI(self):    
        # add timer to UI
        self.timer = QtCore.QBasicTimer()
        # add render_widget to UI
        self.render_widget = RenderWidget()        
        self.ui.horizontalLayout_4.addWidget(self.render_widget)
        #change color of UI frame to red
        self.ui.frame.setStyleSheet("QWidget { background-color: %s }" %  
            "Red")
        
    def connectWiiBoard(self):
        board = wiiboard.Wiiboard()
        try:        
            #The wii board must be in sync mode at this time
            board.connect("00:22:4C:55:A2:32") 
            time.sleep(0.1)
            board.setLight(True)
            self.ui.frame.setStyleSheet("QWidget { background-color: %s }" %  
            "Green")
            self.board = board
            self.ui.textEdit.append(time.ctime() + " Connection successful")
            
        except bluetooth.btcommon.BluetoothError:
            self.ui.textEdit.append(time.ctime() + " Connection failed")
            
    def startAcquisition(self):
        self.ui.textEdit.append(time.ctime() + " Starting acquisition")
        self.ui.textEdit.append(time.ctime() + " " + str(self.board.lastEvent.totalWeight))
        self.timer.start(1, self)
        self.render_widget.initPoints()        
        self.render_widget.update()
        
        # set acquisition limit 
        self.acquisition_limit = 600
        
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.render_widget.points.append(self.getCurrentPosition())
            self.render_widget.update()
            
            if len(self.render_widget.points) > self.acquisition_limit:
                self.timer.stop()
                self.ui.textEdit.append(time.ctime() + " Stopping acquisition")
                np.save('test.npy', self.render_widget.points)
                
    
    def getCurrentPosition(self):
        """returns center of mass from latest board Wii measurement"""
        last_event = self.board.lastEvent
        M=last_event.totalWeight
        TR=last_event.topRight
        TL=last_event.topLeft
        BR=last_event.bottomRight
        BL=last_event.bottomLeft
        R=TR+BR
        L=TL+BL
        T=TR+TL
        B=BR+BL
        if M>0:
            return (time.time(), 215*(R - L)/M, 117.5*(T - B)/M)
        else:
            return (time.time(), 0,0)
            
class RenderWidget(QtGui.QWidget):
    def __init__(self):
        super(RenderWidget, self).__init__()
        
        self.initUI()
    
        self.initPoints()
    
    def initPoints(self):
        self.points = [(time.time(), 0, 0)]                
    
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
        scale_x = 1.0
        scale_y = 1.0
        for i in range(len(self.points) - 1):
            x_1, y_1 = self.points[i][1:3]
            x_2, y_2 = self.points[i + 1][1:3]
            qp.drawLine(x_1 * scale_x, y_1 * scale_y, 
                        x_2 * scale_x, y_2 * scale_y)         
            
#a=np.load('test.npy');
#plot(a[:,1],a[:,2])            
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())