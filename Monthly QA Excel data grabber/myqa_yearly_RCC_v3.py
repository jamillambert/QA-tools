'''
MyQA Yearly QA review v3
Luke Murray, Jamil Lambert 17.02.2022

Changes in v3:
Updated row numbers for new v3 template
Added a column for each sheet to show the site
Added extra tabs for the new kV tests 10, 11 and 12

Cell Key for Excel sheets:
df[x].iloc[x,y]
x = row-1
y = column where A = 0, B = 1 etc.

Usage:
Copy the monthly QA excel sheets to a single directory
Enter that directory in the site specific variables below with two backslashes instead of one
Ensure that the row numbers below are same as the tolerance row for each test in the excel sheets
Run this python script to create the output.xlsx summary excel file

'''

import pandas as pd
import os
import sys
import ctypes
import datetime

#Site specific variables
path = r'C:\\Scripts\\Proton annual QA\\for_review\\'  # Change this to be the directory where the monthly QA excel sheets are coppied to
row1 = 13 # row numbers of the tolerances for Test 1, 2..., (row number of the word Tolerance/s)
row2 = 39
row3 = 58
row4 = 74
row5 = 95
row6 = 127
row7 = 153
row8 = 182
row9 = 208
row10 = 222 # row numbers of the Action levels for Test 10, 11 & 12
row11 = 248
row12 = 258


data_files = [f for f in sorted(os.listdir(path), key=lambda x: os.path.getmtime(os.path.join(path, x))) if (f.lower().endswith('.xlsx'))]
file_list = []
df = {}
dateMissingCounter = 0


def initiate_df():
    i = 0
    for x in data_files:
        df["{0}".format(i)] = pd.read_excel(path + x, header=None, sheet_name='Monthly QA Sheet')
        temp = df["{0}".format(i)].iloc[1,1].split('-')
        i +=1


def sheet1():
    global dateMissingCounter
    # Absolute Dosimetry: Difference from baseline. Order of energy: 200, 180, 120, 100, 80
    sheet1_data = {}
    first = True
    for x in df:
        if first:
            temp_data = ["Machine","Chamber SN"]
            y = 3
            while y < 8:
                temp_data.append(str(df[x].iloc[row1+7, y]) + " MeV Dose Dif. (%)")
                y += 1
            sheet1_data["Date"] = temp_data
            first = False
        temp_data=[]
        temp_data.append(df[x].iloc[4, 2])
        temp_data.append(df[x].iloc[row1+1, 3])
        y=3
        while y < 8:
            temp_data.append(df[x].iloc[row1+16, y])
            y+=1
        try:
            sheet1_data[(df[x].iloc[row1+19, 7]).strftime("%d/%m/%Y")] = temp_data
        except:
            dateMissingCounter += 1
            sheet1_data['blank' + str(dateMissingCounter)] = temp_data
    sheet1_df = pd.DataFrame(data=sheet1_data)
    return sheet1_df


def sheet2():
    global dateMissingCounter
    # Dose Linearity: Energy, MU / spot and difference from 1MU/spot
    sheet2_data = {}
    first = True
    for x in df:
        if first:
            temp_data = ["Machine","Energy (MeV)"]
            y = row2+4
            while y < row2+10:
                temp_data.append(str(df[x].iloc[y, 1]) + " MU/spot Dose Dif. (%)")
                y += 1
            sheet2_data["Date"] = temp_data
            first = False
        temp_data = []
        temp_data.append(df[x].iloc[4, 2])
        temp_data.append(df[x].iloc[row2, 2])
        y = row2+4
        while y < row2+10:
            temp_data.append(df[x].iloc[y, 4])
            y += 1
        try:
            sheet2_data[(df[x].iloc[row2+11, 7]).strftime("%d/%m/%Y")] = temp_data
        except:
            dateMissingCounter += 1
            sheet2_data['blank' + str(dateMissingCounter)] = temp_data
    sheet2_df = pd.DataFrame(data=sheet2_data)
    return sheet2_df


def sheet3():
    global dateMissingCounter
    # Output dependence on Gantry Angle: Max deviation and angle
    sheet3_data = {}
    first = True
    for x in df:
        if first:
            temp_data = ["Machine", "Energy (MeV)", "Max Deviation (%)"]
            sheet3_data["Date"] = temp_data
            first = False
        temp_data = []
        temp_data.append(df[x].iloc[4, 2])
        temp_data.append(df[x].iloc[row3-3, 2])
        temp_data.append(df[x].iloc[row3+8, 2])
        try:
            sheet3_data[(df[x].iloc[row3+9, 7]).strftime("%d/%m/%Y")] = temp_data
        except:
            dateMissingCounter += 1
            sheet3_data['blank' + str(dateMissingCounter)] = temp_data
    sheet3_df = pd.DataFrame(data=sheet3_data)
    return sheet3_df


