CoordMode, Mouse, Screen
#SingleInstance Force

buttonPressed := False

PgDn::
    if (buttonPressed == False){
        Run "C:\Users\nicho\Desktop\ahk mevo stream scripts\OBS Scene Switcher.ahk"
        buttonPressed = True
    } else{
        Send, {PgDn}
    }
Return