"""
                      ymmmo              `.-::::::-.`
                      dmmmy`           .:////////////--.`
 :hdddddddddddyo-     dmmmmddddds     -//////////////////:
 smmmmmmmmmmmmmmmy`   dmmmmmmmmmd`   .//////::::::-. :////.
 ymmmd::::::/smmmmo   dmmmh::::-`    -///.            .///.
 ymmmd       `hmmmy   dmmmy          .//.              .//.
 ymmmd       `hmmmy   dmmmy          `//.              .//`
 ymmmd       `hmmmy   dmmmy          .-``              ``-.
 ymmmd       `hmmmy   dmmmy          `.-`              `-.
 ymmmd       `hmmmy   ymmmm+-...       `:`            .:`
 ymmmd       `hmmmy   -dmmmmmmmmh`      `-.          --
 /dmms        ommd+    `+ydmmmmmh`        `--``  `.--`
                                          `--.`...../ss`
This is the class that controls the data flow between the GUI and the actual model. It interacts with both, while
neither can interact with each other. It contains a View object and several objects from the Model package and
orchestrates the order in which they will work. The main method is Run. It also utilizes a config.ini file to determine
several variables that change in between runs of the program.
"""
from tkinter.filedialog import askopenfilename, asksaveasfilename

from Model.ReadFile import Reader
from Model.Parser import Parser
from Model.Indexer import Indexer
from Model.Stemmer import Stemmer
from Model.WriteFile import Writer
from Model.Searcher import Searcher
from View.View import View
from View.EngineGUI import EngineGUI
import time
import os
import concurrent.futures
import configparser
from tkinter import *
import re

from Model.Ranker import Ranker # remove this!!!!

config = configparser.ConfigParser()  # creates the config object that reads the .ini file
config.read('config.ini')
parts = int(config['Control']['parts'])  # number of parts to divide the corpus into (10 files minimum)
fileNum = int(config['Control']['file_number'])   # number of files to index, max 1815
thread_mode = config['Control']['thread_mode']  # if to thread or not
number_of_threads = int(config['Control']['number_of_threads'])  # number of threads
__docs_delimiter = config['Indexer']['docs_delimiter']  # the delimiter of path files. Useful if working on linux
path_delimiter = config['Indexer']['path_delimiter']  # Use to change between the Windows and Linux
stem_mode = 1  # default mode is to stem
cache_dictionary = {}  # the important data structures that will be created at the end.
final_dictionary = {}
documents_dictionary = {}


# The function that merges the final dictionaries. Called from handle files.  It iterates through the dictionary and
# adds new terms or updates new ones that weren't seen before.
def __update_and_merge_dictionaries(doc_id, file_id, term_dictionary_ref, documents_dictionary_ref_ref,
                                    check_this_dictionary):
    max_tf = 0
    length = 0
    for key, value in check_this_dictionary.items():
        if key in term_dictionary_ref:
            term_dictionary_ref[key] += __docs_delimiter + doc_id + __docs_delimiter + str(value)
        else:
            term_dictionary_ref[key] = doc_id + __docs_delimiter + str(value)

        if value > max_tf:
            max_tf = value
        length += value
    documents_dictionary_ref_ref[doc_id] = [max_tf, length, 0, file_id]


# Receives a list of the document dictionary and the output of the read file (a list of document ID's and the text)
# creates temporary posting files. Takes into account if its necessary to stem or not.
def handle_files(file_list_ref, documents_dictionary_ref):
    terms_dictionary = {}

    if stem_mode:
        # This code take a document's text from the list and parsing & stemming the text
        for value in file_list_ref:
            doc_id = value[0]
            file_name = value[2]
            after_stemming = Stemmer.stemWithCache(Parser.start(value[1]))
            # This function update the document parameters
            __update_and_merge_dictionaries(doc_id, file_name, terms_dictionary, documents_dictionary_ref,
                                            after_stemming)
            # This function merge all the dictionary in loop and create dictionary for the whole part
    else:
        # This code take a document's text from the list and only parsing the text
        for value in file_list_ref:
            doc_id = value[0]
            file_name = value[2]
            after_parse = Parser.start(value[1])
            # This function update the document parameters
            __update_and_merge_dictionaries(doc_id, file_name, terms_dictionary, documents_dictionary_ref, after_parse)
            # This function merge all the dictionary in loop and create dictionary for the whole part

    # This function create new temp posting file for each part
    Indexer.create_temp_posting_file(terms_dictionary)


