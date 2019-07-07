import wx
if __name__ != "__main__":
    import StreamController.Gui as Gui
else:
    import Gui

controllerGui = Gui.createWindow()
controllerGui.App.MainLoop()