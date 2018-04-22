"""
The Parser gets string and try to figure out what is the terms in the string, the main function will
return a dictionary with terms (the keys) and with frequent of the term and if we need to stemm the word (the values).

Rules:
3.555555 --> 3.56 | 2/3 --> 0.67 | 1,345 --> 1345 | 6% --> 6 percent | 10.6 percentage --> 10.6 percent
DDth Month YYYY or DD Month YYYY or DD Month YY or Month DD, YYYY --> DD/MM/YYYY | DD Month or Month DD --> DD/MM
DD Month --> MM/YYYY | Abigail --> abigail | NBA --> nba | israel's --> israel | 5 --> 5.00 | yes/no --> (1) yes, (2) no
5-8 --> (1) 5 + (2) 8 |Abigail Paradise --> (1) abigail + (2) paradise + (3) abigail paradise
"""

import configparser
__config = configparser.ConfigParser()
__config.read('config.ini')

__months_dictionary = {'january': '01', 'jan': '01', 'february': '02', 'feb': '02', 'march': '03', 'mar': '03',
                       'april': '04', 'apr': '04', 'may': '05', 'june': '06', 'jun': '06', 'july': '07', 'jul': '07',
                       'august': '08', 'aug': '08', 'september': '09', 'sep': '09', 'october': '10', 'oct': '10',
                       'november': '11', 'nov': '11', 'december': '12', 'dec': '12'}

__months_set = {'january', 'jan', 'february', 'feb', 'march', 'mar', 'april', 'apr',
                'may', 'june', 'jun', 'july', 'jul', 'august', 'aug', 'september',
                'sep', 'october', 'oct', 'november', 'nov', 'december', 'dec'}

__punctuations_set = {'[', '(', '{', '`', ')', '<', '|', '&', '~', '+', '^', '@', '*', '?', '$', '.',
                      '>', ';', '_', '\'', ':', ']', '/', '\\', "}", '!', '=', '#', ',', '\"', '-'}


__stop_words = ''
__stem_mode = 0


def set_stemmer_mode(stem_bool):
    global __stem_mode
    __stem_mode = stem_bool


def set_stop_words_file(path):
    global __stop_words
    with open(path) as wordbook:
        __stop_words = set(word.strip() for word in wordbook)


# This function clean numeric tokens
def __clean_numeric(token):
    token = token.replace(',', '')
    token = ' '.join(token.split())
    return "{:.2f}".format(float(token))


# This function clean the token
def __clean_token(token):
    token_length = len(token)
    while (token_length > 0) and token[0] in __punctuations_set:
        token = token[1:]
        token_length -= 1

    while (token_length > 1) and token[token_length - 1] in __punctuations_set:
        token = token[:-1]
        token_length -= 1

    return token


# This function clean the token and return boolean if we removed and suffix
def __clean_token_with_boolean(token):
    is_cleaned_suffix = False
    token_length = len(token)
    while (token_length > 0) and token[0] in __punctuations_set:
        token = token[1:]
        token_length -= 1

    while (token_length > 1) and token[token_length - 1] in __punctuations_set:
        token = token[:-1]
        token_length -= 1
        is_cleaned_suffix = True

    return token, is_cleaned_suffix


# This function check if the token is valid number and return True if so
def __is_valid_number(token):
    percent_symbol_flag = False
    fraction_flag = False
    number_of_dots = 0

    two_last_char = token[-2:]
    # one_last_char = two_last_char[-1:]

    if two_last_char == "bn":
        token = token[:-2]
        for c in token:
            is_numeric_number = c.isnumeric()
            is_punctuation = False
            if c == '.' or c == ',' or c == '%' or c == '/':
                is_punctuation = True
                if c == '.':
                    number_of_dots += 1
            if (not is_numeric_number) and (not is_punctuation):
                return False

        if number_of_dots > 1:
            return False
        else:
            return True

    else:
        for c in token:
            if c == '%':
                percent_symbol_flag = True
            elif c == '/':
                fraction_flag = True
            is_numeric_number = c.isnumeric()
            is_punctuation = False
            if c == '.' or c == ',' or c == '%' or c == '/':
                is_punctuation = True
                if c == '.':
                    number_of_dots += 1
            if (not is_numeric_number) and (not is_punctuation):
                return False

        if number_of_dots > 1:
            return False
        if percent_symbol_flag:
            i = 0
            while i < (len(token) - 1):
                if token[i] == '%':
                    return False
                i += 1

        if fraction_flag:
            fraction_list = token.split('/')
            if not fraction_list[1].isnumeric():
                return False
            if len(fraction_list) != 2:
                return False

    return True


