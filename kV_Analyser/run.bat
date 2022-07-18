@echo off 
set savefile=.\output.txt
del .\Measurements\*.opg
.\bin\dcmodify -ie -e "(0028,1052)" .\Measurements\*.dcm
cls
echo Please Wait
.\bin\dcmodify -ie -e "(0028,1053)" .\Measurements\*.dcm
cls
echo 5%% Please Wait
.\bin\dcmodify -ie -e "(0028,1054)" .\Measurements\*.dcm
cls
echo 10%% Please Wait
.\bin\dcmodify -ie -e "(3002,000d)" .\Measurements\*.dcm
cls
echo 15%% Please Wait
.\bin\dcmodify -ie -i "(3002,0022)=1000" .\Measurements\*.dcm
cls
echo 20%% Please Wait
.\bin\dcmodify -ie -i "(3002,0024)=0" .\Measurements\*.dcm
cls
echo 25%% Please Wait
.\bin\dcmodify -ie -i "(3002,0026)=1000" .\Measurements\*.dcm
cls
echo 30%% Please Wait
del .\Measurements\*.dcm.bak
cls
echo 35%% Please Wait
java -jar .\bin\dicom2opg.jar .\Measurements\*.dcm -exit > .\dicom2opg_log.txt
pause
cls
echo 50%% Please Wait
cls
python .\bin\analyse_kV_dose.py
Pause