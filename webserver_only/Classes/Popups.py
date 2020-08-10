import tkinter
from tkinter import Tk, Label, StringVar
from tkinter.font import Font
import threading
import time
import logging

logger = logging.getLogger(__name__)

from Classes.Exceptions import PopupError, PopupNotExist, PrematureExit


class ChangeableText:
    def __init__(self, unchanging_text, default_additional):
        self.text = unchanging_text
        self.value = default_additional
        self.changed = False

    def set_value(self, value):
        self.value = value
        self.changed = True

    def __str__(self):
        return f"{self.text} {self.value}"


class WarningPopup:
    """
    functions to remember:
    popup.open()
    popup.set_task("task name", 10: int time tasks takes)
    """
    stop = False
    popup_open = False

    def __init__(self, *args, **kwargs):
        self.win_x_size = 400
        self.win_y_size = 150
        self.timer_event = threading.Event()
        self.current_label_text = ChangeableText("Current Task:",
                                                 "No current task")
        self.time_till_label_text = ChangeableText("", "0.0")

    def start_timer(self, secs_to_count, blocking=False):
        if not self.popup_open:
            raise PopupNotExist("The Popup has been closed, " +
                                "You shouldn't start a task")
        self.timer_run = True
        if blocking:
            self._timer(secs_to_count)
        else:
            self.timer_event = threading.Event()
            self.timer_thread = threading.Thread(target=self._timer,
                                                 args=(secs_to_count,))
            self.timer_thread.start()

    def _timer(self, secs_to_count):
        last_time = 0
        end_time = time.time() + secs_to_count
        while not self.timer_event.is_set():
            try:
                time_left = end_time - time.time()
                if time_left != last_time:
                    self.time_till_label_text.set_value(round(time_left, 1))
                    last_time = time_left
                    if time_left <= 0:
                        break
                time.sleep(.06)
            except KeyboardInterrupt:
                break
        print("timer done")

    def set_task(self, task_name: str, task_time: int):
        if not self.popup_open:
            raise PopupNotExist("The Popup has been closed, " +
                                "You shouldn't start a task")
        print(f"Starting task: {task_name} which takes {task_time} seconds")
        self.set_current_label(task_name)
        self.start_timer(task_time)

    def set_current_label(self, current_task: str):
        self.current_label_text.set_value(current_task)

    def open(self):
        self.thread = threading.Thread(target=self.create)
        self.thread.start()
        self.popup_open = True

    def create(self, run_wait_time=.1):
        self.run_wait_time = run_wait_time
        self.root = Tk()
        self.root.wm_attributes("-topmost", 1)
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        pos_right = int(self.root.winfo_screenwidth()/2 - self.win_x_size/2)
        pos_up = int(self.root.winfo_screenheight()/3 - self.win_y_size/2) 
        self.root.geometry(f"{self.win_x_size}x{self.win_y_size}" +
                           f"+{pos_right}+{pos_up}")

        self.top_font = Font(self.root, "Arno 15", name="Arno_15")
        self.top_2_font = Font(self.root, "Arno 12", name="Arno_10")
        top_text = "Do Not Touch The Computer"
        top_2_text = "This window will close when\n the program is finished"

        top_label = Label(self.root, text=top_text, font="Arno_15")
        top_label.config(fg="Red")
        top_label.pack()
        top_2_label = Label(self.root, text=top_2_text, font="Arno_10")
        top_2_label.pack()
        self.current_var = StringVar()
        current_label = Label(self.root, textvariable=self.current_var).pack()
        self.time_var = StringVar()
        self.time_till_label = Label(self.root,
                                     textvariable=self.time_var).pack()
        self.loop()

    def on_exit(self, *args):
        self.timer_event.set()
        print("exited prematurely")
        self.stop = True

    def loop(self):
        while self.stop is False and not self.timer_event.is_set():
            if self.time_till_label_text.changed:
                self.time_var.set(self.time_till_label_text)
                self.time_till_label_text.changed = False
            if self.current_label_text.changed:
                self.current_var.set(self.current_label_text)
                self.current_label_text.changed = False
            try:
                self.root.update()
            except tkinter._tkinter.TclError:
                return
            time.sleep(self.run_wait_time)

        self.root.quit()
        self.popup_open = False
        return

    def close(self):
        Logger.debug("closing thread")
        self.stop = True
        self.thread.join()
        Logger.debug("thread closed")
        return


def Question(question: str, window_name: str, style="YesNo", tall=False):
    question = QuestionDialog(question, window_name, style, tall)
    while question.has_answer is False:
        time.sleep(.05)
    return question.value


class QuestionDialog():
    def __init__(self, question: str, window_name: str, style, tall):
        self.value = False
        self.has_answer = False
        self.root = tkinter.Tk()
        self.root.wm_attributes("-topmost", 1)
        self.root.winfo_toplevel().title(window_name)
        self.win_x_size = 400
        if tall is False:
            self.win_y_size = 100
        else:
            self.win_y_size = 150
        pos_right = int(self.root.winfo_screenwidth()/2 - self.win_x_size/2)
        pos_up = int(self.root.winfo_screenheight()/3 - self.win_y_size/2) 
        self.root.geometry(f"{self.win_x_size}x{self.win_y_size}" +
                           f"+{pos_right}+{pos_up}")
        self.root.positionfrom("program")
        if style == "YesNo":
            self.create_yes_no(question)

    def create_yes_no(self, question):
        self.frame = tkinter.Frame(self.root)
        self.frame.place(relx=.5, rely=.5, anchor=tkinter.screen,)
        self.label = tkinter.Label(self.frame, text=question)
        self.yes_button = tkinter.Button(self.frame,
                                         text="Yes", command=self.msg_yes,
                                         width=10,)
        self.no_button = tkinter.Button(self.frame,
                                        text="No", command=self.msg_no,
                                        width=10)
        self.label.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
        self.yes_button.grid(row=2, column=1, padx=10, pady=10)
        self.no_button.grid(row=2, column=2, padx=10, pady=10)
        self.root.mainloop()

    def msg_yes(self):
        self.value = True
        self.root.quit()
        self.has_answer = True

    def msg_no(self):
        self.value = False
        self.root.quit()
        self.has_answer = True

if __name__ == "__main__":
    Logger.debug(Question("A really simple question", "too cool"))
