; Inno Setup script for JournalTherapyCat
; Save this file and open it with Inno Setup (https://jrsoftware.org/) to compile an installer.

[Setup]
AppName=JournalTherapyCat
AppVersion=1.0
DefaultDirName={pf}\JournalTherapyCat
DefaultGroupName=JournalTherapyCat
Compression=lzma2
SolidCompression=yes
OutputBaseFilename=JournalTherapyCat-Installer
DisableDirPage=no
DisableProgramGroupPage=no

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Files]
; Copy the single-file EXE and the optional DB and README
Source: "{#src}\dist\JournalTherapyCat.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#src}\dist\journal.db"; DestDir: "{app}"; Flags: ignoreversion uninsneveruninstall
Source: "{#src}\dist\README.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\JournalTherapyCat"; Filename: "{app}\JournalTherapyCat.exe"
Name: "{commondesktop}\JournalTherapyCat"; Filename: "{app}\JournalTherapyCat.exe"; Tasks: createDesktopIcon

[Run]
Filename: "{app}\JournalTherapyCat.exe"; Description: "Starte JournalTherapyCat"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\journal.db"

; Helper: Set a compiler variable with the project root to keep paths relative when opened from this folder
[Code]
procedure InitializeSetup;
begin
  ExpandConstant('{srcexe}');
end
