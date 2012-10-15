# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 13:17:46 2012

@author: FL232714
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import lfilter, lfilter_zi, filtfilt, butter
 
def smooth_time_series(t, x, kernel_time_window, sampling_freq):
    """ assuming that x(t) is a time series with unregular sampling,
        calculates a smoothed time series y(new_t) with a regular sampling_freq
        using a kernel with time window kernel_time_window"""
    # calculate input properties
    delta_t = t[-1] - t[0]
    dt_min = min(t[1:] - t[:-1])
    
    # create output variables
    new_t = np.linspace(0, delta_t, np.ceil(delta_t * sampling_freq))
    y = np.zeros(new_t.shape)

    # define interpolation window and variables
    window_length = np.ceil(kernel_time_window / dt_min)
    window = np.hanning(window_length)
    window = window / np.sum(window)

    for (index, t_min) in enumerate(new_t):        
        # interpolating x by step function on grid
        t_max = t_min + kernel_time_window
        interp_grid = linspace(t_min,
                               t_max,
                               window_length)
        index_min = (t >= t_min).nonzero()[0][0]
        index_max = (t <= t_max).nonzero()[0][-1]
        if index_max > index_min + 1:
            interp = interp1d(t[index_min:index_max],
                              x[index_min:index_max], 
                                bounds_error=False,
                                fill_value = 0)
            values = interp(interp_grid)
            
            # multiplying by weighting window        
            y[index] = np.multiply(window, values).sum()
        else:
            y[index] = x[index_min]
            
    return (new_t, y)
    
def interp_time_series(t, x, kernel_time_window, sampling_freq):
    """simple interpolation of time series"""
    # calculate input properties
    delta_t = t[-1] - t[0]
    
    # create output variables
    new_t = np.linspace(0, delta_t, np.ceil(delta_t * sampling_freq))
    interp = interp1d(t, x, kind='linear', bounds_error=False, fill_value = 0)
    return (new_t, interp(new_t))

def lp_filter(xn):
    b, a = butter(3, 0.05)
    return filtfilt(b, a, xn)
    
if __name__ == "__main__":
    data = np.load("acquisition_florian.npy")
    t = data[:, 0]
    dt = t[1:] - t[:-1]
    t = np.concatenate((np.array([0.]), np.cumsum(dt)))
    
    x = data[:, 1]
    y = data[:, 2]
    
    
    dx = x[1:] - x[:-1]
    dy = y[1:] - y[:-1]
    sampling_freq = 100
    kernel_time_window = 20 * min(dt)
    (new_t, new_x) = interp_time_series(t, 
                    x, 
                    kernel_time_window, 
                    sampling_freq)
    
    (new_t, new_y) = interp_time_series(t,
                    y,
                    kernel_time_window,
                    sampling_freq)
    filt_t = lp_filter(new_t)
    filt_x = lp_filter(new_x)
    filt_y = lp_filter(new_y)
 

    clf()
    subplot(2, 2, 1)
    #plot(t, x, 'o-')
    plot(filt_t, filt_x, 'o')
    subplot(2, 2, 2)
    #plot(t, y, 'o-')
    plot(filt_t, filt_y, 'o')
    subplot(2, 1, 2)
#    subplot(2, 1, 1)    
#    plot(x, y, 'o-')
#    subplot(2, 1, 2)
    plot(filt_x, filt_y, 'o-')