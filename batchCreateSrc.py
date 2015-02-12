#!/usr/bin/env python

import sigTools

def generateTaskList():
        Data = ('NULL')
        CMD = "select UID, URL from URLs where length(USource) < 1 or USource is NULL or USource = %s"
        resultList = sigTools.dbExecution(CMD, Data)

        return resultList


def updateSource(polishedSrc, UID):
        Data= (polishedSrc, UID)        
        CMD = "update URLs set USource = %s where UID = %s"
        resultList = sigTools.dbExecution(CMD, Data)

        return resultList

def main():
        taskList = generateTaskList()
        for item in taskList[2]:
                UID = item[0]
                pageURL = item[1]
                print UID
                polishedSrc = sigTools.getSource(pageURL)
                print polishedSrc
                resultList = updateSource(polishedSrc, UID)
                print resultList


if __name__ == "__main__":
        main()

