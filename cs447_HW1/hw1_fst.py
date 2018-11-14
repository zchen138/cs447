from fst import *

# here are some predefined character sets that might come in handy.
# you can define your own
AZ = set("abcdefghijklmnopqrstuvwxyz")
VOWS = set("aeiou")
CONS = set("bcdfghjklmnprstvwxz")
PT = set("pt")
EU = set("eu")
U = set("u")
E = set("e")
AIO = set("aio")
IE = set("ie")
NPTR = set("nptr")
NPTRE = set("nptre")
AIOU = set("aiou")
NPTRE = set("nptre")

NPTRVOW = set("nptraeiou")

# Implement your solution here
def buildFST():
    #
    # The states (you need to add more)
    # ---------------------------------------
    # 
    f = FST("q0")  # q0 is the initial (non-accepting) state
    f.addState("q1")  # first rule
    f.addState("q2")  # second rule
    f.addState("q3")  # third rule

    #here we add the states for the first rule
    f.addState("q4")
    f.addState("q5")
    f.addState("q6")
    f.addState("q7")

    #here we are adding the states for the second rule
    f.addState("q8")
    f.addState("q9")
    f.addState("q10")
    f.addState("q11")
    f.addState("q12")
    f.addState("q13")
    f.addState("q14")
    f.addState("q15")
    f.addState("q16")
    f.addState("q17")
    f.addState("q18")
    f.addState("q19")

    #here we are adding the states for the third rule
    f.addState("q20")
    f.addState("q21")

    f.addState("q_EOW", True)  # an accepting state (you shouldn't need any additional accepting states)

    #
    # The transitions (you need to add more):
    # ---------------------------------------
    # transduce every element in this set to itself:
    f.addEpsilonTransition("q0", "q1")

    # get rid of this transition! (it overgenerates):
    f.addSetTransition("q1", VOWS - U, "q1")
    f.addSetTransition("q1", CONS | U, "q4")

    f.addSetTransition("q4", CONS | U, "q4")
    f.addSetTransition("q4", AIO, "q1")
    f.addTransition("q4", "e", "", "q5")
    f.addTransition("q4", "e", "e", "q6")

    f.addTransition("q5", "", "ing", "q_EOW")
    f.addTransition("q5", "e", "ee", "q7")

    f.addSetTransition("q6", CONS | U, "q4")
    f.addSetTransition("q6", VOWS - U, "q1")

    f.addTransition("q7", "", "ing", "q_EOW")

    #second rule
    f.addEpsilonTransition("q0", "q2")
    f.addSetTransition("q2", AZ - VOWS, "q2")
    f.addSetTransition("q2", AIOU, "q8")
    f.addSetTransition("q2", E, "q9")
    f.addTransition("q2", "", "ing", "q_EOW")

    f.addSetTransition("q8", AZ - NPTRE, "q2")
    f.addSetTransition("q8", NPTR, "q10")
    f.addSetTransition("q8", E, "q19")
    f.addTransition("q8", "n", "", "q11")
    f.addTransition("q8", "p", "", "q12")
    f.addTransition("q8", "t", "", "q13")
    f.addTransition("q8", "r", "", "q14")

    f.addSetTransition("q9", AZ - NPTRE, "q2")
    f.addSetTransition("q9", NPTR, "q10")
    f.addSetTransition("q9", E, "q19")
    f.addTransition("q9", "n", "", "q15")
    f.addTransition("q9", "r", "", "q16")
    f.addTransition("q9", "t", "", "q17")
    f.addTransition("q9", "p", "", "q18")

    f.addSetTransition("q10", AZ - VOWS, "q2")
    f.addSetTransition("q10", E, "q9")
    f.addSetTransition("q10", AIOU, "q8")

    f.addTransition("q11", "", "nning", "q_EOW")
    f.addTransition("q12", "", "pping", "q_EOW")
    f.addTransition("q13", "", "tting", "q_EOW")
    f.addTransition("q14", "", "rring", "q_EOW")

    f.addTransition("q15", "", "ning", "q_EOW")
    f.addTransition("q16", "", "ring", "q_EOW")
    f.addTransition("q17", "", "tting", "q_EOW")
    f.addTransition("q18", "", "pping", "q_EOW")

    f.addSetTransition("q19", AZ - VOWS, "q2")
    f.addSetTransition("q19", AIOU, "q8")
    f.addSetTransition("q19", E, "q9")

    #third rule
    f.addEpsilonTransition("q0", "q3")
    f.addSetTransition("q3", AZ - IE, "q3")
    f.addTransition("q3", "i", "", "q20")
    f.addTransition("q20", "e", "", "q21")
    f.addTransition("q21", "", "ying", "q_EOW")



    # Return your completed FST
    return f
    

if __name__ == "__main__":
    # Pass in the input file as an argument
    if len(sys.argv) < 2:
        print("This script must be given the name of a file containing verbs as an argument")
        quit()
    else:
        file = sys.argv[1]
    #endif

    # Construct an FST for translating verb forms 
    # (Currently constructs a rudimentary, buggy FST; your task is to implement a better one.
    f = buildFST()
    # Print out the FST translations of the input file
    f.parseInputFile(file)
