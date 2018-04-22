import configparser
import linecache
from numpy import sqrt
from collections import Counter
import os
from numpy import log2

__config = configparser.ConfigParser()
__config.read('config.ini')  # This function call to the config file
path_delimiter = __config['Indexer']['path_delimiter']  # Use to change between the Windows and Linux
docs_delimiter = __config['Indexer']['docs_delimiter']  # The delimiter between the docs


""" 
This function gets the query terms dictionary and return the a dictionary that looks like:
    +----------+----------------------------------------+
    |          | +------------------------------------+ |
    |          | | doc1 |  doc2  |  doc3  |doc4       | |
    | term1    | |      |        |        |           | |
    |          | +--------------------------------------+
    |          | | 1    |   0.7  |  0.6   |  0.5      | |
    |          | +------+--------+--------+-----------+ |
    |          |                                        |
    +----------+ +------+--------+--------+-----------+ |
    |          | | doc6 |  doc7  |  doc8  | doc9      | |
    |          | |      |        |        |           | |
    |          | +------------------------------------+ |
    | term4    | |      |        |        |           | |
    |          | | 0.6  |  0.4   |  0.3   |  0.6      | |
    |          | +------------------------------------+ |
    +----------+----------------------------------------+
"""


def get_mini_posting(folder_path, final_dictionary, cache_dictionary, query_terms_dictionary):
    mini_posting_local = {}
    for term, w_iq in query_terms_dictionary.items():
        if term not in final_dictionary:
            continue
        link_to_line = final_dictionary[term][1]
        if not link_to_line == '*':
            file_name = link_to_line[0] + '.txt'
            line_index = link_to_line[1]
            file_path = folder_path + path_delimiter + file_name
            if os.path.exists(file_path):
                line = linecache.getline(file_path, line_index)
            else:
                print("We can't find your path:" + file_path)
        else:
            line = cache_dictionary[term][0]  # (relevant_line, (file_name, line_index))
            link_tuple = cache_dictionary[term][1]
            file_name = link_tuple[0] + '.txt'
            line_index = link_tuple[1]
            file_path = folder_path + path_delimiter + file_name
            if os.path.exists(file_path):
                line_from_posting = linecache.getline(file_path, int(line_index))
                line += docs_delimiter + line_from_posting
            else:
                print("We can't find your path:" + file_path)

        linecache.clearcache()
        line = line.split(docs_delimiter)  # split the line by delimiter
        docs_id_list = line[::2]  # create list of docs id
        frequent_list = list(map(float, line[1::2]))  # create list of frequents
        mini_posting_local[term] = (docs_id_list, frequent_list)

    return mini_posting_local


