#!/usr/bin/env python

#Example Error
#{u'errorCode': 500, u'error': u'Could not download page (403)'}

import urllib
import urllib2
import json
from datetime import datetime
import sys
sys.path.append('/usr/home/sigacts')
import sigTools


def buildList():
        nullVal = None
        Data = ("0000-00-00%", nullVal)
        CMD = "select UID, URL from URLs where DateDate like %s and Status is %s limit 8"
        resultList = sigTools.dbExecution(CMD, Data)

        return resultList[2]


def grabContent(pageURL):
        apiToken = "{{API_KEY}}"
        apiURL = "http://api.diffbot.com/v2/article?url="
        pageURL = pageURL.replace("&amp;","&")
        pageURL = urllib.quote_plus(pageURL)
        requestURL = apiURL + pageURL + "&token=" + apiToken

        pageRequest = urllib2.Request(requestURL)
        pageContent = urllib2.urlopen(pageRequest).read()

        return pageContent


def updateEntry(finalDate, UID):
        now = datetime.now()
        currentDate = now.strftime("%Y-%m-%d %H:%M:%S")

        Data = (finalDate, 'diffBot', currentDate, UID)
        CMD = "UPDATE URLs SET DateDate = %s, DateDater = %s, DateDated = %s WHERE UID = %s"
        resultList = sigTools.dbExecution(CMD, Data)

        return resultList


def main():
        pageURL = "http://www.thedailytimes.com/news/second-suspect-arrested-in-weekend-richy-kreme-robbery/article_2a3ef1fa-c5c3-11e3-a2cb-001a4bcf887a.html"
        #readResponse = grabContent(pageURL)
        #data = json.loads(readResponse)
        #print data

        resultList = buildList()

        for item in resultList:
                UID = item[0]
                pageURL = item[1]
                print UID

                try:
                        readResponse = grabContent(pageURL)
                        data = json.loads(readResponse)
                        pageDate = data['date']
                        finalDate = datetime.strptime(pageDate, "%a, %d %b %Y %H:%M:%S %Z")
                        resultList = updateEntry(finalDate, UID)
                        print "      " + str(finalDate)
                        print "      " + str(resultList)
                except:
                        errorMsg = "NeedHumanWork"
                        Data = (errorMsg, UID)
                        CMD = "UPDATE URLs SET Status = %s WHERE UID = %s"
                        resultList = sigTools.dbExecution(CMD, Data)
                        print "      Error: " + str(resultList)


if __name__ == "__main__":
        main()