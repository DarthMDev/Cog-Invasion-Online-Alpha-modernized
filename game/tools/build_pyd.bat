@echo off
title Cog Invasion PYD Builder

echo Building Cog Invasion Online lib folder into a pyd...
..\Panda3D-CI\python\ppython.exe -OO tools/build_tools/make.py -n
echo Done building pyd!
echo Protecting the pyd file...
rem "C:\Program Files (x86)\The Enigma Protector\enigma32" ..\libcoginvasion.enigma
echo Done!
pause >nul
