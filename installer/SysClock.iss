#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{B6B27268-A1EF-4FB0-9577-2F23C6EC86A1}
AppName=SysClock
AppVersion={#AppVersion}
AppPublisher=Tenqo Digital
AppPublisherURL=https://github.com/Tenqo/SysClock
AppSupportURL=https://github.com/Tenqo/SysClock/issues
AppUpdatesURL=https://github.com/Tenqo/SysClock/releases
DefaultDirName={localappdata}\Programs\SysClock
DefaultGroupName=SysClock
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=01-Windows-SysClock-Setup
SetupIconFile=..\src\sysclock\assets\digital_clock_icon.ico
UninstallDisplayIcon={app}\SysClock.exe
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
Compression=lzma2
SolidCompression=yes
CloseApplications=yes
RestartApplications=no

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "..\dist\SysClock.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\SysClock"; Filename: "{app}\SysClock.exe"
Name: "{autodesktop}\SysClock"; Filename: "{app}\SysClock.exe"; Tasks: desktopicon
