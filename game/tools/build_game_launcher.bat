@echo off
title Cog Invasion Launcher Builder

echo Building Cog Invasion Online launcher...
..\Panda3D-CI\python\ppython.exe -m direct.showutil.pfreezeEXE -i direct.*.* -i encodings.* -i Pmw.*.* -i base64 -i site -o tools\launcher.exe -x panda3d lib\launcher.py
echo Done building launcher!
echo Protecting the exe file...
"C:\Program Files (x86)\The Enigma Protector\enigma32" ..\launcher.enigma
echo Done!
pause >nul
