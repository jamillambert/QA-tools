## kV output measurement with the Lynx and sphinx

**Save the dicom files from myQA in the “Measurements” folder, or modify the script to point to the location:**

S:\Clinical\Radiotherapy\Physics\QA\NE22\2. Proton\2. Daily QA\kV_Dose_Analysis\Measurements\

There is a new patient in Mosaiq with ID: 1QA-NE22-151121

The patient has 3 fields:
 - **090A1 is for the oblique dose**, it is the same field for the daily QA with the sphinx.  Measure the oblique dose with the Lynx (Iris 95%) using 120kV, 160mA, 500ms, after the image displays in myQA save the dicom file in the above folder
 - **000A1 is for the orthogonal kV dose**, do a GOTO treatment gantry to move to Gantry = 0° and GOTO treatment couch to move to PPS x = 0, then extract the imaging panels and measure the dose with the Lynx (Iris 95%) for the pelvis protocol with no modifications (120kV, 50mA, 100ms). Save the dicom file in the above folder
 - MIMI is the same as the existing field for the imaging QA

Once the images are saved in the above folder run the script and record the results in myQA. Measurements are moved to .\_old_measurements\ when the script is run.  The python script and baseline files are in .\bin\


### Step by step instructions in the myQA task:

1.	Set up the Sphinx and Lynx on PPS align and perform sphinx daily QA

2.	Make sure the couch bars are out

3.	In Adapt Insight select the obliques using **120kV, 160mA, 500ms**

4.	In "01 - kV dose - Measurement" select the Lynx and perform the background

5.	Set the measurement for 10s with iris 95%, with the x-rays ready click measure and during the measurement take both oblique x-rays

6.	Save the image in S:\Clinical\Radiotherapy\Physics\QA\NE22\2. Proton\2. Daily QA\kV_Dose_Analysis\Measurements\

7.	In Mosaiq send the 000A1 field

8.	GOTO treatment Gantry then PPS

9.	Insert imaging panels

10.	In Adapt Insight select orthogonal x-rays

11.	Select pelvis protocol **(120kV, 50mA, 100ms)**

12.	Measure again as above and take the orthogonal x-ray during the measurement, save the image in the same folder as above with a different name to the first image

13.	Run the script located in the kV_Dose_Analysis folder, there is a shortcut to the folder on the desktop containing "Run_kV_Analysis_Script.bat"

14.	In "02 - kV dose - Input" record the results from the script

15.	If all 3 sources pass finish both the measurement and input tests and this task

16.	If any source fails or the result is either Right_only, or Left_only repeat the measurements ensuring the correct settings are used in Adapt Insight and the x-ray starts and completes while the measurement is running in myQA



