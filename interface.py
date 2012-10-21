# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 21:45:26 2012

@author: bastien
"""

import sys
import numpy as np
import matplotlib.figure
import matplotlib.backends.backend_qt4agg
from PyQt4 import QtCore, QtGui, uic
import os.path 
from scipy.interpolate import interp1d
from wizard import AcquisitionWizard

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
        # display tab
        # add display_widget to UI
        self.display_widget = DisplayWidget()        
        self.ui.tab.layout().addWidget(self.display_widget)
        
        # analysis tab
        self.analysis_widget = AnalysisWidget()
        self.ui.tab_2.layout().addWidget(self.analysis_widget)

    def initData(self):
        self.wizard = None
        self.current_data = []
        
    def connectSlots(self):
        QtCore.QObject.connect(self.ui.pushButton,
                               QtCore.SIGNAL('clicked()'),
                                self.openAcquisitionWizard)                            
        
        QtCore.QObject.connect(self.ui.pushButton_4,
                               QtCore.SIGNAL('clicked()'),
                                self.loadAcquisitionFileFromDisk)                            
        

    
        
        
    def loadAcquisitionFileFromDisk(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 
                                                     "Charger acquisition",
                                                     filter="Numpy files (*.npy)")

        if os.path.exists(str(filename)): 
            dataAnalyzer = WiiBoardDataAnalyzer(filename)                
            self.current_data = dataAnalyzer            
            self.display_widget.setData(dataAnalyzer)
            self.analysis_widget.setData(dataAnalyzer)
        self.display_widget.redraw()
        self.analysis_widget.redraw()
        self.updateIndicators()

    def updateIndicators(self):
        if self.current_data != []:
            self.ui.lineEdit.setText(str(self.current_data.lengthPath()))
            
    
        
    def openAcquisitionWizard(self):
        if self.wizard == None:
            self.wizard = AcquisitionWizard()
            
            QtCore.QObject.connect(self.wizard,
                               QtCore.SIGNAL('finished(int)'), 
                               self.resetWizard)
                               
            self.wizard.show()
    
    def resetWizard(self, value):
        self.wizard = None

class DisplayWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.initData()

        self.initUI()
    
        
        
    def initUI(self):
        dpi = 100
        self.fig = matplotlib.figure.Figure((4.0, 4.0), dpi)
        self.fig.subplots_adjust(hspace=0.45, wspace=0.3)
        self.canvas = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self)
        
        
        axes_x = self.fig.add_subplot(221)
        axes_y = self.fig.add_subplot(222)
        axes_m = self.fig.add_subplot(223)        
        axes_xy = self.fig.add_subplot(224)
    
        
        self.axes = [axes_x, axes_y, axes_m, axes_xy]        
        
        mpl_toolbar = matplotlib.backends.backend_qt4agg.NavigationToolbar2QTAgg(self.canvas, self)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(mpl_toolbar)
        
        self.setLayout(vbox)
        self.redraw()
        
    def initData(self):
        self.data = []

    def setData(self, data):
        self.data = data

    def redraw(self):
        if self.data != []:        
            t = self.data.t
            x = self.data.x
            y = self.data.y
            m = self.data.m
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
            
            # m data
            self.axes[2].plot(t, m)
            self.axes[2].set_title("mass")            
            
            # xy data
            self.axes[3].plot(x, y, "bo-")
            self.axes[3].set_title("x-y coordinates")
                    
            self.canvas.draw() 
    
    
class AnalysisWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.initData()

        self.initUI()
    
        
        
    def initUI(self):
        dpi = 100
        self.fig = matplotlib.figure.Figure((4.0, 4.0), dpi)
        self.fig.subplots_adjust(hspace=0.45, wspace=0.3)
        self.canvas = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self)
        
        
        axes_x = self.fig.add_subplot(221)
        axes_y = self.fig.add_subplot(222)
        axes_m = self.fig.add_subplot(223)        
        axes_xy = self.fig.add_subplot(224)
    
        
        self.axes = [axes_x, axes_y, axes_m, axes_xy]        
        
        mpl_toolbar = matplotlib.backends.backend_qt4agg.NavigationToolbar2QTAgg(self.canvas, self)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(mpl_toolbar)
        
        self.setLayout(vbox)
        self.redraw()
        
    def initData(self):
        self.data = []

    def setData(self, data):
        self.data = data

    def redraw(self):
        if self.data != []:        
            t = self.data.t
            x = self.data.x
            y = self.data.y
            m = self.data.m
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
            
            # m data
            self.axes[2].plot(t, m)
            self.axes[2].set_title("mass")            
            
            # xy data
            self.axes[3].plot(x, y, "bo-")
            self.axes[3].set_title("x-y coordinates")

#            sampling_freq = 500        
#            (t, x, y) = self.resampleData(sampling_freq)
#            
#            # x fft data
#            self.axes[3].psd(x, NFFT=len(t), pad_to=len(t), Fs=sampling_freq)
#            self.axes[3].set_xlim(0, 5)            
#            self.axes[3].set_title('x displacement')
#            
#            # y fft data
#            self.axes[4].psd(y, NFFT=len(t), pad_to=len(t), Fs=sampling_freq)
#            self.axes[4].set_xlim(0, 5)
#            self.axes[4].set_title('y displacement')
                        
            self.canvas.draw() 
        
    
    def resampleData(self, sampling_freq=100):
        if self.data != []:        
            t = self.data[0]
            x = self.data[1]
            y = self.data[2]
    
            delta_t = t[-1] - t[0]
    
            new_t = np.linspace(0, delta_t, np.ceil(delta_t * sampling_freq))
            def interp(data):
                interpolation = interp1d(t, data, kind='linear', bounds_error=False, fill_value = 0)
                return interpolation(new_t)
            
            new_x = interp(x)
            new_y = interp(y)
        return (new_t, new_x, new_y)

class WiiBoardDataAnalyzer(object):
    def __init__(self, filename):

        # get raw data series        
        raw_data = np.load(str(filename))                
        t = raw_data[:, 0]
        tl = raw_data[:, 1]
        tr = raw_data[:, 2]
        bl = raw_data[:, 3]
        br = raw_data[:, 4]
        m = raw_data[:, 5]
        reference_mass = m.mean()
        R = tr + br
        L = tl + bl
        T = tr + tl
        B = br + bl
        x, y = (215 * (R - L) / reference_mass, 
                         117.5 * (T - B) / reference_mass)
        # interpolate the raw data on uniform scale and store
        dt = t[1:] - t[:-1]
        mean_dt = dt.mean()
        t = np.concatenate((np.array([0.]), np.cumsum(dt)))
        sampled_t = np.linspace(0, t.max(), np.ceil(t.max() / mean_dt))
        self.t = sampled_t
        self.m = interp1d(t, m)(sampled_t)
        self.x = interp1d(t, x)(sampled_t)
        self.y = interp1d(t, y)(sampled_t)
       
    def lengthPath(self):
        dx = self.x[1:] - self.x[:-1]
        dy = self.y[1:] - self.y[:-1]
        dx2 = dx * dx
        dy2 = dy * dy
        return np.sqrt(dx2 + dy2).sum()
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
