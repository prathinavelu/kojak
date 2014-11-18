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


with open('story_list.pkl','rb') as infile:
    story_list = pickle.load(infile)
    
client=MongoClient()
stories=client.dsbc.newyorker

baseurl = str(story_list[0]['story_url'])
username = "praveen.rt@gmail.com"
password = "617prav"
mydriver =webdriver.Chrome('/Users/Praveen/chromedriver')
mydriver.get(baseurl)

time.sleep(3)

send_button = mydriver.find_element_by_id("sign-in")
send_button.click()
login_form = mydriver.find_element_by_id('username')
login_form.send_keys(username)
password_form=mydriver.find_element_by_id('userpass')
password_form.send_keys(password)
remember_button = mydriver.find_element_by_class_name("rememberTxt-screen")
remember_button.click()
signin_button = mydriver.find_element_by_id("signIn")
signin_button.click()

time.sleep(1)

    
for s in story_list:
    d = s
    txt = ''
    if int(d['date'][-4:]) < 2001:
        break
    newurl = str(d['story_url'])
    mydriver.get(newurl)
    try:
        parentElement = WebDriverWait(mydriver, 10).until(
            EC.presence_of_element_located((By.ID,"articleBody"))
    )
    except TimeoutException:
        continue    
    elementList = parentElement.find_elements_by_tag_name("p")
    for element in elementList:
        txt = txt + ' ' + element.text
    d['text'] = txt
    stories.insert(d)