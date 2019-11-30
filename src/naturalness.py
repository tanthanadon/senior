from CodeTokenizer.tokenizer import TokeNizer
import sys, token, tokenize
from pathlib import Path
import re
import pandas as pd
# For bash command
import os

from nltk.util import pad_sequence
from nltk.util import bigrams
from nltk.util import ngrams
from nltk.util import everygrams
from nltk.lm.preprocessing import pad_both_ends
from nltk.lm.preprocessing import flatten
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.lm import MLE
from nltk.lm import NgramCounter
from nltk.lm import Vocabulary

def tokenizer1():
    TN = TokeNizer("Python")

    f = open("example.py", "r")
    content = f.read()
    #print(content)

    tokens = TN.getPureTokens(content)
    print(tokens)

def testExperiment():
    PATH_PYTHON = "/home/thanadon/Documents/Project/Sample Projects/requests/requests"
    
    p = Path(PATH_PYTHON)
    files = list(p.rglob("*.py"))
    
    d = {}
    #print(type(d))
    # vocabulary
    tokens = []
    
    for file in files:
        if (file != "/home/thanadon/Documents/Project/Sample Projects/requests/requests/api.py"):
            tokens.append(tokenization(file))
    #print(tokens)
    n = 2
    ngrams = list(everygrams(tokens, max_len=n))
    # Model
    lm = MLE(n)
    #print(len(lm.vocab))
    #print(vocab)
    train, vocab = padded_everygram_pipeline(n, tokens)
    lm.fit(train, vocab)
    #print(len(lm.vocab.lookup("if")))
    #test = testTokenization("/home/thanadon/Documents/Project/Sample Projects/requests/requests/api.py")
    #print(test)
    #print(lm.entropy("for"))
    #print(lm.perplexity("for"))
    #print(lm.generate(5, random_seed=3))   
    
def testWritingToken():
    PATH_PYTHON = "/home/thanadon/Documents/Project/Sample Projects/requests/requests"
    PATH_TOKEN = "/home/thanadon/Documents/Project/LanguageModel/tokens/"
    # requests/requests
    p = Path(PATH_PYTHON)
    files = list(p.rglob("*.py"))
    id = 0
    for file in files:
        #print(file)
        name = str(id) + ".py.tokens"
        dir = PATH_TOKEN + name
        print(dir)
        output = Path(dir)
        output.write_text("Test")
        id = id + 1


def tokenization(file):
    file = open(file, encoding='utf-8', errors='ignore')
    tokgen = tokenize.generate_tokens(file.readline)
    line = ''
    temp = ''
    for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
        type1 = re.search("^'''", ttext)
        type2 = re.search('^"""', ttext)
        #print(repr(ttext))
        #print(type1)
        #print(type2)
        #print(ttext)
        if ttext != "\n" and bool(type1 or type2) == False:
            if toktype != tokenize.COMMENT:
                #print(repr(ttext))
                if toktype == tokenize.STRING:
                    temp = '<str>'
                    
                else:
                    temp = ttext
                line = line + temp + ' '
                #print(repr(temp))
        
                
    #print(line)
    return line


def createTokenFile(pythonPath, tokenPath, tokenID):
    #print(line)
    tokenLine = tokenization(pythonPath)
    #print(tokenLine)
    fileName = str(tokenID) + ".py.tokens"
    PATH_OUTPUT = str(tokenPath) + "/" + str(fileName)
    print(PATH_OUTPUT)
    
    output = Path(PATH_OUTPUT)
    #print(output.exists())
    # If the file does not exist, it will prepare new files
    
    with output.open(mode='w+') as file:
            #print(fid)
            file.write(tokenLine)
            file.close()
    #print(pythonPath.resolve())
    list = [str(pythonPath.resolve()), PATH_OUTPUT]
    return list
    

def prepareToken(PATH_PYTHON, PATH_TOKEN, projectName):
    p = Path(PATH_PYTHON)
    q = Path(PATH_TOKEN+projectName+"/")
    q.mkdir(parents=True, exist_ok=True)
    files = list(p.rglob("*.py"))
    d = {}
    #print(type(d))
    tokenID = 0
    pairDirList = []
    
    for file in files:
        pairDirList = createTokenFile(file, q, tokenID)
        tokenID = tokenID + 1
        #print(tempList[1])
        d[pairDirList[0]] = pairDirList[1]
    
    return d
    

