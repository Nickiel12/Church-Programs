#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#SingleInstance, force

numPerSec := 100 / A_Args[2]
value := A_Args[2]
waitBetween := 1000 / numPerSec
total := waitBetween * A_Args[2]
i := 0
MsgBox, %total%
if (A_Args[1] == True){
    while (i < total){
        i++
        Send {Volume_Up}
        Sleep, waitBetween
    }
}Else{
    while (i < total){
        i++
        Send {Volume_Down}
        Sleep, waitBetween
    }
}