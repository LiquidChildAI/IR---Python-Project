#!/usr/bin/env python


import csv
import re
from nltk.corpus import stopwords
import nltk
from stemming.porter2 import stem
from nltk import *
from nltk.tokenize import word_tokenize
from string import punctuation
from collections import Counter
import collections
from collections import defaultdict
from datetime import datetime
import math
import pickle
import string
import gc # Garbage Collector


STOPWORDS = ['a','able','about','across','after','all','almost','also','am','among',
             'an','and','any','are','as','at','be','because','been','but','by','can',
             'cannot','could','dear','did','do','does','either','else','ever','every',
             'for','from','get','got','had','has','have','he','her','hers','him','his',
             'how','however','i','if','in','into','is','it','its','just','least','let',
             'like','likely','may','me','might','most','must','my','neither','no','nor',
             'not','of','off','often','on','only','or','other','our','own','rather','said',
             'say','says','she','should','since','so','some','than','that','the','their',
             'them','then','there','these','they','this','tis','to','too','twas','us',
             'wants','was','we','were','what','when','where','which','while','who',
             'whom','why','will','with','would','yet','you','your']


class myI:

    def __init__(self):
        gc.enable()
        print ("Starting __init__ myI.py")
        # word :   { ( file,freq )+ ( file,freq ) }
        self.invIndex = defaultdict(list) # each value is a list  ( postring list of:  term : [ [filename.txt,df, tf] ] )
        self.documentsVectorsDictionary = dict(dict())
        self.idfDic = dict()

        #Directories and Files
        self.log_file_path = outputdir+"\log.csv"
        self.all_seeds_file_path = outputdir+"\seeds.txt"
        self.dict_file_path = outputdir+"\invertedIndexDictionary.csv"
        self.dir_path = outputdir+"\Corpus"
        self.N = len (os.listdir(self.dir_path))

        #Stop Words list Initialize
        self.stopWords = STOPWORDS
        self.stopWords.extend( nltk.corpus.stopwords.words('english') )

        #Punctuation Char list Init
        self.punctuationChars = []
        for cp in string.punctuation :
            self.punctuationChars.append(cp)

        for cw in string.whitespace :
            self.punctuationChars.append(cw)

        for cn in string.digits:
            self.punctuationChars.append(cn)

        self.stopWords.extend(self.punctuationChars)

        #Create Dir
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

        self.writeToLog("myI __init__ Completed")


    #Tokenizing and Cleaning a file. Returns a dictionary of its term:frequency
    def tokenFile(self,file_path):
        try:
            with open(file_path, 'r') as content_file:
                content = content_file.read()
                content_file.close()
        except Exception:
            self.writeToLog( str("Error opennig file" + file_path) )
            return

        return self.tokenText(content)


    #Tokenizing and Cleaning a file. Returns a dictionary of its term:frequency
    def tokenText(self,text):

        #Initialize Stemmer
        st = nltk.stem.PorterStemmer() # Porter Algorithm Stemming

        #start cleanning text
        word_tokens = nltk.wordpunct_tokenize(text.lower())  # parse to single tokens and perform lowercase

        vocabulary_tokens = []
        for w in word_tokens:
            if w not in self.stopWords: # get rid of stop words
                for c in w:
                    if c in self.punctuationChars: #Clean punctutation chars from word
                        w = w.replace(c,"")
                    if c not in string.ascii_letters:
                        w = w.replace(c,"")

                w = st.stem(w)  # Porter Stemming
                if len(w) > 0: # If there are left chars, add the word to the vocabulary
                    vocabulary_tokens.append(w)


        del(word_tokens) #del word_tokens
        word_tokens = vocabulary_tokens

        # getting 2 words and 3 words as a single term from tokens  ( words that clean from stopwords and punctuation)
        bi_terms = bigrams(word_tokens)
        tri_terms = trigrams(word_tokens)

        # adding to the total tokens the bi terms and tri terms
        word_tokens.extend(bi_terms)
        word_tokens.extend(tri_terms)
        del(bi_terms)
        del(tri_terms)

        freq = Counter(word_tokens)  # Create Dictionary of terms and term frequency
        del (word_tokens)
        freq = collections.OrderedDict(sorted(freq.items())) # sort
        gc.collect()
        return freq  # returns Dictionary of  (word:frequency)


    #Write strign to log file
    def writeToLog(self,string ):
        try:
           with open( (self.log_file_path),'a') as logFile:
            logFile.write(str(datetime.now()) + '\t' + string + '\n')
            logFile.close
        except:
            print 'Error Writing to Log file'


    #Calculate df of a term in a document given as dictionary ( the total number of words in the document is given by parameter and needs to be calculated ahead)
    def tf(self,term , docAsDic ):  # term: freq
        #print (  "Calc df"  )
        if term in docAsDic  :
            calc = 1 + (math.log10((docAsDic[term])))
            return float(calc)
            #print ' Tf : ' + str(calc)
        else:
            return 0


    #Calculate the idf of a term
    def idf(self, term):
        try:
            numOfDocsContatining = len ( (self.invIndex[term]) )
            return float( math.log10( float (self.N / float(numOfDocsContatining)) ) )
        except Exception:
            return 0

    ################################################################################
    #Create Inverted Index and returns a list of the pages dictionaries
    #Inverted Index as follow:   term/word : list of(page name, df in page)
    def createIndex(self):
        files_in_dir = os.listdir(self.dir_path)
        print "Files found in Directory (" + self.dir_path + ") :" + str(files_in_dir)
        print (  "** CreateIndex func - Processing ** "  )

        #listPagesDic = []
        for f in files_in_dir:
            try:
                fDic = self.tokenFile( self.dir_path + '\\' + f ) # getting file as a dictionary
                print str( "Appending to Index from " + str(self.dir_path + '\\' + f) )

                for word in fDic:
                    if word in self.invIndex:
                        #----------------------------filename,df---------,tf
                        self.invIndex[word].append( [str(f) ,fDic[word] , self.tf(word,fDic)]  )  # enter file name and term frequency to the inverted index
                    else:
                        self.invIndex[word] = [[str(f) ,fDic[word] , self.tf(word,fDic)]]
                del (fDic) # Free Memory
                collected = gc.collect()
                print "Garbage collector: collected %d objects." % (collected)
            except:
                print 'Error in files loop in create index '

        self.invIndex = collections.OrderedDict( sorted(self.invIndex.items()) )  # sort dictionary by key
        collected = gc.collect()

        #Writing dictionary to csv ( CSV columns as follow:  'term/word' : 'list of(page name, df in page)' : 'idf' )
        try:
            writer = csv.writer(open(self.dict_file_path, 'wb'))
            print '**** Writing to csv ***'
            for key, value in self.invIndex.items():
                #writer.writerow([key, value, 'idf : ' + str(key) + ' = ' + str ( self.idf(str(key)) )])
                 writer.writerow([key, value])
            print '**** Done Writing to csv ***'
        except Exception:
            print 'Error Writing Dictionary to .CSV file'

    ################################################################################

    #Norma of a page given as dictionary ('dic')
    def normDict(self,dic):
            counter = 0
            for t in dic:
                 counter += float( math.pow((dic[t]), 2) )
            return float( math.sqrt(counter) )

    #Return a vector (as dictionary term: w)
    def createVectorFromPageDictionary(self,pageDic):
            normaOfPage = float ( self.normDict(pageDic) )
            vectorPage = dict() # holds the page vector tf*idf values

            for term in pageDic:
                _idf = 0
                if term in self.idfDic:
                    _idf = float ( self.idfDic[term] )

                _tf = float( self.tf(term,pageDic) )
                w = float ( _idf * _tf )
                wNormalized = float ( w / normaOfPage )
                vectorPage[term] = wNormalized
            return vectorPage


    def createDocumentsVectorList(self):
        files = os.listdir(self.dir_path)
        for file_name in files:
            tokens = self.tokenFile(self.dir_path + '\\' + file_name)
            pDic = Counter(tokens)
            pageVector = self.createVectorFromPageDictionary(pDic)
            self.documentsVectorsDictionary[file_name] = pageVector

            del(pageVector)
        gc.collect()

    #Creating IDF dictionary ( term : idf value )
    def createIdfDic(self):
        for t in self.invIndex:
            self.idfDic[t] = self.idf(t)




# main invertedIndex function
def main():
    global outputdir
    if len (sys.argv) == 2:
        outputdir = str(sys.argv[1])
        try:
            print 'myI Started at:'    + str(datetime.now())
            c = myI()
            c.createIndex()
            c.createIdfDic()
            c.createDocumentsVectorList()

            gc.collect()

            try:
                print '*** Writing DicVec Pickle *** '
                output = open(str(outputdir)+"\dicVec.pkl", 'wb')
                pickle.dump(c.documentsVectorsDictionary,output)
                output.close()
                print '*** Done DicVec Writing Pickle *** '
            except:
                print '*** Error Writing DicVec Pickle *** '


            try:
                print '*** Writing idfDic Pickle *** '
                output = open(str(outputdir)+"\idfDic.pkl", 'wb')
                pickle.dump(c.idfDic,output)
                output.close()
                print '*** Done Writing idfDic Pickle *** '
            except:
                print '*** Error Writing idfDic Pickle *** '
        except:
            print 'Error In myI'
    else:
        print 'Enter Outputdir'



if  __name__ =='__main__':

    main()
    print 'myI after main Completed'

