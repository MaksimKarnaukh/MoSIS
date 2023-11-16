@echo off
set PYTHONPATH=%PYTHONPATH%;%cd%\src
cd doc
make html
cd ..