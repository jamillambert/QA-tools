"""Analyses Lynx images from the kV Obliques and Orthogonal X-Rays on the ProteusONE

Required:
          baseline.npy - baseline values stored in a numpy array file
          opg files of the lynx images stored in the path specified below
Options:
          -d turn on debugging, outputs the quadrant pixel values and region mean values

29.03.2021 Jamil Lambert
14.04.21 v3 JL changed quadrants to determine which source was used
13.07.21 v3.1 JL changed output formatting including in history file, added -d debugging option"""

import sys, os, re
import numpy as np

path = '.\\Measurements\\'  # Directory with opg files in it
# Baseline values stored in this file (NP10 = 67053, NE22 = 68212, RG2 = 68246, NE22 loan ID = 19260936)
baseline_value_file = '.\\bin\\baseline_ID18066528.npy'
history_file = '.\\bin\\history.npy'  # History stored in this file
tolerance = 10  # tolerance for pass/fail in %

debug = False
for a in sys.argv:
    if a == '-d':
        debug = True

try:
    tempList = np.load(history_file)
    kV_history = tempList.tolist()
except FileNotFoundError:
    kV_history = [
        '{:<22} {:^40} {:^11} {:^11} {:^11} {:^11} {:^11} {:^11} {:>11} {:>11} {:>11} {:>11}'.format(
            'Analysis Date','file', 'source','BL', 'BR', 'TL','TR', 'CTR','Dose diff','whole mean',
            'left mean','right mean')]

try:
    baselines = np.load(baseline_value_file)
    c0 = baselines[0]  # Baseline date
    c1 = baselines[1]  # Baseline set by
    c2 = float(baselines[2])  # Orthogonal average pixel value, pps x = 0
    c3 = float(baselines[3])  # Left obliques average pixel value in left range
    c4 = float(baselines[4])  # Left oblique average pixel value in right range
    c5 = float(baselines[5])  # Right oblique average pixel value in left range
    c6 = float(baselines[6])  # Right oblique average pixel value in right range
    c7 = int(baselines[7])  # Start x for left range
    c8 = int(baselines[8])  # End x for left range
    c9 = int(baselines[9])  # Start x for right range
    c10 = int(baselines[10])  # End x for right range
except ValueError:
    print('Baseline file: ' + baseline_value_file + ' could not be loaded.  Script exiting')
    exit(1)
file_list = [f for f in os.listdir(path) if f.endswith(".opg")]
xray_source_1 = 'None'
xray_source_2 = 'None'
dose_diff_1 = 0
dose_diff_2 = 0
max_diff = 0
max_diff_source = 'None'
if len(file_list) < 1:
    print(
        'No measurement files found\n\n'
        'Previous measurements, which the script has already been run on, are in '
        '.\\_old_measurements \nMove back into the .\\Measurements folder '
        'if you wish to re run the script on them\n')
    exit(1)
if debug:
    print('{:^30} {:^11} {:^11} {:^11} {:^11} {:^11} {:^11} {:>11} {:>11} {:>11} {:>11}'.format(
        'file', 'source', 'BL','BR', 'TL', 'TR', 'CTR','Dose diff','whole mean','left mean','right mean'))
else:
    print('{:^22}\t{:^9}\t{:^14}'.format('file', 'source', 'difference (%)'))
