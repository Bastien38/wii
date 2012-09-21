# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 10:08:44 2012

@author: FL232714
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 21:45:26 2012

@author: bastien
"""

import sys, time
import random
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
        self.ui.frame.setStyleSheet("QWidget { background-color: %s }" %  
        "Green")

        self.ui.textEdit.append(time.ctime() + " Connection successful")
            
            
    def startAcquisition(self):
        self.ui.textEdit.append(time.ctime() + " Starting acquisition")
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
        return (time.time(), random.randint(0, 300), random.randint(0, 500))
            
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
        
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()
        
    def drawPoints(self, qp):
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        if len(self.points) > 1:
            for i in range(len(self.points) - 1):
                x_1, y_1 = self.points[i][1:3]
                x_2, y_2 = self.points[i + 1][1:3]
                qp.drawLine(x_1, y_1, x_2, y_2)         
                
#a=np.load('test.npy');
#plot(a[:,1],a[:,2])            
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())