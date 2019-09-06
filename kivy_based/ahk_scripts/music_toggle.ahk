#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#SingleInstance, force

; 5 sec
; 50 = total reps CONST

; 2 per rep
; wait of 100 milisecs

; 50/5? = 10 reps per secs?
; 1000/10 = every 100 secs.
; 

; how many timer does it run?
; frequency*total_reps = run time

numPerSec := 50 / A_Args[2]
waitBetween := 1000 / numPerSec
total := 50
i := 0
MsgBox, %total% : %numPerSec% : %waitBetween%
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