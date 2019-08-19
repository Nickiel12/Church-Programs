import pathlib2
import os

from Gui import GuiApp

path = pathlib2.Path(
    "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"+
    "\\OBS Studio\\OBS Studio (64bit).lnk")
os.startfile(str(path))
app = GuiApp()
app.run()