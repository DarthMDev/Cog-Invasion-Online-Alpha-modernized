@echo off
title Cog Invasion Launcher Builder

echo Building Cog Invasion Online launcher...
..\Panda3D-CI\python\ppython.exe -m direct.showutil.pfreezeEXE -i direct.*.* -i encodings.* -i Pmw.*.* -i base64 -i site -o launcher.exe -x panda3d launcher.py
echo Done building launcher!
mt.exe -manifest launcher.exe.manifest -outputresource:launcher.exe;1
del launcher.exe.manifest
pause >nul
