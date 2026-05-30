from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains as ac
from selenium.webdriver.common.keys import Keys

import csv,pickle,unicodedata
import openpyxl as xl,re,time

import smtplib,os,csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
file_path = "series.csv"
if os.path.exists(file_path):
    os.remove(file_path)
file_path = "films.csv"
if os.path.exists(file_path):
    os.remove(file_path)
file_path = "netflix_backlog.xlsx"
if os.path.exists(file_path):
    os.remove(file_path)
try :
    
    browser = webdriver.Firefox()
    browser.get("https://www.netflix.com")
    wait = WebDriverWait(browser,10)
    action = ac(browser)
    with open("netflix_cookies.pkl","rb") as f:
        cookies = pickle.load(f)
    for cookie in cookies :
        if "sameSite" in cookie :
            cookie.pop("sameSite")
        browser.add_cookie(cookie)
    browser.refresh()
    profiles = WebDriverWait(browser,60).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR,'li.profile')))
    profileDict = {}
    for profile in profiles:
        nameelement = profile.find_element(By.CLASS_NAME,"profile-name")
        name  = nameelement.text
        profileDict[name] = profile
    profile = profileDict["M.J"]
    profile.click()
    #time.sleep(1)
    alltitles = []
    for j in range(4):
        #contents = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR,"#row-2 > div > div > div > div > div > div.slider-item.slider-item-0")))
        time.sleep(4)
        contents = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR,"#row-2 > div > div > div > div > div > div.slider-item")))
        for content in contents :
            print(content.get_attribute("class"))
        print(len(contents))
        filtered_content = [content for content in contents if re.search(r"slider-item-\d+",content.get_attribute("class"))]
        print(len(filtered_content))
        for content in filtered_content :
            print(content.get_attribute("class"))

        for content in filtered_content:
            title_elem = content.find_element(By.CSS_SELECTOR,"div.title-card > div > a.slider-refocus")
            title = title_elem.get_attribute("aria-label")
            if title not in alltitles :
                alltitles.append(title)
            else:
                continue
            print("scraping data of ")
            print(title)
            card = WebDriverWait(content,10).until(ec.presence_of_element_located((By.CSS_SELECTOR,"div.title-card")))
            time.sleep(1)
            browser.execute_script("arguments[0].scrollIntoView({block:'center'});",card)
            time.sleep(1)
            action.move_to_element(card).pause(1).move_by_offset(1, 1).perform()
            time.sleep(1)
            #browser.execute_script(By.XPATH,'//*[@id="appMountPoint"]/div/div/div/div/div[1]/div[2]/div/div[3]/a/div/div/div/div/div[1]/div[4]/button'))
            more = WebDriverWait(browser,10).until(ec.presence_of_element_located((By.CSS_SELECTOR,'#appMountPoint > div > div > div > div > div:nth-child(2) > div.focus-trap-wrapper.previewModal--wrapper.mini-modal > div > div.previewModal--info > a > div > div > div > div > div.buttonControls--container.has-smaller-buttons.mini-modal > div.buttonControls--expand-button.default-ltr-iqcdef-cache-bjn8wh > button')))
            browser.execute_script("arguments[0].click();",more)
            wait.until(ec.presence_of_element_located((By.CLASS_NAME,"detail-modal-container")))
            episodeSelector = browser.find_elements(By.CLASS_NAME,"episodeSelector")
            if len(episodeSelector)>0:
                try:
                    current_elem = wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME,"allEpisodeSelector-season-label")))
                except Exception:
                    current_elem = []
                if len(current_elem) > 0 :
                    current_season = wait.until(ec.presence_of_element_located((By.CLASS_NAME,"allEpisodeSelector-season-label"))).text[0:-1]
                else :
                    current_season = "1"
                print(current_season)
                
                current_season_elem = re.findall(r"\d+",current_season)
                if len(current_season_elem) > 0:
                    current_season_num = int(current_season_elem[0])
                else :
                    current_season_num = int(unicodedata.numeric(current_season[-1])) if current_season[-1].isnumeric() else 1
                
                seasons = {}
                dropdown_elem = browser.find_elements(By.CSS_SELECTOR,"div.episodeSelector-dropdown>div>button")
                if len(dropdown_elem) > 0:
                    dropbox = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,"div.episodeSelector-dropdown>div>button")))
                    dropbox.click()
                    dropbox_elements = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR,"div.episodeSelector-dropdown>div ul>li>div")))
                    for element in dropbox_elements:
                        season , episodes = element.text.split("\n")
                        print(season,episodes)
                        if not re.search(r'\d+', season):
                            print(season)
                            season = season.strip()
                            season = season[:-1]+ str(int(unicodedata.numeric(season[-1]))) if season[-1].isnumeric() else ' 1'
                        num , stg = episodes.split(" ")
                        seasons[season.strip()[-1]] = int(num[1:])
                    print(f"seasons  dict {seasons}")
                else :
                    seasons["1"] = -1
                progress_elements = wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME,"titleCard-progress")))
                watched_episodes = []
                for progress_element in progress_elements:
                    progress = float(progress_element.get_attribute("value"))
                    watched_episodes.append(progress)
                for value in watched_episodes:
                    if value < 0.5 :
                        watched_episodes.remove(value)
                episodes_left = {}
                i = current_season_num 
                print(i)
                data = []
                while(i<=len(seasons)):
                    if i == current_season_num:
                        episodes_left[f"Season{i}"] = seasons[str(i)] - len(watched_episodes)
                        data.append([title,f"Season {i}",episodes_left[f"Season{i}"]])
                    else:
                        episodes_left[f"Season{i}"] = seasons[str(i)] 
                        data.append([title,f"Season {i}",f"{episodes_left[f'Season{i}']} left"])
                    i +=1
                print(episodes_left)
                
                with open("series.csv","a",newline="",encoding="utf-8") as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerows(data)
            else :
                summary = wait.until(ec.presence_of_element_located((By.CLASS_NAME,"summary"))).text
                listofnumbers = re.findall(r"\d+",summary)
                if len(listofnumbers) > 1:
                    time_left = f"{int(listofnumbers[1]) - int(listofnumbers[0])}minutes Left"
                else :
                    time_left = f"{int(listofnumbers[0])}minutes Left"
                print(time_left)
                data = [title,time_left]
                with open("films.csv","a",newline="",encoding="utf-8") as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerow(data)
            browser.find_element(By.TAG_NAME,"body").send_keys(Keys.ESCAPE)

            
        time.sleep(2)

        handles = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "#row-2>div>div>div span.handle>b")))
        print(handles)
        right_arrow_area = handles[-1]
        time.sleep(2)
        browser.execute_script("arguments[0].scrollIntoView({block:'center',inline:'center'});",right_arrow_area)
        browser.execute_script("arguments[0].click();",right_arrow_area)
        time.sleep(2)


except Exception :
    print("an exception has occured it is %s"%(Exception))

#finally: 
    #browser.quit()

wb = xl.Workbook()
sheet = wb.active
sheet.title = "Everythin in Continue watching of Maple "
sheet["A1"] = "TITLE"
sheet["B1"] = "Episodes or minutes left"
sheet.merge_cells("B1:C1")

with open("films.csv","r",encoding="utf-8") as file :
    rows = csv.reader(file)
    for j,row in enumerate(rows):
        movie_title = row[0]
        minutes_left = row[1]
        sheet["A"+str(j+2)] = movie_title
        sheet["B"+str(j+2)] = minutes_left
        sheet.merge_cells(f"{'B'+str(j+2)}:{'C'+str(j+2)}")
    j+=2
with open("series.csv","r",encoding="utf-8") as file :
    rows = csv.reader(file)
    for row in rows:
        
        sheet["A"+str(j+1)] = row[0]
        sheet["B"+str(j+1)] = row[1]
        sheet["C"+str(j+1)] = row[2]
        j+=1
sheet.column_dimensions["A"].width = 30
sheet.column_dimensions["C"].width = 30
sheet.column_dimensions["B"].width = 30
sheet.freeze_panes = "D2"
wb.save("netflix_backlog.xlsx")
