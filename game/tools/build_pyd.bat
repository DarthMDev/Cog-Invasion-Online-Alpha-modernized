@echo off
title Cog Invasion PYD Builder

echo Building Cog Invasion Online lib folder into a pyd...
..\Panda3D-CI\python\ppython.exe -m direct.showutil.pfreeze -i direct.*.* -i lib.coginvasion.*.* -i encodings.* -i base64 -i site -o tools\libcoginvasion.pyd -x panda3d -x lib.server.*.* __main__
echo Done building pyd!
echo Protecting the pyd file...
"C:\Program Files (x86)\The Enigma Protector\enigma32" ..\libcoginvasion.enigma
echo Done!
pause >nul
