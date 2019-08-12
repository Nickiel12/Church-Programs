import atexit
import json
import math
import threading
import time
from tkinter import Tk, Label, StringVar
from tkinter.font import Font
import tkinter
import pathlib2
import os

class ChangeableText:
    def __init__(self, unchanging_text, default_additional):
        self.text = unchanging_text
        self.value = default_additional

    def set_value(self, value):
        self.value = value

    def __str__(self):
        return f"{self.text} {self.value}"

class WarningPopup:  
    stop = False
    
    def __init__(self, *args, **kwargs):    
        self.win_x_size = 400
        self.win_y_size = 150
        self.top_label_text = "Do Not Touch The Computer"
        self.top_2_label_text = "This window will close\n when the program is finished"
        self.current_label_text = "No current Process"    
        self.time_till_label_text = ChangeableText("Time will next process:", "0.0")
        
    def open(self):
        self.thread = threading.Thread(target=self.create)
        self.thread.start()
            
    def create(self, run_wait_time = .1):
        self.root = Tk()
        pos_right = int(self.root.winfo_screenwidth()/2 -self.win_x_size/2)
        pos_up = int(self.root.winfo_screenheight()/3 - self.win_y_size/2) 
        self.root.geometry(f"{self.win_x_size}x{self.win_y_size}+{pos_right}+{pos_up}")
        
        self.top_font = Font(self.root, "Arno 15", name="Arno")
        top_var = StringVar()
        top_label = Label(self.root, textvariable=top_var, font="Arno").pack()
        top_2_var = StringVar()
        top_2_label = Label(self.root, textvariable=top_2_var).pack()
        current_var = StringVar() 
        current_label = Label(self.root, textvariable=current_var).pack()
        time_var = StringVar()
        time_till_label = Label(self.root, textvariable=time_var).pack()

        while self.stop == False:
            top_var.set(self.top_label_text)
            top_2_var.set(self.top_2_label_text)
            current_var.set(self.current_label_text)
            time_var.set(self.time_till_label_text)
            try:
                self.root.update()
            except tkinter._tkinter.TclError:
                return
            time.sleep(run_wait_time)
        self.root.quit()
            
    def close(self):
        print("closing thread")
        self.stop = True
        print("thread closed")
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
    popup = WarningPopup()
    popup.open()
    time_to_wait = 10
    current_count = 0
    for i in range(time_to_wait):
        for i in range(10):
            current_count += .1
            popup.time_till_label_text.set_value(round(time_to_wait - current_count, 1))
            time.sleep(.1)
    popup.close()