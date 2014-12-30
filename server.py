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
	if timestampDiff not in range(0,5000): #> 4000:
		dictValues['errno'] = '1'
		print 'sanity check failed with timestamp difference = ' + str(timestampDiff)

def getSleeptime():
	if dictValues['errno'] is '0':
		currentTimestamp = int(time.time())
		iSleepTime = dictValues['timestamp'] + 3600 - currentTimestamp + 60 
		if iSleepTime not in range(0,5000):
			iSleepTime = 60
		sSleepTime = str(iSleepTime)
		sSleepTime = sSleepTime.zfill(4)

	else:
		iSleepTime = ERR_CLIENT_SLEEP_TIME
		sSleepTime = str(iSleepTime)
	return sSleepTime



def OCGthread():
	print 'OCGthread started'
	# global dictValues
	while True:
		try:
			httpResponse = requests.get(OER_URL)
		except Exception, errorhttp:
			print "ERROR: Cant GET the URL"
			print errorhttp
			time.sleep(ERR_SERVERTHREAD_SLEEP_TIME)
			continue
#		print "recieved"
		if httpResponse.status_code == 200:		#if success
			dictValues['errno'] = '0'
			jsonValues = httpResponse.text
			jsonDictValues = json.loads(jsonValues)

			iCurrRate = jsonDictValues['rates']['INR']
			if iCurrRate >= 100: 	#Raise error if currency rate is greater than Rs.100 as the
									#client cannot display values greater than Rs.100
				dictValues['errno'] = '1'
				print "ERROR: Rate is higher than Rs 100."
			iCurrRate = iCurrRate * 100
			sCurrRate = str(iCurrRate)
			dictValues['rate'] = sCurrRate[:4]

			if jsonDictValues['timestamp'] is dictValues['timestamp']:
				time.sleep(60)
				continue
			dictValues['timestamp'] = jsonDictValues['timestamp']
			OERtimestamp = dictValues['timestamp']
			currentTimestamp = int(time.time())
			sleepTime = OERtimestamp + 3600 + 60 - currentTimestamp #Sleep extra 60 seconds
			# if sleepTime not in range(0,4000):
			# 	sleepTime = ERR_SERVERTHREAD_SLEEP_TIME
			# 	print "invalid sleep time value = " + str(sleepTime)

			print "\r\nFetched new values and updated the dictValues[]\r\n"

		else:									#if fails, sleep for 10 sec and retry
			dictValues['errno'] = '1'
			sleepTime = ERR_SERVERTHREAD_SLEEP_TIME
			print "Error in httpResponse statuscode = " + str(httpResponse.status_code)

		try:
			time.sleep(sleepTime)
		except Exception, errstring:
			print errstring
			print "sleeptime = " + str(sleepTime)
			time.sleep(ERR_SERVERTHREAD_SLEEP_TIME)

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