# This function handle sentence that begin with more than 2 words start with uppercase
def __insert_uppercase_sentence(terms_dictionary, sentence_list):
    valid_words = []
    list_length = len(sentence_list)
    while list_length != 0:
        token = sentence_list.pop(0)
        list_length -= 1
        if token in __stop_words:
            valid_words.append(token)
        else:
            if token[-2:] == "'s":
                token = token[:-2]
            valid_words.append(token)
            __add_to_dictionary_with_checks(terms_dictionary, token, len(token))

    if len(valid_words) > 1:
        __insert_to_dictionary(terms_dictionary, " ".join(valid_words), 1)


# This function gets dictionary and day, month and year and add the date to the dictionary
def __insert_dates(terms_dictionary, day, month, year):
    month = __months_dictionary[month]
    day_length = len(day)
    year_length = len(year)
    if year_length != 0:
        if 0 < int(year) < 100:
            year = "19" + year
        if day_length != 0:
            if day_length == 1:
                day = "0" + day
            __insert_to_dictionary(terms_dictionary, day + "/" + month + "/" + year, 0)
        else:
            __insert_to_dictionary(terms_dictionary, month + "/" + year, 0)
    elif day_length != 0:
        if day_length == 1:
            day = "0" + day
        __insert_to_dictionary(terms_dictionary, day + "/" + month, 0)


# This function gets dictionary, token to insert and number that indicate if the word needs stemming
def __insert_to_dictionary(terms_dictionary, token, to_stem):
    if __stem_mode:
        if token in terms_dictionary:
            terms_dictionary[token][0] += 1
        else:
            terms_dictionary[token] = [1, to_stem]
    else:
        if token in terms_dictionary:
            terms_dictionary[token] += 1
        else:
            terms_dictionary[token] = 1


# This function gets dictionary, token to insert and the length of the token, check if the length smaller then 4
# also, this function check if the 2 last chars are "'s" and remove it
def __add_to_dictionary_with_checks(terms_dictionary, token, token_length):
    if token_length > 2 and token[-2:] == "'s":
        token = token[:-2]

    if token_length <= 3:
        __insert_to_dictionary(terms_dictionary, token, 0)
    else:
        __insert_to_dictionary(terms_dictionary, token, 1)


