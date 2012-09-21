# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 21:45:26 2012

@author: bastien
"""

import sys, time, bluetooth
import wiiboard
import numpy as np
import matplotlib.figure
import matplotlib.backends.backend_qt4agg
from PyQt4 import QtCore, QtGui, uic
import os.path 

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
        QtCore.QObject.connect(self.ui.pushButton_3,
                               QtCore.SIGNAL('clicked()'),
                                self.loadLatestAcquisition)

    def initUI(self):    
        # acquisition tab
        # add timer to UI
        self.timer = QtCore.QBasicTimer()
        # add render_widget to UI
        self.render_widget = RenderWidget()        
        self.ui.horizontalLayout_4.addWidget(self.render_widget)
        #change color of UI frame to red
        self.ui.frame.setStyleSheet("QWidget { background-color: %s }" %  
            "Red")
        
        # analysis tab
        self.analysis_widget = AnalysisWidget()
        self.ui.tab_2.layout().addWidget(self.analysis_widget)
        
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
                np.save('acquisition.npy', self.render_widget.points)
                
    
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
    
    def loadLatestAcquisition(self):
        if os.path.exists('acquisition.npy'):
            try:
                data = np.load('acquisition.npy')
                self.analysis_widget.points = [(x[0], x[1], x[2]) for x in data]
                self.analysis_widget.update()
            except:
                print "error reading file"
        else:
            print "could not find acquisition file"
        
            
class RenderWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.initUI()
    
        self.initPoints()
    
    def initPoints(self):
        self.points = []                
    
    def initUI(self): 
        dpi = 100
        matplotlib.figure.Figure()
        fig = matplotlib.figure.Figure((4.0, 4.0), dpi)
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
        self.axes.grid(True)
        x = [point[1] for point in self.points]
        y = [point[2] for point in self.points]
        self.axes.plot(x, y, "o-") 
        self.canvas.draw()    
    
class AnalysisWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.initUI()
    
    def initUI(self):
        dpi = 100
        self.fig = matplotlib.figure.Figure((4.0, 4.0), dpi)
        self.canvas = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self)
        
        axes_x = self.fig.add_subplot(221)
        axes_y = self.fig.add_subplot(222)
        axes_xy = self.fig.add_subplot(212)
    
        self.axes = [axes_x, axes_y, axes_xy]        
        
        mpl_toolbar = matplotlib.backends.backend_qt4agg.NavigationToolbar2QTAgg(self.canvas, self)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(mpl_toolbar)
        
        self.setLayout(vbox)
    
    def paintEvent(self, e):
        for ax in self.axes:        
            ax.clear()  
            ax.grid(True)
        
        self.canvas.draw() 
        
#a=np.load('test.npy');
#plot(a[:,1],a[:,2])            
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
