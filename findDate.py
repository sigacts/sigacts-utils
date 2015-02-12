#!/usr/bin/env python

import sigTools
import re
import datetime
import urllib2


def generateTaskList():
	Data = ()
	CMD = "SELECT URLs.UID, URLs.URL FROM URLs WHERE URLs.DateDate LIKE '0000-00-00 00:00:00'"
	resultList = sigTools.dbExecution(CMD, Data)

	return resultList


def parseSameSymbols(matchesList):
	cleanList = []

	for item in matchesList:

		workingDate = matchesList[0].split("/")

		if len(workingDate) < 3:
			workingDate = matchesList[0].split("-")

		if len(workingDate) == 3:
			year = workingDate[0]
			month = str(workingDate[1])
			day = str(workingDate[2])
	
			stringDate = str(year) + "-" + str(month) + "-" + str(day) + " 00:00:00"
			cleanList.append(stringDate)

	return cleanList


def parseNoSymbols(matchesList):
	cleanList = []
	for item in matchesList:
		testYear = item[:4]

		now = datetime.datetime.now()
		currentYear = now.strftime("%Y")
		if int(testYear) < (int(currentYear) + 1):
			if int(testYear) > 1990:
				testYear = str(testYear)
				testMon = str(item[4:][:2])
				testDay = str(item[6:])
				time = " 00:00:00"
				stringDate = testYear + "-" + testMon + "-" + testDay + time
				cleanList.append(stringDate)

	return cleanList


def validateDate(dateList):
	cleanList = []

	for item in dateList:
		try:
			finalDate = datetime.datetime.strptime(item, '%Y-%m-%d %H:%M:%S')
			finalDate = str(finalDate)
		 	cleanList.append(finalDate)
		except:
			pass

	return cleanList


def findDateInURL(pageURL):

	dateRegEx = re.compile('\d{4}[/]\d{2}[/]\d{2}')
	matchesList = dateRegEx.findall(pageURL)
	dateList = []
	cleanList = []

	if len(matchesList) > 0:
		dateList = parseSameSymbols(matchesList)
		if len(dateList) > 0:
			cleanList = validateDate(dateList)

	else:
		dateRegEx = re.compile('\d{4}\d{2}\d{2}')
		matchesList = dateRegEx.findall(pageURL)
		if len(matchesList) > 0:
			dateList = parseNoSymbols(matchesList)
			cleanList = validateDate(dateList)
	return cleanList


def main():

	resultList = generateTaskList()
	
	for item in resultList[2]:
		cleanDateList = []
		UID = item[0]
		pageURL = item[1]
		pageURL = pageURL.replace("&amp;","&")

		cleanDateList = findDateInURL(pageURL)
		if len(cleanDateList) > 0:
			print UID + " :: " + pageURL
			print "  " + str(cleanDateList)
			finalDate = cleanDateList[0]

			try:
				now = datetime.datetime.now()
				currentDate = now.strftime("%Y-%m-%d %H:%M:%S")
				Data = (finalDate, 'Bot-URL', currentDate, UID)
				CMD = "UPDATE URLs SET DateDate = %s, DateDater = %s, DateDated = %s WHERE UID = %s"
				#print (CMD, Data)
				resultList = sigTools.dbExecution(CMD, Data)
				print "  " + str(resultList)
			except:
				print "Bad Entry -- " + UID


if __name__ == "__main__":
	main()
