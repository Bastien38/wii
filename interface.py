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

try:
    from PyQt4.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QtCore.QString = type("")

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
        self.analysis_widget = AnalysisWidget(self.ui.tab_2.layout())
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
    def __init__(self, layout):
        QtGui.QWidget.__init__(self)
        
        self.children_layout = layout

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
        #TODO
        # list of indicators to be calculated for each acquisition
        indicator_labels = [u"Longueur du statokinésigramme (mm)", 
                            u"Position moyenne selon X (mm)",
                            u"Position moyenne selon Y (mm)",
                            u"Vitesse instantanée moyenne (mm / ms)",
                            u"Vitesse instantanée moyenne selon X (mm / ms)",
                            u"Vitesse instantanée moyenne selon Y (mm / ms)",
                            u""]
                            
        functions = [WiiBoardDataAnalyzer.lengthPath,
                     WiiBoardDataAnalyzer.meanX,
                     WiiBoardDataAnalyzer.meanY,
                     WiiBoardDataAnalyzer.meanSpeed,
                     WiiBoardDataAnalyzer.meanXSpeed,
                     WiiBoardDataAnalyzer.meanYSpeed]
        
        self.child_widgets = []
        for ind, label in enumerate(indicator_labels):
            text_label = QtGui.QLabel(QtCore.QString(label))
            data_label = QtGui.QLineEdit(str(''))
            data_label.setReadOnly(True)
            HBoxLayout = QtGui.QHBoxLayout()
            HBoxLayout.addWidget(text_label)
            HBoxLayout.addWidget(data_label)
            self.child_widgets.append([text_label, 
                                       data_label, 
                                       functions[ind]])
            self.children_layout.addLayout(HBoxLayout)
            
            
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

            for ax in self.axes:        
                ax.clear()  
                ax.grid(True)

#            # x data
#            self.axes[0].hist(x[1:] - x[:-1], 20)
#            self.axes[0].set_title("Histogramme $dx$")
#
#            # y data
#            self.axes[1].hist(y[1:] - y[:-1], 20)
#            self.axes[1].set_title("Histogramme $dy$")
            
            self.axes[0].plot(t, x)
            self.axes[0].set_title(u"déplacement en x")
            self.axes[0].plot(t, x.min() * np.ones(x.shape))
            self.axes[0].text(t.max(), 1.05 * x.min(), '%d'%int(x.min()),
                ha='center', va='bottom')
            self.axes[0].plot(t, x.max() * np.ones(x.shape))            
            self.axes[0].text(t.max(), 1.05 * x.max(), '%d'%int(x.max()),
                ha='center', va='top')

            # y data
            self.axes[1].plot(t, y)
            self.axes[1].set_title(u"déplacement en y")
            self.axes[1].plot(t, y.min() * np.ones(y.shape))
            self.axes[1].text(t.max(), 1.05 * y.min(), '%d'%int(y.min()),
                ha='center', va='bottom')
            self.axes[1].plot(t, y.max() * np.ones(y.shape))            
            self.axes[1].text(t.max(), 1.05 * y.max(), '%d'%int(y.max()),
                ha='center', va='top')
                        
            
            # fft data
            [Y_fft, f_fft] = self.data.fftXY()
            fr, Yfft = self.data.fftXY()
            self.axes[2].semilogx(f_fft[1:-1], abs(Y_fft[1:-1]))
            self.axes[2].set_xlim(0.01,20)
            self.axes[2].semilogx([0.5,0.5],[0,max(abs(Y_fft[1:-1]))],'r')
            self.axes[2].semilogx([2,2],[0,max(abs(Y_fft[1:-1]))],'r')
            self.axes[2].set_title(u"FFT déplacement XY")            
            self.axes[2].set_xlabel(u"Fréquence (Hz)")
            
            # xy ellipse data
            from matplotlib.patches import Ellipse

            def plot_point_cov(points, nstd=2, ax=None, **kwargs):
                """
            Plots an `nstd` sigma ellipse based on the mean and covariance of a point
            "cloud" (points, an Nx2 array).
            
            Parameters
            ----------
            points : An Nx2 array of the data points.
            nstd : The radius of the ellipse in numbers of standard deviations.
            Defaults to 2 standard deviations.
            ax : The axis that the ellipse will be plotted on. Defaults to the
            current axis.
            Additional keyword arguments are pass on to the ellipse patch.
            
            Returns
            -------
            A matplotlib ellipse artist
            """
                pos = points.mean(axis=0)
                cov = np.cov(points, rowvar=False)
                return plot_cov_ellipse(cov, pos, nstd, ax, **kwargs)
            
            def plot_cov_ellipse(cov, pos, nstd=2, ax=None, **kwargs):
                """
            Plots an `nstd` sigma error ellipse based on the specified covariance
            matrix (`cov`). Additional keyword arguments are passed on to the
            ellipse patch artist.
            
            Parameters
            ----------
            cov : The 2x2 covariance matrix to base the ellipse on
            pos : The location of the center of the ellipse. Expects a 2-element
            sequence of [x0, y0].
            nstd : The radius of the ellipse in numbers of standard deviations.
            Defaults to 2 standard deviations.
            ax : The axis that the ellipse will be plotted on. Defaults to the
            current axis.
            Additional keyword arguments are pass on to the ellipse patch.
            
            Returns
            -------
            A matplotlib ellipse artist
            """
                def eigsorted(cov):
                    vals, vecs = np.linalg.eigh(cov)
                    order = vals.argsort()[::-1]
                    return vals[order], vecs[:,order]
        
