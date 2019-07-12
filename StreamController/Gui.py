import wx
from enum import Enum
from types import SimpleNamespace

from functools import partial

class ChurchGui():
    
    def __init__(self, *args, **kwargs):
        self.App = wx.App()
        self.Frame = MainFrame()
        self.Frame.Show()
        self.Access = self.Frame.Access

class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(parent = None,
                        title = 'Stream Controller')
        self.panel = MainPanel(self)

        filemenu= wx.Menu()
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        self.SetSize(0, 0, 400, 400)
        self.Center()

        self.Access = self.panel.Access

class MainPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.stream_panel = StreamControllerPanel(self)
        self.scene_panel = ScenePanel(self)

        self.main_sizer.Add(self.stream_panel, 
            flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|wx.BOTTOM, border=10)
        
        self.main_sizer.Add(self.scene_panel, 1, 
            flag=wx.CENTER|wx.EXPAND|wx.ALL, border=10)
        
        self.Access = SimpleNamespace(**{"StreamPanel":self.stream_panel.AccessOptions,
            "ScenePanel":self.scene_panel.AccessOption})

class StreamControllerPanel(wx.Panel):
    streamingToggle = False
    ENABLED_COLOR = wx.Colour(0, 255, 0)
    DISABLED_COLOR = wx.Colour(255, 0, 0)

    def __init__(self, parent):
        super().__init__(parent)

        mainSizer = wx.BoxSizer()
        self.SetBackgroundColour(wx.Colour(255, 0, 0))
        self.SetSizer(mainSizer)

        self.create_stream_controller(mainSizer)

        self.AccessOptions = SimpleNamespace(**{"ToggleButton": self.StreamToggleButton})
        
    def create_stream_controller(self, mainSizer):
        Stream_Sizer = wx.BoxSizer(wx.VERTICAL)

        self.StreamToggleButton = wx.Button(self, label = "Toggle Stream Status")
        self.StreamToggleButton.Bind(wx.EVT_BUTTON, self.OnToggleStreamButton)
        Stream_Sizer.Add(self.StreamToggleButton, flag = wx.CENTER|wx.ALL, border=10)
        
        StreamHorizontal = wx.BoxSizer(wx.HORIZONTAL)
        
        StreamToggleLabel = wx.StaticText(self, label="Stream Status:")
        StreamHorizontal.Add(StreamToggleLabel, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_LEFT, border=10)

        self.StreamStatusLabel = wx.StaticText(self, label="Not Streaming")
        self.StreamStatusLabel.BackgroundColour = wx.Colour(200, 0, 0)
        
        StreamHorizontal.Add(self.StreamStatusLabel, flag=wx.TOP|wx.BOTTOM|wx.ALIGN_RIGHT, border=10)
        Stream_Sizer.Add(StreamHorizontal)

        mainSizer.Add(Stream_Sizer, flag=wx.CENTER)

    def OnToggleStreamButton(self, event):
        if self.streamingToggle == False:
            self.StreamStatusLabel.LabelText = "Streaming!!!!"
            self.StreamStatusLabel.BackgroundColour = self.ENABLED_COLOR
            self.streamingToggle = True
        else:
            self.StreamStatusLabel.LabelText = "Not Streaming"
            self.StreamStatusLabel.BackgroundColour = self.DISABLED_COLOR
            self.streamingToggle = False

class ScenePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer()

        self.create_panel(main_sizer)

        self.SetBackgroundColour(wx.Colour(0, 255, 0))

        self.AccessOption = SimpleNamespace(**{"SceneRadio":self.scene_radio,
            "SceneCheckbox":self.scene_checkbox})
        
        self.SetSizer(main_sizer)

    def create_panel(self, mainSizer:wx.BoxSizer):
        mainSizer.AddStretchSpacer()
        center_screen_sizer = wx.BoxSizer(wx.VERTICAL)

        self.scene_radio = wx.RadioBox(self, label = "Scene Selection", choices=["PP Center", "Live Camera"],
            style=wx.RA_SPECIFY_ROWS)

        self.scene_checkbox = wx.CheckBox(self, label="Auto")

        center_screen_sizer.Add(self.scene_radio, flag=wx.CENTER|wx.EXPAND)

        center_screen_sizer.Add(self.scene_checkbox, wx.SizerFlags(0).Center())

        mainSizer.Add(center_screen_sizer, wx.SizerFlags(0).Expand().Center())
        mainSizer.AddStretchSpacer()

def createGui():
    return ChurchGui()

if __name__ == "__main__":
    window = createGui()
    print(window.Access.ScenePanel.SceneRadio.Bind(wx.EVT_RADIOBOX, lambda event:
        print(window.Access.ScenePanel.SceneRadio.GetSelection())))
    window.Access.ScenePanel
    window.App.MainLoop()