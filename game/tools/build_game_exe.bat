@echo off
title Cog Invasion EXE Builder

set folderpath="C:\Users\Public\Documents\panda3d\build_test\tools"

echo Building Cog Invasion Online executable...
ppython.exe -m direct.showutil.pfreezeEXE -i encodings.* -i base64 -i site -o tools\coginvasion.exe -x panda3d -x direct -x pandac tools\exe_initializer.py
echo Done building exe!
mt.exe -manifest tools\coginvasion.exe.manifest -outputresource:tools\coginvasion.exe;1
del tools\coginvasion.exe.manifest
pause >nul
