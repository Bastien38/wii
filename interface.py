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
from scipy.signal import filtfilt, butter

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        # load the UI
        self.ui = uic.loadUi("interface.ui", self)
        
        # customize the UI
        self.initUI()

        # init class data
        self.initData()
        
        # connect slots
        self.connectSlots()
        
        # maximize window
        self.setWindowState(QtCore.Qt.WindowMaximized)        
       

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

    def initData(self):
        self.acquisition_mode_on = False 
        self.board = wiiboard.Wiiboard()
        self.acquisition_limit = 600
        self.save_filename = "acquisition.npy"
        
    def connectSlots(self):
        QtCore.QObject.connect(self.ui.pushButton,
                               QtCore.SIGNAL('clicked()'), 
                               self.connectWiiBoard)
        QtCore.QObject.connect(self.ui.pushButton_2,
                               QtCore.SIGNAL('clicked()'), 
                               self.toggleAcquisition)
        QtCore.QObject.connect(self.ui.pushButton_3,
                               QtCore.SIGNAL('clicked()'),
                                self.loadLatestAcquisition)
        QtCore.QObject.connect(self.ui.pushButton_4,
                               QtCore.SIGNAL('clicked()'),
                                self.loadAcquisitionFileFromDisk)                            
        QtCore.QObject.connect(self.ui.pushButton_5,
                               QtCore.SIGNAL('clicked()'),
                                self.analysis_widget.smoothData)
        QtCore.QObject.connect(self.ui.pushButton_6,
                               QtCore.SIGNAL('clicked()'),
                                self.saveAcquisitionAs)
        
    def connectWiiBoard(self):
        board = wiiboard.Wiiboard()
        try:
            time.sleep(0.1)
            #The wii board must be in sync mode at this time
            board.connect("00:22:4C:55:A2:32") 
            time.sleep(0.1)            
            board.setLight(True)
            self.ui.frame.setStyleSheet("QWidget { background-color: %s }" %  
            "Green")
            self.logMessage("Connection to Wii board successful")
            self.board = board
        except bluetooth.btcommon.BluetoothError:
            self.logMessage("Connection to Wii board failed")

    def logMessage(self, message, add_timestamp=True):
        if add_timestamp:
            message = time.ctime() + " " + message
        self.ui.textEdit.append(message)
            
    def toggleAcquisition(self):
        if self.acquisition_mode_on:
            self.acquisition_mode_on = False
            self.ui.pushButton_2.setText(u"Lancer l'acquisition")
        else:
            if self.board.status == "Disconnected":
                self.logMessage("Could not start acquisition because Wii board is not connected")
            else:
                self.logMessage("Starting acquisition")
                self.timer.start(1, self)
                self.render_widget.initPoints()        
                self.render_widget.update()
                self.acquisition_mode_on = True
                self.ui.pushButton_2.setText(u"Stopper l'acquisition")
            
        
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.acquisition_mode_on:
                self.render_widget.points.append(self.getCurrentPosition())
                self.render_widget.update()
                
                if len(self.render_widget.points) > self.acquisition_limit:
                    self.timer.stop()
                    self.logMessage("Stopping acquisition")
                    np.save(self.save_filename, self.render_widget.points)
                    self.logMessage("Autosaving acquisition to " + self.save_filename)
            else:
                self.timer.stop()
                self.logMessage("Stopping acquisition")
                
    def getCurrentPosition(self):
        """returns center of mass from latest board Wii measurement"""
        last_event = self.board.lastEvent
        M = last_event.totalWeight
        TR = last_event.topRight
        TL = last_event.topLeft
        BR = last_event.bottomRight
        BL = last_event.bottomLeft
        R = TR + BR
        L = TL + BL
        T = TR + TL
        B = BR + BL
        if M > 0:
            return (time.time(), 215*(R - L)/M, 117.5*(T - B)/M)
        else:
            return (time.time(), 0, 0)
    
    def loadData(self, filename):
        data = np.load(filename)        
        t = data[:, 0]
        dt = t[1:] - t[:-1]
        t = np.concatenate((np.array([0.]), np.cumsum(dt)))
        x = data[:, 1]
        y = data[:, 2]
        return (t, x, y)
        
    def loadLatestAcquisition(self):
        filename = self.save_filename
        self.loadAcquisitionFile(filename)
        
    def loadAcquisitionFileFromDisk(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 
                                                     "Charger acquisition",
                                                     filter="Numpy files (*.npy)")
        self.loadAcquisitionFile(str(filename))
        
    def loadAcquisitionFile(self, filename):
        if os.path.exists(filename): 
            try:
                self.analysis_widget.data = self.loadData(filename)
                self.analysis_widget.redraw()
                self.logMessage("Loaded file " + filename)
            except:
                self.logMessage("Error reading file " + filename)
        else:
            self.logMessage("Could not find file " + filename)
        
    def saveAcquisitionAs(self):
        if not self.acquisition_mode_on and self.render_widget.points != []:
            filename = QtGui.QFileDialog.getSaveFileNameAndFilter(self,
                                                                  "Sauvegarder acquisition",
                                                                  filter="Numpy files (*.npy)")
            np.save(filename, self.render_widget.points)
            self.logMessage("Saving acquisition to " + self.filename)
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
        
        self.initData()

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
        self.redraw()
        
    def initData(self):
        self.data = []

    def redraw(self):
        if self.data != []:        
            t = self.data[0]
            x = self.data[1]
            y = self.data[2]
            for ax in self.axes:        
                ax.clear()  
                ax.grid(True)

            # x data
            self.axes[0].plot(t, x)
            self.axes[0].set_title("x displacement")
            self.axes[0].plot(t, x.min() * np.ones(x.shape))
            self.axes[0].text(t.max(), 1.05 * x.min(), '%d'%int(x.min()),
                ha='center', va='bottom')
            self.axes[0].plot(t, x.max() * np.ones(x.shape))            
            self.axes[0].text(t.max(), 1.05 * x.max(), '%d'%int(x.max()),
                ha='center', va='top')

            # y data
            self.axes[1].plot(t, y)
            self.axes[1].set_title("y displacement")
            self.axes[1].plot(t, y.min() * np.ones(y.shape))
            self.axes[1].text(t.max(), 1.05 * y.min(), '%d'%int(y.min()),
                ha='center', va='bottom')
            self.axes[1].plot(t, y.max() * np.ones(y.shape))            
            self.axes[1].text(t.max(), 1.05 * y.max(), '%d'%int(y.max()),
                ha='center', va='top')
            
            # xy data
            self.axes[2].plot(x, y, "bo-")
            self.axes[2].set_title("x-y coordinates")
        
        self.canvas.draw() 
        
    def smoothData(self):
        def lp_filter(xn):
            b, a = butter(3, 0.05)
            return filtfilt(b, a, xn)
        new_t = lp_filter(self.data[0])
        new_x = lp_filter(self.data[1])
        new_y = lp_filter(self.data[2])
        self.data = (new_t, new_x, new_y)
        self.redraw()
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
