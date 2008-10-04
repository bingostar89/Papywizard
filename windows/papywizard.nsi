; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "papywizard"
!define PRODUCT_VERSION "1.1"
!define PRODUCT_WEB_SITE "http://trac.gbiloba.org/papywizard"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\papywizard.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 1.67 compatible
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Language Selection Dialog Settings
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "..\licence_CeCILL_V2-en.txt"
; Components page
!insertmacro MUI_PAGE_COMPONENTS
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\papywizard.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Install.exe"
InstallDir "$PROGRAMFILES\papywizard"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Section "SectionPrincipale" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File "dist\w9xpopen.exe"
  CreateDirectory "$SMPROGRAMS\papywizard"
  CreateShortCut "$SMPROGRAMS\papywizard\papywizard.lnk" "$INSTDIR\papywizard.exe"
  CreateShortCut "$DESKTOP\papywizard.lnk" "$INSTDIR\papywizard.exe"
  ;File "dist\python25.dll"    ; pas nessaire, inclus dans library.zip
  File "dist\papywizard.exe"
  File "dist\msvcr71.dll"
  File "dist\library.zip"
  ;
  ; Sources
  File "..\__init__.py"
  SetOutPath "$INSTDIR\papywizard"
  File "..\papywizard\__init__.py"
  SetOutPath "$INSTDIR\papywizard\scripts"
  File "..\papywizard\common\*.*"
  SetOutPath "$INSTDIR\papywizard\common"
  File "..\papywizard\common\*.*"
  SetOutPath "$INSTDIR\papywizard\controller"
  File "..\papywizard\controller\*.*"
  SetOutPath "$INSTDIR\papywizard\hardware"
  File "..\papywizard\hardware\*.*"
  SetOutPath "$INSTDIR\papywizard\model"
  File "..\papywizard\model\*.*"
  SetOutPath "$INSTDIR\papywizard\view"
  File "..\papywizard\view\*.*"
  SetOutPath "$INSTDIR\share\locale\en\LC_MESSAGES"
  File "..\locale\en\LC_MESSAGES\papywizard.mo"
  SetOutPath "$INSTDIR\share\locale\fr\LC_MESSAGES"
  File "..\locale\fr\LC_MESSAGES\papywizard.mo"
  SetOutPath "$INSTDIR\share\locale\pl\LC_MESSAGES"
  File "..\locale\pl\LC_MESSAGES\papywizard.mo"
SectionEnd

;Section "GTK+ runtime" SEC02
;  SetOutPath $TEMP
;  File "dist\gtk+-2.10.13-setup.exe"
;  ExecWait '"$TEMP\gtk+-2.10.13-setup.exe" /SP- /SILENT'
;  Delete "$TEMP\gtk+-2.10.13-setup.exe"
;SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\papywizard\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\papywizard\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\papywizard.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\papywizard.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Papywizard"
;  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "GTK+ 2.10.13 runtime"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) a ete desinstalle avec succes de votre ordinateur."
FunctionEnd

Function un.onInit
!insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Etes-vous certains de vouloir desinstaller totalement $(^Name) et tous ses composants ?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\library.zip"
  Delete "$INSTDIR\msvcr71.dll"
  Delete "$INSTDIR\papywizard.exe"
  Delete "$INSTDIR\w9xpopen.exe"
  Delete "$INSTDIR\papywizard.exe.log"
  Delete "$SMPROGRAMS\papywizard\Uninstall.lnk"
  Delete "$SMPROGRAMS\papywizard\Website.lnk"
  Delete "$SMPROGRAMS\papywizard\papywizard.lnk"
  RMDir  "$SMPROGRAMS\papywizard"
  Delete "$DESKTOP\papywizard.lnk"

  ; Sources
  Delete "$INSTDIR\__init__.py"
  Delete "$INSTDIR\papywizard\__init__.py"
  Delete "$INSTDIR\papywizard\scripts\*.*"
  Delete "$INSTDIR\papywizard\common\*.*"
  Delete "$INSTDIR\papywizard\controller\*.*"
  Delete "$INSTDIR\papywizard\hardware\*.*"
  Delete "$INSTDIR\papywizard\model\*.*"
  Delete "$INSTDIR\papywizard\view\*.*"
  Delete "$INSTDIR\share\locale\en\LC_MESSAGES\papywizard.mo"
  Delete "$INSTDIR\share\locale\fr\LC_MESSAGES\papywizard.mo"
  Delete "$INSTDIR\share\locale\pl\LC_MESSAGES\papywizard.mo"
  RMDir  "$INSTDIR\papywizard\scripts"
  RMDir  "$INSTDIR\papywizard\common"
  RMDir  "$INSTDIR\papywizard\controller"
  RMDir  "$INSTDIR\papywizard\hardware"
  RMDir  "$INSTDIR\papywizard\model"
  RMDir  "$INSTDIR\papywizard\view"
  RMDir  "$INSTDIR\papywizard"
  RMDir  "$INSTDIR\share\locale\en\LC_MESSAGES"
  RMDir  "$INSTDIR\share\locale\en"
  RMDir  "$INSTDIR\share\locale\fr\LC_MESSAGES"
  RMDir  "$INSTDIR\share\locale\fr"
  RMDir  "$INSTDIR\share\locale\pl\LC_MESSAGES"
  RMDir  "$INSTDIR\share\locale\pl"
  RMDir  "$INSTDIR\share\locale"
  RMDir  "$INSTDIR\share"
  RMDir  "$INSTDIR"
  
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
