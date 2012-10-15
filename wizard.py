# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 20:05:24 2012

@author: bastien
"""
import sys
from PyQt4 import QtGui, uic

class AcquisitionWizard(QtGui.QWizard):
    def __init__(self):
        QtGui.QWizard.__init__(self)
        
        # load the UI
        self.ui = uic.loadUi("acquisition_wizard.ui", self)
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    wizard = AcquisitionWizard()
    wizard.show()
    sys.exit(app.exec_())
