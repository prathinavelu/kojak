from datetime import date
from bs4 import BeautifulSoup
import urllib2
import pickle

story_list = []
base_url = "http://www.newyorker.com/magazine/fiction"
soup = BeautifulSoup( urllib2.urlopen(base_url) )
max_pages = int(soup.find("span", { "id" : "maxPages" }).text)


for a in soup.find("section", {"id" : "in-current-issue" }).findAll("article"):
    dict = {}
    dict['date'] = a.find("time").text
    dict['title'] = a.find('h2').text
    dict['story_url'] = a.find('h2').find('a')['href'] 
    dict['word_count'] = a.find('meta')['content']
    try:
        dict['description'] = a.find('p').text
    except AttributeError:
        dict['description'] = ''
    try:
        dict['author'] = a.find('h3').find("a")['title']
    except AttributeError:
        dict['author'] = ''
    print dict
    print
    story_list.append(dict)


n = 1

while n <= max_pages:
    new_url = "http://www.newyorker.com/magazine/fiction/page/" + str(n)
    new_soup = soup = BeautifulSoup( urllib2.urlopen(new_url) )
    for a in new_soup.find("div", { "class" : "posts" }).findAll("article"):
        dict = {}
        dict['date'] = a.find("time").text
        dict['title'] = a.find('h2').text
        dict['story_url'] = a.find('h2').find('a')['href'] 
        dict['word_count'] = a.find('meta')['content']
        try:
            dict['description'] = a.find('p').text
        except AttributeError:
            dict['description'] = ''
        try:
            dict['author'] = a.find('h3').find("a")['title']
        except AttributeError:
            dict['author'] = ''
        print dict
        print n
        story_list.append(dict)
    n += 1

with open('story_list_new.pkl', 'w') as picklefile:
    pickle.dump(story_list, picklefile)