# explanation
## Summary

This project defines a simple document management system using Python. It retrieves web pages, processes and stores their content, and allows for various operations such as adding, deleting, searching, and analyzing text documents.
## Libraries and Imports

**BeautifulSoup** from bs4: Parses HTML and XML documents.

**os**: Interacts with the operating system.

**SequenceMatcher** from difflib: Compares sequences of text.

**Counter** from collections: Counts elements in a collection.

**requests**: Makes HTTP requests.

**nltk.tokenize** and **nltk.corpus.stopwords**: Tokenizes text and removes stopwords.

**gensim.parsing.preprocessing**: Removes stopwords from text.

##  Functions

***1. AddDoc(url, Filemanager)***

 - This function fetches the content of the given URL, processes it, and stores it as a text file.

 - Retrieves the HTML content of the URL.

 - Extracts the first three paragraphs of the page.

 - Saves these paragraphs to a text file named after the URL's last path component.

 - Removes stopwords from the text and updates the file.

 - Updates the Filemanager dictionary with the URL and the file name.


***2. DeleteDoc(url)***

- This function deletes the text file corresponding to the given URL and removes the entry from the Filemanager dictionary.

***3. SearchDoc(searchword)***
- This function searches for a given word across all text files in a specified directory and prints the names of files containing the word.

***4. Mostusedword(url)***
- This func finds and prints the most frequently occurring word in the text file corresponding to the given URL.

***5. Similarfile(fileid1, fileid2)***
- This func calculates and prints the similarity ratio between the contents of two text files.

***6. Popularword()***
- This func prints the most common word across all text files in a specified directory.

***7. SearchDoc2(searchword)***
- This func counts and prints the number of text files in a specified directory that contain the given search word.


## Example

**Adding Documents:**
```
list = ["https://en.wikipedia.org/wiki/Albert_Einstein", "https://en.wikipedia.org/wiki/Carl_Jung"]
for url in list:
    AddDoc(url, Filemanager)
```


**Finding the Most Used Word in a Document:**
```
url = "https://en.wikipedia.org/wiki/Albert_Einstein"
Mostusedword(url)
```

**Deleting a Document:**
```
url = "https://en.wikipedia.org/wiki/Albert_Einstein"
DeleteDoc(url)
```
