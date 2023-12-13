import sys 
import unidecode
import string
import os
import csv

def basic(gt_file, tk_file, llm_type):
    gt_file = open("gt/"+gt_file, "r")
    tk_file = open(llm_type+tk_file, "r")

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
                lwc += 1
            twc += 1
    print("bc total words: ", twc)
    print("bc similar words: ", wc)
    if twc > 0:
        percentage = round(100 * (wc/twc), 3)
        percentage_str = str(percentage) + "%"
        print("bc percentage: ", percentage, "%")
    else:
        print("bc percentage: 0")
    gt_file.close()
    tk_file.close()
    return [str(twc), str(wc), percentage_str]

def c1(gt_file, tk_file, llm_type):
    #remove punctuation (. , ! -) and apostrophes (')
    #removes accented characters entirely, does not just get rid of accent
    #removes parenthesis
    #if lists become unaligned due to split or combination of words, consider this to an extent of words being 1 off
        #minimally account
    #gets rid of accented characters
    gt_file = open("gt/"+gt_file, "r")
    tk_file = open(llm_type+tk_file, "r")
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
            elif idx > 0 and idx < tk_len and word.lower() == tk_line[idx - 1].lower():
                wc += 1
                lwc += 1
            elif idx > 0 and idx + 1 < tk_len and word.lower() == tk_line[idx + 1].lower():
                wc += 1
                lwc += 1
            twc += 1
    print("gc total words: ", twc)
    print("gc similar words: ", wc)
    if twc > 0:
        percentage = round(100 * (wc/twc), 3)
        print("gc percentage: ", percentage, "%")
        percentage_str = str(percentage) + "%"
    else:
        print("gc percentage: 0")
    gt_file.close()
    tk_file.close()
    return [str(twc), str(wc), percentage_str]

def c2(gt_file, tk_file, llm_type):
    #checks via dictionary structure. Checks true word accuracy in the entire document
    gt_file = open("gt/"+gt_file, "r")
    tk_file = open(llm_type+tk_file, "r")
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
            if (word.lower() in gt_dict) and (gt_dict[word.lower()] > 0):
                gt_dict[word.lower()] -= 1
                lwc += 1
                wc += 1
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
    return [str(twc), str(wc), percentage_str]
            

def main(): 
    #take txt file "file_names"
    if len(sys.argv) != 3:
        print("Please enter 1) the .txt file of file names you wish to compare and 2) the language model you wish to compare against your ground truth files")
        return
    tk_file = open(sys.argv[1])
    lines = tk_file.readlines()
    tk_name = []
    for line in lines:
        tk_name.append(line.strip())
    

    #check our list with gt and tk files. should have corresponding gt and tk file
    llm_type = str(sys.argv[2])
    pair = []
    errors = 0
    if not os.path.isdir(llm_type):
        print("The language model you specified does not exist in this folder. Please place all of your transcriptions in a folder titled after the language model you wish to compare against")
        return
    
    #check if all files necessary exist
    gt_file_list = os.listdir('gt')
    tk_file_list = os.listdir(llm_type) 
    for name in tk_name:
        gtf = name + "_gt.txt"
        tkf = name + "_" + llm_type + ".txt" 
        if gtf not in gt_file_list:
            print(gtf + " not in ground truth file directory")
            errors += 1
 
        if tkf not in tk_file_list:
            print(tkf + " not in transcription files directory")
            errors += 1

        pair.append((gtf, tkf)) #(groundtruth, transcription)
    if errors > 0:
        print("please fix directory files before proceeding with file comparisons")
        return
    #now pair set will have all files that you need to process
    filename = llm_type + "_vsGroundTruthComparator.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["File Name", 
                 "Total Words (Basic)", 
                 "Total Similar Words (Basic)", 
                 "Basic Comparator Accuracy", 
                 "Total Words (Generous)",
                 "Total Similar Words (Generous)",
                 "Generous Comparator Accuracy",
                 "Total Words (Dictionary)",
                 "Total Similar Words (Dictionary)",
                 "Dictionary Comparator"]
        writer.writerow(field)

        llm_type = llm_type+"/" #LLM TYPE
        for transcribe_set in pair:
            print("")
            print("<<< evaluating " + transcribe_set[1] + " >>>")
            
            b_arr = basic(transcribe_set[0], transcribe_set[1], llm_type)
            c1_arr = c1(transcribe_set[0], transcribe_set[1], llm_type)
            c2_arr = c2(transcribe_set[0], transcribe_set[1], llm_type)
            writer.writerow([transcribe_set[1], b_arr[0], b_arr[1], b_arr[2], c1_arr[0], c1_arr[1], c1_arr[2], c2_arr[0], c2_arr[1], c2_arr[2]])
    
    return

  
if __name__=="__main__": 
    main() 