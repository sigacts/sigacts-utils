#!/usr/bin/env python

import re
import time
import urllib
import urllib2
import sigTools
import cookielib
import email.utils
from lxml import html
from dateutil import parser
from datetime import datetime
from cookielib import CookieJar
from HTMLParser import HTMLParser
from xml.dom.minidom import parseString


def getFeedContent(feedURL):
        urlopen = urllib2.urlopen
        request = urllib2.Request
        cookiejar = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        urllib2.install_opener(opener)

        txdata = None
        txheaders = {'User-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

        req = request(feedURL, txdata, txheaders)

        response = urllib2.urlopen(req)
        feedContent = response.read()

        return feedContent


def parseFeedContent(feedContent):
        dom = parseString(feedContent)
        items = dom.getElementsByTagName("item")
        varTitl = "title"
        varPubd = "pubDate"
        varLink = "link"
        varDesc = "description"

        if len(items) == 0:
                items = dom.getElementsByTagName("entry")
                varTitl = "title"
                varPubd = "published"
                varLink = "link"
                varDesc = "summary"

        eventList = []
        max = len(items)
        for i in range(0,max):

                try:
                        pubTitle = items[i].getElementsByTagName(varTitl)[0].firstChild.wholeText
                        pubTitle = html.fromstring(pubTitle).text
                        pubTitle = pubTitle.encode("utf-8", 'replace')
                        pubTitle = pubTitle.strip()
                except:
                        pubTitle = ""

                if len(pubTitle) > 197:
                        pubTitle = pubTitle[:197]
                        pubTitle = pubTitle = "..."

                try:
                        pubDate = items[i].getElementsByTagName(varPubd)[0].firstChild.nodeValue
                        pubDate = pubDate.encode("utf-8", 'replace')
                except:
                        varPubd = varPubd.lower()
                        pubDate = items[i].getElementsByTagName(varPubd)[0].firstChild.nodeValue
                        pubDate = pubDate.encode("utf-8", 'replace')

                try:
                        pubLink = items[i].getElementsByTagName(varLink)[0].firstChild.nodeValue
                except:
                        pubLink = items[i].getElementsByTagName(varLink)[0].getAttribute("href")

                pubLink = pubLink.encode("utf-8", 'replace')
                pubLink = expandURL(pubLink)
                pubLink = pubLink.split("utm_source")[0]
                linkLen = len(pubLink) - 1
                if pubLink[linkLen:] == "?":
                        pubLink = pubLink[:linkLen]
                
                try:
                        pubDesc = items[i].getElementsByTagName(varDesc)[0].firstChild.wholeText
                except:
                        pubDesc = ""

                pubDesc = pubDesc.encode("utf-8", 'replace')
                pubDesc = pubDesc.replace("&nbsp;", " ")
                pubDesc = pubDesc.replace("&#160;", " ")
                pubDesc = convertEntites(pubDesc)
                pubDesc = remove_html_tags(pubDesc)
                pubDesc = remove_extra_spaces(pubDesc)
                pubDesc = pubDesc.strip()
                pubDesc = paraTruncate(pubDesc)

                cleanDate = cleanFeedDate(pubDate)
                itemList = [cleanDate, pubLink, pubTitle, pubDesc]
                eventList.append(itemList)
                #print cleanFeedDate(pubDate)

        return eventList


def cleanFeedDate(feedDate):

        feedDate = feedDate.replace("  ", " ")

        dateRegEx = re.compile('20\d\d[-/][0-9][0-9][-/][0-9][0-9]')
        matchesList = dateRegEx.findall(feedDate)

        if len(matchesList) > 0:
                timeStruct = "%Y-%m-%d"
                cleanDate = datetime.strptime(matchesList[0], timeStruct)

        matchesList = []
        dateRegEx = re.compile('20\d\d[-/][0-9][0-9][-/][0-9][0-9].[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')
        matchesList = dateRegEx.findall(feedDate)

        if len(matchesList) > 0:
                timeStruct = "%Y-%m-%dT%H:%M:%S"
                cleanDate = datetime.strptime(matchesList[0], timeStruct)


        matchesList = []
        dateRegEx = re.compile('\w\w\w, ([\d]\d|\d) \w\w\w')
        matchesList = dateRegEx.findall(feedDate)

        if len(matchesList) > 0:
                timeStruct = "%a, %d %b %Y %H:%M:%S %Z"
                #dateList = rfc822.parsedate_tz(feedDate)
                dateList = email.utils.parsedate(feedDate)
                epochTime = time.mktime(dateList)
                cleanDate = datetime.fromtimestamp(epochTime)

        matchesList = []
        dateRegEx = re.compile('\w\w\w \w\w\w \d')
        matchesList = dateRegEx.findall(feedDate)

        if len(matchesList) > 0:
                cleanDate = parser.parse(feedDate)

        matchesList = []
        dateRegEx = re.compile('((Mon)|(Tues)|(Wednes)|(Thurs)|(Fri)|(Satur)|(Sun))day')
        matchesList = dateRegEx.findall(feedDate)

        if len(matchesList) > 0:
                timeStruct = "%A, %d %b %Y %H:%M:%S %Z"
                #dateList = rfc822.parsedate_tz(feedDate)
                dateList = email.utils.parsedate(feedDate)
                epochTime = time.mktime(dateList)
                cleanDate = datetime.fromtimestamp(epochTime)

        return cleanDate


def getFeedList():
        Data = ()
        #CMD = "select feedID, feedURL from RSSFeeds order by rand() limit 1"
        #CMD = "select feedID, feedURL from RSSFeeds where lastGrab is NULL order by rand() limit 1"
        #CMD = "select feedID, feedURL from RSSFeeds where feedID = 1"
        CMD = "select feedID, feedURL from RSSFeeds order by lastGrab Asc limit 1"
        resultList = sigTools.dbExecution(CMD, Data)
        
        return resultList[2]


def updateGrabTime(feedID):
        now = datetime.now()
        currentDate = now.strftime("%Y-%m-%d %H:%M:%S")

        Data = (currentDate, feedID)
        CMD = "update RSSFeeds set lastGrab = %s where feedID = %s"
        resultList = sigTools.dbExecution(CMD, Data)

        return resultList


def remove_html_tags(data):
        p = re.compile(r'<.*?>')
        return p.sub(' ', data)


def remove_extra_spaces(data):
        p = re.compile(r'\s+')
        return p.sub(' ', data)


def convertEntites(textContent):
        parser = HTMLParser()
        textContent = textContent.decode('utf-8')
        html_decoded_string = parser.unescape(textContent)
        html_decoded_string = html_decoded_string.encode("utf-8", 'replace')
        return html_decoded_string


def paraTruncate(content, length=300, suffix='...'):
        if len(content) <= length:
                return content
        else:
                return content[:length].rsplit(' ', 1)[0] + suffix


def expandURL(passedURL):
  try:
    resp = urllib.urlopen(passedURL)
    resp.getcode()
    newLink = resp.url
  except:
    newLink = passedURL
  return newLink


def appendEvent(UID, itemDate, itemTitle, itemDesc, itemURL):
        rightNow = datetime.now()
        currentDate = rightNow.strftime("%Y-%m-%d %H:%M:%S")
        DateDated = currentDate
        DateDater = "RSSFeed"
        Origin = "RSS-Feed"
        Status = 'NeedsLoc'
        emptyField = ""
        Data = (UID,
                DateDated,
                itemDate,
                DateDated,
                DateDater,
                itemTitle,
                emptyField,
                itemDesc,
                itemURL,
                Origin,
                Status)
        CMD = "insert into URLs (UID, UDate, DateDate, DateDated, "
        CMD += "DateDater, UTitle, UError, UFirstP, URL, Origin, Status"
        CMD += ") values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        resultList = sigTools.dbExecution(CMD, Data)

        return resultList


def main():
        #feedList = getFeedList()
        feedList = [[0, "http://feeds.reuters.com/Reuters/domesticNews"]]
        
        for item in feedList:
                feedID = item[0]
                feedURL = item[1]
                print feedURL

                feedContent = getFeedContent(feedURL)
                itemList = parseFeedContent(feedContent)

                for link in itemList:
                        itemDate = str(link[0])
                        itemTitle = link[2]
                        itemLink = link[1]
                        itemDesc = link[3]
                        UID = sigTools.newRandomUID()
                        print UID
                        print appendEvent(UID, itemDate, itemTitle, itemDesc, itemLink)

                print "  total items: " + str(len(itemList))


if __name__ == "__main__":
        main()