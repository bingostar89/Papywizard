@echo off
REM PATH=%PATH%;C:\Python25
set PYTHONPATH=%PYTHONPATH%;%CD%
C:\Python25\python setup.py py2exe
pause
