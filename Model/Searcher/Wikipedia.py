import wikipediaapi
from Model.Parser import Parser
from collections import Counter
from Model.Stemmer import Stemmer

number_of_results = 5  # Number of results we want to return

def print_sections(sections):
    line = ''
    for s in sections:
        line += s.title + s.text[0:100]
    return line


class Wiki:

    #This function gets query and stem_mode and return a dictionary with relevant terms with weight per term
    def find(self, query, stem_mode):

        total_value = 0
        for x in range(0, 5):  # We want to use this value for the weights
            total_value += x

        sum_of_df = 0
        wiki_wiki = wikipediaapi.Wikipedia('en')  # Which language we want to search the term for
        page_py = wiki_wiki.page(query)  # Define the query in the file

        query_dictionary = {}  # The dictionary we will return to the user
        if page_py.exists():
            line = page_py.summary  # Here we collect the summary about the page in wiki
            if len(line) < 300:  # If we wiki didn't return a specific term, we ask for the sections
                line = print_sections(page_py.sections)
            if stem_mode:
                stop_set = {'disambigu'}  # Popular words we want to avoid
                query_after = Stemmer.stemWithCache(Parser.start(query))
                terms_dictionary = Stemmer.stemWithCache(Parser.start(line))
            else:
                stop_set = {'Disambiguation'}  # Popular words we want to avoid
                query_after = Parser.start(query)
                terms_dictionary = Parser.start(line)

            concept = {}
            links = page_py.links  # Here we collect the links from the page in wiki
            for title in sorted(links.keys()):
                if stem_mode:
                    term = Stemmer.stemWithCache(Parser.start(links[title].title))
                else:
                    term = Parser.start(links[title].title)

                for t, value in term.items():  # For each term in summary dictionary, we need to check the values
                    if links[title].ns == 0 and t in terms_dictionary and \
                            t not in query_after and t not in stop_set:
                        if t not in concept:
                            concept[t] = value
                        else:
                            concept[t] += value  # we want to add the value (the df to the dictionary)

            # Here we ask only for most common query results
            query_dictionary = dict(Counter(concept).most_common(number_of_results))
            for term, value in query_dictionary.items():
                sum_of_df += value

            for term, value in query_dictionary.items():
                positive_value = int(total_value * value / sum_of_df) + 1
                if positive_value == 0:
                    positive_value = 1
                query_dictionary[term] = positive_value
            if len(query_after) is not 0:
                query = list(query_after.keys())[0]
        else:
            print("Invalid query")

        query_dictionary[query] = number_of_results
        return query_dictionary
