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

        self.createStreamController(self.main_sizer)

        self.createCenterController(self.main_sizer)

    def createCenterController(self, mainSizer):
        self.Center_Screen_Sizer = wx.BoxSizer()
        
        self.SceneControllerLabel = wx.StaticText(self, label="Scene Options")
        self.Center_Screen_Sizer.Add(self.SceneControllerLabel, 
            flag = wx.CENTER|wx.ALL, border=10)
        self.CurrentSceneLabel = wx.StaticText(self, label="Currently No Scene")

    def createStreamController(self, mainSizer):
        self.Stream_Sizer = wx.BoxSizer(wx.VERTICAL)

        self.StreamToggleButton = wx.Button(self, label = "Toggle Stream Status")
        self.StreamToggleButton.Bind(wx.EVT_BUTTON, self.OnToggleStreamButton)
        self.Stream_Sizer.Add(self.StreamToggleButton, flag = wx.CENTER|wx.ALL, border=10)
        
        self.StreamToggleLabel = wx.StaticText(self, label="Stream Status:")

        self.StreamStatusLabel = wx.StaticText(self, label="Not Streaming")
        self.StreamStatusLabel.BackgroundColour = wx.Colour(200, 0, 0)
        
        StreamHorizontal = wx.BoxSizer(wx.HORIZONTAL)
        StreamHorizontal.Add(self.StreamToggleLabel, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_LEFT, border=10)
        StreamHorizontal.Add(self.StreamStatusLabel, flag=wx.TOP|wx.BOTTOM|wx.ALIGN_RIGHT, border=10)
        self.Stream_Sizer.Add(StreamHorizontal)

        mainSizer.Add(self.Stream_Sizer, flag=wx.CENTER)


    def OnToggleStreamButton(self, event):
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