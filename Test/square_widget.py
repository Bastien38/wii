# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 11:58:02 2012

@author: bastien
"""

import sys
from PyQt4 import QtCore, QtGui

class CustomWidget(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)

        # Give the frame a border so that we can see it.
        self.setFrameStyle(1)

        layout = QtGui.QVBoxLayout()
        self.label = QtGui.QLabel('Test')
        layout.addWidget(self.label)
        self.setLayout(layout)

    def resizeEvent(self, event):
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        new_size = QtCore.QSize(10, 10)
        new_size.scale(event.size(), QtCore.Qt.KeepAspectRatio)
        self.resize(new_size)

class MainWidget(QtGui.QWidget):
    def __init__(self, parent=None):
       QtGui.QWidget.__init__(self, parent)

       layout = QtGui.QVBoxLayout()
       self.custom_widget = CustomWidget()
       layout.addWidget(self.custom_widget)
       self.setLayout(layout)


app = QtGui.QApplication(sys.argv)
window = MainWidget()
window.show()
sys.exit(app.exec_())
