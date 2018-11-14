########################################
## CS447 Natural Language Processing  ##
##           Homework 1               ##
##       Julia Hockenmaier            ##
##       juliahmr@illnois.edu         ##
########################################
##
## Part 1:
## Develop a smoothed n-gram language model and evaluate it on a corpus
##
import os.path
import sys
import random
from operator import itemgetter
from collections import defaultdict
import math
#----------------------------------------
#  Data input
#----------------------------------------

# Read a text file into a corpus (list of sentences (which in turn are lists of words))
# (taken from nested section of HW0)
def readFileToCorpus(f):
    """ Reads in the text file f which contains one sentence per line.
    """
    if os.path.isfile(f):
        file = open(f, "r") # open the input file in read-only mode
        i = 0 # this is just a counter to keep track of the sentence numbers
        corpus = [] # this will become a list of sentences
        print("Reading file ", f)
        for line in file:
            i += 1
            sentence = line.split() # split the line into a list of words
            #append this lis as an element to the list of sentences
            corpus.append(sentence)
            if i % 1000 == 0:
    	#print a status message: str(i) turns int i into a string
    	#so we can concatenate it
                sys.stderr.write("Reading sentence " + str(i) + "\n")
        #endif
    #endfor
        return corpus
    else:
    #ideally we would throw an exception here, but this will suffice
        print("Error: corpus file ", f, " does not exist")
        sys.exit() # exit the script
    #endif
#enddef


# Preprocess the corpus to help avoid sess the corpus to help avoid sparsity
def preprocess(corpus):
    #find all the rare words
    freqDict = defaultdict(int)
    for sen in corpus:
	    for word in sen:
	       freqDict[word] += 1
	#endfor
    #endfor

    #replace rare words with unk
    for sen in corpus:
        for i in range(0, len(sen)):
            word = sen[i]
            if freqDict[word] < 2:
                sen[i] = UNK
	    #endif
	#endfor
    #endfor

    #bookend the sentences with start and end tokens
    for sen in corpus:
        sen.insert(0, start)
        sen.append(end)
    #endfor

    return corpus
#enddef

#Should generate a vocab that exist within the corpus
def preprocessTest(vocab, corpus):
    #replace test words that were unseen in the training with unk
    for sen in corpus:
        for i in range(0, len(sen)):
            word = sen[i]
            if word not in vocab:
                sen[i] = UNK
	    #endif
	#endfor
    #endfor

    #bookend the sentences with start and end tokens
    for sen in corpus:
        sen.insert(0, start)
        sen.append(end)
    #endfor

    return corpus
#enddef

# Constants
UNK = "UNK"     # Unknown word token
start = "<s>"   # Start-of-sentence token
end = "</s>"    # End-of-sentence-token


#--------------------------------------------------------------
# Language models and data structures
#--------------------------------------------------------------

# Parent class for the three language models you need to implement
class LanguageModel:
    # Initialize and train the model (ie, estimate the model's underlying probability
    # distribution from the training corpus)
    def __init__(self, corpus):
        print("""Your task is to implement five kinds of n-gram language models:
      a) an (unsmoothed) unigram model (UnigramModel)
      b) a unigram model smoothed using Laplace smoothing (SmoothedUnigramModel)
      c) an unsmoothed bigram model (BigramModel)
      d) a bigram model smoothed using absolute discounting (SmoothedBigramModelAD)
      e) a bigram model smoothed using kneser-ney smoothing (SmoothedBigramModelKN)
      """)
    #enddef

    # Generate a sentence by drawing words according to the
    # model's probability distribution
    # Note: think about how to set the length of the sentence
    #in a principled way
    def generateSentence(self):

        return "mary had a little lamb ."
    #emddef

    # Given a sentence (sen), return the probability of
    # that sentence under the model
    def getSentenceProbability(self, sen):

        return 0.0
    #enddef

    # Given a corpus, calculate and return its perplexity
    #(normalized inverse log probability)
    def getCorpusPerplexity(self, corpus):

        return 0.0
    #enddef

    # Given a file (filename) and the number of sentences, generate a list
    # of sentences and write each to file along with its model probability.
    # Note: you shouldn't need to change this method
    def generateSentencesToFile(self, numberOfSentences, filename):
        filePointer = open(filename, 'w+')
        for i in range(0,numberOfSentences):
            sen = self.generateSentence()
            prob = self.getSentenceProbability(sen)

            stringGenerated = str(prob) + " " + " ".join(sen)
            print(stringGenerated, end="\n", file=filePointer)

	#endfor
    #enddef
