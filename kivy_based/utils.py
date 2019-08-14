import atexit
import json
import math
import threading
import time
import timeit
from tkinter import Tk, Label, StringVar
from tkinter.font import Font
import tkinter
import pathlib2
import os

import logging
from logging import debug
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG,
        format= '%(asctime)s - %(levelname)s - %(message)s')

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
    
    def __init__(self, *args, **kwargs):
        self.win_x_size = 400
        self.win_y_size = 150
        self.current_label_text = ChangeableText("Current Task:", "No current task")    
        self.time_till_label_text = ChangeableText("Time till next task:", "0.0")

    def start_timer(self, secs_to_count, blocking=False):
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
                #debug(f"time_left is {time_left}")
                #debug(f"end_time is {end_time}")
                if time_left != last_time:
                    popup.time_till_label_text.set_value(round(time_left, 1))
                    last_time = time_left
                    if time_left <= 0:
                        break
            except KeyboardInterrupt:
                break

    def set_task(self, task_name:str, task_time:int):
        self.set_current_task(task_name)
        self.start_timer(task_time)

    def set_current_task(self, current_task:str):
        self.current_label_text.set_value(current_task)

    def open(self):
        self.thread = threading.Thread(target=self.create)
        self.thread.start()
            
    def create(self, run_wait_time = .1):
        self.run_wait_time = run_wait_time
        self.root = Tk()
        pos_right = int(self.root.winfo_screenwidth()/2 -self.win_x_size/2)
        pos_up = int(self.root.winfo_screenheight()/3 - self.win_y_size/2) 
        self.root.geometry(f"{self.win_x_size}x{self.win_y_size}+{pos_right}+{pos_up}")
        
        self.top_font = Font(self.root, "Arno 15", name="Arno_15")
        self.top_2_font = Font(self.root, "Arno 12", name="Arno_10")
        top_text = "Do Not Touch The Computer"
        top_2_text = "This window will close when\n the program is finished"

        top_label = Label(self.root, text = top_text, font="Arno_15").pack()
        top_2_label = Label(self.root, text = top_2_text, font = "Arno_10").pack()
        self.current_var = StringVar() 
        current_label = Label(self.root, textvariable=self.current_var).pack()
        self.time_var = StringVar()
        self.time_till_label = Label(self.root, textvariable=self.time_var).pack()
        
        self.loop()
        
    def loop(self):
        while self.stop == False:
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

    def close(self):
        debug("closing thread")
        self.stop = True
        self.thread.join()
        debug("thread closed")
        return

def Settings():
    path = pathlib2.Path(os.path.abspath(__file__)).parent/"options.json"
    with open(path) as file:
        json_file = json.load(file)
    return DotDict(json_file)

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    def __init__(self, iterable):
        super().__init__()
        if isinstance(iterable, dict):
            for k, v in iterable.items():
                self[k] = v

    def __getattr__(*args):
        val = dict.get(*args)
        return DotDict(val) if type(val) is dict else val
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__ 

if __name__ == "__main__":
    try:
        begin_time = time.time() 
        popup = WarningPopup()
        popup.open()
        
        popup.set_task("Waiting", 10)
        time.sleep(20)

        popup.start_timer(10, blocking=False)
        time.sleep(10)

        popup.close()
    except KeyboardInterrupt:
        if popup.timer_thread and popup.timer_thread.isAlive():
            popup.timer_event.set()
        popup.close()
        debug("Program Force Closed")
        print(f"Program took {time.time() - begin_time}")