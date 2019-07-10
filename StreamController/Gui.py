import wx
from enum import Enum
from types import SimpleNamespace

myEnum = Enum("GuiEnums", ' '.join([
    "button1",
    "button2"
]))

class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(parent = None,
                        title = 'Stream Controller')
        self.panel = MainPanel(self)

class MainPanel(wx.Panel):

    streamingToggle = False
    ENABLED_COLOR = wx.Colour(0, 255, 0)
    DISABLED_COLOR = wx.Colour(255, 0, 0)

    def __init__(self, parent):
        super().__init__(parent)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)
        
        self.Stream_Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Visible_Screen_Sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer.Add(self.Stream_Sizer, flag=wx.CENTER)
        self.main_sizer.Add(self.Visible_Screen_Sizer, flag=wx.CENTER)

        StreamToggleButton = wx.Button(self, label = "Toggle Stream Status")
        StreamToggleButton.Bind(wx.EVT_BUTTON, self.OnToggleButton)
        self.Stream_Sizer.Add(StreamToggleButton, flag = wx.CENTER|wx.ALL, border=10)
        
        self.StreamToggleLabel = wx.StaticText(self, label="Stream Status:")

        self.StreamStatusLabel = wx.StaticText(self, label="Not Streaming")
        self.StreamStatusLabel.BackgroundColour = wx.Colour(200, 0, 0)
        
        StreamHorizontal = wx.BoxSizer(wx.HORIZONTAL)
        StreamHorizontal.Add(self.StreamToggleLabel, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_LEFT, border=10)
        StreamHorizontal.Add(self.StreamStatusLabel, flag=wx.TOP|wx.BOTTOM|wx.ALIGN_RIGHT, border=10)
        self.Stream_Sizer.Add(StreamHorizontal)

    def OnToggleButton(self, event):
        if self.streamingToggle == False:
            self.StreamStatusLabel.LabelText = "Streaming!!!!"
            self.StreamStatusLabel.BackgroundColour = self.ENABLED_COLOR
            self.streamingToggle = True
        else:
            self.StreamStatusLabel.LabelText = "Not Streaming"
            self.StreamStatusLabel.BackgroundColour = self.DISABLED_COLOR
            self.streamingToggle = False


def createWindow():
    mainApp = wx.App()
    mainFrame = MainFrame()
    mainFrame.Show()
    return SimpleNamespace(**{"App": mainApp, "Frame": mainFrame})

if __name__ == "__main__":
    window = createWindow()
    window.App.MainLoop()