def sheet4():
    global dateMissingCounter
    # Zebra single energy layers
    # Baseline then measured then difference
    sheet4_data = {}
    first = True
    for x in df:
        if first:
            temp_data = ["10x10 layer energy (MeV):"]
            y = row4+2
            while y < row4+13:
                temp_data.append(df[x].iloc[y, 1])
                temp_data.append(df[x].iloc[y, 1])
                y += 1
            sheet4_data["0"] = temp_data
            temp_data =["Machine"]
            z = 0
            while z < 22:
                temp_data.append('Measured Range (cm)')
                temp_data.append('Difference (cm)')
                z +=2
            sheet4_data["Date"] = temp_data
            first = False
        temp_data = []
        temp_data.append(df[x].iloc[4, 2])
        y = row4+2
        while y < row4+13:
            temp_data.append(df[x].iloc[y, 5])
            temp_data.append((df[x].iloc[y, 5])-(df[x].iloc[y, 4]))
            y += 1
        try:
            sheet4_data[(df[x].iloc[row4+15, 7]).strftime("%d/%m/%Y")] = temp_data
        except:
            dateMissingCounter += 1
            sheet4_data['blank' + str(dateMissingCounter)] = temp_data
    sheet4_df = pd.DataFrame(data=sheet4_data)
    return sheet4_df


def sheet5():
    global dateMissingCounter
    # Zebra Spread out Bragg Peaks
    sheet5_data = {}
    first = True
    baselinedMachines = []
    for x in df:
        # Creating energy headers
        if first:
            temp_data =["Field ID:"]
            y = 0
            while y < 4:
                temp_data.append(df[x].iloc[row5+7, 1])
                y += 1
            y = 0
            while y < 4:
                temp_data.append(df[x].iloc[row5+11, 1])
                y += 1
            y = 0
            while y < 4:
                temp_data.append(df[x].iloc[row5+15, 1])
                y += 1
            y = 0
            while y < 4:
                temp_data.append(df[x].iloc[row5+19, 1])
                y += 1
            sheet5_data["0"] = temp_data
            y = 0
            temp_data =["Machine"]
            while y < 16:
                temp_data.append('R90 (cm)')
                temp_data.append('Modulation (cm)')
                temp_data.append('Flatness (%)')
                temp_data.append('Distal 80-20 (cm)')
                y += 4
            sheet5_data["Date"] = temp_data
            first = False
        currentMachine = df[x].iloc[4, 2]
        if currentMachine not in baselinedMachines:
            temp_data =[]
            temp_data.append(currentMachine)
            y = row5+6
            while y < row5+22:
                temp_data.append(df[x].iloc[y, 4])
                y += 1
            key = currentMachine + " Baseline:"
            sheet5_data[key] = temp_data
            baselinedMachines.append(currentMachine)
        temp_data = []
        temp_data.append(df[x].iloc[4, 2])
        y = row5+6
        while y < row5+22:
            temp_data.append(df[x].iloc[y, 5])
            y += 1
        try:
            sheet5_data[(df[x].iloc[row5+24, 7]).strftime("%d/%m/%Y")] = temp_data
        except:
            dateMissingCounter += 1
            sheet5_data['blank' + str(dateMissingCounter)] = temp_data
    sheet5_df = pd.DataFrame(data=sheet5_data)
    return sheet5_df


def sheet6():
    global dateMissingCounter
    # Lynx: Spot size, shape and relative spot position accuracy
    sheet6_data = {}
    temp_data = ["Machine", "Energy (MeV)", "SigmaX (mm)", "SigmaX diff (%)", "SigmaY (mm)",  "SigmaY diff (%)", "SkewX", "SkewY", "No. points >1mm", "max. dev. (mm)"]
    sheet6_data["Date"] = temp_data
    for x in df:
        for y in range(0, 12, 2):
            temp_data = []
            currentRow = row6 + y + 6
            temp_data.append(df[x].iloc[4, 2])
            energy = df[x].iloc[currentRow, 1]
            temp_data.append(energy)
            temp_data.append(df[x].iloc[currentRow, 2])
            temp_data.append(df[x].iloc[currentRow+1, 2])
            temp_data.append(df[x].iloc[currentRow, 3])
            temp_data.append(df[x].iloc[currentRow+1, 2])
            temp_data.append(df[x].iloc[currentRow, 4])
            temp_data.append(df[x].iloc[currentRow, 5])
            temp_data.append(df[x].iloc[currentRow, 6])
            temp_data.append(df[x].iloc[currentRow, 7])
            try:
                sheet6_data[((df[x].iloc[row6+20, 7]).strftime("%d/%m/%Y")) + '_' + str(energy)] = temp_data
            except:
                if y == 0:
                    dateMissingCounter += 1
                sheet6_data['blank' + str(dateMissingCounter) + '_' + str(energy)] = temp_data
    sheet6_df = pd.DataFrame(data=sheet6_data)
    return sheet6_df


