# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 11:52:01 2012

@author: bastien
"""
filename = 'Odile_YO.npy'
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
    if (dev > 1) & (i1 <> 0) & (i1 <> size(ss) -1):
        m[i1] = 0.5 * (m[i1+1] + m[i1-1])
        x[i1] = 0.5 * (x[i1+1] + x[i1-1])
        y[i1] = 0.5 * (y[i1+1] + y[i1-1])

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

#figure()    
[Y_fft,f_fft]=fonct_fft(t,x-mean(x))
semilogx(f_fft,abs(Y_fft))
semilogx([0.5,0.5],[0,max(abs(Y_fft[1:-1]))],'r')
semilogx([2,2],[0,max(abs(Y_fft[1:-1]))],'r')
#xlim(0.01,20)
#title(u"FFT déplacement X")            
#xlabel(u"Fréquence (Hz)")
EX1 = sum(abs(Y_fft[(f_fft>0.01) & (f_fft<0.5)]**2))
EX2 = sum(abs(Y_fft[(f_fft>0.5) & (f_fft<2)]**2))
EX3 = sum(abs(Y_fft[f_fft>2]**2))
#print "++++++++++++++++++++++++++++++++++++++++"
#print "dep X"
#print "bande 1 = " + str(EX1/(EX1+EX2+EX3)*100)
#print "bande 2 = " + str(EX2/(EX1+EX2+EX3)*100)
#print "bande 3 = " + str(EX3/(EX1+EX2+EX3)*100)


#figure()    
[Y_fft,f_fft]=fonct_fft(t,y-mean(y))
#semilogx(f_fft,abs(Y_fft))
#semilogx([0.5,0.5],[0,max(abs(Y_fft[1:-1]))],'r')
#semilogx([2,2],[0,max(abs(Y_fft[1:-1]))],'r')
#xlim(0.01,20)
#title(u"FFT déplacement Y")            
#xlabel(u"Fréquence (Hz)")
EY1 = sum(abs(Y_fft[(f_fft>0.01) & (f_fft<0.5)]**2))
EY2 = sum(abs(Y_fft[(f_fft>0.5) & (f_fft<2)]**2))
EY3 = sum(abs(Y_fft[f_fft>2]**2))
#print "++++++++++++++++++++++++++++++++++++++++"
#print "dep Y"
#print "bande 1 = " + str(EY1/(EY1+EY2+EY3)*100)
#print "bande 2 = " + str(EY2/(EY1+EY2+EY3)*100)
#print "bande 3 = " + str(EY3/(EY1+EY2+EY3)*100)

dx = x[1:] - x[:-1]
dy = y[1:] - y[:-1]
dx2 = dx * dx
dy2 = dy * dy
L = np.sqrt(dx2 + dy2).sum()

dt = t[1:] - t[:-1]
vitesse_inst = np.sqrt((dx2 + dy2) / dt)

#print "++++++++++++++++++++++++++++++++++++++++"
#print 'Longueur = ' + str(L)

points=np.vstack((x,y)).transpose()
pos = points.mean(axis=0)
cov = np.cov(points, rowvar=False)

def eigsorted(cov):
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    return vals[order], vecs[:,order]

            
vals, vecs = eigsorted(cov)
theta = np.degrees(np.arctan2(*vecs[:,0][::-1]))
            
# Width and height are "full" widths, not radius
width, height = 2 * 1.8 * np.sqrt(vals)

#print 'theta =' + str(-theta+90) + '°'
##print 'largeur = ' + str(height) + ' mm' #attention c'est inversé, c'est bien le nom qui compte
##print 'hauteur = ' + str(width) + ' mm'
#print 'aire = ' + str(np.pi * width * height) + ' mm²'
#print 'largeur / hauteur =' + str(height/width) 
#print 'LFS = ' + str(L / (np.pi * width * height)) + ' mm^(⁻1)'
##print 'vitesse moyenne = ' +  str(mean(vitesse_inst)) + ' mm/s'
##print 'variance vitesse = ' +  str(var(vitesse_inst)) + ' mm/s'

print filename
print 'dep X'
print "bande 1 = " + format(EX1/(EX1+EX2+EX3)*100,'10.2f') +' %'
print "bande 2 = " + format(EX2/(EX1+EX2+EX3)*100,'10.2f') +' %'
print "bande 3 = " + format(EX3/(EX1+EX2+EX3)*100,'10.2f') +' %'
print 'depY'
print "bande 1 = " + format(EY1/(EY1+EY2+EY3)*100,'10.2f') +' %'
print "bande 2 = " + format(EY2/(EY1+EY2+EY3)*100,'10.2f') +' %'
print "bande 3 = " + format(EY3/(EY1+EY2+EY3)*100,'10.2f') +' %'
print 'Longueur = ' + format(L,'1.2f') + ' mm'
print 'theta = ' + format(-theta+90,'1.2f') + '°'
print 'aire = ' + format(np.pi * width * height,'1.2f') + ' mm²'
print 'largeur / hauteur = ' + format(height/width,'1.2f') 
print 'LFS = ' + format(L / (np.pi * width * height),'1.2f') + ' mm^(⁻1)'

#figure()
#subplot(211)
#plot(t-t[0],y)
#subplot(212)
#plt.specgram(y,scale_by_freq=True, NFFT=300,Fs=1/(t[1]-t[0]),pad_to=3000, noverlap=299,xextent=(0,t[-1]-t[0]),interpolation='nearest', cmap='jet',window=window_hanning)#,pad_to=1000
#plt.xlabel('Temps (s)')
#plt.ylabel(u'Fréquence (Hz)')
#ylim(0.5,2)
#colorbar()
#clim(-20,20)

#Papa
#YO
#Longueur = 821.285291009
#theta =-18.2467560453°
#aire = 381.92238304 mm²


#YF
#Longueur = 863.67586318
#theta =18.8974620005°
#aire = 709.175630899 mm²

#Bastien 
#YO
#Longueur = 891.835354464
#theta =0.729289333569°
#aire = 114.227874885 mm²

#YF
#Longueur = 958.578095523
#theta =2.31526216997°
#aire = 282.251863273 mm²

#YF2
#Longueur = 627.701259991
#theta =2.54361737685°
#aire = 384.431240132 mm²

#YO2
#Longueur = 842.841863242
#theta =0.46635252762°
#aire = 67.9949729379 mm²

#YO2A
#Longueur = 894.369106086
#theta =9.86614130833°
#aire = 89.9064780483 mm²

#Alix
#YO
#Longueur = 985.339003192
#theta =-12.7818482687°
#aire = 251.466051877 mm²

#YOA
#Longueur = 982.476439882
#theta =-17.395600066°
#aire = 155.695655952 mm²

#YF
#Longueur = 1055.92720184
#theta =-3.80863800171°
#aire = 205.31958742 mm²

#MarionYO.npy
#dep X
#bande 1 =      93.19 %
#bande 2 =       5.30 %
#bande 3 =       1.51 %
#depY
#bande 1 =      92.89 %
#bande 2 =       6.61 %
#bande 3 =       0.50 %
#Longueur = 1046.74 mm
#theta = 20.81°
#aire = 185.95 mm²
#largeur / hauteur = 0.49
#LFS = 5.63 mm^(⁻1)

#MarionYF.npy
#dep X
#bande 1 =      73.21 %
#bande 2 =      23.90 %
#bande 3 =       2.89 %
#depY
#bande 1 =      95.09 %
#bande 2 =       4.10 %
#bande 3 =       0.81 %
#Longueur = 1112.54 mm
#theta = 2.37°
#aire = 410.39 mm²
#largeur / hauteur = 0.20
#LFS = 2.71 mm^(⁻1)

#MarionYOA.npy
#dep X
#bande 1 =      50.63 %
#bande 2 =      44.12 %
#bande 3 =       5.24 %
#depY
#bande 1 =      89.99 %
#bande 2 =       8.95 %
#bande 3 =       1.07 %
#Longueur = 1054.72 mm
#theta = 5.61°
#aire = 114.47 mm²
#largeur / hauteur = 0.28
#LFS = 9.21 mm^(⁻1)