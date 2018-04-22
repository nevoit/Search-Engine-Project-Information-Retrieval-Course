"""

A class that receives a file path, goes through the different files and separates the text files inside.
It outputs a list of CleanText objects.

"""
import os.path  # enables operating system dependant functions, useful for traversing through files and directories

path = ""  # The path to the file
docNumList = []  # A list of all doc nums in the file
textList = []  # A list of all the texts in a file
cleanList = []  # The list that will be returned at the end.
length = 0  # The number of documents in the current file (length of docNumList)
fileName = ""  # The file name of the documents. Used for part 2 of the assignment


# The function that strips the doc number, header and the text. Returns a List with tuples containing the doc number
# and text of each document in the given file path.
def separate(newPath=""):
    __clearLists()  # clean the data structures.
    global path
    global docNumList
    global textList
    global cleanList
    global length
    global fileName

    if newPath == "":  # There was a problem with the filepath given
        print("Error: No file path given.")
        return

    path = newPath

    for root, dirs, files in os.walk(path):  # traverses the given file path.
        fileName = files[0]
        text_file = open(os.path.join(path, files[0]), 'r', encoding="ISO-8859-1")  # The encoding of text files.
        textList = text_file.read().split("</TEXT>")  # Split at </TEXT> tag.
        text_file.close()
        del textList[-1]  # The last object in the list is the garbage past the final </TEXT> tag.

        length = len(textList)
        __takeDocNum()
        __takeText()
        __createCleanList()
    return cleanList


# Extracts the queries from a given file path. Returns them as a list with tuples: (query number , query)
def extract_queries(query_file_path):
    query_list = []
    query_num = ""
    title = ""
    description = ""
    narrative = ""

    with open(query_file_path, 'r') as text_file:
        text_file = text_file.read()
        text_file = text_file.split()
        i = 2  # Begin at the third word ( "Number:" )
        while i < len(text_file):
            if text_file[i] == "Number:":
                query_num = text_file[i + 1]
                i += 1
            if text_file[i] == "<title>":
                i += 1
                while not text_file[i] == "<desc>":  # Concatenate title until you reach the description
                    title = title + " " + text_file[i]
                    i += 1
                i += 1
                title.strip()  # remove white space at beginning
            if text_file[i] == "Description:":
                i += 1
                while not text_file[i] == "<narr>":  # Read until you reach this tag
                    description = description + " " + text_file[i]
                    i += 1
                i += 1
                description.strip()
            if text_file[i] == "Narrative:":
                i += 1
                while not text_file[i] == "</top>":  # Read until you reach this tag
                    narrative = narrative + " " + text_file[i]
                    i += 1
                narrative.strip()
                tuple = (query_num, title, description, narrative)
                query_num = ""
                title = ""
                description = ""
                narrative = ""
                query_list.append(tuple)
            i += 1
    return query_list


# Extract the docNum from a whole Document
def __takeDocNum():
    global length
    global textList
    global docNumList

    for i in range(length):
        docNum = (textList[i].split("</DOCNO>", 1)[0]).split("<DOCNO>")[1].strip()
        docNumList.append(docNum)


# Extract the clean text
def __takeText():
    global length
    global textList

    for i in range(length):
        text = textList[i].split("<TEXT>")[1].strip()
        # remove problematic or meaningless strings that clutter the corpus
        text = text.replace('\n', " ")
        text = text.replace('CELLRULE', " ")
        text = text.replace('TABLECELL', " ")
        text = text.replace('CVJ="C"', " ")
        text = text.replace('CHJ="C"', " ")
        text = text.replace('CHJ="R"', " ")
        text = ' '.join(text.split())
        textList[i] = text


# creates the dictionary to be returned
def __createCleanList():
    global length
    global docNumList
    global cleanList
    global textList
    global fileName

    for i in range(length):
        cleanList.append((docNumList[i], textList[i], fileName))


# Delete Reader's data structures
def __clearLists():
    global docNumList
    global textList
    global cleanList
    global length
    global path
    global headerList

    headerList = []
    docNumList = []
    textList = []
    cleanList = []
    length = 0
    path = ""


def reset():
    __clearLists()
