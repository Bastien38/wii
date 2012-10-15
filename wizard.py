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
        
        # init internals of wizard
        self.initInternals()
        
        # init slots
        self.connectSlots()
        
    def initData(self):
        self.wii_board = wiiboard.Wiiboard()
        self.reference_mass = 0
        
    def initInternals(self):
        def wizardPage1Validation():
            return self.wii_board.isConnected()
        self.ui.wizardPage1.isComplete = wizardPage1Validation

        def wizardPage2Validation():
            return self.reference_mass != 0
        self.ui.wizardPage2.isComplete = wizardPage2Validation
        
    def connectSlots(self):
        QtCore.QObject.connect(self.ui.pushButton,
                               QtCore.SIGNAL('clicked()'), 
                               self.connectWiiBoard)
                
    def connectWiiBoard(self):
        discovery = self.wii_board.discover()
        if discovery is not None:
            if not self.wii_board.isConnected():
                self.wii_board.connect(discovery)
                self.wii_board.setLight(False)
                self.ui.lineEdit_2.setText(u"Connecté")
                QtCore.QObject.emit(self.ui.wizardPage1,
                            QtCore.SIGNAL("completeChanged()"))
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    wizard = AcquisitionWizard()
    wizard.show()
    sys.exit(app.exec_())