#endclass

# Unigram language model
class UnigramModel(LanguageModel):
    def __init__(self, corpus):
        self.prob_dict = {}
        self.count_dict = {}
        self.corpus_length = 0.0
        self.train(corpus)
    #endddef

    # Add observed counts from corpus to the distribution
    def train(self, corpus):
        longest_corpus_sentence_length = 0

        for sen in corpus:
            sen_len = len(sen)
            if (sen_len>longest_corpus_sentence_length):
                longest_corpus_sentence_length = sen_len
            for word in sen:
                if word == start:
                    continue
                if word not in self.count_dict:
                    self.count_dict[word] = 1.0
                else:
                    self.count_dict[word] += 1.0
                self.corpus_length += 1.0

        test_tot = 0.0
        for key, value in self.count_dict.items():
            self.prob_dict[key] = value/self.corpus_length
            test_tot += self.prob_dict[key]

            #endfor
        #endfor
        self.max_sentence_length = 2*longest_corpus_sentence_length
    #enddef

    def generateSentence(self):

        sentence = ["<s>"]
        curLength = 0
        while (curLength<self.max_sentence_length):

            word = self.draw()
            sentence.append(word)
            if word == end:
                return sentence
            curLength = curLength + 1

        sentence.append("</s>")

        return sentence
    #emddef

    # Given a sentence (sen), return the probability of
    # that sentence under the model
    def getSentenceProbability(self, sen):

        cur_log_value = 0.0

        for word in sen:
            if word != start:
                cur_log_value += math.log(self.prob(word))

        return (math.exp(cur_log_value))
    #enddef

    def getCorpusPerplexity(self, corpus):
        length = 0.0
        total = 0.0
        for sen in corpus:
            for word in sen:
                if word == start:
                    continue
                else:
                    length += 1.0
                    total += math.log(self.prob(word))

        total = total * (-1.0)
        total = total/length
        total = math.exp(total)

        return total

    #return probiblity of a word
    def prob(self, word):
        return self.prob_dict[word]

    # Generate a single random word according to the distribution
    def draw(self):

        returnWord = ""
        rand = random.random()
        for word in self.count_dict.keys():
            rand -= self.prob(word)

            if rand <= 0.0:
                return word
            returnWord = word

        return returnWord
    #endddef
#endclass

