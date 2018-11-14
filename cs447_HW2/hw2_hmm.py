########################################
## CS447 Natural Language Processing  ##
##           Homework 2               ##
##       Julia Hockenmaier            ##
##       juliahmr@illnois.edu         ##
########################################
##
## Part 1:
## Train a bigram HMM for POS tagging
##
import os.path
import sys
from operator import itemgetter
from collections import defaultdict
import numpy as np
import math
# Unknown word token
UNK = 'UNK'

def smallProbMultiplication(num1, num2):
    return (math.log(num1) + math.log(num2))

def smallProbArrayMult(col_arr, trans_arr):
    new_trans_arr = np.log(trans_arr)

    return (col_arr + new_trans_arr)

class Trellis():
    ''' array, array, dict-keys are (word, tag), bigram object, dict'''
    def __init__(self, tags, words, emission_prob, transition_bigram, tag_prob):
        #first generate a numpy trellis array and fill it with zeros, it will
        #rows as tags and words as columns
        #we are working in log space
        self.words = words
        self.tags = tags
        self.trellis_arr = np.zeros((len(tags), len(words)))
        #create a traceback dict and possible emission tuple set
        self.backtrace_dict = {}
        possible_emission_tups = set(emission_prob.keys())
        #second fill in the first column of the trellis by multiplying
        #the inital prob of tag by the emision prob
        for i in range (len(tags)):
            if (words[0], tags[i]) in possible_emission_tups:
                #so the first tag should be number of times the tag occurs as the first element/number of sentences
                if (tags[i] in tag_prob):
                    self.trellis_arr[i][0] = smallProbMultiplication(tag_prob[tags[i]], emission_prob[(words[0], tags[i])])
                else:
                    self.trellis_arr[i][0] = np.NINF
            else:
                #since the element is zero then it should be set to negative infinity
                self.trellis_arr[i][0] = np.NINF
        #then generate all other columns of the tag

        #for a column
        for col in range (1, len(words)):
            for row in range (len(tags)):

                cur_word = words[col]
                cur_tag = tags[row]
                #see if you can emitt the tag from this word, if not then 0
                if (cur_word, cur_tag) in possible_emission_tups:
                    #create a array of the transitional probabilities and create an array for the last column
                    last_col = self.trellis_arr[:,col-1]

                    transitions = self.getTransitionalProbForTag(cur_tag, transition_bigram, tags)

                    #log the transition column and then add both column together into a array
                    result_prob_arr = smallProbArrayMult(last_col, transitions)

                    prob_max_val = np.amax(result_prob_arr)
                    prob_max_index = np.argmax(result_prob_arr)
                    #do the log thing again but this time with the emision probability and the largest val
                    self.trellis_arr[row][col] = prob_max_val + math.log(emission_prob[(cur_word, cur_tag)])

                    #fill the traceback dict map the (i,j) to previous index of the max value
                    self.backtrace_dict[(row, col)] = prob_max_index
                else:
                    self.trellis_arr[row][col] = np.NINF

        #for the last column find the (i, len(col)-1) with the greatest value
        last_col = self.trellis_arr[:, len(words)-1]
        last_col_max_val = np.amax(last_col)
        self.last_tag_index = np.argmax(last_col)
        self.last_tag = tags[self.last_tag_index]

    def getSentenceTags(self):
        tag_arr = []
        #append the last tag to our tag array
        tag_arr.append(self.last_tag)
        #look through your backtrace dict for the last word tag combo go from len(words)-1 to 1
        cur_last_tag_index = self.last_tag_index
        for col in range (len(self.words)-1, 0, -1):
            last_index = self.backtrace_dict[(cur_last_tag_index, col)]
            tag_arr.append(self.tags[last_index])
            cur_last_tag_index = last_index

        #return that tag sentence

        tag_arr.reverse()
        return tag_arr

    def getTransitionalProbForTag(self,cur_tag, transition_bigram, all_tags):
        transition_prob_arr = []
        for prev_tag in all_tags:
            transition_prob_arr.append(transition_bigram.prob(prev_tag, cur_tag))
        return np.array(transition_prob_arr)