for file_name in file_list:
    file_path = path + file_name
    pixel_data = np.empty(shape=(600, 600))
    with open(file_path) as opg_file:
        for i, line in enumerate(opg_file):
            if i == 26 and not line.startswith("<asciibody>"):
                print('format missmatch in opg file, line 27 =\"' + line + '\" expected \"<asciibody>\"')
            elif 30 < i < 631:  # lines 31 to 631 contain the pixel data
                new_line = [p for p in re.split("\s|,|;", line) if p]
                pixel_data[i - 31] = np.array(
                    new_line[1:])  # the first entry on the line is the y position and needs to be removed
    whole_array = np.array(pixel_data).astype(float)
    # If taken in Lynx2D the images are rotated 180 compared to myQA, the opg file can be renamed
    # from _i_000.opg to _i_180.opg and the below will correct for the rotation
    if int(file_name[-7:-4]) == 180:
        TL = np.sum(whole_array[0:100, 0:100])
        BL = np.sum(whole_array[500:600, 0:100])
        TR = np.sum(whole_array[0:100, 500:600])
        BR = np.sum(whole_array[500:600, 500:600])
        startL = c7 - 1
        endL = c8
        startR = c9 - 1
        endR = c10
    else:
        TL = np.sum(whole_array[500:600, 500:600])
        BL = np.sum(whole_array[0:100, 500:600])
        TR = np.sum(whole_array[500:600, 0:100])
        BR = np.sum(whole_array[0:100, 0:100])
        startL = 600 - c8
        endL = 600 - c7 + 1
        startR = 600 - c10
        endR = 600 - c9 + 1
    CTR = np.sum(whole_array[150:450, 150:450])
    total = np.sum(whole_array)
    left_array = np.array(whole_array[:, startL:endL])
    right_array = np.array(whole_array[:, startR:endR])
    whole_mean = np.mean(whole_array)
    left_mean = np.mean(left_array)
    right_mean = np.mean(right_array)

    if TL > 500000 and BR > 500000:
        xray_source_1 = 'Orthogonal'
        dose_diff_1 = (whole_mean - c2) / c2 * 100
        xray_source_2 = 'None'
        dose_diff_2 = 0
    elif BL > 200000 and TR < 500000 and TL < 500000:
        xray_source_1 = 'Left_only'
        dose_diff_1 = (left_mean - c3) / c3 * 100
        xray_source_2 = 'None'
        dose_diff_2 = 0
    elif BL < 200000 and TR > 500000 > TL:
        xray_source_1 = 'Right_only'
        dose_diff_1 = (right_mean - c6) / c6 * 100
        xray_source_2 = 'None'
    elif BL > 200000 and TR > 500000 > TL:  # Both obliques at the same time
        xray_source_1 = 'Obl_Left'
        dose_diff_1 = (left_mean - c3 - c5) / (c3 + c5) * 100
        xray_source_2 = 'Obl_Right'
        dose_diff_2 = (right_mean - c4 - c6) / (c4 + c6) * 100
    else:
        xray_source_1 = 'Unknown'
        dose_diff_1 = 999
        xray_source_2 = 'None'
        dose_diff_2 = 0

    if xray_source_1 != 'None':
        if debug:
            print(
                '{:<30} {:<11} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f}'.format(
                    file_name[:30], xray_source_1, BL, BR, TL, TR, CTR, dose_diff_1, whole_mean, left_mean, right_mean))
        else:
            print('{:<22}\t{:<9}\t{:>9.1f}'.format(file_name[:22], xray_source_1, dose_diff_1))
        kV_history.append(
            '{:<22} {:<40} {:<11} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f}'.format(
                np.datetime_as_string(np.datetime64('now')), file_name[:40], xray_source_1, BL, BR, TL, TR, CTR,
                dose_diff_1, whole_mean, left_mean, right_mean))
    if xray_source_2 != 'None':
        if debug:
            print(
                '{:<30} {:<11} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f}'.format(
                    file_name[:30], xray_source_2, BL, BR, TL, TR, CTR, dose_diff_2, whole_mean, left_mean, right_mean))
        else:
            print('{:<22}\t{:<9}\t{:>9.1f}'.format(file_name[:22], xray_source_2, dose_diff_2))
        kV_history.append(
            '{:<22} {:<40} {:<11} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f} {:>11.1f}'.format(
                np.datetime_as_string(np.datetime64('now')), file_name[:40], xray_source_2, BL, BR, TL, TR, CTR,
                dose_diff_2, whole_mean, left_mean, right_mean))
    if abs(dose_diff_1) > abs(max_diff):
        max_diff = dose_diff_1
        max_diff_source = xray_source_1
    if abs(dose_diff_2) > abs(max_diff):
        max_diff = dose_diff_2
        max_diff_source = xray_source_2
    if np.max(whole_array) == 1023:
        saturatedPx = np.count_nonzero(whole_array == 1023)
        print('\nWarning! {:.0f} saturated pixels in image: {:<22}\n'.format(saturatedPx, file_name))
if max_diff == 999:
    print('\nAnalysis failed for at least one measurement, please check files with \'Unknown\' source')
elif abs(max_diff) > tolerance:
    print('\nMaximum dose difference of ' + '{:.1f}'.format(max_diff) + '% OUT OF TOLERANCE')
else:
    print('\nPass.  Dose within tolerance\n')
if -5 > max_diff > -20 and max_diff_source == 'Obl_Right':
    print('\nCheck that the couch bars are OUT and repeat the oblique measurement\n\n')
elif max_diff > 20 and max_diff_source == 'Obl_Left':
    print('\nCheck that the couch is in the Sphinx treatment position and repeat the oblique measurement\n\n')
kV_history = np.array(kV_history)
np.save(history_file, kV_history)
