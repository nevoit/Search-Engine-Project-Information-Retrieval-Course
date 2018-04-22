import configparser
import threading
import os
import shutil
import json

__config = configparser.ConfigParser()
__config.read('config.ini')

__temp_posting_files_folder = ''
__output_folder = ''
__docs_delimiter = __config['Indexer']['docs_delimiter']
__term_delimiter = __config['Indexer']['term_delimiter']
__path_delimiter = __config['Indexer']['path_delimiter']

__file_index = 0  # number of file we created
__file_index_mutex = threading.Lock()  # Python create mutex
__dictionary_name = ''
__cache_name = ''
__document_name = ''
__cache_path = ''
__dictionary_path = ''
__document_path = ''


# setter for the stemmer mode
def set_stemmer_mode(stem_bool):
    global __cache_name
    global __dictionary_name
    global __document_name

    if stem_bool:
        __dictionary_name = 'dictionary_with_stem'
        __cache_name = 'cache_with_stem'
        __document_name = 'document_with_stem'
    else:
        __dictionary_name = 'dictionary_without_stem'
        __cache_name = 'cache_without_stem'
        __document_name = 'document_without_stem'


# Setter for the temp posting folder path
def set_temp_posting_folder_path(path):
    global __temp_posting_files_folder
    global __output_folder
    __temp_posting_files_folder = path + __path_delimiter + 'temp_files' + __path_delimiter
    __output_folder = path


# Also we remove the temp posting file
def remove_temp_file():
    if os.path.exists(__temp_posting_files_folder):
        shutil.rmtree(__temp_posting_files_folder)


# Getter for the file index
def get_file_index():
    return __file_index


# Setter for file index for zero
def reset_file_index():
    global __file_index
    __file_index = 0


# remove the files we created
def reset():
    global __file_index
    remove_temp_file()
    __file_index = 0

    if os.path.exists(__dictionary_path):
        os.remove(__dictionary_path)
    if os.path.exists(__cache_path):
        os.remove(__cache_path)
    if os.path.exists(__document_path):
        os.remove(__document_path)


# This function gets temp dictionary and write the dictionary to disk
def write_dictionary_to_temp_posting_file(dictionary):
    global __file_index
    __file_index_mutex.acquire()  # mutex.lock
    __file_index += 1  # index for file number
    local_index = __file_index  # using local index to ovid sync problem
    __file_index_mutex.release()  # mutex.unlock
    # Save sorted by key dictionary
    file_path = __temp_posting_files_folder + str(local_index) + '.txt'

    if not os.path.exists(__temp_posting_files_folder):
        os.makedirs(__temp_posting_files_folder)

    current_file = open(file_path, "w", encoding='utf-8')
    for key, value in sorted(dictionary.items(), key=lambda t: t[0]):
        current_file.write(str(key) + __term_delimiter + value + '\n')
    current_file.close()


# This function gets final dictionary and write the dictionary to disk
def save_final_dictionary(dictionary, folder_name):
    global __dictionary_path
    folder_name += __path_delimiter
    file_path = folder_name + __dictionary_name + '.json'
    __dictionary_path = file_path

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(file_path, 'w') as fp:
        json.dump(dictionary, fp)


# This function return final dictionary
def load_final_dictionary(folder_path, stem_mode):
    data = None

    if stem_mode:
        path = folder_path + __path_delimiter + 'dictionary_with_stem' + '.json'
    else:
        path = folder_path + __path_delimiter + 'dictionary_without_stem' + '.json'

    if os.path.exists(path):
        with open(path, 'r') as fp:
            data = json.load(fp)
    return data


# This function gets cache dictionary and write the dictionary to disk
def save_cache(dictionary, folder_name):
    global __cache_path
    folder_name += __path_delimiter
    file_path = folder_name + __cache_name + '.json'
    __cache_path = file_path

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(file_path, 'w') as fp:
        json.dump(dictionary, fp)


# This function return cache dictionary
def load_cache(folder_path, stem_mode):
    data = None

    if stem_mode:
        path = folder_path + __path_delimiter + 'cache_with_stem' + '.json'
    else:
        path = folder_path + __path_delimiter + 'cache_without_stem' + '.json'

    if os.path.exists(path):
        with open(path, 'r') as fp:
            data = json.load(fp)
    return data


# This function gets cache dictionary and write the dictionary to disk
def save_documents(dictionary, folder_name):
    global __document_path
    folder_name += __path_delimiter
    file_path = folder_name + __document_name + '.json'
    __document_path = file_path

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(file_path, 'w') as fp:
        json.dump(dictionary, fp)


# This function return documents dictionary
def load_documents(folder_path, stem_mode):
    data = None

    if stem_mode:
        path = folder_path + __path_delimiter + 'document_with_stem' + '.json'
    else:
        path = folder_path + __path_delimiter + 'document_without_stem' + '.json'

    if os.path.exists(path):
        with open(path, 'r') as fp:
            data = json.load(fp)
    return data


""" These functions save the results of the query to a file in the TREC EVAL format. This is a really weird format where 
 half of the required parameters are not even used. Each line in the output file will look as such:
 query_id iter docno rank  sim  run_id
   ^       ^     ^    ^     ^     ^   
3 digit    0  doc id  int float string

number                 (---ignored---)
  
  The controller calls this function when the user wants to save the results of a query file, and sends it the path 
  where to save the results, and a list of results. Each node in the list represents the results for a certain query.
 """
def save_query_file_results(results, save_results_path):
    with open(save_results_path, 'w') as srp:
        for query_result in results:
            query_id = query_result[0]
            for doc in query_result[1]:
                line = "%s %s %s %s %s %s \n" % (query_id, "0", doc, "1", "0", "run-id")
                srp.write(line)

""" This function is similar to the above but called when the user would like to save the results of a regular,
manually inserted query. """
def save_regular_result(results, save_results_path):
    with open(save_results_path, 'w') as srp:
        for doc_id in results:
            line = "%s %s %s %s %s %s \n" % ("000", "0", doc_id, "1", "0", "run-id")
            srp.write(line)