# This function gets dictionary and text to parse and push tokens to the dictionary.
# The function returns text that need second parse
def __parse_it(terms_dictionary, text):
    re_parse_list = []
    sentence_list = []

    # replace the symbol '-' with space
    text = text.replace('-', ' ')
    text = text.split()

    index = 0
    index_last_token = len(text) - 1

    while index < index_last_token+1:
        # cleaning the token and check if we removed any suffix
        token, is_cleaned_suffix = __clean_token_with_boolean(text[index])
        token_length = len(token)
        contains_th = False  # This boolean use for check if the last 2 char in the token equal to 'th'
        if token_length > 2 and token[-2:] == "th":  # Check if the  last 2 char in the token equal to 'th'
            contains_th = True

        if token_length > 0:  # check if the token not empty
            token_lower = token.lower()  # save the token in lower cases for others uses
            if token_lower in __months_set:  # case 1: the token is a month, for example: May, June
                if index != index_last_token:  # if the token is not the last token in the list
                    # bringing the next token after we cleaned the next token
                    next_token = __clean_token(text[index + 1])
                    if str.isnumeric(next_token):  # case 1.1: the token is a number, for example: 12, 1992, 95
                        if 0 < int(next_token) <= 31:  # case 1.1.1: the token is a day, for example: 12
                            if index + 1 != index_last_token:  # if the token is not the last token in the list
                                # bringing the double next token after we cleaned the double next token
                                double_next_token = __clean_token(text[index + 2])
                                # case 1.1.1.1: the token is a year, for example: 95, 1992
                                if str.isnumeric(double_next_token) and 0 < int(double_next_token) <= 2050:
                                    __insert_dates(terms_dictionary, next_token, token_lower, double_next_token)
                                    index += 2
                                # case 1.1.1.2: the token is not a year, some token we don't recognize
                                else:
                                    __insert_dates(terms_dictionary, next_token, token_lower, '')
                                    index += 1
                            else:  # if the token is the last token in the list
                                __insert_dates(terms_dictionary, next_token, token_lower, '')
                                index += 1
                        elif 0 < int(next_token) <= 2050:  # case 1.1.2: the token is a year, for example: 95, 1992
                            __insert_dates(terms_dictionary, '', token_lower, next_token)
                            index += 1
                        else:  # case 1.1.1: the token is not a day or year but other number, for example: 9999, 2070
                            __insert_to_dictionary(terms_dictionary, token, 0)
                    else:  # case 1.1: if token is not a number
                        if token_lower in __stop_words:
                            pass
                        else:
                            __add_to_dictionary_with_checks(terms_dictionary, token_lower, token_length)
                else:  # if the token is the last token in the list
                    if token_lower in __stop_words:
                        pass
                    else:
                        __add_to_dictionary_with_checks(terms_dictionary, token_lower, token_length)
            # case 2: the token is a day, for example: 12 or 12th
            elif (str.isnumeric(token) and 0 < int(token) <= 31) or\
                    (contains_th and str.isnumeric(token[:-2]) and 0 < int(token[:-2]) <= 31):
                if contains_th:  # Check if the  last 2 char in the token equal to 'th'
                    token = token[:-2]

                if index != index_last_token:  # if the token is not the last token in the list
                    # bringing the next token after we cleaned the next token
                    next_token = __clean_token(text[index + 1])
                    next_token_lower = next_token.lower()  # save the token in lower cases for others uses
                    if next_token_lower in __months_set:  # case 2.1:  the token is a month, for example: May, June
                        if index + 1 != index_last_token:  # if the token is not the last token in the list
                            # bringing the double next token after we cleaned the double next token
                            double_next_token = __clean_token(text[index + 2])
                            # case 2.1.1: the double token is a year
                            if str.isnumeric(double_next_token) and 0 < int(double_next_token) <= 2050:
                                __insert_dates(terms_dictionary, token, next_token_lower, double_next_token)
                                index = index + 2
                            else:  # if the double token is not a year, some token we don't recognize
                                __insert_dates(terms_dictionary, token, next_token_lower, '')
                                index = index + 1
                        else:  # if the token is the last token in the list
                            __insert_dates(terms_dictionary, token, next_token_lower, '')
                            index = index + 1
                    else:  # if the next token is not a month, we use
                        __insert_to_dictionary(terms_dictionary, "{:.2f}".format(float(token)), 0)
                else:  # if the token is the last token in the list
                    __insert_to_dictionary(terms_dictionary, "{:.2f}".format(float(token)), 0)
            elif token[0].isupper():  # case 3: if the first char is upper case
                if '/' in token:
                    re_parse_list += token.split('/')
                    index += 1
                    continue
                if not is_cleaned_suffix:  # if we not cleaned a punctuation from the suffix
                    sentence_list.append(token_lower)  # we adding the the token in lower case to list
                    next_upper_number = 0  # number of tokens with upper case after the first token
                    if index != index_last_token:  # if the token is not the last token in the list
                        # cleaning the next token and check if we removed any suffix
                        next_token, is_cleaned_suffix = __clean_token_with_boolean(text[index + 1])
                        if '/' in next_token:
                            re_parse_list += next_token.split('/')
                            index += 1
                            continue
                        while len(next_token) == 0 or next_token[0].isupper():
                            if len(next_token) != 0:
                                next_token = next_token.lower()
                                sentence_list.append(next_token)
                            next_upper_number += 1
                            # if we removed any punctuation from the suffix we need to stop for example: DOG CAT,
                            if is_cleaned_suffix:
                                break
                            # if the next token is not the last token in the list
                            if (index + next_upper_number) != index_last_token:
                                next_token, is_cleaned_suffix = \
                                    __clean_token_with_boolean(text[index + next_upper_number + 1])
                                if '/' in next_token:
                                    re_parse_list += next_token.split('/')
                                    index += 1
                                    break
                            else:
                                break
                    index += next_upper_number  # move the index forward
                    # this function fix the handle the list and add the tokens
                    __insert_uppercase_sentence(terms_dictionary, sentence_list)
                else:  # if we cleaned a punctuation from the suffix
                    if token_lower in __stop_words:
                        pass
                    else:
                        __add_to_dictionary_with_checks(terms_dictionary, token_lower, token_length)
            elif token[0].isdigit():  # case 4: if the first char is a digit
                if __is_valid_number(token):  # case 4.1: check if the token is a valid number
                    if token[token_length - 1] == '%':  # case 4.1.1: the number is contains % at the end
                        token = token[:-1]  # remove the % from the last position
                        if '/' in token:  # case 4.1.1.1: the number is contains one '/'
                            fraction_list = token.split('/')  # split the token by decimeter '/'
                            if len(fraction_list) == 2:  # check if it is fraction
                                up = float(__clean_numeric(fraction_list[0]))
                                down = float(__clean_numeric(fraction_list[1]))
                                if down != 0:
                                    token = "{:.2f}".format(up / down)
                                else:
                                    __insert_to_dictionary(terms_dictionary, "{:.2f}".format(up) + " percent", 0)
                                    __insert_to_dictionary(terms_dictionary, "{:.2f}".format(down) + " percent", 0)
                                    index += 1
                                    continue
                        else:  # the number is not contains one '/'
                            token = __clean_numeric(token)  # remove others symbols
                        __insert_to_dictionary(terms_dictionary, token + " percent", 0)  # add the token with percent
                    elif '/' in token:  # case 4.1.2: the number is contains one '/'
                        fraction_list = token.split('/')  # split the token by decimeter '/'
                        if len(fraction_list) == 2:  # check if it is fraction
                            up = float(__clean_numeric(fraction_list[0]))
                            down = float(__clean_numeric(fraction_list[1]))
                            if down != 0:
                                token = "{:.2f}".format(up / down)
                            else:
                                __insert_to_dictionary(terms_dictionary, "{:.2f}".format(up), 0)
                                __insert_to_dictionary(terms_dictionary, "{:.2f}".format(down), 0)
                                index += 1
                                continue
                        __insert_to_dictionary(terms_dictionary, token, 0)
                    elif token[-2:] == 'bn':
                        clean_token = __clean_numeric(token[:-2])
                        __insert_to_dictionary(terms_dictionary, clean_token, 0)  # add only the token
                        __insert_to_dictionary(terms_dictionary, "billion", 0)  # add the billion
                    else:  # case 4.1.3: it's regular number
                        token = __clean_numeric(token)
                        if index != index_last_token:  # if the token is not the last token in the list
                            next_token = __clean_token(text[index + 1])  # clean the next token
                            if next_token == ("percent" or "percentage" or "%"):  # if the next token is percent
                                __insert_to_dictionary(terms_dictionary, (token + " percent"), 0)
                                index += 1
                            else:  # if the next token is not percent
                                __insert_to_dictionary(terms_dictionary, token, 0)
                        else:  # if the token is the last token in the list
                            __insert_to_dictionary(terms_dictionary, token, 0)
                else:  # case 4.1: check if the token is a valid number
                        __add_to_dictionary_with_checks(terms_dictionary, token_lower, token_length)
            else:  # case 5: regular word
                if '/' in token:
                    re_parse_list += token.split('/')
                    index += 1
                else:
                    if token_lower in __stop_words:
                        pass
                    else:
                        __add_to_dictionary_with_checks(terms_dictionary, token_lower, token_length)
        # after we finish with the cases we need to jump to the next token
        index += 1

    return ' '.join(re_parse_list)


