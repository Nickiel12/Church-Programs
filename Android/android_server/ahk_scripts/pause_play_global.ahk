#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#SingleInstance, force
SetTitleMatchMode, RegEx
SetTitleMatchMode, Fast

if WinExist("ahk_exe Dopamine.exe"){
    if !WinActive("ahk_exe Dopamine.exe"){
        WinActivate
        sleep 100
        Send {Media_Play_Pause}
    }
}
