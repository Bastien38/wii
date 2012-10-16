# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 20:05:24 2012

@author: bastien
"""
import sys
from PyQt4 import QtCore, QtGui, uic
import wiiboard

class AcquisitionWizard(QtGui.QWizard):
    def __init__(self):
        QtGui.QWizard.__init__(self)
        
        # load the UI
        self.ui = uic.loadUi("acquisition_wizard.ui", self)

        # init data
        self.initData()
        
        # init UI
        self.initUI()        
        
        # init internals of wizard
        self.initInternals()
        
        # init slots
        self.connectSlots()
        
    def initData(self):
        self.wii_board = wiiboard.Wiiboard()
        self.reference_mass = 0
        self.mass_timer = QtCore.QBasicTimer()
        self.display_timer = QtCore.QBasicTimer()
        self.time_out = 100
        self.ts_x = TimeSeries(50, 200)
        self.ts_y = TimeSeries(50, 200)
        self.acquisition_mode = False
        self.acquisition_start = None
        self.acquisition_data = None
        
    def initUI(self):
        x_y_layout = QtGui.QHBoxLayout()        
        self.x_plot = SimplePlotWidget(-250, 250)
        self.y_plot = SimplePlotWidget(-200, 200)
        x_y_layout.addWidget(self.x_plot)        
        x_y_layout.addWidget(self.y_plot)
        self.ui.wizardPage3.layout().addLayout(x_y_layout)
        self.x_y_plot = PathPlotWidget(-250, 250, -200, 200)
        self.ui.wizardPage3.layout().addWidget(self.x_y_plot)
        for child in [self.x_plot, self.y_plot, 
                      self.x_y_plot]:
                child.setMinimumSize(100, 100)
                
    def initInternals(self):
        def wizardPage1Validation():
            if self.wii_board.isConnected():
                self.mass_timer.start(self.time_out, self)
                return True
            else:
                return False
        self.ui.wizardPage1.isComplete = wizardPage1Validation

        def wizardPage2Validation():
            if self.reference_mass !=0:
                self.display_timer.start(self.time_out, self)
                self.wii_board.queue_logging = True
                return True
            else:
                return False
        self.ui.wizardPage2.isComplete = wizardPage2Validation
        
    def connectSlots(self):
        QtCore.QObject.connect(self.ui.pushButton,
                               QtCore.SIGNAL('clicked()'), 
                               self.connectWiiBoard)
        QtCore.QObject.connect(self.ui.pushButton_2,
                               QtCore.SIGNAL('clicked()'), 
                               self.updateMassFromMeasures)
                               
        QtCore.QObject.connect(self.ui.pushButton_3,
                               QtCore.SIGNAL('clicked()'), 
                               self.startAcquisition)
                               
    def startAcquisition(self):
        self.acquisition_mode = True
        self.acquisition_start = 0
        
    def connectWiiBoard(self):
        discovery = self.wii_board.discover()
        if discovery is not None:
            if not self.wii_board.isConnected():
                self.wii_board.connect(discovery)
                self.wii_board.setLight(False)
                self.ui.lineEdit_2.setText(u"Connecté")
                QtCore.QObject.emit(self.ui.wizardPage1,
                            QtCore.SIGNAL("completeChanged()"))
                
                
    def timerEvent(self, event):
        if event.timerId() == self.mass_timer.timerId():
            self.ui.lcdNumber.display(self.wii_board.lastEvent.totalWeight)

        if event.timerId() == self.display_timer.timerId():
            data = self.wii_board.getQueuedEvents()
            
            for item in data:
                if self.acquisition_mode:
                    
                coords = item.spatial_coords(self.reference_mass)
                self.ts_x.add_data_point(item.time_stamp / 1000, 
                                         coords[0])
                self.ts_y.add_data_point(item.time_stamp / 1000,
                                         coords[1])
    
            self.x_plot.data[0] = self.ts_x.get_values()
            self.x_plot.update()            
            
            self.y_plot.data[0] = self.ts_y.get_values()
            self.y_plot.update()
            
            points = []
            for i, x in enumerate(self.x_plot.data[0]):
                points.append((x, self.y_plot.data[0][i]))
            self.x_y_plot.data = points
            self.x_y_plot.update()
            
    def updateMassFromMeasures(self):
        current_weight = self.wii_board.lastEvent.totalWeight
        self.ui.lineEdit.setText(str(current_weight))
        self.reference_mass = current_weight
        QtCore.QObject.emit(self.ui.wizardPage2,
                            QtCore.SIGNAL("completeChanged()"))
    
class SimplePlotWidget(QtGui.QWidget):
    def __init__(self, min_y, max_y, autoscale = False):
        QtGui.QWidget.__init__(self)
        self.min_y = min_y
        self.max_y = max_y
        self.data = [[]]
        self.color_array = [QtCore.Qt.black]
        self.autoscale = autoscale

        
    def paintSingleData(self, qp, size, color, data):
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        last_xy = None
        for ind, point in enumerate(data):
            cur_xy = (size.width() * ind / len(data), 
                      size.height() * (self.max_y - point) / (self.max_y - self.min_y))
            if last_xy != None:
                qp.drawLine(last_xy[0], last_xy[1], cur_xy[0], cur_xy[1])
            last_xy = cur_xy
            
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        size = self.size()        
        if self.autoscale:
            all_values = [item for sublist in self.data for item in sublist]
            if len(all_values) != 0:
                self.min_y = min(all_values)
                self.max_y = max(all_values)
                if self.min_y == self.max_y:
                    self.min_y -= 1
                    self.max_y += 1
        for ind, val in enumerate(self.data):
            self.paintSingleData(qp, size, self.color_array[ind], val) 
        qp.drawText(self.rect(), 
                    QtCore.Qt.AlignTop, 
                    "min=%.2f max=%.2f delta=%.2f" % (self.min_y, 
                                                      self.max_y, 
                                                      self.max_y - self.min_y))
        qp.end()
      
class TimeSeries(object):
    def __init__(self, sampling_interval, bin_count):
        self.sampling_interval = sampling_interval
        self.bin_count = bin_count
        self.data = [(0, 0)] * bin_count
        self.last_bin = None
    
    def add_data_point(self, time, value):
        bin = int(time / self.sampling_interval)
        if self.last_bin == None:
            self.last_bin = bin

        array_index = 0
        if bin > self.last_bin:
            for i in range(bin - self.last_bin):
                self.data.append((0, 0))
            array_index = len(self.data) - 1
        else:
            array_index = len(self.data) - 1 - (self.last_bin - bin)
        
        if array_index >= 0:
            old_tuple = self.data[array_index]
            self.data[array_index] = (old_tuple[0] + value, old_tuple[1] + 1)
        
        if len(self.data) > self.bin_count:
            self.data = self.data[-self.bin_count:]
                            
        self.last_bin = bin
    
    def get_values(self):
        output_values = []
        last_value = None
        for item in self.data:
            if item[1] > 0:
                last_value = item[0] / item[1]
                output_values.append(last_value)
            elif last_value != None:
                output_values.append(last_value)

        return output_values
                
class PathPlotWidget(QtGui.QWidget):
    def __init__(self, min_x, max_x,
                 min_y, max_y, autoscale = False):
        QtGui.QWidget.__init__(self)
        self.min_x = min_x
        self.max_x = max_x        
        self.min_y = min_y
        self.max_y = max_y
        self.data = []
        self.autoscale = autoscale
            
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        size = self.size()        
        if self.autoscale:
            x_values = [item[0] for item in self.data]
            y_values = [item[1] for item in self.data]
            if len(x_values) != 0:
                self.min_x = min(x_values)
                self.max_x = max(x_values)
                
                if self.min_x == self.max_x:
                    self.min_x -= 1
                    self.max_x += 1            
            
                self.min_y = min(y_values)
                self.max_y = max(y_values)

                if self.min_y == self.max_y:
                    self.min_y -= 1
                    self.max_y += 1
                    
            dx = self.max_x - self.min_x
            dy = self.max_y - self.min_y
            aspect_ratio = dy / dx * size.width() / size.height() 
            if aspect_ratio > 1:
                # x sollte kleiner sein
                size = QtCore.QSize(size.width() / aspect_ratio, 
                                    size.height())
            else:
                size = QtCore.QSize(size.width(), 
                                    size.height() * aspect_ratio)
        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        last_xy = None
        for point in self.data:
            cur_xy = (size.width()  * (point[0] - self.min_x) / (self.max_x - self.min_x), 
                      size.height() * (self.max_y - point[1]) / (self.max_y - self.min_y))
            if last_xy != None:
                qp.drawLine(last_xy[0], last_xy[1], cur_xy[0], cur_xy[1])
            last_xy = cur_xy

        qp.drawText(self.rect(), 
                    QtCore.Qt.AlignTop, 
                    "min=(%.2f, %.2f) max=(%.2f, %.2f) delta=(%.2f, %.2f)" % (
                        self.min_x, self.min_y, 
                        self.max_x, self.max_y, 
                        self.max_x - self.min_x, self.max_y - self.min_y))
        qp.end()
        
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    wizard = AcquisitionWizard()
    wizard.show()
    sys.exit(app.exec_())
