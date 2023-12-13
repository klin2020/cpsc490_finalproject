from colorama import Fore
import sys 
import unidecode
import string
import os

#take one llm + gt file and print out llm file with errors based on gt file
#specify which type of comparator you want to see

def basic(gt_file, tk_file, file_name):
    gt_file = open(gt_file, "r")
    tk_file = open(tk_file, "r")

    wc = 0
    twc = 0
    for line in gt_file:
        lwc = 0
        gt_line = line.split()
        tk_line = tk_file.readline().split()
        tk_len = len(tk_line)
        for idx, word in enumerate(gt_line):
            if idx < tk_len and word.lower() == tk_line[idx].lower():
                #if lists are aligned, check words at same indices
                wc += 1
                print(Fore.GREEN + word) #correct word
                lwc += 1
            else:
                print(Fore.RED + word) #incorrect word
            twc += 1
    print(Fore.WHITE + "<<< evaluated " + file_name + " with basic comparator (bc) >>>")
    print("bc total words: ", twc)
    print("bc similar words: ", wc)
    if twc > 0:
        percentage = round(100 * (wc/twc), 3)
        percentage_str = str(percentage) + "%"
        print("bc percentage: ", percentage, "%")
    else:
        print("bc percentage: 0 %")
    gt_file.close()
    tk_file.close()
    return 

def c1(gt_file, tk_file, file_name):
    #remove punctuation (. , ! -) and apostrophes (')
    #removes accented characters entirely, does not just get rid of accent
    #removes parenthesis
    #if lists become unaligned due to split or combination of words, consider this to an extent of words being 1 off
        #minimally account
    #gets rid of accented characters
    gt_file = open(gt_file, "r")
    tk_file = open(tk_file, "r")
    wc = 0
    twc = 0
    for line in gt_file:
        lwc = 0
        gt_line = unidecode.unidecode(line)
        tk_line = unidecode.unidecode(tk_file.readline())
        tk_line = tk_line.translate(str.maketrans('', '', string.punctuation))
        gt_line = gt_line.split()

        for idx, word in enumerate(gt_line):
            if "(" in word or "&" in word:
                gt_line.remove(word)
                #remove paranthetical additions in transcription
            else:
                gt_line[idx] = word.translate(str.maketrans('', '', string.punctuation))
                #remove punctuation from string
        tk_line = tk_line.split()
        tk_len = len(tk_line)

        for idx, word in enumerate(gt_line):
            if idx < tk_len and word.lower() == tk_line[idx].lower():
                #if lists are aligned, check words at same indices
                wc += 1
                lwc += 1
                print(Fore.GREEN + word) #correct word
            elif idx > 0 and idx < tk_len and word.lower() == tk_line[idx - 1].lower():
                wc += 1
                lwc += 1
                print(Fore.GREEN + word) #correct word
            elif idx > 0 and idx + 1 < tk_len and word.lower() == tk_line[idx + 1].lower():
                wc += 1
                lwc += 1
                print(Fore.GREEN + word) #correct word
            else:
                print(Fore.RED + word) #incorrect word
            twc += 1
    print(Fore.WHITE + "<<< evaluated " + file_name + " with generous comparator (gc) >>>")
    print("gc total words: ", twc)
    print("gc similar words: ", wc)
    if twc > 0:
        percentage = round(100 * (wc/twc), 3)
        print("gc percentage: ", percentage, "%")
        percentage_str = str(percentage) + "%"
    else:
        print("gc percentage: 0%")
    gt_file.close()
    tk_file.close()
    return 

def c2(gt_file, tk_file, file_name):
    #checks via dictionary structure. Checks true word accuracy in the entire document
    gt_file = open(gt_file, "r")
    tk_file = open(tk_file, "r")
    wc = 0
    twc = 0
    gt_dict = {}
    for line in gt_file:
        gt_line = unidecode.unidecode(line)
        gt_line = gt_line.split() #split into list of words

        for idx, word in enumerate(gt_line):
            # clean up words in gt file, add to dictionary
            if "(" in word or "&" in word:
                gt_line.remove(word)
                #remove paranthetical additions in transcription
            else:
                #remove punctuation from string and make lowercase, add gt word to dictionary
                gt_line[idx] = word.translate(str.maketrans('', '', string.punctuation))
                gt_line[idx] = gt_line[idx].lower()
                gt_dict[gt_line[idx]] = gt_dict.setdefault(gt_line[idx], 0) + 1
                twc += 1 
    for line in tk_file:
        # go through transcribed file, check against gt_dict
        lwc = 0
        tk_line = unidecode.unidecode(line)
        tk_line = tk_line.translate(str.maketrans('', '', string.punctuation))
        tk_line = tk_line.split()
        for idx, word in enumerate(tk_line):
        # if the current transcribed word matches a key in gt_dict, and gt_dict[key] > 0
            # increase lwc and wc
            # subtract value at gt_dict[key]
            if (tk_line[idx].lower() in gt_dict) and (gt_dict[tk_line[idx].lower()] > 0):
                gt_dict[tk_line[idx].lower()] -= 1
                lwc += 1
                wc += 1
                print(Fore.GREEN + word) #correct word
            else:
                print(Fore.RED + word) #incorrect word

    print(Fore.WHITE + "<<< evaluated " + file_name + " with dictionary comparator (dict comp) >>>")
    print("dict comp total words: ", twc)
    print("dict comp similar words: ", wc)
    if twc > 0:
        percentage = round(100 * (wc/twc), 3)
        print("dict comp percentage: ", percentage, "%")
        percentage_str = str(percentage) + "%"
    else:
        print("dict comp percentage: 0")
    gt_file.close()
    tk_file.close()
    return 

def main(): 
    #take txt file "file_names"
    file_name = input("file name: ")
    file_name = str(file_name)
    llm_type = input("language model: ")
    llm_type = str(llm_type)

    llm_file = file_name + "_" + llm_type + ".txt"
    gt_file = file_name + "_gt.txt"
    if not os.path.isfile(llm_file) or not os.path.isfile(gt_file):
        #make sure both files are in directory
        print("llm file or ground truth file is not in the present working directory. Please fix this before continuing")
        return

    which_comp = input("Enter which comparator you wish to see (basic, generous, dictionary): ")
    if which_comp == "basic":
        basic(gt_file, llm_file, file_name)
    elif which_comp == "generous":
        c1(gt_file, llm_file, file_name)
    elif which_comp == "dictionary":
        c2(gt_file, llm_file, file_name)
    else:
        print("You did not enter a valid comparator")
        return
    return


if __name__=="__main__": 
    main() 