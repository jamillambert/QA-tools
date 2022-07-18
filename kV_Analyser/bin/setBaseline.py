#Creates baseline file for the kV dose script
import numpy

SN = 18066528 #(0018, 1000) Device Serial Number 
c0 = r'15/02/2022' #Baseline date
c1 = r'JL' #Baseline set by
c2 = 142 #Orthogonal average pixel value, (whole mean), pps x = 0
c3 = 53 #Left obliques average pixel value in left range
c4 = 12 #Left oblique average pixel value in right range
c5 = 1 #Right oblique average pixel value in left range
c6 = 262 #Right oblique average pixel value in right range
c7 = 1 #Start x for left range
c8 = 80 #End x for left range
c9 = 500 #Start x for right range
c10 = 600 #End x for right range


baselineValueFile = r'baseline.npy'
previousValueFile = r'previous_baseline.npy'
try:    
    baselines = numpy.load(baselineValueFile)
    numpy.save(previousValueFile, baselines)
except:
    print('No previous baseline found')
baselines = numpy.array([c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,SN])
numpy.save(baselineValueFile, baselines)
