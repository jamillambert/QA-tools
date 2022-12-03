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


def read_history(history_file):
    try:
        tempList = np.load(history_file)
        kV_history = tempList.tolist()
    except FileNotFoundError:
        kV_history = [
            '{:<22} {:^40} {:^11} {:^11} {:^11} {:^11} {:^11} {:^11} {:>11} {:>11} {:>11} {:>11}'.format(
                'Analysis Date','file', 'source','BL', 'BR', 'TL','TR', 'CTR','Dose diff','whole mean',
                'left mean','right mean')]
    return kV_history


def read_baselines(baseline_value_file):
    c = []
    try:
        baselines = np.load(baseline_value_file)
        c.append(baselines[0])  # Baseline date
        c.append(baselines[1]) # Baseline set by
        c.append(float(baselines[2]))  # Orthogonal average pixel value, pps x = 0
        c.append(float(baselines[3]))  # Left obliques average pixel value in left range
        c.append(float(baselines[4]))  # Left oblique average pixel value in right range
        c.append(float(baselines[5]))  # Right oblique average pixel value in left range
        c.append(float(baselines[6]))  # Right oblique average pixel value in right range
        c.append(int(baselines[7]))  # Start x for left range
        c.append(int(baselines[8]))  # End x for left range
        c.append(int(baselines[9]))  # Start x for right range
        c.append(int(baselines[10]))  # End x for right range
        c.append(10) # Tolerance, to be added to the baseline file later
    except ValueError:
        print('Baseline file: ' + baseline_value_file + ' could not be loaded.  Script exiting')
        exit(1)
    return c


def load_opg_file(file_path):
    pixel_data = np.empty(shape=(600, 600))
    with open(file_path) as opg_file:
        for i, line in enumerate(opg_file):
            if i == 26 and not line.startswith("<asciibody>"):
                print('format missmatch in opg file, line 27 =\"' + line + '\" expected \"<asciibody>\"')
            elif 30 < i < 631:  # lines 31 to 631 contain the pixel data
                new_line = [p for p in re.split("\s|,|;", line) if p]
                pixel_data[i - 31] = np.array(
                    new_line[1:])  # the first entry on the line is the y position and needs to be removed
    return np.array(pixel_data).astype(float)


def print_result(data, debug):
    if debug:
        print(f'{data[0]:<30} {data[1]:<11} {data[2]:>11.1f} {data[3]:>11.1f} {data[4]:>11.1f} {data[5]:>11.1f} {data[6]:>11.1f} {data[7]:>11.1f} {data[8]:>11.1f} {data[9]:>11.1f} {data[10]:>11.1f}')
    else:
        print(f'{data[0]:<22}\t{data[1]:<9}\t{data[7]:<9.1f}')
            
def print_heading(data, debug):
    if debug:
        print(f'{data[0]:^30} {data[1]:^11} {data[2]:^11} {data[3]:^11} {data[4]:^11} {data[5]:^11} {data[6]:^11} {data[7]:>11} {data[8]:>11} {data[9]:>11} {data[10]:>11}')
    else:
        print(f'{data[0]:^30}\t{data[1]:^9}\t{data[7]:^9}')
            
        
def add_history(data, kV_history):
    time = np.datetime_as_string(np.datetime64('now'))
    new_line = f'{time:<22} {data[0]:<40} {data[1]:<11} {data[2]:>11.1f} {data[3]:>11.1f} {data[4]:>11.1f} {data[5]:>11.1f} {data[6]:>11.1f} {data[7]:>11.1f} {data[8]:>11.1f} {data[9]:>11.1f} {data[10]:>11.1f}'
    kV_history.append(new_line)

  
