@echo off
SET PATH=C:/Program Files/OpenModelica1.21.0-64bit/bin/;C:/Program Files/OpenModelica1.21.0-64bit/lib//omc;C:/Program Files/OpenModelica1.21.0-64bit/lib/;C:/Users/Maksim/AppData/Roaming/.openmodelica/binaries/Modelica;C:/Users/Maksim/AppData/Roaming/.openmodelica/libraries/Modelica 4.0.0+maint.om/Resources/Library/mingw64;C:/Users/Maksim/AppData/Roaming/.openmodelica/libraries/Modelica 4.0.0+maint.om/Resources/Library/win64;C:/Users/Maksim/AppData/Roaming/.openmodelica/libraries/Modelica 4.0.0+maint.om/Resources/Library;C:/Program Files/OpenModelica1.21.0-64bit/bin/;%PATH%;
SET ERRORLEVEL=
CALL "%CD%/control_loop.exe" %*
SET RESULT=%ERRORLEVEL%

EXIT /b %RESULT%