def start(text):
    terms_dictionary = {}
    split_tokens = __parse_it(terms_dictionary, text)

    if len(split_tokens) != 0:
        __parse_it(terms_dictionary, split_tokens)

    return terms_dictionary


# This function gets text and return list of sentence separate by dot (there is special cases)
# Example: "Hello, my name is Nevo.[" What is your name?"
# Another example: "I love U.S. and Tomer like U.S. too."
# This function knows how to separate the sentences above
def sentences(text):
    list_of_sentences = []
    # Set of words that we don't want to
    words_with_dots = {'mr.', 'ms.', 'lt.', 'col.', 'minister.'}

    # replace the symbol '-' with space
    text = text.replace('-', ' ')
    text = text.split()

    sentence = ''
    for token in text:
        one_last_char = token[-1:]  # We want to check the last char in any word

        index = 2  # This index uses for cutting the index'th char from the end
        while one_last_char in __punctuations_set and len(token) >= index and one_last_char is not '.':
            one_last_char = token[-index:][0]  # Cutting the index'th char from the end
            index += 1

        if token.count(".") > 1:  # If the word contains more then one dot, it's not the end
            sentence += token + ' '
        # If the last char is dot and the token is not in our special cases set, the token finish the sentence
        elif one_last_char is '.' and token.lower() not in words_with_dots:
            sentence += token + ' '
            list_of_sentences.append(sentence)
            sentence = ''
        else:
            sentence += token + ' '

    if not sentence == '':
        list_of_sentences.append(sentence)

    return list_of_sentences