def analyse(path, c, kV_history, history_file, debug):
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
    data = ('file', 'source', 'BL','BR', 'TL', 'TR', 'CTR','Dose diff','whole mean','left mean','right mean')
    print_heading(data, debug)
    for file_name in file_list:
        file_path = path + file_name
        whole_array = load_opg_file(file_path)
        # If taken in Lynx2D the images are rotated 180 compared to myQA, the opg file can be renamed
        # from _i_000.opg to _i_180.opg and the below will correct for the rotation
        if int(file_name[-7:-4]) == 180:
            TL = np.sum(whole_array[0:100, 0:100])
            BL = np.sum(whole_array[500:600, 0:100])
            TR = np.sum(whole_array[0:100, 500:600])
            BR = np.sum(whole_array[500:600, 500:600])
            startL = c[7] - 1
            endL = c[8]
            startR = c[9] - 1
            endR = c[10]
        else:
            TL = np.sum(whole_array[500:600, 500:600])
            BL = np.sum(whole_array[0:100, 500:600])
            TR = np.sum(whole_array[500:600, 0:100])
            BR = np.sum(whole_array[0:100, 0:100])
            startL = 600 - c[8]
            endL = 600 - c[7] + 1
            startR = 600 - c[10]
            endR = 600 - c[9] + 1
        CTR = np.sum(whole_array[150:450, 150:450])
        left_array = np.array(whole_array[:, startL:endL])
        right_array = np.array(whole_array[:, startR:endR])
        whole_mean = np.mean(whole_array)
        left_mean = np.mean(left_array)
        right_mean = np.mean(right_array)

        if TL > 500000 and BR > 500000:
            xray_source_1 = 'Orthogonal'
            dose_diff_1 = (whole_mean - c[2]) / c[2] * 100
            xray_source_2 = 'None'
            dose_diff_2 = 0
        elif BL > 200000 and TR < 500000 and TL < 500000:
            xray_source_1 = 'Left_only'
            dose_diff_1 = (left_mean - c[3]) / c[3] * 100
            xray_source_2 = 'None'
            dose_diff_2 = 0
        elif BL < 200000 and TR > 500000 > TL:
            xray_source_1 = 'Right_only'
            dose_diff_1 = (right_mean - c[6]) / c[6] * 100
            xray_source_2 = 'None'
        elif BL > 200000 and TR > 500000 > TL:  # Both obliques at the same time
            xray_source_1 = 'Obl_Left'
            dose_diff_1 = (left_mean - c[3] - c[5]) / (c[3] + c[5]) * 100
            xray_source_2 = 'Obl_Right'
            dose_diff_2 = (right_mean - c[4] - c[6]) / (c[4] + c[6]) * 100
        else:
            xray_source_1 = 'Unknown'
            dose_diff_1 = 999
            xray_source_2 = 'None'
            dose_diff_2 = 0
                    
        if xray_source_1 != 'None':
            data = (file_name[:30], xray_source_1, BL, BR, TL, TR, CTR, dose_diff_1, whole_mean, left_mean, right_mean)   
            print_result(data, debug)
            add_history(data, kV_history)
        if xray_source_2 != 'None':
            data = (file_name[:30], xray_source_2, BL, BR, TL, TR, CTR, dose_diff_2, whole_mean, left_mean, right_mean)
            print_result(data, debug)
            add_history(data, kV_history)

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
    elif abs(max_diff) > c[11]:
        print('\nMaximum dose difference of ' + '{:.1f}'.format(max_diff) + '% OUT OF TOLERANCE')
    else:
        print('\nPass.  Dose within tolerance\n')
    if -5 > max_diff > -20 and max_diff_source == 'Obl_Right':
        print('\nCheck that the couch bars are OUT and repeat the oblique measurement\n\n')
    elif max_diff > 20 and max_diff_source == 'Obl_Left':
        print('\nCheck that the couch is in the Sphinx treatment position and repeat the oblique measurement\n\n')
    kV_history = np.array(kV_history)
    np.save(history_file, kV_history)


def main():
    path = '.\\Measurements\\'  # Directory with opg files in it
    # Baseline values stored in this file (NP10 = 67053, NE22 = 68212, RG2 = 68246, NE22 loan ID = 19260936)
    baseline_value_file = '.\\bin\\baseline_ID18066528.npy'
    history_file = '.\\bin\\history.npy'  # History stored in this file

    debug = False
    for a in sys.argv:
        if a == '-d':
            debug = True
            
    kV_history = read_history(history_file)
    constants = read_baselines(baseline_value_file)
    analyse(path, constants, kV_history, history_file, debug)
    
    
if __name__ == "__main__":
    main()
