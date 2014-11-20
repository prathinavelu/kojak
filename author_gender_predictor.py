from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import time
from pymongo import MongoClient
import datetime
import pickle
from genderPredictor import genderPredictor
from zipfile import ZipFile
import csv
import os


def classify_gender_list(list, lookup_names, classifier):
    d = dict()
    for author in list:
        author_dict = dict()
        firstname = author[:author.find(' ')].replace('.','')
        author_dict['wiki'] = search_wiki(author)
        if len(firstname) > 1:
            author_dict['gender1'] = classify_gender(firstname,classifier)
        else:
            author_dict['gender1'] = ''
        d[author] = author_dict    
    return d
    
    
def classify_gender(n, classifier_func):       
    if n.upper() in names.keys():
        c = names[n.upper()]
        if c[0] > c[1]:
            return 'M'
        else:
            return 'W'       
    else:
        return classifier_func(n)
        
            
    
def get_author(story_url):
    newurl = str(story_url)
    mydriver.get(newurl)
    try:
        parentElement = WebDriverWait(mydriver, 10).until(
            EC.presence_of_element_located((By.ID,"masthead"))
    )
    except TimeoutException:
        print 'timeout!'
        return ''    
    h = parentElement.text
    #head = parentElement.find_elements_by_tag_name("h3")
    if h.find('BY') > 0:
        txt = h[h.find('BY')+3:]
    else:
        txt = ''
    if txt != '':
        print txt
    else:
        print 'nothing!'
    return txt
    
def search_wiki(name):
    txt = ''
    if name == '':
        return {'text': '', 'gender': ''}
    newurl = 'http://en.wikipedia.org/wiki/Main_Page'
    mydriver.get(newurl)
    search_form = mydriver.find_element_by_id('searchInput')
    search_form.send_keys(name)
    search_form.send_keys(Keys.RETURN)
    try:
        parentElement = WebDriverWait(mydriver, 10).until(
            EC.presence_of_element_located((By.ID,"mw-content-text"))
    )
    except TimeoutException:
        print 'wiki timeout!'
        return ''    
    elementList = parentElement.find_elements_by_tag_name("p")
    for element in elementList:
        txt = txt + ' ' + element.text 
    if txt.count(' he ')+txt.count(' his ') > txt.count(' she ')+txt.count(' her '):
        g = 'M'
    else:
        g = 'F'
    print txt
    return {'text': txt, 'gender':g}
    
    
if __name__ == '__main__':

    with open('story_list.pkl','rb') as infile:
        slist = pickle.load(infile)
        
    client=MongoClient()
    stories_other =client.dsbc.newyorker_other
    
    zf=ZipFile('names.zip', 'r')
    filenames=zf.namelist()
    names=dict()
    genderMap={'M':0,'F':1}
    for filename in filenames:
        file=zf.open(filename,'r')
        rows=csv.reader(file, delimiter=',')        
        for row in rows:
            name=row[0].upper()
            gender=genderMap[row[1]]
            count=int(row[2])
            
            if not names.has_key(name):
                names[name]=[0,0]
            names[name][gender]=names[name][gender]+count
        file.close()

    gp = genderPredictor()
    gp.trainAndTest()
    
    mydriver =webdriver.Chrome('/Users/Praveen/chromedriver')
    mydriver.implicitly_wait(10)
    
    if not os.path.exists('full_story_list.pkl'):
        new_list = []
        for s in slist:
            s_new = s
            if s_new['author'] == '' and int(s_new['date'][s_new['date'].rfind(' ')+1:]) >2000:
                s_new['author'] = get_author(s_new['story_url'])
            new_list.append(s_new)
        
        with open('full_story_list.pkl', 'w') as picklefile:
            pickle.dump(new_list, picklefile)
    else:
        with open('full_story_list.pkl','rb') as infile:
            new_list = pickle.load(infile)
        
        
    name_list = list(set([x['author'] for x in new_list]))
    
    detailed_name_dict = classify_gender_list(name_list, names, gp.classify)
    
    for s in new_list:
        s_new = s
        author = s_new['author']
        d =detailed_name_dict[author]
        s_new['gender1'] = d['gender1']
        s_new['wiki'] = d['wiki']
        print s_new['title']
        print s_new['author']
        print s_new['gender1']
        print s_new['wiki']['gender']
        print
        stories_other.insert(s_new)

        
        
        
        
        
        
        
        
        
        
        
        