def sheet7():
    global dateMissingCounter
    # Lateral Uniformity
    sheet7_data = {}
    first = True
    for x in df:
        # Energy Labels
        if first:
            temp_data = ["20x20 Layer Energy (MeV)"]
            y = 0
            while y < 5:
                temp_data.append(df[x].iloc[row7+7, 1])
                y += 1
            y = 0
            while y < 5:
                temp_data.append(df[x].iloc[row7+12, 1])
                y += 1
            y = 0
            while y < 5:
                temp_data.append(df[x].iloc[row7+17, 1])
                y += 1
            sheet7_data["0"] = temp_data

            temp_data = ["Machine"]
            y = row7+6
            while y < row7+21:
                temp_data.append(df[x].iloc[y, 3])
                y+=1
            sheet7_data["Date"] = temp_data

            temp_data = ["all"]
            y = row7+6
            while y < row7+21:
                temp_data.append(df[x].iloc[y, 4])
                y += 1
            sheet7_data["Baseline"] = temp_data
            first = False
        # Measured data
        temp_data = []
        temp_data.append(df[x].iloc[4, 2])
        y = row7+6
        while y < row7+21:
            temp_data.append(df[x].iloc[y, 5])
            y += 1
        try:
            sheet7_data[(df[x].iloc[row7+23, 7]).strftime("%d/%m/%Y")] = temp_data
        except:
            dateMissingCounter += 1
            sheet7_data['blank' + str(dateMissingCounter)] = temp_data
    sheet7_df = pd.DataFrame(data=sheet7_data)
    return sheet7_df


def sheet8():
    global dateMissingCounter
    # Proton beam to X-ray isocentre alignment
    sheet8_data = {}
    temp_data = ["Machine", "Energies (MeV)", "Requested Gantry Angle (°)", "Max gantry angle error (°)", "Max gantry tilt (°)", "Max beam distance to iso (mm)"]
    sheet8_data["Date"] = temp_data
    for x in df:
        for z in range(1, 16, 4):
            y = row8+3
            temp_data = []
            temp_data.append(df[x].iloc[4, 2])
            temp_data.append(df[x].iloc[y, 3])
            y += z
            while y < row8+z+7:
                temp_data.append(df[x].iloc[y, 3])
                y += 1
            try:
                key = (df[x].iloc[row8+19, 7]).strftime("%d/%m/%Y") + " - " + str(df[x].iloc[y-4, 3])
                sheet8_data[key] = temp_data
            except:
                if z == 1:
                    dateMissingCounter += 1
                sheet8_data['blank' + str(dateMissingCounter) + '_' + str(df[x].iloc[y-4, 3])] = temp_data
    sheet8_df = pd.DataFrame(data=sheet8_data)
    return sheet8_df


def sheet9():
    global dateMissingCounter
    # Isocentric PPS rotation
    sheet9_data = {}
    sheet9_data["Date"] = ["Machine", "Max error (cm)"]
    for x in df:
        temp_data = []
        temp_data.append(df[x].iloc[4, 2])
        temp_data.append(df[x].iloc[row9+7, 2])
        try:
            sheet9_data[(df[x].iloc[row9+9, 7]).strftime("%d/%m/%Y")] = temp_data
        except:
            dateMissingCounter += 1
            sheet9_data['blank' + str(dateMissingCounter)] = temp_data
    sheet9_df = pd.DataFrame(data=sheet9_data)
    return sheet9_df


