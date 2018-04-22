"""
     The GUI module. We followed the MVC architecture - This package is only responsible for creating the UI, receiving
the user input and sending it to the controller. It contains a reference of the control and utilizes some of its'
functions.

Date: 31.12 1:34 am

The layers are as so:

 ________________________main_ frame_________________________________
|                                                                    |
| ________search_frame___________  __________results_frame__________ |
||                               ||                                 ||
|| ______search_window__________ || ____________LOGO_______________ ||
|||                             ||||                               |||
|||                             ||||  _____search_results________  |||
|||  [query entry][load query]  |||| |                           | |||
|||  [checkbox]                 |||| |  1.                       | |||
|||                             |||| |  2.                       | |||
|||_______search_button_________|||| |  3.                       | |||
|||                             |||| |  .                        | |||
|||                             |||| |  .                        | |||
|||                             |||| |  .                        | |||
|||           START             |||| |  .                        | |||
|||                             |||| |                           | |||
|||                             |||| |___________________________| |||
|||                             ||||                               |||
|||_______bottom_buttons________||||  _______save_results________  |||
|||                             |||| |                           | |||
||| Load index     Reset        |||| |                           | |||
|||                             |||| |___________________________| |||
|||_____________________________||||_______________________________|||
||_______________________________||_________________________________||
|____________________________________________________________________|
"""
from tkinter import messagebox
from Controller import Control
from tkinter.filedialog import askdirectory, asksaveasfilename, askopenfilename
from View.customButton import customButton
from tkinter import *
import tkinter as tk
from tkinter.ttk import Separator, Style
import os
import _thread

cwd = os.getcwd()  # current working directory


