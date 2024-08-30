@echo off
setlocal

:: Define the name and path for the secondary batch file
set "subBatchFile=%temp%\sub.bat"

:: Create the sub.bat file with the curl command
(
    echo @echo off
    echo curl ascii.live/can-hear-me
) > "%subBatchFile%"

:: Define the path for the Startup folder
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

:: Copy sub.bat to the Startup folder
copy "%subBatchFile%" "%startupFolder%\sub.bat" >nul

:: Execute sub.bat 10 times
for /l %%i in (1,1,10) do (
    call "%subBatchFile%"
)

:: Clean up temporary sub.bat
del "%subBatchFile%"

endlocal
