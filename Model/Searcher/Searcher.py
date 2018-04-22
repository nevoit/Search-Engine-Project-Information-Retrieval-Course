from Model.Parser import Parser
from Model.Stemmer import Stemmer
from Model.Ranker import Ranker
from Model.Searcher.Wikipedia import Wiki
import configparser
from collections import Counter

__config = configparser.ConfigParser()
__config.read('config.ini')  # This function call to the config file
path_delimiter = __config['Indexer']['path_delimiter']  # Use to change between the Windows and Linux
REGULAR_RESULTS_NUMBER = int(__config['Searcher']['regular_results_number'])
EXPAND_RESULTS_NUMBER = int(__config['Searcher']['expand_results_number'])
SENTENCE_NUMBER = int(__config['Searcher']['sentence_number'])


class Searcher:
    stem_mode = 0
    folder_path = ''

    def __init__(self):
        self.ranker = Ranker.Ranker()

    def __set_stem_mode(self, stem_mode):
        self.stem_mode = stem_mode
        if stem_mode:
            self.folder_path = self.folder_path + path_delimiter + 'posting_with_stem' + path_delimiter
            self.denominator = 1.7  # Range (1 : dictionary_length)
            self.idf_weight = 0.8  # Range (0 : 1]
            self.df_weight = 0.7  # Range (0 : 1]
        else:
            self.folder_path = self.folder_path + path_delimiter + 'posting_without_stem' + path_delimiter
            self.denominator = 1.3  # Range (1 : dictionary_length)
            self.idf_weight = 0.2  # Range (0 : 1]
            self.df_weight = 0.7  # Range (0 : 1]

    def __set_folder_path(self, folder_path):
        self.folder_path = folder_path

    # This function expand query by using Wiki, This function return expand_results_number of results
    def expand(self, stem_mode, folder_path, final_dictionary, cache_dictionary, documents_dictionary, term):
        if final_dictionary is None or cache_dictionary is None or documents_dictionary is None:
            return []

        self.__set_folder_path(folder_path)
        self.__set_stem_mode(stem_mode)
        wiki = Wiki()  # Create object of Wiki

        terms_dictionary = wiki.find(term, stem_mode)  # Return the relevant terms and weight for each term
        dictionary = self.ranker.rank(self.folder_path, final_dictionary, cache_dictionary, documents_dictionary,
                                      terms_dictionary, EXPAND_RESULTS_NUMBER, stem_mode)
        return list(dictionary.keys())

    def search(self, stem_mode, folder_path, final_dictionary, cache_dictionary, documents_dictionary, query):
        if final_dictionary is None or cache_dictionary is None or documents_dictionary is None:
            return []
        else:
            self.__set_folder_path(folder_path)
            self.__set_stem_mode(stem_mode)

            # This code take a document's text from the list and parsing (or parsing and stemming) the text
            terms_dictionary = self.__parse_stem(query)
            dictionary = self.ranker.rank(self.folder_path, final_dictionary, cache_dictionary, documents_dictionary,
                                          terms_dictionary, REGULAR_RESULTS_NUMBER, stem_mode)
            return list(dictionary.keys())

    def multi_search(self, stem_mode, folder_path, final_dictionary, cache_dictionary,
                     documents_dictionary, query_list):
        if final_dictionary is None or cache_dictionary is None or documents_dictionary is None:
            return []
        else:
            list_for_return = []
            self.__set_folder_path(folder_path)
            self.__set_stem_mode(stem_mode)

            for query_tuple in query_list: # iterates over the queries in the query file given
                # This code take a document's text from the list and parsing & stemming the text
                query_num = query_tuple[0]
                title = query_tuple[1]
                description = query_tuple[2]
                narrative = query_tuple[3]

                narrative_sentences = Parser.sentences(narrative)
                new_narrative = ''
                for sentence in narrative_sentences:
                    if "not relevant" not in sentence:
                        new_narrative += " " + sentence
                    elif stem_mode and "are relevant" in sentence:
                        new_narrative += " " + sentence

                narrative = new_narrative
                # We define a words we want to avoid in our parse and stem
                terms_dictionary = self.__parse_stem(title)
                description_dictionary = self.__parse_stem(description + ' ' + narrative)
                if self.stem_mode:
                    words_to_avoid = {"relev", "document", "discuss", "consid", "i.e", "issu"}
                else:
                    words_to_avoid = {"relevant", "documents", "document", "discuss", "discussing",
                                      "information", "considered", "i.e", "issues"}

                description_dictionary_other = {}
                for key, value in description_dictionary.items():
                    if key in final_dictionary and key not in words_to_avoid:
                        # idf * query_tf
                        term_idf = final_dictionary[key][0][0]
                        description_dictionary_other[key] = (self.idf_weight * term_idf) + \
                                                            (self.df_weight * value)

                results_num = int(len(description_dictionary_other) / self.denominator)
                description_dictionary_other = dict(Counter(description_dictionary_other).most_common(results_num))

                for key, value in description_dictionary_other.items():
                    if key in terms_dictionary:
                        terms_dictionary[key] += description_dictionary_other[key]
                    else:
                        terms_dictionary[key] = description_dictionary_other[key]

                dictionary = self.ranker.rank(self.folder_path, final_dictionary, cache_dictionary,
                                              documents_dictionary, terms_dictionary, REGULAR_RESULTS_NUMBER, stem_mode)
                list_for_return.append((query_num, list(dictionary.keys())))

        return list_for_return

    # This function gets document id and returns list of the most popular sentences in the documents
    def find_popular_sentences(self, stem_mode, folder_path, final_dictionary, cache_dictionary,
                               documents_dictionary, doc_id, text):
        # If the dictionaries are empty, we cant continue
        if final_dictionary is None or cache_dictionary is None or documents_dictionary is None:
            return []
        else:
            self.__set_folder_path(folder_path)
            self.__set_stem_mode(stem_mode)

            # We need to parse and stem the text again, because it's slow to fetch the values from posting
            after_dictionary = self.__parse_stem(text)

            # We want to normalize the values with the max_tf value
            max_tf = documents_dictionary[doc_id][0]

            for key, value in after_dictionary.items():  # Here we update the tf of the document
                after_dictionary[key] = value/max_tf

            list_of_sentence = Parser.sentences(text)  # Here we get the list of sentences from Parser

            # Here we initialize the dictionary of sentences
            sentence_dictionary = {}
            for sentence_index in range(0, len(list_of_sentence)):
                sentence_dictionary[sentence_index] = 0

            term_with_after_dictionary = {}  # dictionary with dictionary after parsing and stemming
            sentence_index = 0
            for sentence in list_of_sentence:  # for every sentence, we doing the following steps
                terms_dictionary = self.__parse_stem(sentence)

                # We delete the terms that not in the final dictionary
                keys_to_delete = []
                for term in terms_dictionary.keys():
                    if term in final_dictionary:
                        pass
                    else:
                        keys_to_delete.append(term)
                for term in keys_to_delete:
                    terms_dictionary.pop(term)

                # Here we save the dictionary after parsing and stemming for later uses
                term_with_after_dictionary[sentence_index] = terms_dictionary
                sentence_index += 1

            # For every sentence we calculate the rank value with the formula tf*idf*freq
            for sentence_index, terms_dictionary in term_with_after_dictionary.items():
                if terms_dictionary is not None:
                    for term, value in terms_dictionary.items():
                        freq = terms_dictionary[term]
                        idf = final_dictionary[term][0][0]
                        tf = after_dictionary[term]
                        sentence_dictionary[sentence_index] += tf*idf*freq

            # Here we choose only the SENTENCE_NUMBER of the best sentences
            list_of_best_sentence = list(dict(Counter(sentence_dictionary).most_common(SENTENCE_NUMBER)).keys())

            # for each key in list_of_best_sentence we update the value to be the sentence
            sentence_index = 0
            for key in list_of_best_sentence:
                list_of_best_sentence[sentence_index] = list_of_sentence[key]
                sentence_index += 1

            return list_of_best_sentence

    def __parse_stem(self, text):
        if self.stem_mode:  # stem mode is True
            after_dictionary = Stemmer.stemWithCache(Parser.start(text))
        else:  # stem mode is False
            after_dictionary = Parser.start(text)
        return after_dictionary
