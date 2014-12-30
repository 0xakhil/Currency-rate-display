import json
import httplib
import datetime
import time
import requests
from threading import Thread
import os
from bottle import route, run


OER_URL = "http://www.openexchangerates.org/api/latest.json?app_id=1e76263ca43b439ea182746c19baaab5"

#Initialize dictValues with errno = 1 and sleeptime = 30
dictValues = {'magic_no':'aaf6','errno':'1','rate':'0000','timestamp':0}

#Values
ERR_SERVERTHREAD_SLEEP_TIME = 5
ERR_CLIENT_SLEEP_TIME = 30 #sleeptime value to send to the client in case of error


def checkSanity():
	currentTimestamp = int(time.time())
	timestampDiff = currentTimestamp - dictValues['timestamp']
	if timestampDiff > 4000:
		dictValues['errno'] = '1'
		print 'sanity check failed with timestamp difference = ' + str(timestampDiff)

def getSleeptime():
	if errono is '0':
		currentTimestamp = int(time.time())
		iSleepTime = OERtimestamp + 3600 - currentTimestamp + 60 
		sSleepTime = str(iSleepTime)
	else:
		iSleepTime = ERR_CLIENT_SLEEP_TIME
		sSleepTime = str(iSleepTime)
	return sSleepTime



def OCGthread():
	# print 'OCGthread started'
	# global dictValues
	while True:
		httpResponse = requests.get(OER_URL)
		print "recieved"
		if httpResponse.status_code == 200:		#if success
			dictValues['errno'] = '0'
			jsonValues = httpResponse.text
			jsonDictValues = json.loads(jsonValues)

			currRate = jsonDictValues['rates']['INR']
			currRate = currRate * 100
			currRate = str(currRate)
			dictValues['rate'] = currRate[:4]

			dictValues['timestamp'] = jsonDictValues['timestamp']
			OERtimestamp = dictValues['timestamp']
			currentTimestamp = int(time.time())
			sleepTime = OERtimestamp + 3600 + 60 - currentTimestamp #Sleep extra 60 seconds

		else:									#if fails, sleep for 10 sec and retry
			dictValues['errno'] = '1'
			sleepTime = ERR_SERVERTHREAD_SLEEP_TIME
			print "Error in httpResponse statuscode = " + str(httpResponse.status_code)

		# temp = str(sleepTime + 30)		#wait extra 30 seconds
		# dictValues['sleeptime'] = temp.zfill(4)

		time.sleep(sleepTime)
		# break

@route("/")
def hello_world():
	return "Hi :)"

@route("/inr")
def inr_function():
	checkSanity()

	sOutputString = dictValues['magic_no'] + dictValues['errno'] + dictValues['rate'] + getSleeptime()
	# print outputString
	return sOutputString


if __name__ == "__main__":

	try:
		t = Thread(None,OCGthread,None,())
		t.start()
	
	except Exception, errtxt:
		print "ERROR starting OCGthread\n"
		print errtxt

	# print dictValues
	# while True:
	# 	PASS

	run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))




