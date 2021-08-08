import pathlib2
import os
import wx

from option_loader import OptHandle

class EditFrame(wx.Frame):

    def __init__(self, opt_instance:OptHandle):
        super().__init__(parent = None, title="Edit Panel")
        self.opt_handle = opt_instance
        self.setup_panel()
        self.SetSize(0, 0, 500, 750)
        self.Center()
    
    def setup_panel(self):
        panel = wx.Panel(self)
        panel.BackgroundColour = wx.Colour(50, 100, 255)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        flex_grid = wx.FlexGridSizer(2, len(self.opt_handle.dict), 2)
        sizer.Add(flex_grid, wx.SizerFlags().Center().Expand())
        
        for key_value_pair in self.opt_handle.dict.items():
            key, value = key_value_pair

            flex_grid.Add(wx.StaticText(panel, label = str(key)), wx.SizerFlags().Center())
            tmp_sizer = wx.BoxSizer()
            tmp_sizer.Add(wx.StaticText(panel, label = str(value)), wx.SizerFlags().Center())
            button = wx.Button(panel, label = "Change Hotkey")
            tmp_sizer.Add(button)
            flex_grid.Add(tmp_sizer, wx.SizerFlags().Right())
            """
            row_sizer = wx.BoxSizer()
            sizer.Add(row_sizer, wx.SizerFlags().Expand())

            left_sizer = wx.BoxSizer()
            left_label = wx.StaticText(panel, label = str(key))
            left_sizer.Add(left_label)
            row_sizer.Add(left_sizer, flags = wx.SizerFlags().Border(wx.LEFT, 20).Center())
            
            right_sizer = wx.BoxSizer()
            right_label = wx.StaticText(panel, label = str(value))
            right_button = wx.Button(panel, label = "Change Key")
            right_sizer.Add(right_label, flags = wx.SizerFlags())
            right_sizer.Add(right_button, flags = wx.SizerFlags())
            row_sizer.Add(right_sizer, flags = wx.SizerFlags().Right())
            """
        
if __name__ == "__main__":
    app = wx.App()
    frame = EditFrame(OptHandle())
    frame.Show()
    app.MainLoop()
