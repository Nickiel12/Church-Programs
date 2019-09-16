import os
import pathlib2
from kivy.app import App

from Gui import GuiApp
from utils import Settings
from webserver import start_web_server

settings = Settings()

programs_to_open = {}
for name, value in settings.startup:
    if name[:3] == "open" and value == True:
        program = name[4:]
        programs_to_open[program] = settings.startup[str(program)+"_path"]

for i in programs_to_open.keys():
    os.startfile(programs_to_open[i])

gui_app = GuiApp()

if __name__ == '__main__':
    start_web_server()
    gui_app.run()
    