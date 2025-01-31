@echo off
SET scriptDirectory=%~dp0
cd /d %scriptDirectory%

REM Set the PYTHONPATH to include the parent directory
SET PYTHONPATH=%scriptDirectory%

"C:/Program Files/Schlumberger/Pipesim_PTK_2023.1/python.exe" "%scriptDirectory%app"