class BigramModel():
    def __init__(self, corpus):
        self.prob_dict = {}
        self.tup_dict = {}
        self.tag_dict = {}
        self.corpus_length = 0.0
        self.train(corpus)
    #endddef
    def train(self, corpus):

        tag_types = set()

        for sen in corpus:
            sen_len = len(sen)
            for i in range (sen_len):
                tag = sen[i]

                if tag in self.tag_dict:
                    self.tag_dict[tag] += 1.0
                else:
                    self.tag_dict[tag] = 1.0

                tag_types.add(tag)
                self.corpus_length += 1.0

                if i != sen_len-1:
                    next_tag = sen[i+1]
                    cur_tup = (tag, next_tag)

                    if cur_tup not in self.tup_dict:
                        self.tup_dict[cur_tup] = 1.0
                    else:
                        self.tup_dict[cur_tup] += 1.0

            #endfor
        #endfor
        self.V_val = len(tag_types)
    #enddef

    def prob(self, first_tag, second_tag):

        cur_tup = (first_tag, second_tag)

        if cur_tup in self.prob_dict:
            return self.prob_dict[cur_tup]
        else:
            #get laplace second word is used here
            tup_count = 0.0
            if (cur_tup in self.tup_dict):
                tup_count = self.tup_dict[cur_tup]

            #actually calculate the probability by dividing the tuple count by Laplace_denominator
            val = (tup_count + 1.0)/(self.tag_dict[first_tag] + self.V_val)

            self.prob_dict[cur_tup] = val

        return self.prob_dict[cur_tup]


# Class that stores a word and tag together
class TaggedWord:
    def __init__(self, taggedString):
        parts = taggedString.split('_');
        self.word = parts[0]
        self.tag = parts[1]

# Class definition for a bigram HMM
class HMM:
### Helper file I/O methods ###
    ################################
    #intput:                       #
    #    inputFile: string         #
    #output: list                  #
    ################################
    # Reads a labeled data inputFile, and returns a nested list of sentences, where each sentence is a list of TaggedWord objects
    def readLabeledData(self, inputFile):
        if os.path.isfile(inputFile):
            file = open(inputFile, "r") # open the input file in read-only mode
            sens = [];
            for line in file:
                raw = line.split()
                sentence = []
                for token in raw:
                    sentence.append(TaggedWord(token))
                sens.append(sentence) # append this list as an element to the list of sentences
            return sens
        else:
            print("Error: unlabeled data file %s does not exist" % inputFile)  # We should really be throwing an exception here, but for simplicity's sake, this will suffice.
            sys.exit() # exit the script

    ################################
    #intput:                       #
    #    inputFile: string         #
    #output: list                  #
    ################################
    # Reads an unlabeled data inputFile, and returns a nested list of sentences, where each sentence is a list of strings
    def readUnlabeledData(self, inputFile):
        if os.path.isfile(inputFile):
            file = open(inputFile, "r") # open the input file in read-only mode
            sens = [];
            for line in file:
                sentence = line.split() # split the line into a list of words
                sens.append(sentence) # append this list as an element to the list of sentences
            return sens
        else:
            print("Error: unlabeled data file %s ddoes not exist" % inputFile)  # We should really be throwing an exception here, but for simplicity's sake, this will suffice.
            sys.exit() # exit the script
