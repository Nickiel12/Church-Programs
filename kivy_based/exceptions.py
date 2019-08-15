class PopupError(Exception):
    pass

class PopupNotExist(PopupError):
    pass

class PopupClosed(PopupError):
    pass
