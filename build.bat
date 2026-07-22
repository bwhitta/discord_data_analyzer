py -m PyInstaller ^
--noconsole ^
--onefile ^
--clean ^
--noupx ^
--workpath .\pyinstaller ^
--distpath "." ^
--add-data "Poppins-Regular.ttf:." ^
--add-data "OFL.txt:." ^
"%~dp0main.py"

pause