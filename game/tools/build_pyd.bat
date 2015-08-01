@echo off
title Cog Invasion PYD Builder

echo Building Cog Invasion Online lib folder into a pyd...
ppython.exe -m direct.showutil.pfreeze -i direct.*.* -i lib.coginvasion.*.* -i encodings.* -i base64 -i site -o tools\libcoginvasion.pyd -x panda3d __main__
echo Done building pyd!
REM mt.exe -manifest tools\libcoginvasion.pyd.manifest -outputresource:tools\libcoginvasion.pyd;2
REM del tools\libcoginvasion.pyd.manifest
pause >nul