### End file I/O methods ###

    ################################
    #intput:                       #
    #    unknownWordThreshold: int #
    #output: None                  #
    ################################
    # Constructor
    def __init__(self, unknownWordThreshold=5):
        # Unknown word threshold, default value is 5 (words occuring fewer than 5 times should be treated as UNK)
        self.minFreq = unknownWordThreshold
        ### Initialize the rest of your data structures here ###

    ################################
    #intput:                       #
    #    trainFile: string         #
    #output: None                  #
    ################################
    # Given labeled corpus in trainFile, build the HMM distributions from the observed counts
    def train(self, trainFile):
        data = self.readLabeledData(trainFile) # data is a nested list of TaggedWords

        #preprocess the data so we get the unkown symbols
        word_arr = []
        tag_arr = []

        word_count_dict = {}
        tag_count_dict = {}

        first_tag_count_dict = {}

        self.unique_tag_arr = []
        tag_set = set()

        for sen in data:
            temp_word_arr = []
            temp_tag_arr = []
            for i in range (len(sen)):

                taggedWord = sen[i]

                word = taggedWord.word
                tag = taggedWord.tag

                if (i==0):
                    if tag in first_tag_count_dict:
                        first_tag_count_dict[tag] += 1.0
                    else:
                        first_tag_count_dict[tag] = 1.0

                if tag not in tag_set:
                    self.unique_tag_arr.append(tag)
                    tag_set.add(tag)

                temp_word_arr.append(word)
                temp_tag_arr.append(tag)

                if word in word_count_dict:
                    word_count_dict[word] += 1
                else:
                    word_count_dict[word] = 1

                if tag in tag_count_dict:
                    tag_count_dict[tag] += 1
                else:
                    tag_count_dict[tag] = 1

            word_arr.append(temp_word_arr)
            tag_arr.append(temp_tag_arr)

        #put words with count less than minFreq into a unknown word array
        Unknown_word_set = set()
        for word,word_count in word_count_dict.items():
            if (word_count<=self.minFreq):
                Unknown_word_set.add(word)

        #mark words seen less than minimum times as UNK
        for sen in word_arr:
            for i in range(len(sen)):
                if (sen[i] in Unknown_word_set):
                    sen[i] = UNK
        #generate a probability of being a tag i for Viterbi P(tag_i)
        self.tag_prob_dict = {}
        for tag, tag_count in first_tag_count_dict.items():
            #find the probability of a starting tag_i existing by taking count(tag_i) as the starting/number sentences
            self.tag_prob_dict[tag] = float(tag_count)/len(sen)

        #generate the bigram model for finding transition probability P(tag_i | tag_i-1)
        self.transition_bigram = BigramModel(tag_arr)


        #generate the emision probabilities P(word_i | tag_i) count(word_i_tag_i)/count(tag_i)
        #generate a dict of tuple to count(tuple)
        self.unique_words = set() # the unique words set holds unique words
        tuple_dict = {}
        for i in range (len(word_arr)):
            for j in range(len(word_arr[i])):
                cur_word = word_arr[i][j]
                cur_tag = tag_arr[i][j]

                self.unique_words.add(cur_word)

                cur_tuple = (cur_word, cur_tag)

                if cur_tuple in tuple_dict:
                    tuple_dict[cur_tuple] += 1.0
                else:
                    tuple_dict[cur_tuple] = 1.0
        self.emission_dict = {}

        for tup,tup_count in tuple_dict.items():
            #divide the tupple count by the count of the current tag
            self.emission_dict[tup] = tup_count/tag_count_dict[tup[1]]




    ################################
    #intput:                       #
    #     testFile: string         #
    #    outFile: string           #
    #output: None                  #
    ################################
    # Given an unlabeled corpus in testFile, output the Viterbi tag sequences as a labeled corpus in outFile
    def test(self, testFile, outFile):
        data = self.readUnlabeledData(testFile)
        f=open(outFile, 'w+')
        for sen in data:
            vitTags = self.viterbi(sen)
            senString = ''
            for i in range(len(sen)):
                senString += sen[i]+"_"+vitTags[i]+" "
            print(senString)
            print(senString.rstrip(), end="\n", file=f)

    ################################
    #intput:                       #
    #    words: list               #
    #output: list                  #
    ################################
    # Given a list of words, runs the Viterbi algorithm and returns a list containing the sequence of tags
    # that generates the word sequence with highest probability, according to this HMM
    def viterbi(self, words):
        #first convert the words to real representation of if they are known or unkown by comparing them to a word set
        parsed_word_arr = []
        for word in words:
            if word in self.unique_words:
                parsed_word_arr.append(word)
            else:
                parsed_word_arr.append(UNK)

        #initialize a trellis object and pass the tag set, words, emission prob and trans prob
        #(self, tags, words, emision_prob, transition_prob, tag_prob):
        trellis = Trellis(self.unique_tag_arr, parsed_word_arr, self.emission_dict, self.transition_bigram, self.tag_prob_dict)

        #get the best track from the trellis
        predicted_tags = trellis.getSentenceTags()
        # returns the list of Viterbi POS tags (strings)
        return trellis.getSentenceTags() # this returns a dummy list of "NULL", equal in length to words

if __name__ == "__main__":
    tagger = HMM()
    tagger.train('train.txt')
    tagger.test('test.txt', 'out.txt')
