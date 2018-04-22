"""
The indexer create the posting file and save the file to the disk, this indexer can save memory because you
can ask to part the temp posting files. we created the inverted file
"""

import configparser
import os
from numpy import log2
from Model.WriteFile import Writer
import shutil

__config = configparser.ConfigParser()
__config.read('config.ini')  # This function call to the config file
__temp_posting_files_folder = ''  # Folder for the temporary posting files
__output_folder = ''  # Folder for the final posting files
__posting_file_name = ''  # Name for the posting file depends in stem mode
__docs_delimiter = __config['Indexer']['docs_delimiter']  # The delimiter between the docs
__term_delimiter = __config['Indexer']['term_delimiter']  # The delimiter between the term to the value
__path_delimiter = __config['Indexer']['path_delimiter']  # Use to change between the Windows and Linux
# Threshold for the idf, if it's lower we save the term in cache
__idf_threshold = __config['Indexer']['idf_threshold']
# You take the first part out of how many parts?
__cache_first_part_out_of = int(__config['Indexer']['cache_first_part_out_of'])
__cache_pointer = __config['Indexer']['cache_pointer']  # How to point to the cache from the dictionary?

__finished_temp_files = 0  # How many files we finished to merge
file_dictionary = {}  # This dictionary save all the temp post files. {file_name -> file_object}


# This function gets line and return order line by frequents of docs, sum of frequents and number of docs in line
def __sort_by_frequents(line, documents_dictionary_ref):
    line = line.split(__docs_delimiter)  # split the line by delimiter
    docs_id_list = line[::2]  # create list of docs id
    frequent_list = list(map(int, line[1::2]))  # create list of frequents

    index = 0
    for doc_id in docs_id_list:
        max_tf = documents_dictionary_ref[doc_id][0]
        frequent_list[index] = frequent_list[index]/max_tf
        index += 1

    tuple_list = zip(docs_id_list, frequent_list)  # create list of tuples (docs_id, frequent_list)
    # sort the list of tuples by frequent_list and reverse the list
    tuple_list_sorted = list(reversed(sorted(tuple_list, key=lambda x: x[1])))
    line = ''
    for doc_id, freq in tuple_list_sorted:
        if line == '':
            line = doc_id + __docs_delimiter + str(freq)
        else:
            line += __docs_delimiter + doc_id + __docs_delimiter + str(freq)
    # return tf + df. tf - sum of all frequents, df - number of documents the term showed,
    return line, sum(frequent_list), len(docs_id_list)


# This function gets line and return relevant line the first part from __cache_first_part_out_of parts
# and non_relevant_line - the continue
def __relevant_non_relevant_documents(line):
    line = line.split(__docs_delimiter)  # split the line by delimiter
    line_length = len(line)

    # we want only the first part from __cache_first_part_out_of parts - depends on your cache size
    relevant_length = int(line_length/__cache_first_part_out_of)
    if not relevant_length % 2 == 0:
        relevant_length -= 1
    relevant_line = __docs_delimiter.join(line[0:relevant_length])
    non_relevant_line = __docs_delimiter.join(line[relevant_length:line_length])

    return relevant_line, non_relevant_line


# This function gets dictionary of files object and dictionary of line counter per file and initial the values
def __update_merged_files_dictionary(merged_files_dictionary, merged_files_counter, file_name):
    folder_path = __output_folder + __posting_file_name  # Folder path with stem or without
    file_path = folder_path + file_name + '.txt'

    if not os.path.exists(folder_path):  # Check if the folder not exist, if so we will create the directory
        os.makedirs(folder_path)

    merged_files_dictionary[file_name] = open(file_path, 'w+', encoding='utf-8')  # Create object for file path
    merged_files_counter[file_name] = 1  # Initial the dictionary of line counter to 1


# This function return the file name for the token
def __get_file_name(first_char):
    if first_char in 'abc':
        return 'abc'
    elif first_char in 'defgh':
        return 'defgh'
    elif first_char in 'ijklmno':
        return 'ijklmno'
    elif first_char in 'pqrs':
        return 'pqrs'
    elif first_char in 'tuvwxyz':
        return 'tuvwxyz'
    else:
        return 'others'


# This function gets file's index and update the dictionaries
def __fetch_line(file_index, lines_dictionary, term_dictionary):
    global __finished_temp_files
    line = file_dictionary[file_index].readline().strip()
    if not line:
        # if is the end of file we clean the dictionaries and close the file object
        term_dictionary.pop(file_index, None)
        lines_dictionary.pop(file_index, None)
        file_dictionary[file_index].close()
        file_dictionary.pop(file_index, None)
        __finished_temp_files += 1  # We want to check how many files finished
    else:
        term = line.split(__term_delimiter)[0]  # take the term from the line
        lines_dictionary[file_index] = line[len(term) + 1:]
        term_dictionary[file_index] = term


# Also we remove the temp posting file
def __remove_posting_files():
    posting_file_name = __path_delimiter + 'posting_with_stem' + __path_delimiter
    folder_path = __output_folder + posting_file_name

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    posting_file_name = __path_delimiter + 'posting_without_stem' + __path_delimiter
    folder_path = __output_folder + posting_file_name

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


# This function update the stemmer mode and change the posting file name.
def set_stemmer_mode(stem_bool):
    global __posting_file_name
    if stem_bool:
        __posting_file_name = __path_delimiter + 'posting_with_stem' + __path_delimiter
    else:
        __posting_file_name = __path_delimiter + 'posting_without_stem' + __path_delimiter
    Writer.set_stemmer_mode(stem_bool)