def clearBefore(PATH_TOKEN, PATH_FILES):
    # Remove all fold files for previous project
    os.system("rm -v "+str(PATH_FILES)+"/fold*")
    
    # Remove all token files for previous project
    os.system("rm -v "+str(PATH_FILES)+"/files/*.tokens")
    
    # Create new directory first
    q = Path(PATH_FILES+"/files")
    q.mkdir(parents=True, exist_ok=True)

    # Copy all tokens files for next project
    os.system("rsync -rv "+str(PATH_TOKEN)+"*.tokens "+str(q))

def calculateEntropy():
    # Get into the directory of MIT language model
    os.chdir("/home/thanadon/Documents/Project/LanguageModel/CacheModelPackage/evaluation")
    os.system("pwd")
    # Run shell script to calculate entropy for 1-10 grams
    for i in range(1,11):
        #os.system("sh python_example.sh "+str(i))
        #with 1-10 grams based on input $1
        os.system("mkdir -p ./results/entropy/python/summary")
        os.system("./scripts/train.py ./data/python/ "+str(i)+" 1.0 2")
        os.system("./scripts/cross.py ./data/python/ "+str(i)+" -ENTROPY -BACKOFF -DEBUG -CACHE -CACHE_ORDER "+str(i)+" -CACHE_DYNAMIC_LAMBDA -WINDOW_CACHE -WINDOW_SIZE 5000 -FILES > ./results/entropy/python/"+str(i)+"gramsCache.txt")
        os.system("./scripts/cross.py ./data/python/ "+str(i)+" -ENTROPY -BACKOFF -DEBUG -FILES > ./results/entropy/python/"+str(i)+"gramsNoCache.txt")
        os.system("python ./scripts/convertCacheResults.py ./results/entropy/python/ ./results/entropy/python/summary/ngrams.csv")   

def clearAfter(PATH_OUTPUT, PATH_CSV, projectName):
    # Create new directory for storing csv file for each project
    os.system("mkdir -p "+str(PATH_CSV))
    # Copy summary of results to the original project
    os.system("rsync -rv "+PATH_OUTPUT+"/summary/ "+str(PATH_CSV))
    # Rename ngram.csv file to project ID
    Path(PATH_CSV+"ngrams.csv").replace(PATH_CSV+projectName+".csv")
    # Remove all summary files for previous project
    os.system("rm -rv "+PATH_OUTPUT+"*")

def main():
    #testTokenization()
    #testWritingToken()
    #testExperiment()
    language = "python"
    
    # Statis Paths
    PATH_SAMPLE = "/home/thanadon/Documents/Project/Sample_Projects/"
    PATH_TOKEN = "/home/thanadon/Documents/Project/LanguageModel/all_tokens/"
    PATH_MITLM = "/home/thanadon/Documents/Project/LanguageModel/CacheModelPackage/"
    PATH_FILES = PATH_MITLM+"evaluation/data/"+language+"/"
    PATH_OUTPUT = PATH_MITLM+"evaluation/results/entropy/"+language+"/"
    PATH_CSV = "/home/thanadon/Documents/Project/LanguageModel/all_csv/"

    # Create the main directory for cloning projects
    Path(PATH_SAMPLE).mkdir(parents=True, exist_ok=True)
    # Create the main directory for storing token files of all projects
    Path(PATH_TOKEN).mkdir(parents=True, exist_ok=True)
    # Create the main directory for storing csv files of all projects
    Path(PATH_CSV).mkdir(parents=True, exist_ok=True)

    #PATH_PYTHON = "/home/thanadon/Documents/Project/Sample_Projects/requests"
    #print(PATH_PYTHON)

    d = {}
    p = Path(PATH_SAMPLE+".")
    # Loop for all directories
    # check each item is a directory or not
    for PATH_PYTHON in p.iterdir():
        if PATH_PYTHON.is_dir():
            try:
                # Get the name of project from the directory
                projectName = str(Path(PATH_PYTHON).parts[-1])
                print(projectName)
                
                # Prepare tokens of each project
                d = prepareToken(PATH_PYTHON, PATH_TOKEN, projectName)
                
                # mapping directories of Python files with the directories of token files
                df = pd.DataFrame([(k, v) for k, v in d.items()], columns=['pythonPath', 'tokenPath'])
                #print(df)
                # convert dataframe to .csv file
                df.to_csv("mappingPython2Token.csv")
        
                # Clear all token files of the previous iteration
                clearBefore(PATH_TOKEN+projectName+"/", PATH_FILES)
        
                calculateEntropy()

                # Clear all csv files of the previous iteration
                clearAfter(PATH_OUTPUT, PATH_CSV, projectName)
            except:
                continue
        else:
            continue
    

#main()

