from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from calendar import monthrange
import re
import datetime
import mariadb
import sys
from dbinfo import *

#connect to db
try:
    conn = mariadb.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
    
cur = conn.cursor()
#Clears the hours table
cur.execute("TRUNCATE hours;")
#Set the date variables and regex
date = datetime.datetime.now()
currMonthDays=monthrange(int(date.strftime("%Y")), int(date.strftime("%m")))
timeRegex = re.compile(r'\d?\d:\d\d')
hourRegex = re.compile(r'^\d?\d')
i = int(date.strftime("%d"))
id = 1
#Set up webscraper config and scrape web page into BS
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
driver.get("https://disneyworld.disney.go.com/calendars/month/" + date.strftime("%Y") + "-" + date.strftime("%m") + "-" + date.strftime("%d")+"/")
parks = ['magic-kingdom', 'epcot', 'hollywood-studios', 'animal-kingdom']
content = driver.page_source
soup = BeautifulSoup(content)
#loop through the source code and grab the hours, then inserts the hours into the database for each park
while i <= currMonthDays[1]:
    parkIterator = 0
    while parkIterator < len(parks):
        header = date.strftime("%B") + str(i) + " " + parks[parkIterator]
        header=header.lower()
        print(header)
        parkHours=soup.find("div", headers=header).find("div", class_="parkHours").find('p')
        parkHours=timeRegex.findall(str(parkHours))
        openTimeHour=hourRegex.search(parkHours[0])
        closeTimeHour=hourRegex.search(parkHours[1])
        print(str(closeTimeHour.group()))
        parkIterator += 1
        cur.execute("INSERT INTO hours (hourID, day, open_time, close_time, park_id) VALUES (" + str(id) + ", " + str(i) + ", " + str(openTimeHour.group()) + ", " + str(closeTimeHour.group()) + ", " + str(parkIterator) + " );")
        id += 1
        #print("open: " + str(openTimeHour.group()) + " close: " + str(closeTimeHour.group()) + " park: " + str(parkIterator))
    i += 1
    print("Finished inserting " + date.strftime("%m") + "/" + str(i))
conn.commit()
conn.close()
