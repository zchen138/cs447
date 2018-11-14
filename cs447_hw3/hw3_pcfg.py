import sys
import os
import math

# The start symbol for the grammar
TOP = "TOP"

'''
A grammatical Rule has a probability and a parent category, and is
extended by UnaryRule and BinaryRule
'''


class Rule:

    def __init__(self, probability, parent):
        self.prob = probability
        self.parent = parent

    # Factory method for making unary or binary rules (returns None otherwise)
    @staticmethod
    def createRule(probability, parent, childList):
        if len(childList) == 1:
            return UnaryRule(probability, parent, childList[0])
        elif len(childList) == 2:
            return BinaryRule(probability, parent, childList[0], childList[1])
        return None

    # Returns a tuple containing the rule's children
    def children(self):
        return ()

'''
A UnaryRule has a probability, a parent category, and a child category/word
'''


class UnaryRule(Rule):

    def __init__(self, probability, parent, child):
        Rule.__init__(self, probability, parent)
        self.child = child

    # Returns a singleton (tuple) containing the rule's child
    def children(self):
        return (self.child,)  # note the comma; (self.child) is not a tuple

'''
A BinaryRule has a probability, a parent category, and two children
'''


class BinaryRule(Rule):

    def __init__(self, probability, parent, leftChild, rightChild):
        Rule.__init__(self, probability, parent)
        self.leftChild = leftChild
        self.rightChild = rightChild

    # Returns a pair (tuple) containing the rule's children
    def children(self):
        return (self.leftChild, self.rightChild)

'''
An Item stores the label and Viterbi probability for a node in a parse tree
'''


class Item:

    def __init__(self, label, prob, numParses):
        self.label = label
        self.prob = prob
        self.numParses = numParses

    # Returns the node's label
    def toString(self):
        return self.label

'''
A LeafItem is an Item that represents a leaf (word) in the parse tree (ie, it
doesn't have children, and it has a Viterbi probability of 1.0)
'''


class LeafItem(Item):

    def __init__(self, word):
        # using log probabilities, this is the default value (0.0 = log(1.0))
        Item.__init__(self, word, 0.0, 1)

'''
An InternalNode stores an internal node in a parse tree (ie, it also
stores pointers to the node's child[ren])
'''


class InternalItem(Item):


    def __init__(self, category, prob, children=()):
        Item.__init__(self, category, prob, 0)
        self.children = children
        # Your task is to update the number of parses for this InternalItem
        # to reflect how many possible parses are rooted at this label
        # for the string spanned by this item in a chart
        self.numParses = -1

        if len(self.children) > 2:
            print("Warning: adding a node with more than two children (CKY may not work correctly)")

    # For an internal node, we want to recurse through the labels of the
    # subtree rooted at this node
    def toString(self):
        ret = "( " + self.label + " "
        for child in self.children:
            ret += child.toString() + " "
        return ret + ")"

'''
A Cell stores all of the parse tree nodes that share a common span

Your task is to implement the stubs provided in this class
'''

#the cell class is misleading, DO NOT PUT THE ITME IN HERE UNLESS ITS FINAL
class Cell:

    def __init__(self):
        self.items = {}
        self.parses = {} #dictinoary that maps label to number of parses
        self.label_set = set() #set of all labels that exist
        self.Main_Internal_Item = None

    def addItem(self, item):
        # Add an Item to this cell
        if item.label in self.items:
            if item.prob > self.items[item.label].prob:
                self.items[item.label] = item
        else:
            self.items[item.label] = item


    def getItem(self, label):
        # Return the cell Item with the given label
        return self.items[label]

    def getItems(self):
        # Return the items in this cell
        return self.items

    def numItems(self):
        return len(self.items.keys())

'''
A Chart stores a Cell for every possible (contiguous) span of a sentence

Your task is to implement the stubs provided in this class
'''


class Chart:

    def __init__(self, sentence):
        length = len(sentence)
        self.matrix = [[Cell() for i in range(length+1)] for j in range(length+1)]

    def getRoot(self):
        # Return the item from the top cell in the chart with
        # the label TOP
        pass

    def getCell(self, i, j):
        return self.matrix[i][j]

    def setCell(self, i, j, cell):
        self.matrix[i][j] = cell


'''
A PCFG stores grammatical rules (with probabilities), and can be used to
produce a Viterbi parse for a sentence if one exists
'''


