import os
import pathlib2
from kivy.app import App
from Gui import GuiApp 
path = pathlib2.Path(
"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"+
"\\OBS Studio\\OBS Studio (64bit).lnk")
os.startfile(str(path))
gui_app = GuiApp()

from webserver import start_web_server
    
if __name__ == '__main__':
    start_web_server()
    gui_app.run()