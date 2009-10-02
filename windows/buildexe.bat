@echo off
set PYTHONPATH=%PYTHONPATH%;%CD%/..
C:\Python25\python setup.py py2exe
pause
