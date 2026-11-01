#ifndef AppVersion
  #error AppVersion required
#endif
#define AppName "Codex Token Usage Monitor"
[Setup]
AppId={{B0BB9691-1988-4CBA-81D8-BD5CE2578248}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Codex Token Usage Monitor contributors
AppPublisherURL=https://github.com/3271741455CJ/Codex-Token-Usage-Monitor
AppSupportURL=https://github.com/3271741455CJ/Codex-Token-Usage-Monitor/issues
AppUpdatesURL=https://github.com/3271741455CJ/Codex-Token-Usage-Monitor/releases
DefaultDirName={localappdata}\Programs\Codex-Token-Usage-Monitor
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
LicenseFile=..\LICENSE
OutputDir=..\release
OutputBaseFilename=Codex-Token-Usage-Monitor-{#AppVersion}-windows-x64-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\Codex-Token-Usage-Monitor.exe
CloseApplications=yes
RestartApplications=no
SetupLogging=no
SignedUninstaller=yes
#ifdef SigningEnabled
SignTool=release_sign
#endif

[Files]
Source: "..\dist\Codex-Token-Usage-Monitor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\Codex-Token-Usage-Monitor.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\Codex-Token-Usage-Monitor.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Codex-Token-Usage-Monitor.exe"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
