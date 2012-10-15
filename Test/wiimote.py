# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 18:41:02 2012

@author: bastien
"""

import cwiid
import sys
from PyQt4 import QtGui, QtCore, uic

class MainWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        # load the UI
        self.ui = uic.loadUi("wiimote.ui", self)
        
        # customize the UI
        self.initUI()

        # init internal variables
        self.initData()
        
        # connect slots
        self.connectSlots()
    
    def initUI(self):
        pass

    def initData(self):
        self.timer = QtCore.QBasicTimer()
        
    def connectSlots(self):
        QtCore.QObject.connect(self.ui.pushButton,
                               QtCore.SIGNAL('clicked()'), 
                               self.connectWiimote)
                               
    def connectWiimote(self):
        self.wm = cwiid.Wiimote()
        self.wm.
        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC                                
        self.timer.start(50, self)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            acc = self.wm.state['acc']
            self.ui.lcdNumber.display(int(acc[0]))
            self.ui.lcdNumber_2.display(int(acc[1]))
            self.ui.lcdNumber_3.display(int(acc[2]))

def test():
    import time
    while True:
        for i in [1, 2, 4, 8, 4, 2]:
            wm.led = i
            time.sleep(0.1)
            wm.rumble = (wm.state['acc'][0] < 126)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWidget()
    window.show()
    sys.exit(app.exec_())
