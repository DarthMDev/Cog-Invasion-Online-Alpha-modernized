@echo off
title Cog Invasion EXE Builder

set folderpath="C:\Users\Public\Documents\panda3d\build_test\tools"

echo Building Cog Invasion Online executable...
..\Panda3D-CI\python\ppython.exe -m direct.showutil.pfreezeEXE -i encodings.* -i base64 -i site -o tools\coginvasion.exe -x panda3d -x direct -x pandac tools\exe_initializer.py
echo Done building exe!
echo Protecting the exe file...
"C:\Program Files (x86)\The Enigma Protector\enigma32" ..\coginvasion.enigma
echo Done!
pause >nul
