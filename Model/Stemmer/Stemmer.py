"""
This is the Stemmer class. It receives the dictionary produced by the parser: The key being the term, and the value
being a list containing 2 parameters - # of repetitions and if it needs to be stemmed or not. The stemmer uses a cache,
a dictionary kept in the memory containing the stemmed version of many words. If a word is already in the cache, we
won't stem it. This has improved run-time by several factors.

The actual stemming is done by using the Natural Language Tool Kit (nltk). It downloads 2 additional modules to do this.
"""
import nltk
from nltk.stem.snowball import EnglishStemmer
import configparser

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
__config = configparser.ConfigParser()
__config.read('config.ini')


cacheDic = {}
# a Dictionary where the key is a parsed word (term), and the key is the stemmers' output.
#  e.g.: {volumes, volume} {university, univers}
stemmedDic = {}
stemmer = EnglishStemmer()


def cacheSize():
    return len(cacheDic.keys())

# stem receives a dictionary with terms from the parser. It will iterate through the dictionary and stem each key,
#  then insert it into a new dictionary. Won't stem if it's in the cache already!


def clean_cache():
    global cacheDic
    cacheDic = {}

def reset():
    global cacheDic
    global stemmedDic
    cacheDic = {}
    stemmedDic = {}

def stemWithCache(termDic):

    global cacheCount
    stemmedDic = {}
    for k, v in termDic.items():
        if v[1] == 0:  # No need to stem it, just add it!
            stemmedDic[k] = v[0]
            continue
        else:
            if k in cacheDic:  # If it's in the cachedDic USE IT!
                stemmedDic[cacheDic[k]] = v[0]
                continue
            if ' ' in k:  # The key is a sentence and not a single word..
                splitKey = k.split()
                stemmedKey = []
                for i in splitKey:  # loop through the words in the sentence
                    if i in cacheDic:  # If we already stemmed/cached the word -
                        stemmed_i = cacheDic[i]
                    else:  # It isn't in cacheDic
                        stemmed_i = stemmer.stem(i)  # stem it
                        cacheDic[i] = stemmed_i  # add it to the cache
                    stemmedKey.append(stemmed_i)  # append it to the list
                stemmedKey = ' '.join(splitKey)  # re-create the sentence
            else:            # else, we can stem the word.
                stemmedKey = stemmer.stem(k)  # the key is a single word
            if stemmedKey in stemmedDic:  # We've already encountered this stemmed word
                currVal = stemmedDic[stemmedKey]
                stemmedDic[stemmedKey] = currVal + v[0]  # sum the num of appearances.
            else:
                stemmedDic[stemmedKey] = v[0]
            cacheDic[k] = stemmedKey  # input into the cache
    return stemmedDic


# Used for comparing run times.#
def stemWithoutCache(termDic):
    stemmedDic = {}
    for k, v in termDic.items():
        if v[1] == 0: #No need to stem it, just add it!
            stemmedDic[k] = v[0]
            continue
        else:
            if(' ' in k): # The key is a sentence and not a single word..
                splitKey = k.split()
                stemmedKey = []
                for i in splitKey: #loop through the words in the sentence
                    stemmed_i = stemmer.stem(i) #stem it
                    stemmedKey.append(stemmed_i) #append it to the list
                stemmedKey = ' '.join(splitKey) # re-create the sentence
            else:            # else, we can stem the word.
                stemmedKey = stemmer.stem(k) #the key is a single word
            if stemmedKey in stemmedDic: #We've already encountered this stemmed word
                currVal = stemmedDic[stemmedKey]
                stemmedDic[stemmedKey] = currVal + v[0] #sum the num of appearances.
            else:
                stemmedDic[stemmedKey] = v[0]
    return stemmedDic