class EngineGUI:
    """
    CTOR - receives the root window and the controller that will utilize this GUI.
    """

    def __init__(self, master, controller):

        # Declaring the class' data members.
        self.controller = controller
        self.expand_mode = IntVar()  # an IntVar representing if we should expand or not
        self.summ_mode = IntVar()  # an IntVar representing if we should summarize or not
        self.stem_mode = IntVar()  # an IntVar representing if we should stem or not
        self.query_line = Entry()  # The input query
        self.doc_id_entry = Entry()  # the doc id that the user would like to retrieve.
        self.start_search_BTN = Button()  # The start button
        self.reset_BTN = Button()  # The reset button
        self.save_results_BTN = Button()  # Save results button
        self.enter_query_BTN = Button()  # Enter query file button
        self.load_index_files_BTN = Button()  # Load index file button
        self.index_file_path = ""  # The file path to the index files..
        self.query_file_path = ""  # The path where the query files are saved
        self.save_results_path = ""  # The file path where the results are to be saved.
        self.query_results = Text()  # The results of the query
        self.doc_results_text = Text()  # the text widget that will display the document content
        self.results_list = []  # The list that the controller sends after a manual query search
        self.query_results_list = []  # The list that the controller sends after a query file search

        self.__main_frame = Frame(master)  # The main frame
        self.__main_frame.config(bg='white')
        self.__set_up_search_frame()  # configure the search frame
        self.__set_up_results_frame()  # configure the results frame
        self.__set_up_doc_search_frame()  # configure the frame with the doc search option

        self.__set_up_separators()  # Window separator and Style

        self.__main_frame.pack()

    """ Configure the top and middle separators using the Separator class."""

    def __set_up_separators(self):
        vertical_sep1 = Separator(self.__main_frame, orient="vertical")
        vertical_sep2 = Separator(self.__main_frame, orient="vertical")
        vertical_sep1.grid(column=1, row=0, sticky="ns", rowspan=5)
        vertical_sep2.grid(column=3, row=0, sticky="ns", rowspan=5)
        horizontal_sep = Separator(self.__main_frame, orient="horizontal")
        horizontal_sep.grid(column=0, row=0, sticky="ew", columnspan=5)
        self.__main_frame.grid_rowconfigure(0, minsize=4, pad=0)  # create some space from the top

        sty = Style(self.__main_frame)
        sty.configure("TSeparator", background="DeepSkyBlue2")

    """ Setting up the left (search) frame. Adds the search engine logo, and calls 3 functions to completely set it
    up. """

    def __set_up_search_frame(self):
        global cwd
        __searchFrame = Frame(self.__main_frame, pady=3)  # The left frame of the window. contains the search box etc.
        __searchFrame.config(borderwidth=2, bg='white')
        __searchFrame.grid(row=1, column=0, sticky=N)  # row 1 of the main frame. Sticks it to the top

        search_img = tk.PhotoImage(file=cwd + '/Resources/searchLogo.png')  # The search engine logo!
        search_label = Label(master=__searchFrame, image=search_img, bg='white')
        search_label.image = search_img  # keep a reference!
        search_label.grid(row=0)

        self.set_up_search_window(__searchFrame)
        self.set_up_search_button_frame(__searchFrame)
        self.set_up_bottom_buttons_frame(__searchFrame)

    """ The right (results) frame of the GUI. Here we add the results logo, call the function to set up the text
    widget that displays the results, and create the button that lets us save the results. """

    def __set_up_results_frame(self):
        global cwd
        __resultsFrame = Frame(self.__main_frame, pady=3)  # The right frame. Contains the results window
        __resultsFrame.config(bg='white')

        results_img = tk.PhotoImage(file=cwd + '/Resources/ResultsLogo.png')
        result_label = Label(master=__resultsFrame, image=results_img, bg='white')
        result_label.image = results_img  # keep a reference!
        result_label.grid(row=0)
        self.set_up_query_result_frame(__resultsFrame)
        self.save_results_BTN = customButton(__resultsFrame, cwd + '/Resources/SaveResultsLogo.png',
                                             self.__fn_save_results, 2, 0, '#81bbf1', state=DISABLED)
        __resultsFrame.grid(row=1, column=2, sticky=N)

    """ The frame that presents the content of a given document. """

    def __set_up_doc_search_frame(self):
        global cwd
        __docResultsFrame = Frame(self.__main_frame, pady=3)  # The right frame. Contains the results window
        __docResultsFrame.config(bg='white')

        results_img = tk.PhotoImage(file=cwd + '/Resources/ResultsLogo.png')
        result_label = Label(master=__docResultsFrame, text="Display Document Contents", bg='white',
                             font=("Times", 25, "bold"), justify=CENTER)
        result_label.image = results_img  # keep a reference!
        result_label.grid(row=0, column=0, columnspan=2)
        self.__set_up_doc_content_frame(__docResultsFrame)  # initialize the text widget
        self.doc_id_entry = Entry(master=__docResultsFrame, justify=LEFT, width=23, font=("Times", 15, "bold"),
                                  highlightcolor='orange', selectbackground='tomato', selectforeground='white')
        self.doc_id_entry.grid(row=1, column=0)
        display_text_btn = Button(__docResultsFrame, command=self.__fn_display_doc, text="Load Document Contents",
                                  bg="DeepSkyBlue2", fg="white", font=('Times', 14, "bold"))
        display_text_btn.grid(row=1, column=1)

        __docResultsFrame.grid(row=1, column=4, sticky=N)

    """ Sets up the 1st window of the search frame. Here we have the entry for the query, the button that lets us
    choose a query file and the checkbox. It will be in the 2nd row of the search frame"""

    def set_up_search_window(self, master):
        global cwd
        searchWindow = Frame(master, bg='white')  # create entry line and enter query file button
        master.grid_rowconfigure(1, minsize=20)  # space between the search logo and query frame
        checkFrame = Frame(searchWindow, bg='white')
        checkFrame.grid(row=1, column=0)
        queryFrame = Frame(searchWindow, bg='white')
        queryFrame.grid(row=0, column=0)

        self.query_line = Entry(master=queryFrame, justify=LEFT, width=22, font=("Times", 16, "bold"),
                                highlightcolor='orange', selectbackground='tomato', selectforeground='white')
        self.enter_query_BTN = customButton(queryFrame, cwd + '/Resources/enterQueryPic.png',
                                            self.__fn_browse_query_file, row=0, col=1, bg_color='#81bbf1', state=NORMAL)
        self.query_line.grid(row=0, column=0)
        expand_box = Checkbutton(master=checkFrame, text="Expand", variable=self.expand_mode,
                                 height=1, width=10, font=("Times", 16, "bold"), selectcolor='RoyalBlue2', bg='white',
                                 bd=5, justify=LEFT)
        summ_box = Checkbutton(master=checkFrame, text="Summarize", variable=self.summ_mode,
                               height=1, font=("Times", 16, "bold"), selectcolor='RoyalBlue2', bg='white',
                               bd=5)
        stem_checkBox = Checkbutton(master=checkFrame, text="Use Stemmer?", variable=self.stem_mode,
                                    height=1, font=("Times", 16, "bold"), selectcolor='RoyalBlue2', bg='white', bd=5)
        expand_box.grid(row=0, column=0)
        summ_box.grid(row=0, column=1)
        stem_checkBox.grid(row=0, column=2)
        searchWindow.grid(row=2)  # row 2 of the main frame

    """ Sets up the frame that holds the Search button. """

    def set_up_search_button_frame(self, master):
        global cwd
        searchButtonFrame = Frame(master)
        master.grid_rowconfigure(3, minsize=30)  # space between query frame and search button
        self.start_search_BTN = customButton(searchButtonFrame, cwd + '/Resources/startSearch.png',
                                             self.__fn_search, 2, 0, '#81bbf1', state=NORMAL)
        searchButtonFrame.config(bg='white')
        searchButtonFrame.grid(row=4)

    """ Sets up the frame that contains the load index file button and the reset button. Also creates the gap between
     the Search button and the bottom buttons. """

    def set_up_bottom_buttons_frame(self, master):
        global cwd
        bottomButtonsFrame = Frame(master)
        bottomButtonsFrame.config(bg='white')
        master.grid_rowconfigure(5, minsize=100)  # space between search button and load/reset buttons
        self.load_index_files_BTN = customButton(bottomButtonsFrame, cwd + '/Resources/load Index Files pic.png',
                                                 self.__fn_load_index_files, row=0, col=0, bg_color='firebrick',
                                                 state=NORMAL)
        self.reset_BTN = customButton(bottomButtonsFrame, cwd + '/Resources/reset pic.png',
                                      self.__fn_reset_memory, row=0, col=1, bg_color='#781605', state=NORMAL)
        bottomButtonsFrame.grid(row=6)

    """ sets up the text widget that will display the search results. Also initializes the scroll bar"""

    def set_up_query_result_frame(self, master):
        results_box = Frame(master)  # the frame that contains the results
        results_box.grid(row=1)
        scroll_bar = Scrollbar(results_box, troughcolor='light steel blue', bg='#81bbf1')
        self.query_results = Text(results_box, height=13, width=50, relief=FLAT, state=DISABLED)
        scroll_bar.pack(side=RIGHT, fill=Y)
        self.query_results.pack(side=LEFT, fill=Y)
        scroll_bar.config(command=self.query_results.yview)
        self.query_results.config(yscrollcommand=scroll_bar.set, fg='DeepSkyBlue4', font=('Times', 14, "bold"),
                                  wrap=WORD)

    """sets up the text widget that will display the search results. Also initializes the scroll bar"""

    def __set_up_doc_content_frame(self, master):
        results_box = Frame(master)  # the frame that contains the results
        results_box.grid(row=2, columnspan=2)
        scroll_bar = Scrollbar(results_box, troughcolor='light steel blue', bg='#81bbf1')
        self.doc_results_text = Text(results_box, height=14, width=50, relief=FLAT, state=DISABLED)
        scroll_bar.pack(side=RIGHT, fill=Y)
        self.doc_results_text.pack(side=LEFT, fill=Y)
        scroll_bar.config(command=self.doc_results_text.yview)
        self.doc_results_text.config(yscrollcommand=scroll_bar.set, fg='DeepSkyBlue4', font=('Times', 14, "bold"),
                                     wrap=WORD)

    """ BUTTON FUNCTIONS """

    """ The function called when the search button is pressed. Calls the relevant function in the controller, and 
    supplies it with the query and the status of the checkbox. """

    def __fn_search(self):
        # print("The query: %s" % self.query_line.get())
        # print("Expand/Summarize box mode: ", self.check_mode.get())
        # print("Stem box mode: ", self.stem_mode.get())

        if len(self.index_file_path) == 0:
            print("No index file loaded!")
            messagebox.showwarning(title="Oops!", message="Please load the index files first.",
                                   parent=self.__main_frame)
        elif self.query_line.get() == "" and len(self.query_file_path) == 0:
            print("No query line OR query file given!")
            messagebox.showwarning(title="Oops!", message="Please enter a query or load a query file first.",
                                   parent=self.__main_frame)
        else:
            self.query_results.config(state=NORMAL)
            self.query_results.delete(1.0, END)
            self.query_results.config(state=DISABLED)  # Read only mode
            self.controller.fn_search(self.query_line.get(), self.expand_mode.get(), self.stem_mode.get(),
                                      self.index_file_path, self.summ_mode.get())

    """ The function called when the load index files button is pressed. Opens a file browser window and send it to
    the controller. """

    def __fn_load_index_files(self):
        global cwd
        title = "Choose Cache and Dictionary Location to Load"
        dir1 = '/home/tomer/Downloads/IR/Search Engine Output'
        path = askdirectory(title=title, initialdir=dir1)
        if len(path) > 0:
            self.index_file_path = path
            self.controller.load_data(self.index_file_path, self.stem_mode.get())
            self.load_index_files_BTN.config(bg="green")
        else:
            print("Load cache and Dict was cancled..")

    """ The function called when the reset button is pressed. Clears the data structures in the program and calls the
     relevant function in the controller. """

    def __fn_reset_memory(self):
        self.query_line.delete(0, END)
        self.doc_id_entry.delete(0, END)
        self.index_file_path = ""
        self.query_file_path = ""

        self.save_results_BTN.config(state=DISABLED)
        self.load_index_files_BTN.config(bg='firebrick')
        self.query_results.config(state=NORMAL)  # Read only mode
        self.query_results.delete(1.0, END)
        self.query_results.config(state=DISABLED)  # Read only mode

        self.doc_results_text.config(state=NORMAL)  # Read only mode
        self.doc_results_text.delete(1.0, END)
        self.doc_results_text.config(state=DISABLED)  # Read only mode

        if os.path.exists(self.save_results_path):
            os.remove(self.save_results_path)

    """ The function called by the controller when the query results return. It displays the results on the text
    widget in the results frame """

    def fn_write_results_to_GUI(self, time, filenum, results):

        self.query_results.config(state=NORMAL)  # Read only mode
        self.query_results.delete(1.0, END)
        self.save_results_BTN.config(state=NORMAL, command=self.__fn_save_results)  # Now we can save the results
        self.query_results.insert(END, "Time Elapsed: %s seconds\n" % time)
        self.query_results.insert(END, "Files retrieved: %s\n" % filenum)
        for i in range(0, len(results)):
            line = "%d. %s \n" % (i + 1, results[i])
            self.query_results.insert(END, line)
        self.query_results.config(state=DISABLED)  # Read only mode
        self.start_search_BTN.config(state=NORMAL)
        self.results_list = results

    """ The function called by the controller when the query FILE results return. It displays the results on the text
    widget in the results frame """

    def fn_write_query_file_to_GUI(self, time, query_num, query_results):

        self.query_results.config(state=NORMAL)  # Read only mode
        self.query_results.delete(1.0, END)
        self.save_results_BTN.config(state=NORMAL,
                                     command=self.__fn_save_query_file_results)  # Now we can save the results
        self.query_results.insert(END, "Time Elapsed: %s seconds\n" % time)
        self.query_results.insert(END, "Queries retrieved: %s\n" % query_num)
        for k in range(query_num):  # iterates over the queries.
            title = "\n----- Results For Query Number %d, Query ID: %s -----\n" % (k + 1, query_results[k][0])
            self.query_results.insert(END, title)
            for i in range(0, len(query_results[k][1])):
                line = "%d. %s \n" % (i + 1, query_results[k][1][i])
                self.query_results.insert(END, line)
        self.query_results.config(state=DISABLED)  # Read only mode
        self.start_search_BTN.config(state=NORMAL)
        self.enter_query_BTN.config(state=NORMAL)
        self.load_index_files_BTN.config(state=NORMAL)
        self.reset_BTN.config(state=NORMAL)
        self.query_results_list = query_results

    """ The function called when the save results button is pressed. Opens a file browser to save the query results
     given by the controller. Then calls the controller and saves the files appropriately """

    def __fn_save_results(self):
        global cwd
        dir1 = cwd  # initial directory
        title = "Select where to save results"
        file_types = (("text file", "*.txt"),)
        self.save_results_path = asksaveasfilename(initialdir=dir1, title=title, filetypes=file_types,
                                                   initialfile="results.txt")
        if len(self.save_results_path) == 0:
            print("canceled saving results..")
        else:
            print("saving results at %s" % self.save_results_path)
            self.controller.fn_save_results(self.results_list, self.save_results_path)

    """ The function that is called when the user wishes to save the results of a query file search """

    def __fn_save_query_file_results(self):
        global cwd
        dir1 = cwd  # initial directory
        title = "Select where to save results"
        file_types = (("text file", "*.txt"),)
        self.save_results_path = asksaveasfilename(initialdir=dir1, title=title, filetypes=file_types,
                                                   initialfile="results.txt")
        if len(self.save_results_path) == 0:
            print("canceled saving results..")
        else:
            print("saving results at %s" % self.save_results_path)
            self.controller.fn_save_query_file_results(self.query_results_list, self.save_results_path)

    """ The function called when the load query file button is pressed. Opens a file browser to open a query file.
    saves the path and notifies the controller by using the appropriate function. """

    def __fn_browse_query_file(self):
        global cwd
        dir1 = '/home/tomer/Downloads/IR'  # initial directory
        title = "Choose query file to load"
        file_types = (("Text file", "*.txt"),)
        self.query_file_path = askopenfilename(initialdir=dir1, title=title, filetypes=file_types)

        if len(self.query_file_path) == 0:  # check if a query file was chosen
            print("cancled file browse..")
        elif len(self.index_file_path) == 0:  # check if the index files were chosen
            print("No index file loaded!")
            messagebox.showwarning(title="Oops!", message="Please load the index files first.",
                                   parent=self.__main_frame)
        else:
            print("Path of query files: \n %s" % self.query_file_path)
            # self.controller.fn_run_query_file(self.query_file_path, self.stem_mode.get(), self.index_file_path)
            query_file_thread = _thread.start_new_thread(self.controller.fn_run_query_file, (self.query_file_path,
                                                                                     self.stem_mode.get(),
                                                                                     self.index_file_path), )
            self.query_line.delete(0, END)
            self.start_search_BTN.config(state=DISABLED)
            self.enter_query_BTN.config(state=DISABLED)
            self.load_index_files_BTN.config(state=DISABLED)
            self.reset_BTN.config(state=DISABLED)

    """ This function is called when the user would like to display the text of a certain documents. """

    def __fn_display_doc(self):
        self.doc_results_text.config(state=NORMAL)  # Read only mode
        self.doc_results_text.delete(1.0, END)
        self.doc_results_text.config(state=DISABLED)  # Read only mode
        results = Control.get_text_from_document(self.doc_id_entry.get(), self.index_file_path)
        self.fn_write_doc_contents(results)

    """ This function sets up the (optional) frame that lets the user display the contents of a specified document"""

    def fn_write_doc_contents(self, contents):

        self.doc_results_text.config(state=NORMAL)  # Read only mode
        self.doc_results_text.insert(END, contents)
        self.doc_results_text.config(state=DISABLED)  # Read only mode
