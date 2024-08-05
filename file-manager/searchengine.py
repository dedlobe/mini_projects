from bs4 import BeautifulSoup
import os
from difflib import SequenceMatcher
import os
from collections import Counter
import requests
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from gensim.parsing.preprocessing import remove_stopwords




#*************works************************************************
def AddDoc (url,Filemanager):

    # we receive the url as a use input in main function
    r=requests.get(url)
    Soup= BeautifulSoup(r.text, 'html.parser').select('body')[0]

    paraghraphs=[]
    links=[]
    i=0
    for tag in Soup.find_all():
        if (i<=3):
            if tag.name=="p":
              paraghraphs.append(tag.text)
              i=i+1
        else:
            break



    name = url.split("/")

    #print(name[-1]) /test
    z = name[-1]
    text = z + ".txt"
    file = open(text, "w", encoding="utf-8")
    file.writelines(paraghraphs[2])
    file.writelines(paraghraphs[3])
    file.close()
    with open (text,'r') as file:
        data=file.read().replace('\n','')
    filtered_sentence=remove_stopwords((data))
    file1=open(text,"w",encoding="utf-8")
    file1.writelines(filtered_sentence)
    file1.close()
    #return paraghraphs[2], paraghraphs[3] // test



    id=url
    Filemanager[id]=name[-1]
    Filemanager.update({id: name[-1]})
    print(Filemanager)



#******************WORKS**************************************
def DeleteDoc(url):
        # url can be the key for our dictionary
        name=Filemanager[url] +".txt"
        del Filemanager[url]
        os.remove(name)
        print(Filemanager)



#**********works***************************************************
def SearchDoc (searchword):
    dir_path ="E:\\codes\\pythonn\\matrix"

    # list to store files
    res = []

    # Iterate directory
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            res.append(path)
    #print(res) /test

    # iterate each file in a directory
    for file in os.listdir(dir_path):
        cur_path = os.path.join(dir_path, file)
        # check if it is a file
        if os.path.isfile(cur_path):
            with open(cur_path, 'r') as file:
                # read all content of a file and search string
                if searchword in file.read():
                    print(Filemanager.get(url)) #filename


#**********************************WORKS*************************************
#url here is the file id as well
def Mostusedword (url):

    z=Filemanager.get(url)
    text = z + ".txt"
    file = open(text, "r")
    frequent_word = ""
    frequency = 0
    words = []
    # Traversing file line by line
    for line in file:

        # splits each line into
        # words and removing spaces
        # and punctuations from the input
        line_word = line.lower().replace(',', '').replace('.', '').split(" ");

        # Adding them to list words
        for w in line_word:
            words.append(w);

            # Finding the max occurred word
    for i in range(0, len(words)):

        # Declaring count
        count = 1

        # Count each word in the file
        for j in range(i + 1, len(words)):

            if (words[i] == words[j]):

                count = count + 1;

                # If the count value is more
        # than highest frequency then
        if (count > frequency):
            frequency = count;
            frequent_word = words[i];

    print("Most repeated word: " + frequent_word)
    print("Frequency: " + str(frequency))
    file.close()


def Similarfile(fileid1,fileid2):
    f1= Filemanager[fileid1] +".txt"
    f2= Filemanager[fileid2] +".txt"

    text1 = open(f1).read()
    text2 = open(f2).read()
    m = SequenceMatcher(None, text1, text2)

    print(m.ratio())

#********************works******************************************************
def Popularword():
    count = Counter()
    DIR = "path:\\to\\your\\folder"

    for filename in os.listdir(DIR):
        if filename.endswith(".txt"):
             #opens the file
            with open(os.path.sep.join([DIR, filename]), 'r') as f:
               for line in f.readlines():

                   #Remove spaces at the beginning and at the end
                   line = line.strip()

                   # count all words in line
                   count.update(line.split())
    print(count.most_common(1))
#*********************works*****************************************************
def SearchDoc2(searchword):
    dir_path ="E:\\codes\\pythonn\\matrix"
    count=0
    # iterate each file in a directory
    for file in os.listdir(dir_path):
        cur_path = os.path.join(dir_path, file)
        # check if it is a file
        if os.path.isfile(cur_path):
            with open(cur_path, 'r') as file:
                # read all content of a file and search string
                if searchword in file.read():
                    count=count+1
    print (count)


if __name__ == '__main__':
 # key:value
 # key--> given url,
 # value--> file name
 # dictionary
 Filemanager=dict()
 url=""

 #**************TEST URLS********************
 #url="https://en.wikipedia.org/wiki/Albert_Einstein"
 #url="https://en.wikipedia.org/wiki/Carl_Jung"
 #url="https://en.wikipedia.org/wiki/Elvis_Presley "
 #url="https://en.wikipedia.org/wiki/Nikola_Tesla"
 #url="https://en.wikipedia.org/wiki/Adele"

#adding multiple docs

 list=["https://en.wikipedia.org/wiki/Albert_Einstein","https://en.wikipedia.org/wiki/Carl_Jung",
       "https://en.wikipedia.org/wiki/Elvis_Presley ","https://en.wikipedia.org/wiki/Nikola_Tesla","https://en.wikipedia.org/wiki/Adele"]
 #for x in range(len(list)):
     #url=list[x]
    # AddDoc(url,Filemanager)
     #Mostusedword(url)



url="https://en.wikipedia.org/wiki/Adele"

fileid1=url
AddDoc(url,Filemanager)
#url2="https://en.wikipedia.org/wiki/Nikola_Tesla"
#fileid2=url2
#AddDoc(url2,Filemanager)
#Similarfile(fileid1,fileid2)


#searchword=input("find name:")
#SearchDoc(searchword)
#Popularword()


wait=input("enter num:")
DeleteDoc(url)