class PCFG:

    def __init__(self, grammarFile, debug=False):
        # in ckyRules, keys are the rule's RHS (the rule's children, stored in
        # a tuple), and values are the parent categories
        self.ckyRules = {}
        self.debug = debug                  # boolean flag for debugging
        # reads the probabilistic rules for this grammar
        self.readGrammar(grammarFile)
        # checks that the grammar at least matches the start symbol defined at
        # the beginning of this file (TOP)
        self.topCheck()

    '''
    Reads the rules for this grammar from an input file
    '''

    def readGrammar(self, grammarFile):
        if os.path.isfile(grammarFile):
            file = open(grammarFile, "r")
            for line in file:
                raw = line.split()
                # reminder, we're using log probabilities
                prob = math.log(float(raw[0]))
                parent = raw[1]
                children = raw[
                    3:]   # Note: here, children is a list; below, rule.children() is a tuple
                rule = Rule.createRule(prob, parent, children)
                if rule.children() not in self.ckyRules:
                    self.ckyRules[rule.children()] = set([])
                self.ckyRules[rule.children()].add(rule)

    '''
    Checks that the grammar at least matches the start symbol (TOP)
    '''

    def topCheck(self):
        for rhs in self.ckyRules:
            for rule in self.ckyRules[rhs]:
                if rule.parent == TOP:
                    return  # TOP generates at least one other symbol
        if self.debug:
            print("Warning: TOP symbol does not generate any children (grammar will always fail)")

    '''
    Your task is to implement this method according to the specification. You may define helper methods as needed.

    Input:        sentence, a list of word strings
    Returns:      The root of the Viterbi parse tree, i.e. an InternalItem with label "TOP" whose probability is the Viterbi probability.
                   By recursing on the children of this node, we should be able to get the complete Viterbi tree.
                   If no such tree exists, return None\
    '''
    '''
    self.items = {}
    self.parses = {} #dictinoary that maps label to number of parses
    self.label_set = set() #set of all labels that exist
    self.Main_Internal_Item = None
    '''
    def CKY(self, sentence):

        sen_length = len(sentence)
        #create the Chart
        chart = Chart(sentence)

        #create the first diagonal
        for j in range(1, sen_length+1):
            cur_cell = chart.getCell(j-1, j)
            cur_word = sentence[j-1]
            cur_rules = self.ckyRules[(cur_word,)]

            for rule in cur_rules:
                cur_item =  InternalItem(rule.parent,rule.prob,(LeafItem(cur_word),))
                cur_item.numParses = 1
                cur_cell.addItem(cur_item)
                cur_cell.parses[rule.parent] = 1
                cur_cell.label_set.add(rule.parent)

            chart.setCell(j-1,j, cur_cell)


        for j in range(1, sen_length+1):
            for i in reversed(range(0,j-1)):
                #the current cell we're checking
                cur_cell = chart.getCell(i, j)

                for k in range(i+1, j):

                    first_check_cell = chart.getCell(i, k)
                    second_check_cell = chart.getCell(k, j)

                    #check the cells are not empty
                    if (first_check_cell.numItems()==0 or second_check_cell.numItems()==0):
                        continue

                    first_cell_items = first_check_cell.getItems()
                    second_cell_items = second_check_cell.getItems()

                    cky_rules = self.ckyRules.keys()

                    for label_1, first_item in first_cell_items.items():
                        for label_2, second_item in second_cell_items.items():
                            rhs = (label_1, label_2)

                            #we found a rule that satisfies the cell
                            if rhs in cky_rules:
                                #check to see if the label alredy exists
                                rules = self.ckyRules[rhs]
                                for rule in rules:
                                    if rule.parent in cur_cell.label_set:
                                        #update the current parse dictionary for this label
                                        cur_cell.parses[rule.parent] += first_check_cell.parses[first_item.label]*second_check_cell.parses[second_item.label]

                                        #create new internalItem
                                        new_prob = rule.prob + first_item.prob + second_item.prob
                                        new_item = InternalItem(rule.parent,new_prob,(first_item, second_item))

                                        cur_cell.addItem(new_item)
                                    #we must create a new internla itme for this rule
                                    else:
                                        #add to the cell's item label set
                                        cur_cell.label_set.add(rule.parent)
                                        #initalize the parse number for this label
                                        cur_cell.parses[rule.parent] = first_check_cell.parses[first_item.label]*second_check_cell.parses[second_item.label]

                                        #create the new internal item to insert
                                        new_prob = rule.prob + first_item.prob + second_item.prob
                                        new_item = InternalItem(rule.parent,new_prob,(first_item, second_item))
                                        cur_cell.addItem(new_item)

                #try to make the mainItem exist if possible

                if (len(cur_cell.label_set)>0):
                    best_prob = float('-inf')
                    best_item = None
                    for key,val in cur_cell.getItems().items():
                        if val.prob > best_prob:
                            best_item = val

                    cur_cell.Main_Internal_Item = best_item

                chart.setCell(i, j, cur_cell)


                #end for

        last_cell = chart.getCell(0, sen_length)
        main_item = last_cell.Main_Internal_Item

        if main_item != None:
            main_item.numParses = last_cell.parses['S']
            return_item = InternalItem('TOP', main_item.prob,(main_item,))
            return_item.numParses = last_cell.parses['S']

            return return_item

        return None

if __name__ == "__main__":
    pcfg = PCFG('toygrammar.pcfg')
    sen = "the woman eats the tuna with a fork and some sushi with the chopsticks".split()

    tree = pcfg.CKY(sen)
    if tree is not None:
        print(tree.toString())
        print("Probability: " + str(math.exp(tree.prob)))
        print("Num parses: " + str(tree.numParses))
    else:
        print("Parse failure!")