#Smoothed unigram language model (use laplace for smoothing)
class SmoothedUnigramModel(LanguageModel):
    def __init__(self, corpus):
        self.prob_dict = {}
        self.count_dict = {}
        self.corpus_length = 0.0
        self.train(corpus)
    #endddef

    def train(self, corpus):
        longest_corpus_sentence_length = 0

        word_types = set()

        for sen in corpus:
            sen_len = len(sen)
            if (sen_len>longest_corpus_sentence_length):
                longest_corpus_sentence_length = sen_len
            for word in sen:
                if word == start:
                    continue

                word_types.add(word)

                if word not in self.count_dict:
                    self.count_dict[word] = 1.0
                else:
                    self.count_dict[word] += 1.0
                self.corpus_length += 1.0

        test_tot = 0.0
        for key, value in self.count_dict.items():
            self.prob_dict[key] = (value+1.0)/(self.corpus_length + len(word_types))

            test_tot += self.prob_dict[key]

            #endfor
        #endfor
        self.max_sentence_length = 2*longest_corpus_sentence_length

    #enddef
    def generateSentence(self):

        sentence = ["<s>"]
        curLength = 0
        while (curLength<self.max_sentence_length):

            word = self.draw()
            sentence.append(word)
            if word == end:
                return sentence
            curLength = curLength + 1
        sentence.append("</s>")

        return sentence
    #emddef

    # Given a sentence (sen), return the probability of
    # that sentence under the model
    def getSentenceProbability(self, sen):

        cur_log_value = 0.0

        for word in sen:
            if word != start:
                cur_log_value += math.log(self.prob(word))

        return (math.exp(cur_log_value))
    #enddef

    def getCorpusPerplexity(self, corpus):
        total = 0.0
        length = 0.0
        for sen in corpus:
            for word in sen:
                if word == start:
                    continue
                else:
                    total += math.log(self.prob(word))
                    length += 1.0

        total = total * (-1.0)
        total = total/length

        total = math.exp(total)
        return total

    #return probiblity of a word
    def prob(self, word):
        return self.prob_dict[word]

    # Generate a single random word according to the distribution
    def draw(self):

        returnWord = ""
        rand = random.random()
        for word in self.count_dict.keys():
            rand -= self.prob(word)

            if rand <= 0.0:
                return word
            returnWord = word


        return returnWord
    #endddef

#endclass

# Unsmoothed bigram language model
class BigramModel(LanguageModel):
    def __init__(self, corpus):
        self.prob_dict = {}
        self.count_dict = {}
        self.tup_dict = {}
        self.first_to_second_word_dict = {}
        self.corpus_length = 0.0
        self.train(corpus)
    #endddef
    def train(self, corpus):
        longest_corpus_sentence_length = 0

        for sen in corpus:
            sen_len = len(sen)
            if (sen_len>longest_corpus_sentence_length):
                longest_corpus_sentence_length = sen_len
            for i in range (sen_len):
                word = sen[i]

                if word not in self.count_dict:
                    self.count_dict[word] = 1.0
                else:
                    self.count_dict[word] += 1.0
                self.corpus_length += 1.0

                if i != sen_len-1:
                    next_word = sen[i+1]
                    cur_tup = (word, next_word)

                    if cur_tup not in self.tup_dict:
                        self.tup_dict[cur_tup] = 1.0
                    else:
                        self.tup_dict[cur_tup] += 1.0

                    #start our first to second word map
                    if word not in self.first_to_second_word_dict:
                        self.first_to_second_word_dict[word] = [next_word]
                    else:
                        arr = self.first_to_second_word_dict[word]
                        if next_word not in arr:
                            arr.append(next_word)
                            self.first_to_second_word_dict[word] = arr

        test_tot = 0.0
        for key, value in self.tup_dict.items():
            self.prob_dict[key] = value/self.count_dict[key[0]]


            test_tot += self.prob_dict[key]


            #endfor
        #endfor
        self.max_sentence_length = 2*longest_corpus_sentence_length
    #enddef

    #return probiblity of a word
    def prob(self, first_word, second_word):
        return self.prob_dict[(first_word, second_word)]
    #endddef

    # Given a sentence (sen), return the probability of
    # that sentence under the model
    def getSentenceProbability(self, sen):

        cur_log_value = 0.0

        for i in range (len(sen)-1):
            cur_word = sen[i]
            next_word = sen[i+1]

            cur_tup = (cur_word, next_word)
            if (cur_tup not in self.tup_dict):
                return 0.0
            else:
                cur_log_value += math.log(self.prob(cur_word, next_word))

        return (math.exp(cur_log_value))
    #enddef

#endclass

