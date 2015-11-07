@echo off
title Cog Invasion PYD Builder

echo Building Cog Invasion Online lib folder into a pyd...
..\Panda3D-CI\python\ppython.exe -m direct.showutil.pfreeze -i direct.*.* -i lib.coginvasion.*.* -i encodings.* -i base64 -i site -o tools\libcoginvasion.pyd -x panda3d -x lib.server.*.* __main__
echo Done building pyd!
echo Packing/obfuscating the pyd file
"C:\Users\Brian\Desktop\upx391w\upx" -9 tools\libcoginvasion.pyd
echo All done!
pause >nul
