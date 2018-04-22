"""
The GUI module. We followed the MVC architecture - This package is only responsible for creating the UI, receiving
the user input and sending it to the controller. It contains a reference of the control and utilizes some of its'
functions.
"""
from Controller import Control
import tkinter.ttk as ttk
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import _thread
import time
import datetime
import os

sec = 0  # Used to measure the current time elapsed. Starts at 0
continueClockLoop = True  # A global variable that determines if to continue displaying the time or not
loaded_dict_docs = 0


class View:
    """
    CTOR - receives the root window and the controller that will utilize this GUI.
    buttonWidth and buttonHeight are the default sizes of the buttons that they all used. We initialized it here for
    easy configuration of the button sizing. fontSize is the font of the text displayed inside the buttons.
    """

    def __init__(self, master, controller):
        self.controller = controller

        buttonWidth = 30  # Parameters to set the width, height and font size of the buttons.
        buttonHeight = 2
        self.fontSize = 15

        # Main Buttons ##
        self.mainWindow = Frame(master)
        self.mainWindow.pack(side=TOP)

        # The status bar at the bottom of the frame
        self.statusBar = Frame(master, bg="white", relief=SUNKEN, height="50", width=(buttonWidth * 2))
        self.statusBar.pack(side=BOTTOM, fill=X)

        """
        The buttons are done as so: A function is called that creates the buttons, with all of the desired options:
        - Window to be placed in
        - the function to be activated upon pressing
        - location in the grid
        - width, height
        At the end, the set function returns a reference to the button for future use.
        """
        """
        The buttons that are available at the beginning: 1. Browse data set, 2. Posting file save location,
        3. Checkbox to stem or not, 4. Load cache, 5. Load Dictionary 6. Start indexing.
        """
        self.data_browse_BTN = self.__setDataBrowseBTN(self.mainWindow, self.__dataSetBrowse, 1, 0, buttonWidth,
                                                       buttonHeight)
        self.save_post_BTN = self.__setSavePostLocBrowseBTN(self.mainWindow, self.__postSaveBrowse, 2, 0, buttonWidth,
                                                            buttonHeight)
        self.stemBox = IntVar()
        self.checkBox_BTN = self.__setCheckBox(self.mainWindow, 3, 0, buttonWidth, buttonHeight, self.stemBox)
        self.load_cache_and_dict_BTN = self.__setLoadCacheAndDictBTN(self.mainWindow, self.__loadCacheAndDict, 4, 0,
                                                                     buttonWidth, buttonHeight)
        self.openedDictWindow = False
        self.start_BTN = self.__setStartBTN(self.mainWindow, self.__startSearch, 0, buttonWidth * 2, buttonHeight)

        """
        The buttons that are available only after indexing: 1. Reset button - available while running, 2. Display dictionary,
        3. Display cache, 4. Save dictionary, 5. Save cache
        """
        # Locked at beginning
        self.reset_BTN = self.__setResetBTN(self.mainWindow, self.__reset, 1, 1, buttonWidth, buttonHeight)
        self.disp_dict_BTN = self.__setDispDictBTN(self.mainWindow, self.__displayDict, 2, 1, buttonWidth, buttonHeight)
        self.disp_cache_BTN = self.__setDispCacheBTN(self.mainWindow, self.__displayCache, 3, 1, buttonWidth,
                                                     buttonHeight)
        self.save_cache_and_dict_BTN = self.__setSaveCacheAndDictBTN(self.mainWindow, self.__saveCacheAndDict, 4, 1,
                                                                     buttonWidth, buttonHeight)

        # Status bar
        self.__setStatusBar()

        self.dataSetChosen = False  # A boolean variable to determine if the data set was already chosen or not
        self.postSaveLocation = False  # A boolean variable to determine if the save location of the posting file was already chosen

    """******** SETTING UP BUTTONS ********
    Each button is initialized using the parameters received from the init function. In addition, we insert the 
    desired title and the font. Afterwards we place it in the grid and return a reference to the button.
    The only function here that does not create a button is the checkbox.
    """

    # Browse for data set
    def __setDataBrowseBTN(self, mainWindow, func, row, col, buttonWidth, buttonHeight):
        browse_data_button = Button(mainWindow, text="Browse For Data Set", width=buttonWidth, height=buttonHeight,
                                    font=('times', self.fontSize, 'bold'), command=func, bg='gainsboro')
        browse_data_button.grid(row=row, column=col)
        return browse_data_button

    # Browse where to save posting files
    def __setSavePostLocBrowseBTN(self, mainWindow, func, row, col, buttonWidth, buttonHeight):
        browse_post_save_button = Button(mainWindow, text="Posting File Save Location", width=buttonWidth,
                                         height=buttonHeight, font=('times', self.fontSize, 'bold'), command=func,
                                         bg='gainsboro')
        browse_post_save_button.grid(row=row, column=col)
        return browse_post_save_button

    # Stemming checkbox
    def __setCheckBox(self, mainWindow, row, col, buttonWidth, buttonHeight, var):
        stem_checkBox = Checkbutton(mainWindow, text="   Use Stemmer?", width=buttonWidth, height=buttonHeight,
                                    font=('times', self.fontSize, 'bold'), variable=var, bg='gainsboro')
        stem_checkBox.grid(row=row, column=col)

    # Start button
    def __setStartBTN(self, mainWindow, func, row, buttonWidth, buttonHeight):
        start_button = Button(mainWindow, text="Start!", width=buttonWidth, height=buttonHeight,
                              font=('times', self.fontSize, 'bold'), command=func, bg='gainsboro')
        start_button.grid(row=row, columnspan=2)
        return start_button

    # Load cache and dictionary button
    def __setLoadCacheAndDictBTN(self, mainWindow, func, row, col, buttonWidth, buttonHeight):
        load_Dict_button = Button(mainWindow, text="Load Cache and Dictionary", width=buttonWidth, height=buttonHeight,
                                  font=('times', self.fontSize, 'bold'), command=func, bg='gainsboro')
        load_Dict_button.grid(row=row, column=col)
        return load_Dict_button

    """
    These buttons are similar except they are initially disabled.
    """

    # Reset button
    def __setResetBTN(self, mainWindow, func, row, col, buttonWidth, buttonHeight):
        reset_button = Button(mainWindow, text="Reset", width=buttonWidth, height=buttonHeight,
                              font=('times', self.fontSize, 'bold'), state=DISABLED, command=func, bg='gainsboro')
        reset_button.grid(row=row, column=col)
        return reset_button

    # Display cache button
    def __setDispCacheBTN(self, mainWindow, func, row, col, buttonWidth, buttonHeight):
        disp_cache_button = Button(mainWindow, text="Display Cache", width=buttonWidth, height=buttonHeight,
                                   font=('times', self.fontSize, 'bold'), state=DISABLED, command=func, bg='gainsboro')
        disp_cache_button.grid(row=row, column=col)
        return disp_cache_button

    # Display dictionary button
    def __setDispDictBTN(self, mainWindow, func, row, col, buttonWidth, buttonHeight):
        disp_dict_button = Button(mainWindow, text="Display Dictionary", width=buttonWidth, height=buttonHeight,
                                  font=('times', self.fontSize, 'bold'), state=DISABLED, command=func, bg='gainsboro')
        disp_dict_button.grid(row=row, column=col)
        return disp_dict_button

    # Save newly created cache and dictionary button
    def __setSaveCacheAndDictBTN(self, mainWindow, func, row, col, buttonWidth, buttonHeight):
        save_cache_button = Button(mainWindow, text="Save Cache and Dictionary", width=buttonWidth, height=buttonHeight,
                                   font=('times', self.fontSize, 'bold'), state=DISABLED, command=func, bg='gainsboro')
        save_cache_button.grid(row=row, column=col)
        return save_cache_button

    """ The status bar contains the current time elapsed. It uses a separate thread for the clock."""

    def __setStatusBar(self):
        self.timeStatus = Label(self.statusBar, text="Time Elapsed: ", font=('times', self.fontSize, 'bold'),
                                bg='white')
        self.timePassed = Label(self.statusBar, font=('times', self.fontSize, 'bold'), text="", bg='white')
        self.timeStatus.pack(side=LEFT, fill=X)
        self.timePassed.pack(side=LEFT, fill=X)

    # BUTTON COMMANDS
    # Here we define the unique functions each button calls upon when clicked.

    """
    This function opens a browse window. If no folder was chosen, nothing will happen. If a valid path was chosen, the
    button color will change and the dataSetChosen flag will be set to true. If the posting save location was already
    chosen, the start button will turn green as well. Other the start button will become orange.
    """

    def __dataSetBrowse(self):
        title = "Choose Corpus and Stop Words Location"
        dir1 = 'C:\\'
        folderName = askdirectory(initialdir=dir1, title=title)
        if len(folderName) > 0:
            if os.path.isdir(os.path.join(folderName, 'corpus')) and os.path.isfile(
                    os.path.join(folderName, 'stop_words.txt')):  # foldername is valid
                self.dataSetChosen = True
                self.data_browse_BTN.config(bg='lawn green')
                self.reset_BTN.config(state=NORMAL, bg='firebrick1')
                if self.postSaveLocation:
                    self.start_BTN.config(state=NORMAL, bg='SpringGreen2')
                else:
                    self.start_BTN.config(bg='dark orange')
                self.controller.data_set_Path(folderName)
            elif os.path.isfile(os.path.join(folderName,
                                             'stop_words.txt')):  # it contains stop words, so it doesnt contain a corpus..
                messagebox.showerror("Woopsie!", "The given folder does not contain a folder named corpus\n"
                                                 "Please choose a new folder.")
            elif os.path.isdir(os.path.join(folderName, 'corpus')):  # Its missing the stopwords
                messagebox.showerror("Woopsie!", "The given folder does not contain stop_words.txt\n"
                                                 "Please choose a new folder.")
            else:  # Doesnt contain either
                messagebox.showerror("Woopsie!", "The given folder does not contain the corpus and stop_words.txt\n"
                                                 "Please choose a new folder.")
        else:
            print("Corpus browse was canceled..")

    """ 
    This function is almost identical to the data set browse function above. The only difference is the flags that are 
    changed and the initial directory.
    """

    def __postSaveBrowse(self):
        title = "Choose Location To Save Posting File:"
        dir1 = '../Resources/'
        folderName = askdirectory(initialdir=dir1, title=title)
        if len(folderName) > 0:
            self.postSaveLocation = True
            self.save_post_BTN.config(bg='lawn green')
            self.reset_BTN.config(state=NORMAL, bg='firebrick1')
            if self.dataSetChosen:
                self.start_BTN.config(state=NORMAL, bg='SpringGreen2')
            else:
                self.start_BTN.config(bg='dark orange')
            self.controller.set_post_save_location(folderName)
        else:
            print("Posting location save was cancled..")

    """
    The 'Start' button. If the data set and posting location were already chosen the button will activate the run
    function in the controller, change text, color, make the reset button available. In addition it will start the 
    timer in the status bar. If not all of the requirements are met, it will display the corresponding warning message.
    While running, the button is disabled. 
    """

    def __startSearch(self):

        if self.dataSetChosen and self.postSaveLocation:
            self.reset_BTN.config(state=DISABLED, bg='gainsboro')
            if self.stemBox.get() == 1:
                self.start_BTN.config(text="Running (with stemming)...", bg='cyan2', state=DISABLED)
            else:
                self.start_BTN.config(text="Running (without stemming)...", bg='cyan2', state=DISABLED)
            self.controller.stopRead = False
            self.save_cache_and_dict_BTN.config(state=DISABLED)
            self.clockThread = _thread.start_new_thread(self.__timeElapsedTick, ())
            self.indexingThread = _thread.start_new_thread(self.controller.startSearch,
                                                           (self.stemBox.get(),))  # Run the indexing in a thread
            self.finishedIndexing = False

        elif self.postSaveLocation:
            messagebox.showwarning(title="Oops!", message="Please choose:\nThe location of the data set",
                                   parent=self.mainWindow)
        elif self.dataSetChosen:
            messagebox.showwarning(title="Oops!", message="Please choose: \nWhere to save the posting files",
                                   parent=self.mainWindow)
        else:
            messagebox.showwarning(title="Oops!",
                                   message="Please choose: \nThe location of the data set \nWhere to save the posting files",
                                   parent=self.mainWindow)

    """
    Opens a browse window to choose the dictionary and cache location and loads them to memory. Can only open .json 
    files. The moment the pathfile is chosen, it begins building the dictionary window in a separate thread. It also 
    enables the reset button.
    """

    def __loadCacheAndDict(self):
        title = "Choose Cache and Dictionary Location to Load"
        dir1 = '../Resources/'
        filename = askdirectory(title=title, initialdir=dir1)
        if len(filename) > 0:
            # Configure buttons
            self.disp_cache_BTN.config(state=NORMAL, bg='forest green')
            self.reset_BTN.config(state=NORMAL, bg='firebrick1')
            self.disp_dict_BTN.config(state=NORMAL, bg='forest green')

            # Load the data structures
            self.controller.load_data(filename, self.stemBox.get())
            self.createDictLines = False
        else:
            print("Load cache and Dict was cancled..")

    """
    Opens a browse window to decide where to save the newly created cache and dictionary. Is available only when the indexing
    process is done. Notifies the controller of the action.
    """

    def __saveCacheAndDict(self):

        dir1 = 'C:\\'
        title = "Choose Where to Save Cache and Dictionary"
        folderName = askdirectory(initialdir=dir1, title=title)
        self.controller.setCacheSave(folderName)
        self.controller.setDictSave(folderName)
        self.controller.set_documents_save(folderName)

    """
    Displays the dictionary by de-iconifying it. Rep
    """
    def __displayDict(self):
        if not self.openedDictWindow:  # first time we display the dictionary
            self.__displayDictFunc()
        self.win.deiconify()
        self.disp_dict_BTN.config(state=DISABLED)
        self.openedDictWindow = True

    """
     A function creates the dictionary window, it is called by the __displayDict function above.
     It creates a treeview widget to display the rows and columns properly. It reads the lines one-by-one from the 
     dictionary .txt file.
    """

    def __displayDictFunc(self):
        global loaded_dict_docs
        global continueClockLoop
        self.createDictLines = True
        self.win = Toplevel()  # Creates a new window for displaying the dictionary
        self.win.resizable(width=0, height=0)
        self.win.title("The Produced Dictionary")
        self.win.protocol("WM_DELETE_WINDOW",
                          self.__closeDictWindow)  # unlock the display button when this window is closed
        header_columns = ['Term', 'idf', 'sum of tf', 'df']
        tree = ttk.Treeview(self.win, columns=header_columns, show="headings", height=30)
        tree.pack(in_=self.win, side=LEFT)
        vsb = ttk.Scrollbar(self.win, orient="vertical", command=tree.yview)
        vsb.pack(side=LEFT, fill='y')
        tree.configure(yscrollcommand=vsb.set)
        for col in header_columns:
            tree.heading(col, text=col)
        dictionary = Control.final_dictionary
        if dictionary is not None:
            for key, data in dictionary.items():
                if not self.createDictLines:
                    self.win.destroy()
                    break
                term = key
                idf = data[0][0]
                sum_tf = data[0][1]
                df = data[0][2]
                item = (term, idf, sum_tf, df)
                tree.insert('', 'end', values=item)
                loaded_dict_docs += 1
            loaded_dict_docs = -1  # stops the loop in the __loadedDictLines function
            continueClockLoop = False

    # unlock the display dictionary button when the window is closed. Called by the __displayDictThread function
    def __closeDictWindow(self):
        self.disp_dict_BTN.config(state=NORMAL)
        self.win.withdraw()

    # A function that is run by a thread to display the number of terms that were inserted into the tree.
    def __loadedDictLines(self):  # ToDo: delete this?
        global loaded_dict_docs

        self.loadStatus = Label(self.statusBar, text="  Terms loaded: ", font=('times', self.fontSize, 'bold'),
                                bg='white')
        self.loadNum = Label(self.statusBar, font=('times', self.fontSize, 'bold'), bg='white')
        self.loadStatus.pack(side=LEFT, fill=X)
        self.loadNum.pack(side=LEFT, fill=X)
        while loaded_dict_docs != -1:
            self.loadNum.config(text=str(loaded_dict_docs))

    """
    Displays the cache by getting it from the controller. Opens a new widget using the TopLevel() function. 
    """

    def __displayCache(self):
        cache = Control.cache_dictionary

        win = Toplevel()  # Creates a new window for displaying the dictionary
        win.resizable(width=0, height=0)
        win.title("The Produced Cache")
        header_columns = ['Term', 'Relevant Line', 'File Name', 'Merged Files counter']
        tree = ttk.Treeview(win, columns=header_columns, show="headings", height=30)
        tree.pack(in_=win, side=LEFT)
        vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        vsb.pack(side=LEFT, fill='y')
        tree.configure(yscrollcommand=vsb.set)
        for col in header_columns:
            tree.heading(col, text=col)
        for key, data in cache.items():
            term = key
            relevant_line = data[0]
            if len(relevant_line) > 200:  # Fixes an annoying bug in windows that won't display long strings properly
                relevant_line = relevant_line[0:200]
            file_name = data[1][0]
            merged_files_counter = data[1][1]
            item = (term, relevant_line, file_name, merged_files_counter)
            tree.insert('', 'end', values=item)

    """
    Reset button - stops indexing process, and deletes all the data structures and files that were created. Resets the
    clock on the status bar. Disables the reset button, changes the start button back.
    """

    def __reset(self):
        print("Stopping search...")
        global continueClockLoop
        continueClockLoop = False
        self.timePassed.config(text=str(datetime.timedelta(seconds=0)))
        self.start_BTN.config(bg='gainsboro', text="Start!")
        self.reset_BTN.config(state=DISABLED, bg='gainsboro')
        self.disp_cache_BTN.config(state=DISABLED, bg='gainsboro')
        self.disp_dict_BTN.config(state=DISABLED, bg='gainsboro')
        self.data_browse_BTN.config(bg='gainsboro')
        self.save_post_BTN.config(bg='gainsboro')
        self.save_cache_and_dict_BTN.config(bg='gainsboro', state=DISABLED)
        try:
            self.loadNum.config(text="")
            self.loadStatus.config(text="")
            self.openedDictWindow = False
        except AttributeError:
            pass
        self.controller.reset()

    """
    A simple clock. Displays the time elapsed on the bottom of the string. Uses the global variables sec and 
    continueClockLoop.
    """

    def __timeElapsedTick(self):
        global sec
        global continueClockLoop
        continueClockLoop = True
        while continueClockLoop:
            self.timePassed.config(text=str(datetime.timedelta(seconds=sec)))
            sec += 1
            time.sleep(1)
        sec = 0
        continueClockLoop = True

    """
    Notifies the View that indexing has concluded and we can now activate these functions.
    Receives from the controller several parameters with info about the indexing process.
    Creates a pop-up window displaying the information received.
    """

    def finished_indexing(self, numOfDocs, dictFileSize, cacheFileSize, totalTime, termNum, postingSize, stemMode):

        self.finishedIndexing = True
        global continueClockLoop
        continueClockLoop = False
        if stemMode == 1:
            stemMode = "Stem mode was on"
        else:
            stemMode = "Stem mode was off"
        self.save_cache_and_dict_BTN.config(state=NORMAL, bg='forest green')
        totalTime = str(datetime.timedelta(seconds=int(totalTime)))
        self.timePassed.config(text=totalTime)
        alert = Toplevel()
        alert.title("Yay! Finished Indexing!")
        message = "Final results:\n " \
                  "Total time elapsed: %s \n %s \n" \
                  " Total number of documents indexed: %s \n " \
                  "Total number of terms: %s \n Size of dictionary: %s bytes \n Size of cache: %s bytes \n " \
                  "Posting file size: %s bytes" % (totalTime, stemMode, numOfDocs, termNum, dictFileSize,
                                                   cacheFileSize, postingSize)
        infoBox = Message(master=alert, text=message, bg='SlateGray3', font=('times', self.fontSize, 'bold'),
                          width=400, justify=CENTER)
        infoBox.pack()
        alert.resizable(0, 0)
        self.start_BTN.config(state=NORMAL, bg='SpringGreen2', text="Start!")
        self.reset_BTN.config(state=NORMAL, bg='firebrick1')