# Smoothed bigram language model (use absolute discounting for smoothing)
class SmoothedBigramModelAD(LanguageModel):
    def __init__(self, corpus):
        self.prob_dict = {}
        self.count_dict = {}
        self.tup_dict = {}
        self.first_to_second_word_dict = {}
        self.s_function_dict = {}
        self.laplace_dict = {}
        self.corpus_length = 0.0
        self.unigram = SmoothedUnigramModel(corpus)
        self.train(corpus)
    #endddef
    def train(self, corpus):
        longest_corpus_sentence_length = 0

        for sen in corpus:
            sen_len = len(sen)
            if (sen_len>longest_corpus_sentence_length):
                longest_corpus_sentence_length = sen_len
            for i in range (sen_len):
                word = sen[i]

                #update the type of words, for laplace
                if word != start:

                    self.corpus_length += 1.0

                if word not in self.count_dict:
                    self.count_dict[word] = 1.0
                else:
                    self.count_dict[word] += 1.0
                self.corpus_length += 1.0

                if i != sen_len-1:
                    next_word = sen[i+1]
                    cur_tup = (word, next_word)

                    if cur_tup not in self.tup_dict:
                        self.tup_dict[cur_tup] = 1.0
                    else:
                        self.tup_dict[cur_tup] += 1.0

                    #start our first to second word map
                    if word not in self.first_to_second_word_dict:
                        self.first_to_second_word_dict[word] = [next_word]
                    else:
                        arr = self.first_to_second_word_dict[word]
                        if next_word not in arr:
                            arr.append(next_word)
                            self.first_to_second_word_dict[word] = arr

            #endfor

        #compute D val
        N_1 = 0.0
        N_2 = 0.0
        for key, val in self.tup_dict.items():
            if (val == 1):
                N_1 += 1.0
            if (val == 2):
                N_2 += 1.0
        self.D_val = N_1/(N_1 + (2*N_2))

        self.max_sentence_length = 2*longest_corpus_sentence_length


    #enddef

    def prob(self, first_word, second_word):

        cur_tup = (first_word, second_word)

        if cur_tup in self.prob_dict:

            return self.prob_dict[cur_tup]
        else:
            #get laplace second word is used here
            laplace_val = 0.0
            if second_word in self.laplace_dict:
                laplace_val = self.laplace_dict[second_word]
            else:
                laplace_val = self.unigram.prob(second_word)#(self.count_dict[second_word] + 1.0)/(self.corpus_length + self.num_word_types)
                self.laplace_dict[second_word] = laplace_val


            #get s_function first word is used here
            s_function_val = 0.0
            if first_word in self.first_to_second_word_dict:
                s_function_val = len(self.first_to_second_word_dict[first_word])
            #compute D/c(w) first word is used here
            D_divide_count = self.D_val/self.count_dict[first_word]
            #compute max()/c(w)
            tup_count = 0.0
            if (cur_tup in self.tup_dict):
                tup_count = self.tup_dict[cur_tup]
            tot = max((tup_count - self.D_val), 0.0)/self.count_dict[first_word]


            #compute rest of function
            tot = tot + (D_divide_count * s_function_val * laplace_val)

            self.prob_dict[cur_tup] = tot

        return tot

    def generateSentence(self):

        sentence = ["<s>"]
        curLength = 0
        while (curLength<self.max_sentence_length):
            word = self.draw(sentence[len(sentence)-1])
            sentence.append(word)
            if word == end:
                return sentence
            curLength = curLength + 1

        sentence.append("</s>")
        return sentence

    def draw(self, first_word):

        possible_second_words = self.first_to_second_word_dict[first_word]
        temp_dict = {}
        for second_word in possible_second_words:
            temp_dict[second_word] = self.prob(first_word, second_word)

        returnWord = ""
        rand = random.random()
        for second_word in temp_dict.keys():
            rand -= temp_dict[second_word]

            if rand <= 0.0:
                return second_word
            returnWord = second_word

        return returnWord

    def getSentenceProbability(self, sen):

        cur_log_value = 0.0

        for i in range (len(sen)-1):
            cur_word = sen[i]
            next_word = sen[i+1]

            cur_tup = (cur_word, next_word)


            cur_log_value += math.log(self.prob(cur_word, next_word))

        return (math.exp(cur_log_value))

    def getCorpusPerplexity(self, corpus):
        total = 0.0
        length = 0.0

        for sen in corpus:
            length += len(sen)-1
            for i in range (len(sen)-1):
                cur_word = sen[i]
                next_word = sen[i+1]

                cur_tup = (cur_word, next_word)


                total += math.log(self.prob(cur_word, next_word))



        total = total * (-1.0)
        total = total/length
        total = math.exp(total)

        return total


