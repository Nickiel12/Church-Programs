CoordMode, Mouse, Screen
#SingleInstance Force

    if WinExist("ProPresenter - Registered To: VALLEY CHRISTAIN CENTER")
    {
        WinActivate
        Sleep 250
        Send {PgDn}
    }

        WinActivate ahk_class Qt5QWindowIcon
        Sleep 350
        Send !j
        Sleep 100

    if WinExist("ProPresenter - Registered To: VALLEY CHRISTAIN CENTER")
    {
        WinActivate
    }        

        Sleep 30000

        WinActivate, ahk_class Qt5QWindowIcon
        Sleep 350
        Send ^j
        Sleep 100

    if WinExist("ProPresenter - Registered To: VALLEY CHRISTAIN CENTER")
    {
        WinActivate
    }
    Run, "C:\Users\nicho\Desktop\ahk mevo stream scripts\SceneChange.ahk"
    ExitApp