# This function gets doc_id and return the relevant text
def get_text_from_document(doc_id, folder_path):
    doc_id = doc_id.strip()

    if doc_id in documents_dictionary:
        path = folder_path + path_delimiter + "corpus" + path_delimiter + documents_dictionary[doc_id][3]

        if os.path.exists(path):
            list_of_separate = Reader.separate(path)
            list_of_separate = [item for item in list_of_separate if item[0] == doc_id]
            doc_id_info = list_of_separate.pop()
            p = re.compile(r'<.*?>')
            text = p.sub('', doc_id_info[1])
        else:
            text = "Sorry, we could not find your document!"
    else:
        text = "Sorry, we could not find your document!"

    return text


class TheControl:

    def __init__(self):
        self.root = Tk()
        # self.view = View(self.root, self)
        self.root.config(cursor="hand2", bg='#474640')
        # self.root.geometry("960x441")
        self.GUI = EngineGUI(self.root, self)

    # This function opens the root window of the GUI, here we set the title and the NT icon
    def start(self):
        self.root.title("NT Super Automated Cyber Hacking IOT Block-Chain AI Search Engine")
        self.root.resizable(0, 0)
        #        self.root.iconbitmap(r'C..\..\,\NT.ico')
        self.root.mainloop()

    # This function calling the reset functions of all the packages
    def reset(self):
        global cache_dictionary
        global final_dictionary
        global documents_dictionary
        cache_dictionary = None
        final_dictionary = None
        documents_dictionary = None
        Indexer.reset()
        Writer.reset()
        Stemmer.reset()
        Reader.reset()

    # Setter for data path
    def data_set_Path(self, path):
        global corpus_path
        print("Received corpus folder..")
        corpus_path = path+"/corpus"

        print("Received stopwords filename..")
        global __stopwords_path
        __stopwords_path = path+"/stop_words.txt"
        Parser.set_stop_words_file(__stopwords_path)

    # Setter for save location
    def set_post_save_location(self, path):
        Indexer.set_posting_folder(path)

    # This function is called by the View when the start button is pressed
    def startSearch(self, stemBool):
        global stem_mode
        stem_mode = stemBool
        Indexer.set_stemmer_mode(stemBool)
        Parser.set_stemmer_mode(stemBool)
        self.run() #begin indexing!

    # Setter for document path
    def set_documents_save(self, folder_name):
        # Save to final dictionary to disk
        Writer.save_documents(documents_dictionary, folder_name)

    # Setter for cache path
    def setCacheSave(self, folder_name):
        # Save to final dictionary to disk
        Writer.save_cache(cache_dictionary, folder_name)

    # Setter for dictionary path
    def setDictSave(self, folder_name):
        # Save to final dictionary to disk
        Writer.save_final_dictionary(final_dictionary, folder_name)

    # This function called when the user clicked on load dictionary and cache
    def load_data(self, folder_path, stem_mode):
        global documents_dictionary
        global cache_dictionary
        global final_dictionary
        if final_dictionary is None or cache_dictionary is None or documents_dictionary is None :
            pass
        else:
            final_dictionary.clear()
            cache_dictionary.clear()
            documents_dictionary.clear()

        documents_dictionary = Writer.load_documents(folder_path, stem_mode)
        cache_dictionary = Writer.load_cache(folder_path, stem_mode)
        final_dictionary = Writer.load_final_dictionary(folder_path, stem_mode)

    # This function is called when the user loads a query file
    def fn_run_query_file(self, query_file_path, stem_mode, folder_path):
        start_search = time.time()  # Time elapsed since query received until results came back
        path = folder_path + path_delimiter + "stop_words.txt"
        Parser.set_stop_words_file(path)
        Parser.set_stemmer_mode(stem_mode)

        if stem_mode:
            Searcher.idf_weight = 0.8
            Searcher.df_weight = 0.7
            Searcher.denominator = 1.3
            Ranker.bm25_weight = 0.1
            Ranker.cos_sim_weight = 0.9
            Ranker.b = 0.6
            Ranker.k = 1.85
            Ranker.bm25_lambda = 0.25
            Ranker.bm25_idf = 0.5

        else:

            Searcher.idf_weight = 0.8
            Searcher.df_weight = 0.7
            Searcher.denominator = 1.3
            Ranker.bm25_weight = 0.1
            Ranker.cos_sim_weight = 0.9
            Ranker.b = 0.6
            Ranker.k = 1.85
            Ranker.bm25_lambda = 0.25
            Ranker.bm25_idf = 0.5

        searcher = Searcher.Searcher()
        results = searcher.multi_search(stem_mode, folder_path, final_dictionary, cache_dictionary,
                                        documents_dictionary, Reader.extract_queries(query_file_path))

        file_num = len(results)  # The number of results
        end_search = time.time()
        total_time = end_search - start_search

        self.display_query_file_results(total_time, file_num, results)

    # This function is called when the user wishes to search a certain query or a file name
    def fn_search(self, query, expand_mode, stem_mode, folder_path, summ_mode):
        path = folder_path + path_delimiter + "stop_words.txt"
        Parser.set_stop_words_file(path)
        Parser.set_stemmer_mode(stem_mode)

        start_search = time.time()  # Time elapsed since query received until results came back
        searcher = Searcher.Searcher()

        if expand_mode == 0 and summ_mode == 0: # regular, manual query search
            results = searcher.search(stem_mode, folder_path, final_dictionary, cache_dictionary,
                                      documents_dictionary, query)

            file_num = len(results)  # The number of results
            end_search = time.time()
            total_time = end_search - start_search
            self.display_results(total_time, file_num, results)

        elif summ_mode == 1:
            doc_id = query
            results = searcher.find_popular_sentences(stem_mode, folder_path, final_dictionary, cache_dictionary,
                                                      documents_dictionary, doc_id,
                                                      get_text_from_document(doc_id, folder_path))
        else: # We need to expand the query
            results = searcher.expand(stem_mode, folder_path, final_dictionary, cache_dictionary,
                                      documents_dictionary, query)

        file_num = len(results)  # The number of results
        end_search = time.time()
        total_time = end_search - start_search
        self.display_results(total_time, file_num, results)

    def __average_document_length(self):
        sum = 0
        for doc_id in documents_dictionary.keys():
            sum += documents_dictionary[doc_id][1]
        avg = sum / len(documents_dictionary)

        print(avg)

    # This function is called by the GUI when the user wants to save the query results
    def fn_save_results(self, results, save_results_path):
        # Calls the writer to save the file
        Writer.save_regular_result(results, save_results_path)

    # This function is called by the GUI when the user wants to save the query results
    def fn_save_query_file_results(self, results, save_results_path):
        # Calls the writer to save the file
        Writer.save_query_file_results(results, save_results_path)

    # displays to the GUI the results of a search on a single query
    def display_results(self, total_time, file_num, results):
        self.GUI.fn_write_results_to_GUI("{:.8f}".format(total_time), file_num, results)

    # displays to the GUI the results of a search on a query file
    def display_query_file_results(self, total_time, file_num, results):
        self.GUI.fn_write_query_file_to_GUI("{:.2f}".format(total_time), file_num, results)

    # A megalomaniac function that computes optimal values for several variables used for ranking documents.
    def Mega_Test(self, query_file_path, stem_mode, folder_path):

        path = folder_path + path_delimiter + "stop_words.txt"
        Parser.set_stop_words_file(path)
        Parser.set_stemmer_mode(stem_mode)
        searcher = Searcher.Searcher()

        results_dict = {}
        query_rel_docs = {} # The dictionary containing each query id (key) and the RELEVANT documents (value, set)
        file_types = (("Comma Separated Value Document", "*.csv"),)
        rel_doc_path = askopenfilename(title="Choose result csv file", filetypes=file_types)
        file_types = (("Any file", "*.*"),)
        save_path = asksaveasfilename(title="Choose where to save BM25 results", filetypes=file_types,
                                      initialfile="mega_test.csv")
        docs = open(rel_doc_path).read()
        docs = docs.split('\n')
        docs = docs[:-1]

        for entry in docs:
            tuple = entry.split(',')
            qid = tuple[0]
            doc = tuple[1]
            if qid in query_rel_docs:
                query_rel_docs[tuple[0]].add(doc)
            else:
                query_rel_docs[tuple[0]] = set()
                query_rel_docs[tuple[0]].add(doc)

        Searcher.denominator = 1.3  # Range [1 : 4]
        Searcher.df_weight = 0.7  # Range (0 : 1]
        Searcher.idf_weight = 0.2
        Ranker.bm25_weight = 0.05
        Ranker.cos_sim_weight =  0.95 # doesn't need a loop
        Ranker.bm25_k = 1.2  # Range: [1.2 - 2.0]
        Ranker.bm25_b = 0.1  # Range: 0.45-1.0
        Ranker.bm25_lambda = 0.2  # Range: 0-1.0

        columns ='bm25 weight, cos sim weight, bm25 k, bm25 b, bm25 lambda, Denominator, searcher idf, searcher df, score\n'
        srp = open(save_path, 'a')
        srp.write(columns)
        srp.close()

        while Ranker.bm25_k <= 2.01:
            Ranker.bm25_b = 0.1
            while Ranker.bm25_b <= 1.01:
                results = searcher.multi_search(stem_mode, folder_path, final_dictionary, cache_dictionary,
                                                documents_dictionary, Reader.extract_queries(query_file_path))
                score = 0
                for entry in results:
                    qid = entry[0]
                    rel_set = query_rel_docs[qid]
                    returned_set = set(entry[1])
                    intersection_set = rel_set.intersection(returned_set)
                    score += len(intersection_set)

                result_score = "%f, %f, %f, %f, %f, %f, %f, %f, %d\n" % \
                               (Ranker.bm25_weight, Ranker.cos_sim_weight, Ranker.bm25_k,
                                Ranker.bm25_b,Ranker.bm25_lambda,
                                Searcher.denominator, Searcher.idf_weight, Searcher.df_weight, score)
                srp = open(save_path, 'a')
                srp.write(result_score)
                srp.close()
                Ranker.bm25_b += 0.1
            Ranker.bm25_k += 0.1


    # This function called when the user clicked on start button
    def run(self):
        global cache_dictionary
        global final_dictionary
        global documents_dictionary
        start_time = time.time()
        cache_dictionary = {}
        final_dictionary = {}
        documents_dictionary = {}

        # Creates a list with all of the file paths in the corpus. Pops to remove the corpus file path
        sub_dirs = [x[0] for x in os.walk(corpus_path)]
        sub_dirs.pop(0)

        files_list = []  # This list will save each part
        file_index = 1  # This index point to current file
        iterate_over_parts = 1  # This part point to the current part

        next_part = int(fileNum / parts) * iterate_over_parts  # The last index of the first part
        if thread_mode == 'on':  # Here we using ThreadPool
            # Init for ThreadPool with number of threads from config file
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=number_of_threads)
            for subdir in sub_dirs:
                textList = Reader.separate(subdir)
                files_list.extend(textList)
                if file_index == next_part:
                    executor.submit(handle_files, files_list, documents_dictionary)
                    files_list = []  # cleaning the files list
                    if not iterate_over_parts + 1 == parts:
                        iterate_over_parts += 1
                        # update the last index of the next part
                        next_part = (int(fileNum / parts) * iterate_over_parts)
                if file_index == fileNum:  # The last index of the last part
                    executor.submit(handle_files, files_list, documents_dictionary)
                    break  # if we not iterate over the whole corpus
                file_index += 1
                # This function shut down the ThreadPool but wait until the Threads will finish
            executor.shutdown(wait=True)
        else:
            for subdir in sub_dirs:
                textList = Reader.separate(subdir)
                files_list.extend(textList)
                if file_index == next_part:
                    handle_files(files_list, documents_dictionary)
                    files_list = []  # cleaning the files list
                    if not iterate_over_parts + 1 == parts:
                        iterate_over_parts += 1
                        # update the last index of the next part
                        next_part = (int(fileNum / parts) * iterate_over_parts)
                if file_index == fileNum:  # The last index of the last part
                    handle_files(files_list, documents_dictionary)
                    break  # if we not iterate over the whole corpus
                file_index += 1

        sub_dirs = None
        files_list = None
        Stemmer.clean_cache()
        # Merge the temp files and removed them
        final_dictionary, cache_dictionary, posting_file_size = Indexer.merge_files(documents_dictionary)

        end_time = time.time()
        total_time = end_time - start_time

        # Stemmer.write_cache()
        print("Number of documents: " + str(len(documents_dictionary)))
        print("Number of terms: " + str(len(final_dictionary)))
        print("Time: " + str("{:.2f}".format(total_time)) + " seconds")
        print("Time: " + str("{:.2f}".format(total_time/60)) + " minutes")

        final_dictionary_file_size = sys.getsizeof(final_dictionary)
        cache_file_size = sys.getsizeof(cache_dictionary)

        print("Posting file size: " + str(posting_file_size) + " Bytes")
        print("Dictionary file size: " + str(final_dictionary_file_size) + " Bytes")
        print("Cache file size: " + str(cache_file_size) + " Bytes")
        Writer.remove_temp_file()

        # Announce to the gui that indexing has concluded.
        global stem_mode
        self.view.finished_indexing(str(len(documents_dictionary)),
                                    str(final_dictionary_file_size),
                                    str(cache_file_size),
                                    str(int(total_time)),
                                    str(len(final_dictionary)),
                                    str(posting_file_size),
                                    stem_mode)