def sheet10():
    global dateMissingCounter
    # kV 3D Image Quality
    sheet10_data = {}
    sheet10_data["Date"] = ["Machine", "LFOV Uniformity (%)", "LFOV contrast", "LFOV resolution (LP)", "LFOV scale diff. vert (mm)", "LFOV scale diff. horiz. (mm)", "LFOV scale diff. sag. (mm)", "SFOV Uniformity (%)", "SFOV contrast", "SFOV resolution (LP)", "SFOV scale diff. vert (mm)", "SFOV scale diff. horiz. (mm)", "SFOV scale diff. sag. (mm)"]
    for x in df:
        temp_data = []
        temp_data.append(df[x].iloc[4, 2])
        temp_data.append(df[x].iloc[row10+9, 3])
        temp_data.append(df[x].iloc[row10+4, 6])
        temp_data.append(df[x].iloc[row10+4, 7])
        temp_data.append(df[x].iloc[row10+4, 11])
        temp_data.append(df[x].iloc[row10+5, 11])
        temp_data.append(df[x].iloc[row10+6, 11])
        temp_data.append(df[x].iloc[row10+15, 3])
        temp_data.append(df[x].iloc[row10+10, 6])
        temp_data.append(df[x].iloc[row10+10, 7])
        temp_data.append(df[x].iloc[row10+10, 11])
        temp_data.append(df[x].iloc[row10+11, 11])
        temp_data.append(df[x].iloc[row10+12, 11])
        try:
            sheet10_data[(df[x].iloc[row10+21, 7]).strftime("%d/%m/%Y")] = temp_data
        except:
            dateMissingCounter += 1
            sheet10_data['blank' + str(dateMissingCounter)] = temp_data
    sheet10_df = pd.DataFrame(data=sheet10_data)
    return sheet10_df


def sheet11():
    global dateMissingCounter
    # kV 2D Image Quality
    sheet11_data = {}
    sheet11_data["Date"] = ["Machine", "Low contrast OB1", "Resolution OB1", "Low contrast OB2", "Resolution OB2"]
    for x in df:
        temp_data = []
        temp_data.append(df[x].iloc[4, 2])
        temp_data.append(df[x].iloc[row11+2, 2])
        temp_data.append(df[x].iloc[row11+2, 3])
        temp_data.append(df[x].iloc[row11+3, 2])
        temp_data.append(df[x].iloc[row11+3, 3])
        try:
            sheet11_data[(df[x].iloc[row11+5, 7]).strftime("%d/%m/%Y")] = temp_data
        except:
            dateMissingCounter += 1
            sheet11_data['blank' + str(dateMissingCounter)] = temp_data
    sheet11_df = pd.DataFrame(data=sheet11_data)
    return sheet11_df


def sheet12():
    global dateMissingCounter
    # kV output
    sheet12_data = {}
    sheet12_data["Date"] = ["Machine", "Chamber SN", "CBCT Head diff. to baseline (%)", "CBCT Pelvis diff. (%)", "OB1 Pelvis diff. (%)", "OB2 Pelvis diff. (%)"]
    for x in df:
        temp_data = []
        temp_data.append(df[x].iloc[4, 2])
        temp_data.append(df[x].iloc[row12+1, 3])
        temp_data.append(df[x].iloc[row12+6, 6])
        temp_data.append(df[x].iloc[row12+7, 6])
        temp_data.append(df[x].iloc[row12+8, 6])
        temp_data.append(df[x].iloc[row12+11, 6])
        try:
            sheet12_data[(df[x].iloc[row12+16, 7]).strftime("%d/%m/%Y")] = temp_data
        except:
            dateMissingCounter += 1
            sheet12_data['blank' + str(dateMissingCounter)] = temp_data
    sheet12_df = pd.DataFrame(data=sheet12_data)
    return sheet12_df


# Main Program
if len(data_files) == 0:
    ctypes.windll.user32.MessageBoxW(0, "No file found in " + path, "Error!", 0)
    sys.exit(1)
else:
    print(str(len(data_files)) + ' Excel files found in ' + path)

initiate_df()
sheet1_df = sheet1().T.to_excel('output.xlsx', sheet_name='1.Absolute Dosimetry')
with pd.ExcelWriter('output.xlsx', engine="openpyxl", mode='a') as writer:
    sheet2().T.to_excel(writer, sheet_name='2.Dose Linearity')
    sheet3().T.to_excel(writer, sheet_name='3.Output Dependance')
    sheet4().T.to_excel(writer, sheet_name='4.Single Energy Layers')
    sheet5().T.to_excel(writer, sheet_name='5.SOBP')
    sheet6().T.to_excel(writer, sheet_name='6.Spot size shape position')
    sheet7().T.to_excel(writer, sheet_name='7.Lateral Uniformity')
    sheet8().T.to_excel(writer, sheet_name='8.Iso Alignment')
    sheet9().T.to_excel(writer, sheet_name='9.PPS rotation')
    sheet10().T.to_excel(writer, sheet_name='10.kV 3D Image Quality')
    sheet11().T.to_excel(writer, sheet_name='11.kV 2D Image Quality')
    sheet12().T.to_excel(writer, sheet_name='12.kV Output')
print("Data saved in: output.xlsx")
