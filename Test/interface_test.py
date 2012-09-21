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
import matplotlib.figure
import matplotlib.backends.backend_qt4agg

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
        return (time.time(),
                0.4 * np.cos(1.9 * time.time()),
                0.3 * np.sin(0.87 * time.time()))
            
class RenderWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.initUI()
    
        self.initPoints()
    
    def initPoints(self):
        self.points = [(time.time(), 0, 0)]                
    
    def initUI(self): 
        dpi = 100
        matplotlib.figure.Figure()
        fig = matplotlib.figure.Figure((4.0, 3.0), dpi)
        canvas = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg(fig)
        canvas.setParent(self)
        self.canvas = canvas
        self.axes = fig.add_subplot(111)
        mpl_toolbar = matplotlib.backends.backend_qt4agg.NavigationToolbar2QTAgg(canvas, self)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(canvas)
        vbox.addWidget(mpl_toolbar)
        
        self.setLayout(vbox)
        
    def paintEvent(self, e):
        self.axes.clear()        
        x = [point[1] for point in self.points]
        y = [point[2] for point in self.points]
        self.axes.plot(x, y, "o-") 
        self.canvas.draw()
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())