#endclass

# Smoothed bigram language model (use absolute discounting and kneser-ney for smoothing)
class SmoothedBigramModelKN(LanguageModel):
    def __init__(self, corpus):
        self.prob_dict = {}
        self.count_dict = {}
        self.tup_dict = {}
        self.first_to_second_word_dict = {}
        self.second_to_first_word_dict = {}
        self.s_function_dict = {}
        self.kn_dict = {}
        self.train(corpus)
    #endddef

    def train(self, corpus):
        longest_corpus_sentence_length = 0

        for sen in corpus:
            sen_len = len(sen)
            if (sen_len > longest_corpus_sentence_length):
                longest_corpus_sentence_length = sen_len
            for i in range(sen_len):
                word = sen[i]

                # update the type of words, for laplace

                if word not in self.count_dict:
                    self.count_dict[word] = 1.0
                else:
                    self.count_dict[word] += 1.0

                if i != sen_len - 1:
                    next_word = sen[i + 1]
                    cur_tup = (word, next_word)

                    if cur_tup not in self.tup_dict:
                        self.tup_dict[cur_tup] = 1.0
                    else:
                        self.tup_dict[cur_tup] += 1.0

                    # start our first to second word map
                    if word not in self.first_to_second_word_dict:
                        self.first_to_second_word_dict[word] = [next_word]
                    else:
                        arr = self.first_to_second_word_dict[word]
                        if next_word not in arr:
                            arr.append(next_word)
                            self.first_to_second_word_dict[word] = arr

                    #start our second to first word map
                    if next_word not in self.second_to_first_word_dict:
                        self.second_to_first_word_dict[next_word] = [word]
                    else:
                        arr = self.second_to_first_word_dict[next_word]
                        if word not in arr:
                            arr.append(word)
                            self.second_to_first_word_dict[next_word] = arr

            # endfor

        # compute D val
        N_1 = 0.0
        N_2 = 0.0
        for key, val in self.tup_dict.items():
            if (val == 1):
                N_1 += 1.0
            if (val == 2):
                N_2 += 1.0
        self.D_val = N_1 / (N_1 + (2 * N_2))

        self.max_sentence_length = 2 * longest_corpus_sentence_length

    def prob(self, first_word, second_word):

        cur_tup = (first_word, second_word)

        if cur_tup in self.prob_dict:

            return self.prob_dict[cur_tup]
        else:
            #get KN value second word
            kn_val = 0.0
            if second_word in self.kn_dict:
                kn_val = self.kn_dict[second_word]
            else:
                kn_val = len(self.second_to_first_word_dict[second_word])
                kn_val = kn_val/len(self.tup_dict)
                self.kn_dict[second_word] = kn_val


            #get s_function first word is used here
            s_function_val = 0.0
            if first_word in self.first_to_second_word_dict:
                s_function_val = len(self.first_to_second_word_dict[first_word])
            #compute D/c(w) first word is used here
            D_divide_count = self.D_val/self.count_dict[first_word]
            #compute max()/c(w)
            tup_count = 0.0
            if (cur_tup in self.tup_dict):
                tup_count = self.tup_dict[cur_tup]
            tot = max((tup_count - self.D_val), 0.0)/self.count_dict[first_word]


            #compute rest of function
            tot = tot + (D_divide_count * s_function_val * kn_val)

            self.prob_dict[cur_tup] = tot

        return tot


    def generateSentence(self):

        sentence = ["<s>"]
        curLength = 0
        while (curLength<self.max_sentence_length):
            word = self.draw(sentence[len(sentence)-1])
            sentence.append(word)
            if word == end:
                return sentence
            curLength = curLength + 1

        sentence.append("</s>")
        return sentence

    def draw(self, first_word):

        possible_second_words = self.first_to_second_word_dict[first_word]
        temp_dict = {}
        for second_word in possible_second_words:
            temp_dict[second_word] = self.prob(first_word, second_word)

        check = 0.0
        for key, val in temp_dict.items():
            check += val

        returnWord = ""
        rand = random.random()
        for second_word in temp_dict.keys():
            rand -= temp_dict[second_word]

            if rand <= 0.0:
                return second_word
            returnWord = second_word

        return returnWord

    def getSentenceProbability(self, sen):

        cur_log_value = 0.0

        for i in range (len(sen)-1):
            cur_word = sen[i]
            next_word = sen[i+1]

            cur_tup = (cur_word, next_word)


            cur_log_value += math.log(self.prob(cur_word, next_word))

        return (math.exp(cur_log_value))

    def getCorpusPerplexity(self, corpus):
        total = 0.0
        length = 0.0

        for sen in corpus:
            length += len(sen)-1
            for i in range (len(sen)-1):
                cur_word = sen[i]
                next_word = sen[i+1]

                cur_tup = (cur_word, next_word)


                total += math.log(self.prob(cur_word, next_word))



        total = total * (-1.0)
        total = total/length
        total = math.exp(total)

        return total
