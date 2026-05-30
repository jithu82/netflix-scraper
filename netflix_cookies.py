import pickle,time
from pathlib import Path


def manual_cookies(browser):
    print("manually login")
    time.sleep(60)
    cookies = browser.get_cookies()
    with open("netflix_cookies.pkl","wb") as f:
        pickle.dump(cookies,f)

def load_cookies(browser):
    path = Path("C:/vs code/python files/netflix scraper/netflix_cookies.pkl")
    if not path.exists() :
        manual_cookies(browser)
        
    with open("netflix_cookies.pkl","rb") as f:
        cookies = pickle.load(f)
    for cookie in cookies :
        if "sameSite" in cookie :
            cookie.pop("sameSite")
        browser.add_cookie(cookie)
    browser.refresh()