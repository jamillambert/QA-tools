# Analyses Lynx images from the kV Obliques and Orthogonal X-Rays on the ProteusONE
# Required:
#           baseline.npy - baseline values stored in a numpy array file
#           opg files of the lynx images stored in the path specified below
# Options:
#           -d turn on debugging, outputs the quadrant pixel values and region mean values
#
# 29.03.2021 Jamil Lambert
# 14.04.21 v3 JL changed quadrants to determine which source was used
# 13.07.21 v3.1 JL changed output formatting including in history file, added -d debugging option

import sys, os, re
import numpy as np

path = '.\\Measurements\\' #Directory with opg files in it
baselineValueFile = '.\\bin\\baseline_ID18066528.npy' # Baseline values stored in this file (NP10 = 67053, NE22 = 68212, RG2 = 68246, NE22 loan ID = 19260936)
tolerance = 10 # tolerance for pass/fail in %

debug = False
for a in sys.argv:
    if a == '-d':
        debug = True

try:
    historyFile = '.\\bin\\history.npy' # History stored in this file
    tempList = np.load(historyFile)
    kVhistory = tempList.tolist()
except:
    kVhistory = ['{:<22} {:^40} {:^11} {:^11} {:^11} {:^11} {:^11} {:^11} {:>11} {:>11} {:>11} {:>11}'.format('Analysis Date', 'file', 'source', 'BL', 'BR', 'TL', 'TR', 'CTR', 'Dose diff', 'whole mean', 'left mean', 'right mean')]

try:    
    baselines = np.load(baselineValueFile)
    c0 = baselines[0] #Baseline date
    c1 = baselines[1] #Baseline set by
    c2 = float(baselines[2]) #Orthogonal average pixel value, pps x = 0
    c3 = float(baselines[3]) #Left obliques average pixel value in left range
    c4 = float(baselines[4]) #Left oblique average pixel value in right range
    c5 = float(baselines[5]) #Right oblique average pixel value in left range
    c6 = float(baselines[6]) #Right oblique average pixel value in right range
    c7 = int(baselines[7]) #Start x for left range
    c8 = int(baselines[8]) #End x for left range
    c9 = int(baselines[9]) #Start x for right range
    c10 = int(baselines[10]) #End x for right range
except:
    print('Baseline file: ' + baselineValueFile + ' could not be loaded.  Script exiting')
    exit(1)
fileList = [f for f in os.listdir(path) if f.endswith(".opg")]
xraySource1 = 'None'
xraySource2 = 'None'
doseDiff1 = 0
doseDiff2 = 0
maxDiff = 0
maxDiffSource = 'None'
if len(fileList) < 1:
    print('No measurement files found\n\nPrevious measurements, which the script has already been run on, are in .\\_old_measurements \nMove back into the .\\Measurements folder if you wish to re run the script on them\n')
    exit(1)
if debug:
    print('{:^30} {:^11} {:^11} {:^11} {:^11} {:^11} {:^11} {:>11} {:>11} {:>11} {:>11}'.format('file','source', 'BL', 'BR', 'TL', 'TR', 'CTR', 'Dose diff', 'whole mean', 'left mean', 'right mean'))
else:
    print('{:^22}\t{:^9}\t{:^14}'.format('file', 'source', 'difference (%)'))
