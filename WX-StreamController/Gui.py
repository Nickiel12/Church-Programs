from functools import partial
import pathlib2
import time
import os
import wx

import logging
from logging import debug
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG,
        format= '%(asctime)s - %(levelname)s - %(message)s')
        
from AHKHandeler import AHKHandeler

import option_loader
from option_loader import JSD

class ChurchGui:

    stream_live = False
    test_stream = False
    ENABLED_COLOR = wx.Colour(0, 255, 0)
    DISABLED_COLOR = wx.Colour(255, 0, 0)
    
    def __init__(self, *args, **kwargs):
        self.opt_hndl = option_loader.OptHandle()
        self.decoder = self.opt_hndl.dict
        self.App = wx.App()
        self.startFrame = StartupFrame()
        self.Frame = MainFrame()

        self.startFrame.Show()
        self.startFrame.button.Bind(wx.EVT_BUTTON, lambda event: self.show_popup())
        self.startFrame.Bind(wx.EVT_CLOSE, self.on_exit)

        self.Frame.Access.stream_panel.StreamToggleButton.Bind(
            wx.EVT_BUTTON, self.OnToggleStreamButton)
        self.Frame.Access.scene_panel.scene_radio.Bind(wx.EVT_RADIOBOX, lambda event: self.on_radio_change(
            self.Frame.Access.scene_panel.scene_radio, event
        ))
        self.Access = self.Frame.Access

        self.scene_hotkey_dict = {
            ScenePanel.scene_radio_choices["Live Camera"]: self.decoder[
                JSD.CAMERA_SCENE_OBS],
            ScenePanel.scene_radio_choices["PP Center"]: self.decoder[
                JSD.CENTER_SCREEN_OBS],
            }

    def bind_hokeys(self):
        self.ahk_handeler.camera_scene_hotkey.bind(self.on_camera_hotkey)
        self.ahk_handeler.screen_scene_hotkey.bind(self.on_center_hotkey)

    def on_camera_hotkey(self):
        self.Access.scene_panel.scene_radio.SetSelection(ScenePanel.scene_radio_choices[
            "Live Camera"])

    def on_center_hotkey(self):
        self.Access.scene_panel.scene_radio.SetSelection(ScenePanel.scene_radio_choices[
            "PP Center"])

    def on_exit(self, event):
        self.startFrame.Destroy()
        self.Frame.Destroy()
        event.Skip()

    def on_radio_change(self, radio, event):
        radio_selec = radio.GetSelection()
        hotkey = self.scene_hotkey_dict[radio_selec]
        self.ahk_handeler.OBS_send(hotkey)

    def show_popup(self):
        popup = wx.TextEntryDialog(self.startFrame, "What would you like the name of the stream to be?")
        if popup.ShowModal() == wx.ID_OK:
            self.startFrame.Unbind(wx.EVT_CLOSE, handler=self.on_exit)
            self.stream_title = popup.GetValue()
            self.switch_frames()

            self.ahk_handeler = AHKHandeler(self.stream_title, self.decoder)
            if not "test" in self.stream_title:
                self.ahk_handeler.ahk.run_script("MsgBox, 4112, Computer Working, The Computer "+
                    "is setting up the stream, please do not touch the keyboard or move the mouse!", 
                    blocking = False)
                time.sleep(.25)

                popup_window = self.ahk_handeler.ahk.win_get("Computer Working")
                popup_window.disable()
                self.ahk_handeler.chrome_facebook_live_start()
                time.sleep(21)
                popup_window.enable()
                popup_window.activate()
                popup_window.send("{Enter}")
                self.test_stream = False
                self.full_test = False
            else:
                if stream_title == "test stream":
                    self.test_stream = True
                else:
                    self.full_test = True
        else:
            self.Frame.Destroy()
            self.startFrame.Destroy()

    def switch_frames(self):
        self.startFrame.Close()
        self.Frame.Show()
        self.stream_live = False
        self.Frame.Access.stream_panel.StreamToggleButton.SetLabel("Go Live")
        self.Frame.Access.stream_panel.StreamStatusLabel.SetLabel("Not Live")
        self.Frame.Access.stream_panel.StreamStatusLabel.BackgroundColour=self.DISABLED_COLOR
    
    def OnToggleStreamButton(self, event):
        if self.stream_live == True:
            popup = wx.MessageDialog(self.Frame, "Are you sure you want to"+
                " stop the live stream?", "Are you sure", wx.YES_NO|wx.NO_DEFAULT)
            if popup.ShowModal() == wx.ID_YES:
                if self.test_stream == False:
                    if self.full_test == True:
                        self.ahk_handeler.stop_facebook_stream()
                    else:
                        self.ahk_handeler.stop_facebook_stream() # Nick's Laptop, (1804, 960), Upstairs, (1174, 922)
                self.stream_live = False
                self.Frame.Access.stream_panel.StreamToggleButton.SetLabel("Go Live")
                self.Frame.Access.stream_panel.StreamStatusLabel.SetLabel("Not Live")
                self.Frame.Access.stream_panel.StreamStatusLabel.BackgroundColour=self.DISABLED_COLOR
            else:
                event.Skip()
        else:
            popup = wx.MessageDialog(self.Frame, "Are you sure you want to"+
                " start the live stream?", "Are you sure", wx.YES_NO|wx.NO_DEFAULT)
            if popup.ShowModal() == wx.ID_YES:
                if self.test_stream == False:
                    if self.full_test == True:
                        self.ahk_handeler.start_facebook_stream((1804, 960))
                    else:
                        self.ahk_handeler.start_facebook_stream((1174, 922)) # Nick's Laptop, (1804, 960), Upstairs, (1174, 922)
                self.stream_live = True
                self.Frame.Access.stream_panel.StreamToggleButton.SetLabel("End Stream")
                self.Frame.Access.stream_panel.StreamStatusLabel.SetLabel("Stream Live")
                self.Frame.Access.stream_panel.StreamStatusLabel.BackgroundColour=self.ENABLED_COLOR
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

        path = pathlib2.Path(os.path.abspath(__file__)).parent / "resources" / "Play Button copy.jpg"
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
        edit_menu = wx.Menu()
        settings = edit_menu.Append(wx.NewId(), "Settings", "Edit the settings.")
        edit_menu.Bind(wx.EVT_MENU,self.open_settings)
        menuBar.Append(edit_menu, "&Edit")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        self.SetSize(0, 0, 400, 350)
        self.Center()

        self.panel = MainPanel(self)
        self.Access = self.panel

    def open_settings(self, event):
        pass

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
        
class StreamControllerPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        mainSizer = wx.BoxSizer()
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetSizer(mainSizer)

        self.create_stream_controller(mainSizer)
        
    def create_stream_controller(self, mainSizer):
        Stream_Sizer = wx.BoxSizer(wx.VERTICAL)

        self.StreamToggleButton = wx.Button(self, label = "Go Live")
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

    scene_radio_choices = {"Live Camera":0, "PP Center":1}

    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer()

        self.create_panel(main_sizer)

        self.SetBackgroundColour(wx.Colour(0, 255, 0))
        
        self.SetSizer(main_sizer)

    def create_panel(self, mainSizer:wx.BoxSizer):
        center_screen_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.scene_radio = wx.RadioBox(self, 
            label = "Scene Selection", 
            choices=list(self.scene_radio_choices.keys()),
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
    window.App.MainLoop()