#endclass



# Sample class for a unsmoothed unigram probability distribution
# Note:
#       Feel free to use/re-use/modify this class as necessary for your
#       own code (e.g. converting to log probabilities after training).
#       This class is intended to help you get started
#       with your implementation of the language models above.
class UnigramDist:
    def __init__(self, corpus):
        self.counts = defaultdict(float)
        self.total = 0.0
        self.train(corpus)
    #endddef

    # Add observed counts from corpus to the distribution
    def train(self, corpus):
        for sen in corpus:
            for word in sen:
                if word == start:
                    continue
                self.counts[word] += 1.0
                self.total += 1.0
            #endfor
        #endfor
    #enddef

    # Returns the probability of word in the distribution
    def prob(self, word):
        return self.counts[word]/self.total
    #enddef

    # Generate a single random word according to the distribution
    def draw(self):
        rand = random.random()
        for word in self.counts.keys():
            rand -= self.prob(word)
            if rand <= 0.0:
                return word
	    #endif
	#endfor
    #enddef
#endclass

#-------------------------------------------
# The main routine
#-------------------------------------------
if __name__ == "__main__":
    #read your corpora
    #zeorth cat need to change this to train
    trainCorpus = readFileToCorpus('train.txt')
    trainCorpus = preprocess(trainCorpus)

    posTestCorpus = readFileToCorpus('pos_test.txt')
    negTestCorpus = readFileToCorpus('neg_test.txt')

    vocab = set()
    # Please write the code to create the vocab over here before the function preprocessTest

    for sentence in trainCorpus:
        for word in sentence:
            vocab.add(word)


    posTestCorpus = preprocessTest(vocab, posTestCorpus)
    negTestCorpus = preprocessTest(vocab, negTestCorpus)

    # Run sample unigram dist code
    unigramMod = UnigramModel(trainCorpus)
    smoothUnigram = SmoothedUnigramModel(trainCorpus)
    #bigramMod = BigramModel(trainCorpus)
    AdBigram = SmoothedBigramModelAD(trainCorpus)
    KnBigram = SmoothedBigramModelKN(trainCorpus)


    print("this is AD bigram")
    print("this is positive test corpus " + str(AdBigram.getCorpusPerplexity(posTestCorpus)))
    print("this isthe negative test corpus " + str(AdBigram.getCorpusPerplexity(negTestCorpus)))
    print("this is KN bigram")
    print("this is positive test corpus " + str(KnBigram.getCorpusPerplexity(posTestCorpus)))
    print("this isthe negative test corpus " + str(KnBigram.getCorpusPerplexity(negTestCorpus)))