for fileName in fileList:
    filePath = path + fileName
    pixelData = np.empty(shape=(600,600))
    with open(filePath) as opgFile:
        for i, line in enumerate(opgFile):
            if i == 26 and not line.startswith("<asciibody>"):
                print('format missmatch in opg file, line 27 =\"' + line + '\" expected \"<asciibody>\"')
            elif i > 30 and i < 631: # lines 31 to 631 contain the pixel data
                newLine = [p for p in re.split("\s|,|;", line) if p]
                pixelData[i-31]=np.array(newLine[1:]) # the first entry on the line is the y position and needs to be removed
    wholeArray = np.array(pixelData).astype(float)
    if int(fileName[-7:-4]) == 180: #If taken in Lynx2D the images are rotated 180 compared to myQA, the opg file can be renamed from _i_000.opg to _i_180.opg and the below will correct for the rotation
        TL = np.sum(wholeArray[0:100, 0:100])
        BL = np.sum(wholeArray[500:600, 0:100])
        TR = np.sum(wholeArray[0:100, 500:600])    
        BR = np.sum(wholeArray[500:600, 500:600])
        startL = c7 - 1
        endL = c8
        startR = c9 - 1
        endR = c10
    else:   
        TL = np.sum(wholeArray[500:600, 500:600])
        BL = np.sum(wholeArray[0:100, 500:600])
        TR = np.sum(wholeArray[500:600, 0:100])
        BR = np.sum(wholeArray[0:100, 0:100])
        startL = 600 - c8
        endL = 600 - c7 + 1
        startR = 600 - c10
        endR = 600 - c9 + 1   
    CTR = np.sum(wholeArray[150:450, 150:450])
    total = np.sum(wholeArray)
    leftArray = np.array(wholeArray[:, startL:endL])
    rightArray = np.array(wholeArray[:, startR:endR])
    wholeMean = np.mean(wholeArray)
    leftMean = np.mean(leftArray)
    rightMean = np.mean(rightArray)

    if TL > 500000 and BR > 500000:
        xraySource1 = 'Orthogonal'
        doseDiff1 = (wholeMean - c2) / c2 * 100
        xraySource2 = 'None'
        doseDiff2 = 0
    elif BL > 200000 and TR < 500000 and TL < 500000:
        xraySource1 = 'Left_only'     
        doseDiff1 = (leftMean - c3) / c3 * 100 
        xraySource2 = 'None' 
        doseDiff2 = 0
    elif BL < 200000 and TR > 500000 and TL < 500000:
        xraySource1 = 'Right_only'      
        doseDiff1 = (rightMean - c6) / c6 * 100
        xraySource2 = 'None'
    elif BL > 200000 and TR > 500000 and TL < 500000: #Both obliques at the same time
        xraySource1 = 'Obl_Left' 
        doseDiff1 = (leftMean - c3 - c5) / (c3 + c5) * 100   
        xraySource2 = 'Obl_Right'          
        doseDiff2 = (rightMean - c4 - c6) / (c4 + c6) * 100
    else:
        xraySource1 = 'Unknown'
        doseDiff1 = 999
        xraySource2 = 'None'
        doseDiff2 = 0

    if xraySource1 != 'None':
        if debug:
            print('{:<30} {:<11} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f}'.format(fileName[:30], xraySource1, BL, BR, TL, TR, CTR, doseDiff1, wholeMean, leftMean,rightMean))
        else:
            print('{:<22}\t{:<9}\t{:>9.1f}'.format(fileName[:22],xraySource1,doseDiff1))
        kVhistory.append('{:<22} {:<40} {:<11} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f}'.format(np.datetime_as_string(np.datetime64('now')), fileName[:40], xraySource1, BL, BR, TL, TR, CTR, doseDiff1, wholeMean, leftMean,rightMean))
    if xraySource2 != 'None':
        if debug:
            print('{:<30} {:<11} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f}'.format(fileName[:30], xraySource2, BL, BR, TL, TR, CTR, doseDiff2, wholeMean, leftMean,rightMean))
        else:
            print('{:<22}\t{:<9}\t{:>9.1f}'.format(fileName[:22],xraySource2,doseDiff2))
        kVhistory.append('{:<22} {:<40} {:<11} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f}'.format(np.datetime_as_string(np.datetime64('now')), fileName[:40], xraySource2, BL, BR, TL, TR, CTR, doseDiff2, wholeMean, leftMean,rightMean))
    if abs(doseDiff1) > abs(maxDiff):
        maxDiff = doseDiff1
        maxDiffSource = xraySource1
    if abs(doseDiff2) > abs(maxDiff):
        maxDiff = doseDiff2
        maxDiffSource = xraySource2
    if np.max(wholeArray) == 1023:
        saturatedPx = np.count_nonzero(wholeArray == 1023)
        print('\nWarning! {:.0f} saturated pixels in image: {:<22}\n'.format(saturatedPx, fileName))
if maxDiff == 999:
    print('\nAnalysis failed for at least one measurement, please check files with \'Unknown\' source')
elif abs(maxDiff) > tolerance:
    print('\nMaximum dose difference of ' + '{:.1f}'.format(maxDiff) + '% OUT OF TOLERANCE')
else:
    print('\nPass.  Dose within tolerance\n')
if maxDiff < -5 and maxDiff > -20 and maxDiffSource == 'Obl_Right':
    print('\nCheck that the couch bars are OUT and repeat the oblique measurement\n\n')
elif maxDiff > 20 and maxDiffSource == 'Obl_Left':
    print('\nCheck that the couch is in the Sphinx treatment position and repeat the oblique measurement\n\n')
kVhistory = np.array(kVhistory)
np.save(historyFile, kVhistory)