# Where to save the temp posting files?
def set_posting_folder(path):
    global __temp_posting_files_folder
    global __output_folder
    __temp_posting_files_folder = path + __path_delimiter + 'temp_files' + __path_delimiter
    __output_folder = path
    Writer.set_temp_posting_folder_path(path)


# This function close all the open files and clean file dictionary
def reset():
    global __finished_temp_files
    global file_dictionary
    __finished_temp_files = 0

    for key, value in file_dictionary:  # This for create the files's objects
        value.close()

    file_dictionary = {}
    __remove_posting_files()


# This function return the number of file that finished the merge
def get_finished_file():
    return __finished_temp_files


# This function gets temp dictionary and write the dictionary to disk
def create_temp_posting_file(terms_dictionary):
    Writer.write_dictionary_to_temp_posting_file(terms_dictionary)


def __update_cosine_denominator(documents_dictionary_ref_ref, line, idf):
    line = line.split(__docs_delimiter)  # split the line by delimiter
    docs_id_list = line[::2]  # create list of docs id
    frequent_list = list(map(float, line[1::2]))  # create list of frequents

    index = 0
    for doc_id in docs_id_list:
        documents_dictionary_ref_ref[doc_id][2] += pow(frequent_list[index] * idf, 2)
        index += 1


# This function merge all the temp posting files
def merge_files(documents_dictionary):
    global __finished_temp_files
    __finished_temp_files = 0
    final_dictionary = {}  # The final dictionary that we created
    # The cache dictionary that we created. We need to find all the terms with idf that smaller the idf knapsack
    cache_dictionary = {}

    lines_dictionary = {}  # This dictionary save the first line for each temp post file {file_name -> docs_list}
    term_dictionary = {}  # This dictionary save the term for each line {file_name -> term}
    documents_dictionary_length = len(documents_dictionary)
    local_file_index = Writer.get_file_index()

    for index in range(1, local_file_index + 1):  # This for create the files's objects
        file_path = __temp_posting_files_folder + str(index) + '.txt'

        if not os.path.exists(__temp_posting_files_folder):
            os.makedirs(__temp_posting_files_folder)

        file_dictionary[index] = open(file_path, 'r', encoding='utf-8')

    for index in range(1, local_file_index + 1):  # This for update the line and term for each file
        __fetch_line(index, lines_dictionary, term_dictionary)

    merged_files_dictionary = {}  # This dictionary store the files' objects
    merged_files_counter = {}  # This dictionary store the in line index for each file

    __update_merged_files_dictionary(merged_files_dictionary, merged_files_counter, 'abc')
    __update_merged_files_dictionary(merged_files_dictionary, merged_files_counter, 'defgh')
    __update_merged_files_dictionary(merged_files_dictionary, merged_files_counter, 'ijklmno')
    __update_merged_files_dictionary(merged_files_dictionary, merged_files_counter, 'pqrs')
    __update_merged_files_dictionary(merged_files_dictionary, merged_files_counter, 'tuvwxyz')
    __update_merged_files_dictionary(merged_files_dictionary, merged_files_counter, 'others')

    while __finished_temp_files != local_file_index:  # while there is another line and term
        original_line = ''
        # This code find the minimum term by lexicographically order
        min_lexicographically_term_file_name = min(term_dictionary.keys(), key=(lambda k: term_dictionary[k]))
        min_lexicographically_term = term_dictionary[min_lexicographically_term_file_name]

        file_name_with_min = []  # This list save keys that equals to the min term
        for key, value in term_dictionary.items():
            if value == min_lexicographically_term:  # if there are more terms that equal to min term 
                if original_line == '':  # if the line is empty
                    original_line = lines_dictionary[key]
                else:  # if the line is not empty - add delimiter
                    original_line += __docs_delimiter + lines_dictionary[key]
                file_name_with_min.append(key)

        for index in file_name_with_min:
            __fetch_line(index, lines_dictionary, term_dictionary)

        # for more information read details about the function
        sorted_line, sum_tf, df = __sort_by_frequents(original_line, documents_dictionary)
        # Here we calculate the idf by the formula log_2(N/df_i)
        # when N = number of documents in the corpus
        # df_i = number of docs per term

        if sum_tf > 1:
            idf = log2(documents_dictionary_length / df)
            __update_cosine_denominator(documents_dictionary, sorted_line, idf)
            first_char = min_lexicographically_term[0]
            if float(idf) < float(__idf_threshold):  # Here we check if the term is popular
                # we gets relevant line and non relevant line depends on the cache size
                relevant_line, non_relevant_line = __relevant_non_relevant_documents(sorted_line)

                file_name = __get_file_name(first_char)
                # here we add the relevant line to the cache and pointer to more non relevant docs in the disk
                cache_dictionary[min_lexicographically_term] = \
                    (relevant_line, (file_name, merged_files_counter[file_name]))
                # we add a pointer from the final dictionary to the cache
                # and we add the non relevant line to the disk
                final_dictionary[min_lexicographically_term] = ((idf, sum_tf, df), __cache_pointer)
                merged_files_dictionary[file_name].write(non_relevant_line + '\n')
                merged_files_counter[file_name] += 1

            else:  # The term is not popular
                # we add the non relevant line to the disk and we add a pointer from the final dictionary to the disk
                file_name = __get_file_name(first_char)
                final_dictionary[min_lexicographically_term] = \
                    ((idf, sum_tf, df), (file_name, merged_files_counter[file_name]))
                merged_files_dictionary[file_name].write(sorted_line + '\n')
                merged_files_counter[file_name] += 1

    Writer.reset_file_index()
    files_size = 0
    for key, value in merged_files_dictionary.items():
        file_path = __output_folder + __posting_file_name + key + '.txt'
        files_size += os.path.getsize(file_path)
        value.close()

    return final_dictionary, cache_dictionary, files_size
