# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 12:28:59 2012

@author: bastien
"""
import sys
from PyQt4 import QtCore, QtGui, uic
import wiiboard

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        # load the UI
        self.ui = uic.loadUi("simple_scale.ui", self)
        
        # customize the UI
        self.initUI()

        # init internal variables
        self.initData()
        
        # connect slots
        self.connectSlots()
    
    def initUI(self):
        self.spw = SimplePlotWidget(-5, 100, True)
        self.ui.verticalLayout_2.addWidget(self.spw)
        
        self.spw_colourful = SimplePlotWidget(-5.5, 50, True)
        self.spw_colourful.data = [[], [], [], []]
        self.spw_colourful.color_array = [QtCore.Qt.blue, QtCore.Qt.red,
                                          QtCore.Qt.yellow, QtCore.Qt.green]
        self.ui.verticalLayout_2.addWidget(self.spw_colourful)
        
        hbox_layout = QtGui.QHBoxLayout()
        self.xpw = SimplePlotWidget(-210, 210, True)
        hbox_layout.addWidget(self.xpw)
        self.ypw = SimplePlotWidget(-120, 120, True)
        hbox_layout.addWidget(self.ypw)
        
        self.ui.verticalLayout_2.addLayout(hbox_layout)

        hbox_layout = QtGui.QHBoxLayout()
        self.ppw = PathPlotWidget(-1, 1, -1, 1, True)
        hbox_layout.addWidget(self.ppw)
        self.ppw.setSizePolicy(QtGui.QSizePolicy.Preferred,
                           QtGui.QSizePolicy.Expanding)
        self.ppw2 = PathPlotWidget(-1, 1, -1, 1, True)
        hbox_layout.addWidget(self.ppw2)
        self.ppw2.setSizePolicy(QtGui.QSizePolicy.Preferred,
                           QtGui.QSizePolicy.Expanding)

        self.ui.verticalLayout_2.addLayout(hbox_layout)
        
        for child in [self.spw, self.spw_colourful, 
                      self.xpw, self.ypw]:
                child.setMinimumSize(100, 100)
                
    def initData(self):
        self.wii_board = wiiboard.Wiiboard()
        
        self.calibration_mass = 80
        
        self.timer = QtCore.QBasicTimer()
        interval = 200
        bin_count = 50
        self.ts_mass = TimeSeries(interval, bin_count)
        self.ts_tl = TimeSeries(interval, bin_count)
        self.ts_tr = TimeSeries(interval, bin_count)
        self.ts_bl = TimeSeries(interval, bin_count)
        self.ts_br = TimeSeries(interval, bin_count)
        
        self.ts_x = TimeSeries(interval, bin_count)
        self.ts_y = TimeSeries(interval, bin_count)
        self.ts_x1 = TimeSeries(50, 200)
        self.ts_y1 = TimeSeries(50, 200)
        
    def connectSlots(self):
        QtCore.QObject.connect(self.ui.pushButton,
                               QtCore.SIGNAL('clicked()'), 
                               self.discoverWiiBoards)

        QtCore.QObject.connect(self.ui.pushButton_2,
                               QtCore.SIGNAL('clicked()'),
                                self.connectWiiBoard)
        
        QtCore.QObject.connect(self.ui.pushButton_3,
                               QtCore.SIGNAL('clicked()'),
                                self.disconnectWiiBoard)
                                
        QtCore.QObject.connect(self.ui.pushButton_4,
                               QtCore.SIGNAL('clicked()'),
                                self.calibrateScale)
                                
    def discoverWiiBoards(self):
        discovery = self.wii_board.discover()
        if discovery is not None:
            self.ui.lineEdit.setText(str(discovery))
        
    def connectWiiBoard(self):
        if not self.wii_board.isConnected():
            self.wii_board.connect(str(self.ui.lineEdit.text()))
            self.wii_board.setLight(False)
            self.wii_board.queue_logging = True
            self.timer.start(250, self)
        
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            last_event = self.wii_board.lastEvent
            M = last_event.totalWeight
            TR = last_event.topRight
            TL = last_event.topLeft
            BR = last_event.bottomRight
            BL = last_event.bottomLeft
            
            self.ui.lcdNumber.display(float(M))
            self.ui.lcdNumber_2.display((TL))
            self.ui.lcdNumber_3.display((TR))
            self.ui.lcdNumber_4.display((BL))
            self.ui.lcdNumber_5.display((BR))
            
            
            
            data = self.wii_board.getQueuedEvents()
            
            for item in data:                
                self.ts_mass.add_data_point(item.time_stamp / 1000, item.totalWeight)
                self.ts_bl.add_data_point(item.time_stamp / 1000, item.bottomLeft)
                self.ts_br.add_data_point(item.time_stamp / 1000, item.bottomRight)
                self.ts_tl.add_data_point(item.time_stamp / 1000, item.topLeft)
                self.ts_tr.add_data_point(item.time_stamp / 1000, item.topRight)
                coords = item.spatial_coords(self.calibration_mass)
                self.ts_x.add_data_point(item.time_stamp / 1000, 
                                         coords[0])
                self.ts_y.add_data_point(item.time_stamp / 1000,
                                         coords[1])
                self.ts_x1.add_data_point(item.time_stamp / 1000, 
                                         coords[0])
                self.ts_y1.add_data_point(item.time_stamp / 1000,
                                         coords[1])
                                         
            self.spw.data[0] = self.ts_mass.get_values()
            self.spw.update()
            
            self.spw_colourful.data = [self.ts_bl.get_values(), 
                                       self.ts_br.get_values(),
                                        self.ts_tl.get_values(),
                                        self.ts_tr.get_values()]
            
            self.spw_colourful.update()
            
            
            self.xpw.data[0] = self.ts_x.get_values()
            self.xpw.update()            
            
            self.ypw.data[0] = self.ts_y.get_values()
            self.ypw.update()
            
            points = []
            for i, x in enumerate(self.xpw.data[0]):
                points.append((x, self.ypw.data[0][i]))
            self.ppw.data = points
            self.ppw.update()
            
            points2 = []
            y_values = self.ts_y1.get_values()
            for i, x in enumerate(self.ts_x1.get_values()):
                points2.append((x, y_values[i]))
            self.ppw2.data = points2
            self.ppw2.update()
            
    def disconnectWiiBoard(self):
        if self.wii_board.isConnected():
            self.wii_board.disconnect()
            self.timer.stop()
    
    def calibrateScale(self):
        self.calibration_mass = self.wii_board.lastEvent.totalWeight

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


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
