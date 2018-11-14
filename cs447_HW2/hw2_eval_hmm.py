########################################
## CS447 Natural Language Processing  ##
##           Homework 2               ##
##       Julia Hockenmaier            ##
##       juliahmr@illnois.edu         ##
########################################
##
## Part 1:
## Evaluate the output of your bigram HMM POS tagger
##
import os.path
import sys
from operator import itemgetter

from hw2_hmm import HMM
import numpy as np

class TaggedWord:
    def __init__(self, taggedString):
        parts = taggedString.split('_');
        self.word = parts[0]
        self.tag = parts[1]

def readLabeledData(inputFile):
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


def getValueIndexes(digit, realValArr):
    index = 0
    indexArr = []
    for val in realValArr:
        if (val==digit):
            indexArr.append(index)
        index = index+1

    return indexArr

def getConfusionVal(j, real_index_arr, predictedValArr):
    numClassified = 0
    for index in  real_index_arr:
        if (predictedValArr[index]==j):
            numClassified = numClassified + 1
    #print(numClassified/len(real_index_arr))
    return numClassified

def confusionMatrixGeneration(tag_set, realValArr, predictedValArr):

    tag_len = len(tag_set)

    realVal_to_indexArr_dict = {}
    for i in range (len(tag_set)):
        realVal_to_indexArr_dict[tag_set[i]] = getValueIndexes(tag_set[i], realValArr)

    confusionArr = np.zeros((tag_len,tag_len), dtype=int)
    for i in range (tag_len):
        for j in range (tag_len):
            confusionArr[i][j] = getConfusionVal(tag_set[j], realVal_to_indexArr_dict[tag_set[i]], predictedValArr)

    return confusionArr

def areTaggedWordEquals(word_1, word_2):
    return (word_1.word==word_2.word and word_1.tag==word_2.tag)

