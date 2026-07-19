py -m PyInstaller ^
--noconsole ^
--onefile ^
--clean ^
--noupx ^
--workpath .\pyinstaller\build ^
--distpath .\pyinstaller\dist ^
--specpath .\pyinstaller ^
"%~dp0main.py"