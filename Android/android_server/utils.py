import threading
import keyboard
import mouse
from functools import partial, wraps
import time
import webbrowser
import logging


from Classes.Exceptions import PopupNotExist
from Classes.Popups import WarningPopup, Question
from Classes.StreamEvents import StreamEvents as SE

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def threaded(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # logger.debug(f"starting thread with target {func}")
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def with_popup(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.popup is False:
            raise PopupNotExist
        func(self, *args, **kwargs)

    return wrapper


class Setup:
    def __init__(self, popup: WarningPopup, MasterApp):
        self.auto_contro = MasterApp.auto_contro
        self.popup = popup
        self.stream_title = MasterApp.States.stream_title
        self.settings = MasterApp.settings
        self.platform_settings = self.settings[f"setup_" +
                                               f"{self.settings['streaming_service']}"]

    def del_popup(self):
        self.popup = False

    def set_popup(self, popup):
        self.popup = popup

    def open_url(self, url, timer_time):
        logger.info(f"Opening {url}")
        self.popup.set_task("Opening Browser", timer_time)
        webbrowser.open(url)

    @with_popup
    @threaded
    def sleep(self, time_to_sleep):
        logger.info(f"setup is sleeping for {time_to_sleep}")
        self.popup.set_task("Waiting", time_to_sleep)
        time.sleep(time_to_sleep)

    @with_popup
    @threaded
    def mouse_click(self, mouse_pos: tuple, timer_time):
        self.popup.set_task("Moving & Clicking Mouse", timer_time)
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click()

    @with_popup
    @threaded
    def write(self, text: str, timer_time):
        self.popup.set_task("Entering Text", timer_time)
        keyboard.write(text)


# more black magic
def make_functions(setup_inst: Setup):
    output = []
    platform_settings = setup_inst.platform_settings
    length = len(platform_settings)
    for i in range(1, length):
        current_type = platform_settings[str(i)]["type"]
        if current_type == "Open URL":
            output.append([partial(setup_inst.open_url,
                                   platform_settings[str(i)]["value"], .2), .2])
        elif current_type == "Wait":
            output.append([partial(setup_inst.sleep,
                                   platform_settings[str(i)]["value"]), platform_settings[str(i)]["value"]])
        elif current_type == "Mouse Movement":
            output.append([partial(setup_inst.mouse_click,
                                   platform_settings[str(i)]["value"], .5), .5])
        elif current_type == "Text Field":
            output.append([partial(setup_inst.write,
                                   setup_inst.stream_title, 1), 1])
        elif current_type == "Go Live":
            setup_inst.auto_contro.settings["go_live"] = platform_settings[str(i)]["value"]
    output.append([partial(setup_inst.auto_contro.obs_send,
                           SE.START_STREAM), 1])
    return output