#                if ax is None:
#                    ax = plt.gca()
            
                vals, vecs = eigsorted(cov)
                theta = np.degrees(np.arctan2(*vecs[:,0][::-1]))
            
                # Width and height are "full" widths, not radius
    
                width, height = 2 * nstd * np.sqrt(vals)
                ellip = Ellipse(xy=pos, width=width, height=height, angle=theta, **kwargs)
#TODO                
                print 'theta =' + str(-theta+90) + '°'
                print 'largeur = ' + str(height) + ' mm'
                print 'hauteur = ' + str(width) + ' mm'
                print 'aire = ' + str(np.pi * width * height) + ' mm²'
                
                
                ax.add_artist(ellip)
                return ellip
            
            points=np.vstack((x,y)).transpose()
            # Plot the raw points...
            x1, y1 = points.T

            #self.axes[3].plot(x1, y1, '.')
            self.axes[3].plot([-102.5,-102.5,-102.5,102.5,102.5,102.5,102.5,-102.5],[-58.75,58.75,58.75,58.75,58.75,-58.75,-58.75,-58.75])            
            self.axes[3].set_xlim(-110,110)
            self.axes[3].set_ylim(-60,60)
            
            plot_point_cov(points, nstd=1.8, alpha=1, color='green', ax=self.axes[3])
            #self.axes[3].plot(x1, y1, 'b.',linewidth=0.2)
#TODO            
#            #nouv Bastien à coder
#            vals, vecs = eigsorted(cov)
#            theta = -np.degrees(np.arctan2(*vecs[:,0][::-1]))+90
#            
#
#            width, height = 2 * 1.8 * np.sqrt(vals) 
#
#         'aire = ' + format(np.pi * width * height,'1.2f') + ' mm²'
#         'largeur / hauteur = ' + format(height/width,'1.2f') 
#         'LFS = ' + format(L / (np.pi * width * height),'1.2f') + ' mm^(⁻1)'
    
#            plt.specgram(delta_depl,scale_by_freq=True, NFFT=100,Fs=1/(t[1]-t[0]),pad_to=300, noverlap=99,xextent=(t[0],t[-1]),interpolation='nearest', cmap='jet',window=window_hanning)#,pad_to=1000
#            plt.xlabel('Temps (s)')
#            plt.ylabel('Fréquence (Hz)')
            
            self.canvas.draw() 
            
            # indicators
            for item in self.child_widgets:
                t, data_label, func = item
                data_label.setText(str('%.1f' % func(self.data)))
                
    
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
        t = raw_data[:, 0]*1e-6         #t in seconds
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
          
        #eliminate incoherent points in the raw signal (if the mass deviates more than 1kg from the mean mass)               
        ss = abs(m - reference_mass)
        for i1,dev in enumerate(ss):
            if (dev > 1) & (i1 <> 0) & (i1 <> np.size(ss) -1):
                m[i1] = 0.5 * (m[i1+1] + m[i1-1])
                x[i1] = 0.5 * (x[i1+1] + x[i1-1])
                y[i1] = 0.5 * (y[i1+1] + y[i1-1])
                       
        # interpolate the raw data on uniform scale and store
        dt = t[1:] - t[:-1]
        mean_dt = dt.mean()
        t = np.concatenate((np.array([0.]), np.cumsum(dt)))
        sampled_t = np.linspace(0, t.max(), np.ceil(t.max() / mean_dt))
        self.dt = mean_dt        
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
    
    def meanSpeed(self):
        dx = self.x[1:] - self.x[:-1]
        dy = self.y[1:] - self.y[:-1]
        dx2 = dx * dx
        dy2 = dy * dy
        return np.sqrt((dx2 + dy2) / self.dt).sum()
    
    def meanXSpeed(self):
        dx = self.x[1:] - self.x[:-1]
        dx2 = dx * dx
        return np.sqrt((dx2) / self.dt).sum()
        
    def meanYSpeed(self):
        dy = self.y[1:] - self.y[:-1]
        dy2 = dy * dy
        return np.sqrt((dy2) / self.dt).sum()
        
    def meanX(self):
        return self.x.mean()
        
    def meanY(self):
        return self.y.mean()
        
    def fftXY(self):
        def fonct_fft(tps,signal):
            Nt = len(tps)
            Te = tps[1] - tps[0]
            fe = 1 / Te
            f0 = fe / Nt   #pour l'abscisse de la fft
                
            Y = np.fft.fft(signal)
            
            N_lim=np.fix(Nt/2)-1
            
            Y_fft=Y[0:N_lim-1]
            f_fft=np.arange(0.,N_lim-1)*f0
            
            return [Y_fft,f_fft]
            
        dx = self.x[1:] - self.x[:-1] #!!!!pourquoi delta???
        dy = self.y[1:] - self.y[:-1]
        dx2 = dx * dx
        dy2 = dy * dy
        delta_xy = np.sqrt(dx2 + dy2)
        
        return fonct_fft(self.t, delta_xy-delta_xy.mean())
        
        

        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
