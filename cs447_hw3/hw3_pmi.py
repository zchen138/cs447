########################################
## CS447 Natural Language Processing  ##
##           Homework 3               ##
##       Julia Hockenmaier            ##
##       juliahmr@illnois.edu         ##
########################################
##
## Part 1:
## Use pointwise mutual information to compare words in the movie corpora
##
import os.path
import sys
from operator import itemgetter
from collections import defaultdict
import itertools
import math
import heapq

# ----------------------------------------
#  Data input
# ----------------------------------------

# Read a text file into a corpus (list of sentences (which in turn are lists of words))
# (taken from nested section of HW0)
def readFileToCorpus(f):
    """ Reads in the text file f which contains one sentence per line.
    """
    if os.path.isfile(f):
        file = open(f, "r")  # open the input file in read-only mode
        i = 0  # this is just a counter to keep track of the sentence numbers
        corpus = []  # this will become a list of sentences
        print("Reading file", f, "...")
        for line in file:
            i += 1
            sentence = line.split() # split the line into a list of words
            corpus.append(sentence) # append this list as an element to the list of sentences
            # if i % 1000 == 0:
            #    sys.stderr.write("Reading sentence " + str(i) + "\n") # just a status message: str(i) turns the integer i into a string, so that we can concatenate it
        return corpus
    else:
        print("Error: corpus file", f, "does not exist")  # We should really be throwing an exception here, but for simplicity's sake, this will suffice.
        sys.exit()  # exit the script

# --------------------------------------------------------------
# PMI data structure
# --------------------------------------------------------------
class PMI:
    # Given a corpus of sentences, store observations so that PMI can be calculated efficiently
    def __init__(self, corpus):
        single_word_count = {}
        word_pair_count = {}

        for sen in corpus:
            word_set = set(sen)
            for word in word_set:
                if word in single_word_count:
                    single_word_count[word] += 1
                else:
                    single_word_count[word] = 1

            word_combo_arr = []
            word_arr = list(word_set)
            for i in range (len(word_arr)):
                for j in range (i+1, len(word_arr)):
                    word_combo_arr.append(self.pair(word_arr[i], word_arr[j]))

            for unique_word_pair in word_combo_arr:
                if unique_word_pair in word_pair_count:
                    word_pair_count[unique_word_pair] += 1
                else:
                    word_pair_count[unique_word_pair] = 1

        self.word_count_dict = single_word_count
        self.word_pair_count_dict = word_pair_count
        self.sen_count = len(corpus)

    # Return the pointwise mutual information (based on sentence (co-)occurrence frequency) for w1 and w2
    def getPMI(self, w1, w2):
        val =float(self.word_pair_count_dict[self.pair(w1, w2)]*self.sen_count)/(self.word_count_dict[w1] * self.word_count_dict[w2])
        return math.log(val, 2)

    # Given a frequency cutoff k, return the list of observed words that appear in at least k sentences
    def getVocabulary(self, k):
        word_arr = []

        for word, count in self.word_count_dict.items():
            if count>=k:
                word_arr.append(word)

        return word_arr

    # Given a list of words and a number N, return a list of N pairs of words that have the highest PMI
    # (without repeated pairs, and without duplicate pairs (wi, wj) and (wj, wi)).
    # Each entry in the list should be a triple (pmiValue, w1, w2), where pmiValue is the
    # PMI of the pair of words (w1, w2)
    def getPairsWithMaximumPMI(self, words, N):
        word_set = set(words)
        heap = []

        for word_pair in self.word_pair_count_dict.keys():
            if word_pair[0] in word_set and word_pair[1] in word_set:
                heapq.heappush(heap, (self.getPMI(word_pair[0],word_pair[1]),(word_pair[0],word_pair[1])))
            if (len(heap)>N+3000):
                heap = heapq.nlargest(N, heap)
        heap = heapq.nlargest(N, heap)
        return_arr = []
        for elem in heap:
            word_pair = elem[1]
            return_arr.append((elem[0], word_pair[0], word_pair[1]))
        return return_arr

    #-------------------------------------------
    # Provided PMI methods
    #-------------------------------------------
    # Writes the first numPairs entries in the list of wordPairs to a file, along with each pair's PMI
    def writePairsToFile(self, numPairs, wordPairs, filename):
        f=open(filename, 'w+')
        count = 0
        for (pmiValue, wi, wj) in wordPairs:
            if count > numPairs:
                break
            count += 1
            print("%f %s %s" % (pmiValue, wi, wj), end="\n", file=f)

    # Helper method: given two words w1 and w2, returns the pair of words in sorted order
    # That is: pair(w1, w2) == pair(w2, w1)
    def pair(self, w1, w2):
        return (min(w1, w2), max(w1, w2))

#-------------------------------------------
# The main routine
#-------------------------------------------
if __name__ == "__main__":
    corpus = readFileToCorpus('movies.txt')
    pmi = PMI(corpus)
    lv_pmi = pmi.getPMI("luke", "vader")
    print("  PMI of \"luke\" and \"vader\": ", lv_pmi)
    numPairs = 100
    for k in [2, 5, 10, 50, 100, 200]:
        print("we are doing a k of %s", str(k))
        commonWords = pmi.getVocabulary(k)    # words must appear in least k sentences
        wordPairsWithGreatestPMI = pmi.getPairsWithMaximumPMI(commonWords, numPairs)
        pmi.writePairsToFile(numPairs, wordPairsWithGreatestPMI, "pairs_minFreq="+str(k)+".txt")
