@echo off
setlocal
echo.
echo Add the baseline values to the setBaseline.py script and backup existing baseline.npy file before continuing
echo.
:PROMPT
SET /P AREYOUSURE=Overrite baselines now (Y/N)?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO ENDPROMPT
python setBaseline.py
cls
echo.
echo Baselines set
echo.
pause
GOTO END
:ENDPROMPT
cls
echo.
echo Nothing done
echo.
pause
:END
endlocal