class Ranker:
    mini_posting = {}
    table_dictionary = {}
    documents_with_rank = {}
    folder_path = ''

    def __set_stem_mode(self, stem_mode):
        self.stem_mode = stem_mode
        if self.stem_mode:
            self.average_document_length = 218.8510685996114
            self.bm25_weight = 0.1
            self.cos_sim_weight = 0.9
            self.bm25_k = 1.85  # Range: [1.2 - 2.0]
            self.bm25_b = 0.6  # Range: 0-1.0
            self.bm25_lambda = 0.25  # Range: 0-1.0
        else:
            self.average_document_length = 244.54214403142814
            self.bm25_weight = 0.05
            self.cos_sim_weight = 0.95
            self.bm25_k = 2  # Range: [1.2 - 2.0]
            self.bm25_b = 0.5  # Range: 0-1.0
            self.bm25_lambda = 0.2  # Range: 0-1.0

        self.bm25_idf = 0.5  # Range: 0-1.0

    def __set_folder_path(self, folder_path):
        self.folder_path = folder_path

    # This method gets query dictionary that contains the terms in query and the number of results we want to get back
    # The method rank the documents and return results_num best documents
    def rank(self, folder_path, final_dictionary, cache_dictionary, documents_dictionary,
             query_terms_dictionary, results_num, stem_mode):
        self.mini_posting = {}
        self.table_dictionary = {}
        self.documents_with_rank = {}
        self.__set_folder_path(folder_path)
        self.__set_stem_mode(stem_mode)

        # Here we prepare the data before the rank methods
        self.mini_posting = get_mini_posting(folder_path, final_dictionary, cache_dictionary, query_terms_dictionary)
        self.__create_documents_dictionary()
        # Here we use the rank methods
        self.__calc_bm_25(final_dictionary, documents_dictionary)
        self.__calc_sim(final_dictionary, documents_dictionary, query_terms_dictionary)

        results_dictionary = dict(Counter(self.documents_with_rank).most_common(results_num))
        return results_dictionary

    """
        This method create easy dictionary to iterate over documents to calculate weight per document
        +----------+----------------+-----------------------+
        |          |                |                       |
        |          |                |                       |
        |          |                |                       |
        | doc1     |  (term1, 1.0)  |  (term4, 0.3)         |
        |          |                |                       |
        |          |                |                       |
        |          |                |                       |
        +---------------------------------------------------+
        |          |                |                       |
        |          |                |                       |
        | doc5     |   (term1, 1.0) |   (ter10, 0.5)        |
        |          |                |                       |
        |          |                |                       |
        |          |                |                       |
        +----------+----------------+-----------------------+
    """
    def __create_documents_dictionary(self):
        for term, value in self.mini_posting.items():
            docs_id_list = value[0]
            frequent_list = value[1]
            index = 0
            for doc_id in docs_id_list:
                term_document_tuple = (term, frequent_list[index])
                if doc_id in self.table_dictionary:
                    self.table_dictionary[doc_id].append(term_document_tuple)
                else:
                    self.table_dictionary[doc_id] = [term_document_tuple]
                index += 1

    # Here we calculate the value of rank for each document by use cos sim formula
    # For more information about the formula:
    def __calc_sim(self, final_dictionary, documents_dictionary, query_terms_dictionary):
        query_terms = 0
        query_max_tf = 0
        number_of_query_terms = len(query_terms_dictionary)
        for term, value in query_terms_dictionary.items():
            query_terms += pow(value, 2)
            if value > query_max_tf:
                query_max_tf = value

        for doc_id, value in self.table_dictionary.items():
            numerator = 0
            denominator_doc_terms = sqrt(documents_dictionary[doc_id][2])
            denominator_query_terms = sqrt(query_terms)
            denominator = denominator_doc_terms * denominator_query_terms

            for term_document_tuple in value:
                term = term_document_tuple[0]
                term_freq = query_terms_dictionary[term]
                term_tf = number_of_query_terms * term_freq / query_max_tf
                tf = term_document_tuple[1]
                idf = final_dictionary[term][0][0]
                numerator += term_tf * tf * idf

            cosine = numerator / denominator
            self.documents_with_rank[doc_id] += self.cos_sim_weight * cosine

    # Here we calculate the value of rank for each document by use cos sim formula
    def __calc_bm_25(self, final_dictionary, documents_dictionary):
        number_of_documents = len(documents_dictionary)
        for doc_id, value in self.table_dictionary.items():
            document_length = documents_dictionary[doc_id][1]
            bm_25_value = 0
            for term_document_tuple in value:
                term = term_document_tuple[0]
                nq = final_dictionary[term][0][2]
                value_for_idf = (number_of_documents - nq + self.bm25_idf)/(nq + self.bm25_idf)
                idf = float(log2(value_for_idf))
                tf = term_document_tuple[1]
                f_query_doc = tf * documents_dictionary[doc_id][0]  # tf * max_tf = freq = df
                numerator = idf * (f_query_doc * (self.bm25_k + 1))
                denominator = (f_query_doc + self.bm25_k * (1 - self.bm25_b + (self.bm25_b * document_length / self.average_document_length)))
                bm_25_value += (numerator / denominator) + self.bm25_lambda * idf

            self.documents_with_rank[doc_id] = self.bm25_weight * bm_25_value
