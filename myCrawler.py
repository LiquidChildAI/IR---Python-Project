#!/usr/bin/env python

import urllib2
import re
import nltk
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
from urllib import urlopen
from nltk import word_tokenize, wordpunct_tokenize
import os
import time
from datetime import datetime
import sys

global usage
usage = str('myCrawler.py [seedfile] [depth] [outputdir] [logfile]')



class myCrawler:

    def __init__(self):

        print ("Starting myCrwaler.py")

        self.log_file_path = outputdir + '\\' + logfile
        self.all_seeds_file_path = outputdir + "\seeds.txt"
        self.dir_path = outputdir + "\Corpus"

        #Create Directories if not exists
        if not os.path.exists(outputdir):
            os.makedirs(self.dir_path)
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

        self.num_of_pages  = 0


        self.writeToLog("myCrawler __init Completed")


    #Write strign to log file
    def writeToLog(self,string ):
        try:
           with open( (self.log_file_path),'a') as logFile:
            logFile.write(str(datetime.now()) + '\t' + string + '\n')
            logFile.close
        except:
            print 'Error Writing to Log file'

    #Write all seed link to seeds file
    def writeToSeeds(self,string):
        try:
           with open( (self.all_seeds_file_path) , 'a') as seedFile:
            seedFile.write(str(datetime.now()) + '\t' + string + '\n')
            seedFile.close
        except:
            print 'Error Writing to Seeds file'

    #Returns a list of all links in a Html page
    def getAllLinks(self,htmlPage):
        soup=BeautifulSoup(htmlPage)

        #links = soup.findAll('a',href=True)
        links = soup.findAll('a',href=re.compile('^/en/'))   # Getting rid of irrelevant paths
        linksArray = []
        print 'Number of Links to Be Processed From Page ' + str(len(links))
        for l in links:
            linksArray.append(  str("http://wikitravel.org" + l.get('href')) )
            #print ( str("http://wikitravel.org" + l.get('href')) )
        return linksArray

    def parseURL(self,seed ):
        print str(seed)
        s_file_name = seed
        s_file_name = s_file_name.replace("http://wikitravel.org/en/","")
        s_file_name = s_file_name.replace("/","" )
        return s_file_name


    def isPath(self, new_file):
        l = ['#','.png','.jpg','File:','.bmp']
        for i in l:
            if i in new_file:
                return False
        return True

    #writes to log,seed, and new_file_path ( for 'recursive' )
    def logAndFileWriteForRecursive(self,new_file_path,pageText,seed,depth):

        self.num_of_pages = self.num_of_pages + 1
        if ( self.num_of_pages % 10 == 0) : # every 10 pages write a message on screen
            print ('Proccessed ' + str(self.num_of_pages) + " Pages so far \n")

        self.writeFile(new_file_path,pageText) # Write a new file
        self.writeToSeeds(seed)   # Write to seeds file
        self.writeToLog( "File was written: " + (new_file_path) +"\t of Seed: " + seed + " Depth = " + str(depth) )



    def recursive(self,seed, rec_depth):

        self.writeToLog( "In recursive with seed " + seed+ " Depth = " + str(rec_depth) )

        new_file_name = self.parseURL(seed) # Parse url so file can be written
        new_file_path = (self.dir_path+'\\' + str(new_file_name) +".txt") # apply a more readable filename

        #Check valid page and if file exists ( in depth = 1), if so no need to go through page again -> return
        if self.isPath(new_file_name) == False :
            print 'Passed: ' + new_file_path
            return
        else:
            print ('Processing: ' + str(new_file_path))


        #Check if can get url
        try:
            html = urllib2.urlopen(seed).read() # html page as text
            pageText = nltk.clean_html(html)   # clean text from html tags
            pageText = ' '.join(pageText.split())
            self.writeToLog( "(HTML) - urlopen().read of " + seed + " in Depth = " + str(depth) + " Recieved Successfully" )

        except Exception: # if url cannot be opened return
            self.writeToLog( "Error Opening " + seed )
            return

        if (rec_depth == 0):
            if os.path.exists(new_file_path) == True :
                return
            self.writeToLog( "In recursive with seed " + seed + " Depth = " + str(rec_depth) )
            self.logAndFileWriteForRecursive(new_file_path,pageText,seed,rec_depth)
            return

        elif (rec_depth > 0):
            self.writeToLog( "In recursive with seed " + seed + " Depth = " + str(rec_depth) )
            if os.path.exists(new_file_path) == False :
                self.logAndFileWriteForRecursive(new_file_path,pageText,seed,rec_depth)
            allPageLinks = self.getAllLinks(html); # get all links

            #Go through all links in page
            for l in allPageLinks:
                self.writeToLog( ("For of links of :" + str(l)) )
                self.recursive(str(l), int(rec_depth-1) )
            return

    # Writes given text to given file path name - added '.txt'
    def writeFile(self,full_path,text):
        try:
            f = open(full_path, 'w')
            f.write(text)
            f.close
        except Exception:
            print ('Error Writing File : ' + str(full_path))



#main crawler function
def main():

    try:
        global seedfile
        global depth
        global outputdir
        global logfile
        nparam = len(sys.argv)
        for i in range(nparam):
            print str(i) + " : " + str(sys.argv[i])

        if nparam == 4 or nparam == 5:
            seedfile = sys.argv[1]
            if nparam == 4:
                depth = 2
                outputdir = sys.argv[2]
                logfile = sys.argv[3]
            if nparam == 5:
                depth = sys.argv[2]
                outputdir = sys.argv[3]
                logfile = sys.argv[4]
        else:
            exit( 'Usage : ' + str(usage))

        c = myCrawler()
        print ('Starting Recursive process pages')
        c.writeToLog("*** Recursive Started ***")
        c.recursive( str(seedfile),int(depth) )
        c.writeToLog("*** Recursive Completed ***")
        c.writeToLog( str("TOTAL PAGES COLLECTED: " + str(c.num_of_pages)) )
    except:
        exit("Error Occured in myCrawler")


if  __name__ =='__main__':
    main()
    print 'myCrwaler Completed'
