#!/usr/bin/env python

## IMPORTANT DEFINE THE LANGUAGE
language = "English"

from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter
from pyth.plugins.xhtml.writer import XHTMLWriter
import re
import sys

from bs4 import UnicodeDammit
from xml.dom.minidom import parseString
import dicttoxml

raw_data_folder = "~/raw_data/factiva/"

doc1 = Rtf15Reader.read(open(raw_data_folder + 'Factiva-20141201-0822marchaus1.rtf', 'rb'))
doc2 = Rtf15Reader.read(open(raw_data_folder + 'Factiva-20141201-0830marchaus2.rtf', 'rb'))
doc3 = Rtf15Reader.read(open(raw_data_folder + 'Factiva-20141201-0834marchaus3.rtf', 'rb'))

xmltext1 = XHTMLWriter.write(doc1, pretty=True).read()
xmltext2 = XHTMLWriter.write(doc2, pretty=True).read()
xmltext3 = XHTMLWriter.write(doc3, pretty=True).read()

xmltext = xmltext1 + "\n\n" + xmltext2 + "\n\n" + xmltext3

# Replace smart quotes
xmltext = xmltext.replace("\xe2\x80\x99\x19", "'")
xmltext = xmltext.replace("\xe2\x80\x9c\x1c", "\"")
xmltext = xmltext.replace("\xe2\x80\x9d\x1d", "\"")
xmltext = xmltext.replace("\xe2\x80\x94\x14", "-")
xmltext = xmltext.replace("\xc2\xa9\xc2\xa9", " ")
xmltext = xmltext.replace("\xe2\x82\xac\xc2\xac", "E")
xmltext = xmltext.replace("\xc2\xa3\xc2\xa3", "L")
xmltext = xmltext.replace("\xe2\x80\x98\x18","'")
xmltext = xmltext.replace("\xe2\x80\x99\x19","'")
xmltext = xmltext.replace("\xe2\x80\x9d", "\"")
xmltext = xmltext.replace("\xe2\x80\xa2", "-")
xmltext = xmltext.replace("\xc3\xa1\xc3\xa1","a")
xmltext = xmltext.replace("\xe2\x80\x93\x13","")
xmltext = xmltext.replace("\xc2\xad","")
xmltext = xmltext.replace("\xe2\x80\x89\t","")
xmltext = xmltext.replace("\xe2\x80\xa6","")
xmltext = xmltext.replace("\xc2\xa0"," ")
xmltext = xmltext.replace("\xe2\x96\xa0"," ")
xmltext = xmltext.replace("\xc3\xa9\xc3\xa9","e")
xmltext = xmltext.replace("\xc3\xbc\xc3\xbc", "u")
xmltext = xmltext.replace("\xe2\x80\x82\x02", " ")

# Define regex pattern and cleanup (remove words longer than...)
regexp = re.compile(r'\W*\b\w{50,}\b')
xmltext = re.sub(regexp, "", xmltext)

# xmltext = UnicodeDammit(xmltext).unicode_markup
# xmltext = UnicodeDammit(xmltext, ["windows-1252"], smart_quotes_to="xml").unicode_markup

# Create list of articles
l = re.findall("([\s\S]+?\\n<p>Document.+)", xmltext)

tagged_article_list = list()

def unlist(result):
    if len(result)>0:
        return result[0]
    else:
        return(None)

# Define regex patterns
pat_title = "<p><strong>(.+)</strong></p>"
pat_words = "<p>([0-9]*|[0-9]*,[0-9]*) words</p>"
pat_factiva_id = "<p>(Document [a-zA-Z0-9]*)</p>"
pat_date = "<p>([0-9]{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) ([0-9]{4})</p>"
pat_page = "<p>([0-9]*)</p>"

for article in l:
    
    title = unlist(re.findall(pat_title, article))
    words = unlist(re.findall(pat_words, article)).replace(",", "")
    factiva_id = unlist(re.findall(pat_factiva_id, article))
    date = ' '.join(unlist(re.findall(pat_date, article)))
    page = unlist(re.findall(pat_page, article))

    split_article = re.findall("<p>.*</p>", article)
    
    for i in range(0, len(split_article)):
        if re.match(pat_title, split_article[i]) is not None:
            title_at = i
            break
        else:
            title_at = None
            
    # Try to find and match author (number of words is always present?)
    # Is the <p> following the title number of words?
    if re.match(pat_words, split_article[title_at + 1]) is not None:
         author = None
    else:
        author = unlist(re.findall("<p>(.+)</p>", split_article[title_at + 1]))

    # Find index of date (date should always be there)
    date_at = None
    for i in range(0, len(split_article)):
        if re.match(pat_date, split_article[i]) is not None:
            date_at = i
            break
    if date_at is None:
        print "It seems there's no date in this article: " + article
        sys.exit()

    # After date is either time or publication
    for i in range(1, 4):
        if re.match("<p>([a-zA-Z].+)</p>", split_article[date_at + i]) is not None:
            publication = unlist(re.findall("<p>(.+)</p>", split_article[date_at + i]))
            publication_id = unlist(re.findall("<p>(.+)</p>", split_article[date_at + i + 1]))
            break

    # Find copyright (after language) and body
    for i in range(0, len(split_article)):
        if re.match("<p>"+language+"</p>", split_article[i]) is not None:
            language_at = i
            break
    if date_at is None:
        print "I couldn't find the language in this article: " + article
        sys.exit()

    copyright = unlist(re.findall("<p>(.+)</p>",split_article[language_at + 1]))

    # Find body: everything from copyright to end of document - 1
    body = ' '.join(split_article[language_at + 2 : len(split_article) - 1]).replace('<p>', '').replace('</p>', '\n\n')

    parts = {'date':date,
             'title':title,
             'author':author,
             'words':words,
             'publication':publication,
             'publication_id':publication_id,
             'page':page,
             'language':language,
             'copyright':copyright,
             'factiva_id':factiva_id,
             'body':body}

    tagged_article_list.append(parts)

# Convert to XML 
xml = dicttoxml.dicttoxml(tagged_article_list, attr_type=False)
f = open('output.xml','w')
f.write(xml)
f.close()
