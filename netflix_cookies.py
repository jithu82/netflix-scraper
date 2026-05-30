import pickle,time
from selenium import webdriver
browser= webdriver.Firefox()
browser.get("https://www.netflix.com/login")
time.sleep(60)
cookies = browser.get_cookies()
with open("netflix_cookies.pkl","wb") as f:
    pickle.dump(cookies,f)
