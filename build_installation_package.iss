[Setup]
AppName=Geoprocessamento Gabriela Figueiredo
AppVersion=1.1.0
DefaultDirName={pf}\GeoprocessamentoGabrielaF
DefaultGroupName=Geoprocessamento Gabriela Figueiredo
OutputDir=.
OutputBaseFilename=Geoprocessamento_Gabriela_F_Installer
Compression=lzma
SolidCompression=yes
SetupIconFile=geo_proc.ico

[Files]
Source: "dist\\Geoprocessamento_Gabriela_F\\*"; DestDir: "{app}"; Flags: recursesubdirs
Source: "geo_proc.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Geoprocessamento Gabriela Figueiredo"; Filename: "{app}\Geoprocessamento_Gabriela_F.exe"; IconFilename: "{app}\geo_proc.ico"
Name: "{commondesktop}\Geoprocessamento Gabriela Figueiredo"; Filename: "{app}\Geoprocessamento_Gabriela_F.exe"; Tasks: desktopicon; IconFilename: "{app}\geo_proc.ico"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\Geoprocessamento_Gabriela_F.exe"; Description: "&Iniciar ferramenta"; Flags: nowait postinstall skipifsilent