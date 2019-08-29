#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#SingleInstance, force


if WinActive("ProPresenter - Registered To: VALLEY CHRISTAIN CENTER")
    {
        Send {A_Args[1]}
    }else if WinExist("ProPresenter - Registered To: VALLEY CHRISTAIN CENTER")
    {
        WinActivate
        Sleep 250
        Send {A_Args[1]}
    }