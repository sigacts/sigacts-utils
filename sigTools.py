#!/usr/bin/env python

import MySQLdb
MySQLdb.escape_string("'")
from urlparse import urlparse

def dbExecution(CMD, Data):
	connection = MySQLdb.connect (	host = "{{DB_URL}}",
									user = "{{USERNAME}}",
									passwd = "{{PASSWORD}}",
									db = "{{DB_NAME}}")
	cursor = connection.cursor()    
	cmdExecution = cursor.execute(CMD, Data)
	numResults = cursor.rowcount
	resultRows = cursor.fetchall()
	cursor.close()
	connection.close()
	resultList = [cmdExecution, numResults, resultRows]
	return resultList


def getSource(fullURL):
	workingSrc = urlparse(fullURL)
	polishedSrc = workingSrc[1]
	if workingSrc[1].startswith("www."):
		polishedSrc = workingSrc[1][len("www."):]

	flagURL = "abclocal.go.com"
	if flagURL in polishedSrc:
		fullURL = fullURL.replace("http://","")
		fullURL = fullURL.replace("https://","")
		stationID = fullURL.split("/")[1]
		polishedSrc = polishedSrc + "/" + stationID

	flagURL = "bizjournals.com"
	if flagURL in polishedSrc:
		fullURL = fullURL.replace("http://","")
		fullURL = fullURL.replace("https://","")
		stationID = fullURL.split("/")[1]
		polishedSrc = polishedSrc + "/" + stationID

	flagURL = "jrn.com"
	if flagURL in polishedSrc:
		fullURL = fullURL.replace("http://","")
		fullURL = fullURL.replace("https://","")
		stationID = fullURL.split("/")[1]
		if stationID == "now-trending":
			polishedSrc = polishedSrc
		else:
			polishedSrc = polishedSrc + "/" + stationID


	if ":" in polishedSrc:
		polishedSrc = polishedSrc.split(":")[0]

	return polishedSrc


def generateOneUID():
	import string
	import random

	size = 8
	chars = string.ascii_uppercase + string.digits
	
	newKey = ""
	for x in range(size):
		randChar = random.choice(chars)
		newKey = newKey + randChar

	return newKey


def newRandomUID():
	finished = "false"
	while finished != "true":
		randomKey = generateOneUID()

		Data = (randomKey)
		CMD = "SELECT UID FROM URLs WHERE UID = %s"
		resultList = dbExecution(CMD, Data)

		if (resultList[0] == 0):
			finished = "true"
		else:
			finished = "false"
	return randomKey


def trunc(s, min_pos = 0, max_pos = 75, ellipsis = True):
    NOT_FOUND = -1

    ERR_MAXMIN = 'Minimum position cannot be greater than maximum position'
    
    if max_pos < min_pos:
        raise ValueError(ERR_MAXMIN)

    if ellipsis:
        suffix = '...'
    else:
        suffix = ''

    length = len(s)
    if length <= max_pos:
        return s + suffix
    else:
        try:
            end = s.rindex('.',min_pos,max_pos)
        except ValueError:
            end = s.rfind(' ',min_pos,max_pos)
            if end == NOT_FOUND:
                end = max_pos
        return s[0:end] + suffix


def main():
	pass


if __name__ == "__main__":
        main()