@echo off
title Cog Invasion Phase File Compiler

set /p file=What phase file do you want compiled? 
ppython.exe tools\tool_Multifile.py --mtype compile --filename %file%

echo Done!
pause >nul
exit
