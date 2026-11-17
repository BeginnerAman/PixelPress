; ============================================================
; PixelPress - Professional Image Compressor
; Inno Setup 6 Installer Script
; Output: dist\PixelPress_Setup.exe
; ============================================================

#define AppName      "PixelPress"
#define AppVersion   "2.1.0"
#define AppPublisher "Aman Vishwakarma"
#define AppExeName   "PixelPress.exe"
#define BuildDir     "dist\PixelPress"

[Setup]
AppId                    = {{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName                  = {#AppName}
AppVersion               = {#AppVersion}
AppPublisher             = {#AppPublisher}
AppCopyright             = Copyright 2026 {#AppPublisher}

DefaultDirName           = {autopf}\{#AppName}
DefaultGroupName         = {#AppName}
AllowNoIcons             = yes
DisableProgramGroupPage  = yes

OutputDir                = dist
OutputBaseFilename       = PixelPress_Setup
SetupIconFile            = icon.ico

Compression              = lzma2/ultra64
SolidCompression         = yes
LZMAUseSeparateProcess   = yes
LZMANumBlockThreads      = 4

WizardStyle              = modern
WizardImageFile          = wizard_large.bmp
WizardSmallImageFile     = wizard_small.bmp

PrivilegesRequired       = lowest
PrivilegesRequiredOverridesAllowed = commandline

VersionInfoVersion       = {#AppVersion}
VersionInfoCompany       = {#AppPublisher}
VersionInfoDescription   = {#AppName} - Professional Image Compressor Setup
VersionInfoProductName   = {#AppName} Desktop Pro
VersionInfoProductVersion = {#AppVersion}

Uninstallable            = yes
UninstallDisplayName     = {#AppName} Desktop Pro
UninstallDisplayIcon     = {app}\icon.ico
CreateUninstallRegKey    = yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";   Description: "{cm:CreateDesktopIcon}";     GroupDescription: "{cm:AdditionalIcons}";
Name: "startmenuicon"; Description: "Create Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}";

[Files]
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon.ico";      DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}";           Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}";     IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#AppName}";     Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
