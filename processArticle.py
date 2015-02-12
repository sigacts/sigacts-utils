#!/usr/bin/env python

import sigTools
import urllib
import urllib2
import datetime
import json
import HTMLParser
import re

import os
filePath = os.path.dirname(os.path.abspath(__file__))


def generateTaskList():
	Data = ("NeedsLoc")
	#CMD = "SELECT UID, URL from URLs WHERE Status like %s ORDER BY UDate DESC LIMIT 20"
	CMD = "SELECT UID, URL from URLs WHERE Status like %s and USource in (select siteSource from sourceLocales) ORDER BY UDate DESC LIMIT 60"
	resultList = sigTools.dbExecution(CMD, Data)

	return resultList


def grabReadbility(pageURL):
	apiToken = "{{API_KEY}}"
	apiURL = "https://www.readability.com/api/content/v1/parser?url="
	pageURL = pageURL.replace("&amp;","&")
	pageURL = urllib.quote_plus(pageURL)
	requestURL = apiURL + pageURL + "&token=" + apiToken

	pageRequest = urllib2.Request(requestURL)
	pageContent = urllib2.urlopen(pageRequest).read()

	return pageContent


def lookupWOEID(pageURL):
	polishedSrc = sigTools.getSource(pageURL)

	print "   " + polishedSrc

	Data = (polishedSrc)
	CMD = "select siteWOEID, siteLat, siteLon from sourceLocales where siteSource = %s"
	resultList = sigTools.dbExecution(CMD, Data)

	return resultList


def runGeocode(pageURL, rawContent):
	resultList = lookupWOEID(pageURL)
	focusWOEID = resultList[2][0][0]
	siteLat = resultList[2][0][1]
	siteLon = resultList[2][0][2]

	try:
		testFocus = int(focusWOEID)
	except:
		print "No WOEID - Quitting ..."
		sys.exit(0)

	pageParams = {	'appid': '{{API_KEY}}',
					'documentContent': rawContent,
					'documentType': 'text/plain',
					'outputType': 'json',
					'focusWoeId': focusWOEID}

	requestData = urllib.urlencode(pageParams)
	requestURL = "http://wherein.yahooapis.com/v1/document"

	pageRequest = urllib2.Request(requestURL, requestData)
	geoResponse = urllib2.urlopen(pageRequest).read()

	return geoResponse, siteLat, siteLon


def remove_html_tags(data):
	p = re.compile(r'<.*?>')
	return p.sub(' ', data)


def remove_extra_spaces(data):
	p = re.compile(r'\s+')
	return p.sub(' ', data)


def prepareArticleContent(readResponse):
	data = json.loads(readResponse)
	pageHeadline = data['title']
	pageHeadline = pageHeadline.encode("utf-8", 'ignore')

	pageExcerpt = data['excerpt']
	pageContent = data['content']

	h = HTMLParser.HTMLParser()
	pageContent = h.unescape(pageContent)
	pageContent = pageContent.replace("\n"," ")
	pageContent = pageContent.replace("\r"," ")
	pageContent = pageContent.replace("\t"," ")
	pageContent = pageContent.encode("utf-8", 'ignore')
	pageContent = remove_html_tags(pageContent)
	pageContent = remove_extra_spaces(pageContent)
	pageContent = pageContent.strip()

	rawContent = pageHeadline + " " + pageContent
	rawContent = urllib.quote_plus(rawContent)
	rawContent = rawContent[:50000]
	
	articleDetails = [pageHeadline, pageExcerpt, pageContent, rawContent]
	
	return articleDetails


def dropOldLocations(UID):
	Data = (UID)
	CMD = "delete from Locations where UID = %s"
	resultList = sigTools.dbExecution(CMD, Data)
	
	return resultList


def dropOldResponses(UID):
	Data = (UID)
	CMD = "delete from apiResponses where UID = %s"
	resultList = sigTools.dbExecution(CMD, Data)
	
	return resultList


def getDate():
	now = datetime.datetime.now()
	currentDate = now.strftime("%Y-%m-%d %H:%M:%S")

	return currentDate


def extractLocation(geoResponse):
	myJSON = json.loads(geoResponse)

	try:
		scopeCount = len(myJSON['document']['localScopes'])

		if scopeCount > 1:
			scopeCount = scopeCount - 1
			placeLat = myJSON['document']['localScopes'][scopeCount]['localScope']['centroid']['latitude']
			placeLon = myJSON['document']['localScopes'][scopeCount]['localScope']['centroid']['longitude']
		else:
			placeLat = myJSON['document']['localScopes']['localScope']['centroid']['latitude']
			placeLon = myJSON['document']['localScopes']['localScope']['centroid']['longitude']
		exactness = 1
	except:
		placeLat = siteLat
		placeLon = siteLon
		exactness = 0

	locationList = [placeLat, placeLon, exactness]

	return locationList


def updateLocation(UID, placeLat, placeLon, exactness):
	currentDate = getDate()

	nullVal = "Unassigned"
	emptyVal = ""
	Data = (UID, placeLat, placeLon, exactness, 'modWorkYHOO', currentDate, nullVal, emptyVal, nullVal)
	CMD = "insert into Locations values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
	resultList = sigTools.dbExecution(CMD, Data)
	
	return resultList


def updateStatus(UID, Status):
	Data = (Status, UID)
	CMD = "update URLs set Status = %s where UID = %s"
	resultList = sigTools.dbExecution(CMD, Data)
	
	return resultList


def main():

	resultList = generateTaskList()
	taskList = resultList[2]

	for item in taskList:

		try:
			UID = item[0]
			pageURL = item[1]

			print UID
			print "   " + pageURL

			resultList = dropOldResponses(UID)
			print "   " + str(resultList)

			pageURL = pageURL.decode('us-ascii', 'ignore')

			readResponse = grabReadbility(pageURL)
			readResponse = readResponse.decode('us-ascii', 'ignore')

			articleDetails = prepareArticleContent(readResponse)

			pageHeadline = articleDetails[0]
			pageExcerpt = articleDetails[1]
			pageContent = articleDetails[2]
			rawContent = articleDetails[3]

			try:
				geoResponse, siteLat, siteLon = runGeocode(pageURL, rawContent)
			
				locationList = extractLocation(geoResponse)

				placeLat = locationList[0]
				placeLon = locationList[1]
				exactness = locationList[2]

				print "   " + str(placeLat) + ", " + str(placeLon)

				resultList = dropOldLocations(UID)
				print "   " + str(resultList)

				resultList = updateLocation(UID, placeLat, placeLon, exactness)
				print "   " + str(resultList)

				nullVal = None
				resultList = updateStatus(UID, nullVal)
				print "   " + str(resultList)

			except:
				print "   Location Error"
				errorVal = 'LocationError'
				resultList = updateStatus(UID, errorVal)
				print "   " + str(resultList)
				geoResponse = None

			currentDate = getDate()
			Data = (UID, pageURL, readResponse, pageContent, geoResponse, currentDate)
			CMD = "INSERT INTO apiResponses VALUES (%s, %s, %s, %s, %s, %s)"
			resultList = sigTools.dbExecution(CMD, Data)
			print "   " + str(resultList)

		except urllib2.HTTPError, e:
			errorMsg = "ErrorErrorError" + str(e.code)
			Data = (errorMsg, UID)
			CMD = "UPDATE URLs SET Status = %s WHERE UID = %s"
			resultList = sigTools.dbExecution(CMD, Data)
			print "   " + str(resultList)
			print "   HTTPError = " + str(e.code)


	taskCount = len(taskList)
	print "\ncompleted " + str(taskCount) + " tasks"


if __name__ == "__main__":
	main()