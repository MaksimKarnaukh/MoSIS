@echo off
SET PATH=;C:/Program Files/OpenModelica1.21.0-64bit/bin/;%PATH%;
SET ERRORLEVEL=
CALL "%CD%/car_model.exe" %*
SET RESULT=%ERRORLEVEL%

EXIT /b %RESULT%
