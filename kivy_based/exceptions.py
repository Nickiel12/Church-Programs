class PopupError(Exception):
    pass


class PopupNotExist(PopupError):
    pass


class PrematureExit(PopupError):
    pass
