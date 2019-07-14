from enum import Enum
from functools import partial
import pathlib2
from types import SimpleNamespace
import os
import wx

import logging
from logging import debug
if __name__=="__main__":
	logging.basicConfig(level=logging.DEBUG,
		format= '%(asctime)s - %(levelname)s - %(message)s')

from AHKHandeler import AHKHandeler

class ChurchGui():
    
    def __init__(self, *args, **kwargs):
        self.App = wx.App()
        self.startFrame = StartupFrame()
        self.Frame = MainFrame()
        self.startFrame.Show()
        self.startFrame.button.Bind(wx.EVT_BUTTON, lambda event: self.show_popup())
        self.Frame.Access.StreamPanel.ToggleButton.Bind(wx.EVT_BUTTON, self.OnToggleStreamButton)
        self.Access = self.Frame.Access

    def show_popup(self):
        popup = wx.TextEntryDialog(self.startFrame, "What would you like the name of the stream to be?")
        if popup.ShowModal() == wx.ID_OK:
            self.stream_title = popup.GetValue()
            self.switch_frames()
            self.ahk_handeler = AHKHandeler(self.stream_title)
            self.ahk_handeler.chrome_facebook_live_start()
        else:
            raise ValueError

    def switch_frames(self):
        self.startFrame.Close()
        self.Frame.Show()
    
    def OnToggleStreamButton(self, event):
        popup = wx.MessageDialog(self.Frame, "Are you sure", "Are you sure you want to"+
            " stop the live stream?", wx.YES_NO)
        if popup.ShowModal() == wx.ID_YES:
            self.ahk_handeler.stop_facebook_stream((1174, 922))
        else:
            event.Skip()

class StartupFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super().__init__(parent = None, title="Start Stream")
        self.startup_panel()

        self.SetSize(0, 0, 300, 250)
        self.Center()

    def startup_panel(self)->wx.Panel:
        panel = wx.Panel()
        sizer = wx.BoxSizer()
        panel.SetSizer(sizer)

        vert_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(vert_sizer, wx.SizerFlags().Center())

        path = pathlib2.Path(os.path.abspath("."))/"StreamController" / "resources" / "Play Button copy.jpg"
        image = wx.Image(str(path))
        image.Rescale(100, 100, wx.IMAGE_QUALITY_HIGH)
        bit_image = wx.Bitmap(image)

        self.button = wx.BitmapButton(self, bitmap=bit_image)
        vert_sizer.Add(self.button, wx.SizerFlags().Center())

class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(parent = None,
                        title = 'Stream Controller')

        filemenu= wx.Menu()
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        self.SetSize(0, 0, 400, 350)
        self.Center()

        self.panel = MainPanel(self)
        self.Access = self.panel.Access

class MainPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        self.BackgroundColour = wx.Colour(200, 200, 220)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.stream_panel = StreamControllerPanel(self)
        self.scene_panel = ScenePanel(self)

        self.main_sizer.Add(self.stream_panel, 
            flag=wx.CENTER|wx.TOP|wx.BOTTOM, border=10)
        
        self.main_sizer.Add(self.scene_panel,  
            flag=wx.CENTER|wx.ALL, border=10)
        
        self.Access = SimpleNamespace(**{"StreamPanel":self.stream_panel.AccessOptions,
            "ScenePanel":self.scene_panel.AccessOption})

class StreamControllerPanel(wx.Panel):

    ENABLED_COLOR = wx.Colour(0, 255, 0)
    DISABLED_COLOR = wx.Colour(255, 0, 0)

    def __init__(self, parent):
        super().__init__(parent)

        mainSizer = wx.BoxSizer()
        self.SetBackgroundColour(wx.Colour(255, 0, 0))
        self.SetSizer(mainSizer)

        self.create_stream_controller(mainSizer)

        self.AccessOptions = SimpleNamespace(**{"ToggleButton": self.StreamToggleButton,
            "StreamStatusLabel": self.StreamStatusLabel})
        
    def create_stream_controller(self, mainSizer):
        Stream_Sizer = wx.BoxSizer(wx.VERTICAL)

        self.StreamToggleButton = wx.Button(self, label = "Stop Stream")
        Stream_Sizer.Add(self.StreamToggleButton, flag = wx.CENTER|wx.ALL, border=10)
        
        StreamHorizontal = wx.BoxSizer(wx.HORIZONTAL)
        
        StreamToggleLabel = wx.StaticText(self, label="Stream Status:")
        StreamHorizontal.Add(StreamToggleLabel, flag=wx.ALL|wx.ALIGN_LEFT, border=10)

        self.StreamStatusLabel = wx.StaticText(self, label="Not Streaming")
        self.StreamStatusLabel.BackgroundColour = wx.Colour(200, 0, 0)
        
        StreamHorizontal.Add(self.StreamStatusLabel, flag=wx.ALL|wx.ALIGN_RIGHT, border=10)
        Stream_Sizer.Add(StreamHorizontal)

        mainSizer.Add(Stream_Sizer, flag=wx.CENTER)


class ScenePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer()

        self.create_panel(main_sizer)

        self.SetBackgroundColour(wx.Colour(0, 255, 0))

        self.AccessOption = SimpleNamespace(**{"Radio":self.scene_radio,
            "Checkbox":self.scene_checkbox})
        
        self.SetSizer(main_sizer)

    def create_panel(self, mainSizer:wx.BoxSizer):
        center_screen_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.scene_radio = wx.RadioBox(self, 
            label = "Scene Selection", 
            choices=["PP Center", "Live Camera"],
            style=wx.RA_SPECIFY_ROWS)

        self.scene_checkbox = wx.CheckBox(self, label="Auto")
        self.scene_checkbox.SetValue(True)
        self.scene_checkbox.Disable()

        center_screen_sizer.Add(self.scene_radio, flag=wx.CENTER|wx.EXPAND)

        center_screen_sizer.Add(self.scene_checkbox, wx.SizerFlags(0).Border(wx.LEFT, 10).Center())

        mainSizer.Add(center_screen_sizer, wx.SizerFlags(0).Center())

def createGui():
    return ChurchGui()

if __name__ == "__main__":
    window = createGui()
    print(window.Access.ScenePanel.Radio.Bind(wx.EVT_RADIOBOX, lambda event:
        print(window.Access.ScenePanel.Radio.GetSelection())))
    window.Access.ScenePanel
    window.App.MainLoop()