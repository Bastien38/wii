# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 12:18:46 2012

@author: bastien
"""
import sys
from PyQt4 import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

class DrawingWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.plot = pg.PlotWidget()        
        hbox_layout = QtGui.QHBoxLayout()
        hbox_layout.addWidget(self.plot)
        self.setLayout(hbox_layout)
        
        self.data = np.random.normal(size=(10, 100))
        self.counter = 0
        plot_item = self.plot.getPlotItem()
        self.curve = plot_item.plot()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)
        
    def update(self):
        self.counter = (self.counter + 1) % 10
        self.curve.setData(self.data[self.counter])
        if self.counter == 1:
            self.plot.enableAutoRange('xy', False)
        

        
        
#
#from pyqtgraph.Qt import QtGui, QtCore
#
##QtGui.QApplication.setGraphicsSystem('raster')
#app = QtGui.QApplication([])
##mw = QtGui.QMainWindow()
##mw.resize(800,800)
#
#win = pg.GraphicsWindow(title="Basic plotting examples")
#win.resize(800,600)
#
#p6 = win.addPlot(title="Updating plot")
#curve = p6.plot(pen='y')
#data = np.random.normal(size=(10,1000))
#ptr = 0
#def update():
#    global curve, data, ptr, p6
#    curve.setData(data[ptr%10])
#    if ptr == 0:
#        p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
#    ptr += 1
#timer = QtCore.QTimer()
#timer.timeout.connect(update)
#timer.start(50)
#
#
### Start Qt event loop unless running in interactive mode or using pyside.
#import sys
#if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#    app.exec_()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    dw = DrawingWidget()
    dw.show()
    app.exec_()