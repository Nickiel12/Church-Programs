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

    def __init__(self, parent):
        super().__init__(parent)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)
        self.topSizer = wx.BoxSizer(wx.VERTICAL)

        self.topLeftButton = wx.Button(self, label="Press Me!!!!",)

        self.topSizer.Add(self.topLeftButton, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.main_sizer.Add(self.topSizer, 0, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)


def createWindow():
    mainApp = wx.App()
    mainFrame = MainFrame()
    mainFrame.Show()
    return SimpleNamespace(**{"App": mainApp, "Frame": mainFrame})

if __name__ == "__main__":
    window = createWindow()
    window.App.MainLoop()