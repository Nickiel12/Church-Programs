import os
import subprocess
import pathlib2
from kivy.app import App

from Gui import GuiApp
from utils import Settings
from webserver import start_web_server

settings = Settings()

ahk_files_path = pathlib2.Path(os.path.abspath(__file__)).parent/"ahk_scripts"

for name, value in settings.startup.items():
    if name[:3] == "open" and value == True:
        program = name[4:]
        print(f"Setup program trying to open is {program}")
        program_path = settings.startup[str(program)+"_path"]
        subprocess.call([str(ahk_files_path/"program_opener.exe"),
                            f".*{program}.*", program_path])

gui_app = GuiApp()

if __name__ == '__main__':
    start_web_server()
    gui_app.run()
    