# A class for evaluating POS-tagged data
class Eval:
    ################################
    #intput:                       #
    #    goldFile: string          #
    #    testFile: string          #
    #output: None                  #
    ################################
    def __init__(self, goldFile, testFile):
        print("Your task is to implement an evaluation program for POS tagging")
        self.gold_corpus = readLabeledData("gold.txt")
        self.test_corpus = readLabeledData("out.txt")
    ################################
    #intput: None                  #
    #output: float                 #
    ################################
    def getTokenAccuracy(self):

        total_words = 0.0
        total_correct = 0.0

        test_corpus = self.test_corpus
        gold_corpus = self.gold_corpus

        if (len(test_corpus)!=len(gold_corpus)):
            print("uh we've got a problem with the two corpus not being same. man fuck my life")

        for sen_index in range (len(test_corpus)):
            sen = test_corpus[sen_index]

            total_words += len(sen)

            for word_index in range(len(sen)):
                taggedWord_test = test_corpus[sen_index][word_index]
                taggedWord_gold = gold_corpus[sen_index][word_index]

                if (areTaggedWordEquals(taggedWord_gold, taggedWord_test)):
                    total_correct += 1.0

        return (total_correct/total_words)

    ################################
    #intput: None                  #
    #output: float                 #
    ################################
    def getSentenceAccuracy(self):
        test_corpus = self.test_corpus
        gold_corpus = self.gold_corpus

        total_sentences = len(test_corpus)

        total_correct = 0.0

        for sen_index in range (len(test_corpus)):
            test_sen = test_corpus[sen_index]
            gold_sen = gold_corpus[sen_index]
            flag = True
            for i in range (len(test_sen)):
                if (areTaggedWordEquals(test_sen[i], gold_sen[i])==False):
                    flag = False
                    break

            if (flag):
                total_correct += 1.0

        return total_correct/total_sentences


    ################################
    #intput:                       #
    #    outFile: string           #
    #output: None                  #
    ################################
    def writeConfusionMatrix(self, outFile):

        test_corpus = self.test_corpus
        gold_corpus = self.gold_corpus

        tag_set_arr = []
        tag_set = set()

        predicted_tags = []
        real_tags = []

        for sen_index in range (len(test_corpus)):
            sen = test_corpus[sen_index]

            temp_real_tags = []
            temp_predicted_tags = []

            for word_index in range(len(sen)):
                taggedWord_test = test_corpus[sen_index][word_index]
                taggedWord_gold = gold_corpus[sen_index][word_index]

                predicted_tag = taggedWord_test.tag
                real_tag = taggedWord_gold.tag

                if predicted_tag not in tag_set:
                    tag_set_arr.append(predicted_tag)
                    tag_set.add(predicted_tag)

                temp_predicted_tags.append(predicted_tag)
                temp_real_tags.append(real_tag)

            predicted_tags.extend(temp_predicted_tags)
            real_tags.extend(temp_real_tags)


        confusion_matrix = confusionMatrixGeneration(tag_set_arr, real_tags, predicted_tags)

        first_row = ['    ']
        for elem in tag_set_arr:
            first_row.append(elem)

        f = open(outFile, "w")
        f.write('   '.join(first_row) + '\n')
        for i in range(len(tag_set_arr)):
            line = confusion_matrix[i].astype(str)
            cur_row = [tag_set_arr[i]]
            cur_row.extend(line)
            f.write('   '.join(cur_row) + '\n')
        f.close()

    ################################
    #intput:                       #
    #    tagTi: string             #
    #output: float                 #
    ################################
    def getPrecision(self, tagTi):
        test_corpus = self.test_corpus
        gold_corpus = self.gold_corpus

        truePos = 0.0
        falsePos = 0.0

        for sen_index in range (len(test_corpus)):
            sen = test_corpus[sen_index]

            for word_index in range(len(sen)):
                taggedWord_test = test_corpus[sen_index][word_index]
                taggedWord_gold = gold_corpus[sen_index][word_index]

                predicted_tag = taggedWord_test.tag
                real_tag = taggedWord_gold.tag

                if predicted_tag==tagTi:
                    if real_tag==tagTi:
                        truePos += 1.0
                    else:
                        falsePos += 1.0
        return truePos/(truePos+falsePos)

    ################################
    #intput:                       #
    #    tagTi: string             #
    #output: float                 #
    ################################
    # Return the tagger's recall on gold tag t_j
    def getRecall(self, tagTj):
        test_corpus = self.test_corpus
        gold_corpus = self.gold_corpus

        truePos = 0.0
        falseNeg = 0.0

        for sen_index in range (len(test_corpus)):
            sen = test_corpus[sen_index]

            for word_index in range(len(sen)):
                taggedWord_test = test_corpus[sen_index][word_index]
                taggedWord_gold = gold_corpus[sen_index][word_index]

                predicted_tag = taggedWord_test.tag
                real_tag = taggedWord_gold.tag

                if real_tag==tagTj:
                    if predicted_tag==tagTj :
                        truePos += 1.0
                    else:
                        falseNeg += 1.0
        return truePos/(truePos+falseNeg)


if __name__ == "__main__":
    # Pass in the gold and test POS-tagged data as arguments
    if len(sys.argv) < 2:
        print("Call hw2_eval_hmm.py with two arguments: gold.txt and out.txt")
    else:
        gold = sys.argv[1]
        test = sys.argv[2]
        # You need to implement the evaluation class
        eval = Eval(gold, test)
        # Calculate accuracy (sentence and token level)
        print("Token accuracy: ", eval.getTokenAccuracy())
        print("Sentence accuracy: ", eval.getSentenceAccuracy())
        # Calculate recall and precision
        print("Recall on tag NNP: ", eval.getRecall('NNP'))
        print("Precision for tag NNP: ", eval.getPrecision('NNP'))
        # Write a confusion matrix
        eval.writeConfusionMatrix("conf_matrix.txt")
