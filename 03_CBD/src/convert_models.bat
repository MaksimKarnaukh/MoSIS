@echo off
cd %~dp0

echo Currently in: %cd%

call ..\..\venv\Scripts\activate.bat
cd ..\\DrawioConvert
python __main__.py -F CBD -e CBDA ..\model_libraries\Models.xml -sSrvg -f -d ..\src\python_models\
