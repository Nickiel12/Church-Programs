import atexit
import json
import threading
import time
import wx
import pathlib2
import os

class WarningPopup:  
    def open(self):
        self.app = wx.App()
        self.create()
            
    def create(self):
        self.popup = PopupFrame()
        self.popup.Show()
        self.app.MainLoop()

    def close(self):
        self.popup.Close()

class PopupFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(parent = None, title="Start Stream")
        self.build_panel()

        self.SetSize(0, 0, 300, 250)
        self.Center()

    def build_panel(self):
        panel = wx.Panel()
        sizer = wx.BoxSizer()
        panel.SetSizer(sizer)

        warning_label = wx.StaticText(self, label="Do not touch the computer")
        sizer.Add(warning_label, flags=wx.SizerFlags().Center())

def Settings():
    path = pathlib2.Path(os.path.abspath(__file__)).parent/"options.json"
    with open(path) as file:
        json_file = json.load(file)
    return DotDict(json_file)

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    def __init__(self, iterable):
        super().__init__()
        if isinstance(iterable, dict):
            for k, v in iterable.items():
                self[k] = v

    def __getattr__(*args):
        val = dict.get(*args)
        return DotDict(val) if type(val) is dict else val
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__ 

if __name__ == "__main__":
    popup = WarningPopup()
    popup.open()
    time.sleep(5)
    popup.close()