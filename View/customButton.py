from tkinter import ttk
import tkinter as tk
from tkinter import *

class customButton(Button):

    def __init__(self, master, pic_path, func, row, col, bg_color, state):

        saveResultsIMG = tk.PhotoImage(file=pic_path)
        super().__init__(master=master, image=saveResultsIMG,bg=bg_color, command=func, state=state)
        self.image = saveResultsIMG  # keep a reference!
        self.grid(row=row, column=col)
