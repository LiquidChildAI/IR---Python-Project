#!/usr/bin/env python

import urllib2
import csv
import re
from nltk.corpus import stopwords
import nltk
from nltk import *
from nltk.tokenize import word_tokenize
from string import punctuation
from collections import Counter
import collections
from collections import defaultdict
from datetime import datetime
import math
import pickle
import webbrowser
import gc
import string
import sys

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

class myQueries:
    def __init__(self):
        print ("Starting myQueries.py")

        if not os.path.exists(outputdir) :
            exit("Outputdir Error")

        try:

            print ("Loading Dictionary Pickle File")
            self.dicVector = pickle.load(open(str(outputdir)+"\dicVec.pkl","rb")  )
            print ("Done Loading Dictionary Pickle File")
            print ("Loading IDF Pickle File")
            self.idfDic = pickle.load(open(str(outputdir)+"\idfDic.pkl","rb")  )
            print ("Done Loading IDF Pickle File")
        except:
            exit("Error openning pickle file")

        self.K_Best = 15  # K Best Results to display
        self.log_file_path = outputdir+"\log.csv"
        self.all_seeds_file_path = outputdir+"\seeds.txt"
        self.dir_path = outputdir+"\Corpus"


        self.N = len (os.listdir(self.dir_path))
        self.stopWords = STOPWORDS
        self.nltkstopwords = nltk.corpus.stopwords.words('english')
        self.stopWords.extend( self.nltkstopwords)
        self.punctuationChars = []

        for c in string.punctuation:
            self.punctuationChars.append(c)

        self.writeToLog("myQueries __init__ Completed")


    #Returns the norma of text given as a dcitionary ( term:frequency )
    def normDict(self,dic):
        counter = 0
        for t in dic:
             counter += float( math.pow((dic[t]), 2) )
        #print 'Norma dic : ' + str(math.sqrt(counter))
        return float( math.sqrt(counter) )


     #Calculate tf of a term in a document given as dictionary ( the total number of words in the document is given by parameter and needs to be calculated ahead)
    def tf(self,term , docAsDic ):  # term: freq
        if term in docAsDic  :
            calc = 1 + (math.log10((docAsDic[term])))
            return float(calc)
            #print ' Tf : ' + str(calc)
        else:
            return 0


    #Tokenizing and Cleaning a file. Returns a dictionary of its term:frequency
    def tokenText(self,text):

        #Initialize Stemmer
        st = nltk.stem.PorterStemmer()  #st = LancasterStemmer()  # Lancaster Algorithm stem

        #start cleanning text
        word_tokens = nltk.wordpunct_tokenize(text.lower())

        vocabulary_tokens = []
        for w in word_tokens:
            if w not in self.stopWords: # get rid of stop words
                for c in w:
                    if c in self.punctuationChars: #Clean punctutation chars from word
                        w = w.replace(c,"")
                    if c not in string.ascii_letters:
                        w = w.replace(c,"")

                #w = w.replace(" ","")
                w = st.stem(w) #PorterStemmer().stem_word(w) # Porter Stemming
                if len(w) > 0:
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
       with open( (self.log_file_path),'a') as logFile:
        logFile.write(str(datetime.now()) + '\t' + string + '\n')
        logFile.close

    #Write all seed link to seeds file
    def writeToSeeds(self,string):
       with open( (self.all_seeds_file_path) , 'a') as seedFile:
        seedFile.write(str(datetime.now()) + '\t' + string + '\n')
        seedFile.close

    #writes the results of the links given by a dictionary of filenames and cosine values.
    def createHTML(self,linksDic,bigramsDic,trigramsDic,qText):

        htmlstr = '<HTML><br><BODY><br><center><H2>Results for : ' + str(qText)  + '</H2></center>'
        ##########################################   TRI GRAMS
        if len(trigramsDic) == 0:
            htmlstr += ' No Results for Tri-Grams. <br>'
        else:
            htmlstr += ' Results for Tri-Grams :<br>'
            count = 0
            for triterm in trigramsDic:
                count+=1
                linkAddress = 'http://www.wikitravel.org/en/'+ str ( triterm[0].replace(".txt","" ) )
                htmlstr += '<br><a href = \' ' + linkAddress + '\'>'+linkAddress+'</a>   Rank: ' +str( ((1-triterm[1])* 10)) + '<br>'


        ##########################################  BI GRAMS
        if len(bigramsDic) == 0:
            htmlstr += ' No Results for Bi-Grams. <br>'
        else:
            htmlstr += ' Results for Bi-Grams :<br>'
            for biterm in bigramsDic:
                linkAddress = 'http://www.wikitravel.org/en/'+ str (biterm[0].replace(".txt","" ) )
                htmlstr += '<br><a href = \' ' + linkAddress + '\'>'+linkAddress+'</a>   Rank: ' +str( ((1-biterm[1])* 10)) + '<br>'

        ############################################# REGULAR

        if len(linksDic) == 0:
            htmlstr += ' No Regular Results . <br>'
        else:
            htmlstr += ' Regular Results :<br>'
            count = 0
            for link in linksDic:
                linkAddress = 'http://www.wikitravel.org/en/'+ str ( link[0].replace(".txt","" ) )
                htmlstr += '<br><a href = \' ' + linkAddress + '\'>'+linkAddress+'</a>   Rank: ' +str( ((1-link[1])* 10)) + '<br>'
                count+=1
                if count == self.K_Best: # Adding only the K best reuslt to HTML page (defined in __init__ )
                    break;

        htmlstr+= '</BODY><br></HTML>'

        #Write html file to disk
        try:
            with open('htmlPage.html','w') as hpage:
                hpage.write(htmlstr)

        except Exception:
            print ' Error writing to HTML file '


    # Returns the cosine between two vectors given as dictionaries
    def CosineVector(self,pV,qV): #given as a dcitionary  (term : w = tf*idf/norma)
        counter = 0.0
        for t in qV:
            if t in pV:
               # print 'pv[t] ' + str(pV[t]) + '  , qV[t] = ' +str(qV[t])
                counter = counter + float ( pV[t] * qV[t] )
        #print 'Counter from Cosine : ' + str(counter)
        return float ( counter )


    #This function gets a query text and retruns a dictionary of the correct filenames (documents) and the cosine values
    #between them and the query.
    def queryResults(self, queryText ):

        #Create query dictionary for regular, biterms and triterms ( term : freq )
        qDic = self.tokenText(queryText) # Dictioanry of terms from query tokens
        biqDic = Counter(bigrams(nltk.wordpunct_tokenize(queryText.lower())))
        triqDic = Counter(trigrams(nltk.wordpunct_tokenize(queryText.lower())))

        #define query vector for bi-terms, tri-terms and regular term search
        qVector = self.createVectorFromPageDictionary(qDic)  # Normalized Vector (as Dic)
        biqVector =self.createVectorFromPageDictionary(biqDic)
        triqVector =self.createVectorFromPageDictionary(triqDic)

        #define list that will hold the correct documents of the cosine result with the query
        cosVectorResult = dict()
        biCosVectorResult = dict()
        triCosVectorResult = dict()

        for pV in self.dicVector:
            #Bi
            cosRes = float ( self.CosineVector(self.dicVector[pV],biqVector) )
            #print 'Cos Result of ' + str(pV) + ' : ' + str(cosRes)
            if cosRes > 0:
                biCosVectorResult[pV] = cosRes

            #Tri
            cosRes = float ( self.CosineVector(self.dicVector[pV],triqVector) )
            #print 'Cos Result of ' + str(pV) + ' : ' + str(cosRes)
            if cosRes > 0:
                triCosVectorResult[pV] = cosRes

            #Regular
            cosRes = float ( self.CosineVector(self.dicVector[pV],qVector) )
            #print 'Cos Result of ' + str(pV) + ' : ' + str(cosRes)
            if cosRes > 0:
                cosVectorResult[pV] = cosRes

        #Sort by cosine value (ASC)
        cosVectorResult =  sorted(cosVectorResult.items(), key=lambda(k,v):(v,k)) # sort by value
        biCosVectorResult =  sorted(biCosVectorResult.items(), key=lambda(k,v):(v,k)) # sort by value
        triCosVectorResult =  sorted(triCosVectorResult.items(), key=lambda(k,v):(v,k)) # sort by value

        #Create the Html and show it
        self.createHTML(cosVectorResult,biCosVectorResult,triCosVectorResult,queryText)
        del(cosVectorResult)
        del(biCosVectorResult)
        del(triCosVectorResult)
        gc.collect()


    #returns a vector (as dictionary -> term: w = tf * id / norm ) of a given page ( as dictionary-> term:frequeny )
    def createVectorFromPageDictionary(self,pageDic):
            normaOfPage = float ( self.normDict(pageDic) )
            vectorPage = dict() # holds the page vector tf*idf values

            for term in pageDic:
                if term in self.idfDic:
                    _idf = float ( self.idfDic[term] )
                    _tf = float( self.tf(term,pageDic) )
                    w = float ( _idf * _tf )
                    wNormalized = float ( w / normaOfPage )
                    vectorPage[term] = wNormalized
            return vectorPage


#main myQueries function
def main():

    global outputdir
    try:
        if len(sys.argv) == 2:
            outputdir = sys.argv[1]
            print 'myQueries Started'
            c = myQueries()

            while True:
                queryText = raw_input("Enter Query: ")
                try:
                    if ( len(queryText) > 1 ):
                        d = c.queryResults(str(queryText))
                        webbrowser.open_new_tab('htmlPage.html')
                    else:
                        print 'Query text must be larger than 1 letter'
                except:
                    print 'Error in query search'
        else:
            print 'Enter output dir'
    except:
        print 'Error in myQueries'

if  __name__ =='__main__':

    main()
    print 'myQueries after main Completed'



