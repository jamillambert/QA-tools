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



class XrayImage:
    def __init__(self, file_path):
        self.left_mean = None
        self.whole_mean = None
        self.right_array = None
        self.left_array = None
        self.CTR = None
        self.whole_array = None
        self.startR = None
        self.endL = None
        self.startL = None
        self.BR = None
        self.TR = None
        self.BL = None
        self.TL = None
        self.endR = None
        self.right_mean = None
        self.xray_source_1 = 'None'
        self.xray_source_2 = 'None'
        self.dose_diff_1 = 0
        self.dose_diff_2 = 0
        self.load_opg_file(file_path)    
    
    def read_quadrants(self, c, angle):
        if angle == 180:
            self.TL = np.sum(self.whole_array[0:100, 0:100])
            self.BL = np.sum(self.whole_array[500:600, 0:100])
            self.TR = np.sum(self.whole_array[0:100, 500:600])
            self.BR = np.sum(self.whole_array[500:600, 500:600])
            self.startL = c[7] - 1
            self.endL = c[8]
            self.startR = c[9] - 1
            self.endR = c[10]
        else:
            self.TL = np.sum(self.whole_array[500:600, 500:600])
            self.BL = np.sum(self.whole_array[0:100, 500:600])
            self.TR = np.sum(self.whole_array[500:600, 0:100])
            self.BR = np.sum(self.whole_array[0:100, 0:100])
            self.startL = 600 - c[8]
            self.endL = 600 - c[7] + 1
            self.startR = 600 - c[10]
            self.endR = 600 - c[9] + 1            

    def load_opg_file(self, file_path):
        pixel_data = np.empty(shape=(600, 600))
        with open(file_path) as opg_file:
            for i, line in enumerate(opg_file):
                if i == 26 and not line.startswith("<asciibody>"):
                    print('format missmatch in opg file, line 27 =\"' +
                        line + '\" expected \"<asciibody>\"')
                elif 30 < i < 631:  # lines 31 to 631 contain the pixel data
                    new_line = [p for p in re.split(
                        "\s|,|;", line) if p]  # type: ignore
                    pixel_data[i - 31] = np.array(
                        new_line[1:])  # the first entry on the line is the y position and needs to be removed
        self.whole_array = np.array(pixel_data).astype(float)
        self.CTR = np.sum(self.whole_array[150:450, 150:450])
        self.left_array = np.array(self.whole_array[:, self.startL:self.endL])
        self.right_array = np.array(self.whole_array[:, self.startR:self.endR])
        self.whole_mean = np.mean(self.whole_array)
        self.left_mean = np.mean(self.left_array)
        self.right_mean = np.mean(self.right_array)

    def calculate_dose_diff(self, c):
        if self.TL > 500000 and self.BR > 500000:
            self.xray_source_1 = 'Orthogonal'
            self.dose_diff_1 = (self.whole_mean - c[2]) / c[2] * 100
            self.xray_source_2 = 'None'
            self.dose_diff_2 = 0
        elif self.BL > 200000 and self.TR < 500000 and self.TL < 500000:
            self.xray_source_1 = 'Left_only'
            self.dose_diff_1 = (self.left_mean - c[3]) / c[3] * 100
            self.xray_source_2 = 'None'
            self.dose_diff_2 = 0
        elif self.BL < 200000 and self.TR > 500000 > self.TL:
            self.xray_source_1 = 'Right_only'
            self.dose_diff_1 = (self.right_mean - c[6]) / c[6] * 100
            self.xray_source_2 = 'None'
        elif self.BL > 200000 and self.TR > 500000 > self.TL:  # Both obliques at the same time
            self.xray_source_1 = 'Obl_Left'
            self.dose_diff_1 = (self.left_mean - c[3] - c[5]) / (c[3] + c[5]) * 100
            self.xray_source_2 = 'Obl_Right'
            self.dose_diff_2 = (self.right_mean - c[4] - c[6]) / (c[4] + c[6]) * 100
        else:
            self.xray_source_1 = 'Unknown'
            self.dose_diff_1 = 999
            self.xray_source_2 = 'None'
            self.dose_diff_2 = 0
                    
    def data_string(self, file_name, source):
        if source == 1:
            xray_source = self.xray_source_1
            dose_diff = self.dose_diff_1
        else:
            xray_source = self.xray_source_2
            dose_diff = self.dose_diff_2
        return file_name[:30], xray_source, self.BL, self.BR, self.TL, self.TR, self.CTR, dose_diff, self.whole_mean, self.left_mean, self.right_mean

    def check_saturation(self, file_name):
        if np.max(self.whole_array) == 1023:
            saturated_pixels = np.count_nonzero(self.whole_array == 1023)
            print('\nWarning! {:.0f} saturated pixels in image: {:<22}\n'.format(saturated_pixels, file_name))



def read_history(history_file):
    try:
        temp_list = np.load(history_file)
        kV_history = temp_list.tolist()
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

def create_file_list(path, extension):
    file_list = [f for f in os.listdir(path) if f.endswith(extension)]
    if len(file_list) < 1:
        print(
            'No measurement files found\n\n'
            'Previous measurements, which the script has already been run on, are in '
            '.\\_old_measurements \nMove back into the .\\Measurements folder '
            'if you wish to re run the script on them\n')
        exit(1)
    return file_list

def check_max(max_diff, max_diff_source, xray):
    if abs(xray.dose_diff_1) > abs(max_diff):
        max_diff = xray.dose_diff_1
        max_diff_source = xray.xray_source_1
    if abs(xray.dose_diff_2) > abs(max_diff):
        max_diff = xray.dose_diff_2
        max_diff_source = xray.xray_source_2
    return max_diff, max_diff_source

def print_max(max_diff, max_diff_source, tolerance):
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

def analyse(path, c, kV_history, history_file, debug):
    file_list = create_file_list(path, ".opg")
    data = ('file', 'source', 'BL','BR', 'TL', 'TR', 'CTR','Dose diff','whole mean','left mean','right mean')
    print_heading(data, debug)
    max_diff = 0
    max_diff_source = 'None'
    for file_name in file_list:
        file_path = path + file_name
        xray = XrayImage(file_path)
        # If taken in Lynx2D the images are rotated 180 compared to myQA, the opg file can be renamed
        # from _i_000.opg to _i_180.opg and the below will correct for the rotation
        xray.read_quadrants(c, file_name[-7:-4])            
        xray.calculate_dose_diff(c)                    
        if xray.xray_source_1 != 'None':
            data = xray.data_string(file_name, 1)   
            print_result(data, debug)
            add_history(data, kV_history)
        if xray.xray_source_2 != 'None':
            data = xray.data_string(file_name, 2)
            print_result(data, debug)
            add_history(data, kV_history)
        max_diff, max_diff_source = check_max(max_diff, max_diff_source, xray)
        xray.check_saturation(file_name)
        print_max(max_diff, max_diff_source, c[11])
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
