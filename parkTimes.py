#!/usr/bin/python

import mariadb
import sys
import datetime
from twython import Twython
#import twitter keys from separate py file
from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
#import dbinfo from separate py file
from dbinfo import *
#connecting to parks db
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
#Set current hour and day
time = datetime.datetime.now()
today = int(time.strftime("%d"))
hour = int(time.strftime("%H"))
#Setting empty string for parks
parksOpen = []
parksClosed = []
cur = conn.cursor()
sendTweet = False
#Checking park hours DB
cur.execute("SELECT p.park_name, h.open_time, h.close_time, h.day FROM parks p RIGHT JOIN hours h on p.park_id = h.park_id;")
for (park_name, open_time, close_time, day) in cur:
    openT = int(open_time)
    closeT = int(close_time)
    closeT += 12
    if openT == hour and day == today:
        parksOpen.append(park_name)
        sendTweet = True
    if closeT == hour and day == today:
        parksClosed.append(park_name)
        sendTweet = True
#Send Tweet if flag is set to true
parksOpenlist = ""
parksClosedlist = ""
if sendTweet == True:
    #Open Twitter connection
    twitter = Twython(
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret
    )
    #Check if there is more than one park in the  open and closed lists, then send twitter update
    if len(parksOpen) > 1:
        for x in range(len(parksOpen)):
            if x == len(parksOpen)-1:
                parksOpenlist = parksOpenlist + "and " + parksOpen[x]
            elif x < len(parksOpen):
                parksOpenlist = parksOpenlist + parksOpen[x] + ", "
        parksOpenlist = parksOpenlist + " have opened for today!"
        twitter.update_status(status=parksOpenlist)
    elif len(parksOpen) == 1:
        parksOpenlist = parksOpen[0] + " has opened for today!"
        twitter.update_status(status=parksOpenlist)
    if len(parksClosed) > 1:
        for x in range(len(parksClosed)):
            if x == len(parksClosed)-1:
                parksClosedlist = parksClosedlist + "and " + parksClosed[x]
            elif x < len(parksClosed):
                parksClosedlist = parksClosedlist + parksClosed[x] + ", "
        parksClosedlist = parksClosedlist + " have closed for today!"
        twitter.update_status(status=parksClosedlist)
    elif len(parksClosed) == 1:
        parksClosedlist = parksClosed[0] + " has closed for today!"
        twitter.update_status(status=parksClosedlist)
elif sendTweet == False:
    print("No openings/closings at this time")