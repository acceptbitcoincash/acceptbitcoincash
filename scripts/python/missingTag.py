import os
import datetime
import codecs
import pathlib
import sys
import argparse
import collections

totalSites = 0
totalTag = 0

missingList = []
failedPaths = 0
missingEntries = 0

seperator = "////////////////////////////////////////////////////"
#logString = ""

index = 0

dirPath = os.path.join("..","..","_data")
filename = os.listdir(dirPath)


ignorePath = os.path.join("resources", "tagIgnore.csv")
tagPath = os.path.join("resources", "tagList.csv")

exceptionsFile = codecs.open(ignorePath, 'r', "utf-8")
exceptionList = exceptionsFile.read().split(",")

parser = argparse.ArgumentParser()
parser.add_argument("-t","--tags",help="Add tags to generate a report on missing tags", nargs='*')

args = parser.parse_args()

print(args)
#grab tag list

tagLogDic = {}
tagEntryDic = {}
tagPathDic = {}
tags = []

if(args.tags is None):
    tagFile = codecs.open(tagPath, 'r', "utf-8")
    tagList = tagFile.read().split(",")
    #tagLogDic = {}.fromkeys(tagList)
    print(tagList)
else:
    tagList = args.tags
    #tagLogDic = {}.fromkeys(tagList)
    print(tagList)

def countFile(dir, filename):
    path = os.path.join(dir, filename)
    #print("Testing site: " + path)
    if filename not in exceptionList:
        if ".yml" in path:
            for tag in tagList:
                #print("PROCESSING: " + tag + " for " +filename)
                file = codecs.open(path, 'r', "utf-8")
                processed = True
                prevName = ''

                pathFail = False
                #global index
                index = 0

                #global missingList
                #missingList = []
                #missingList.append("\n" + filename + ": " + tag + "\n File, Name \n")

                #global logString
                #logString = "\n\n" + filename + ": " + tag + "\n File, Name \n"
                logString = ""
                logHead = "\n\n" + seperator + "\n" + filename + ": " + tag + "\nFile, Name\n----------------------------------------------------\n"
                
                #print(missingList)

                tagFailedPaths = 0
                tagMissingEntries = 0
                tagString = tag + ": "
                for line in file:
                    #print(line)
                    #print("testing tag: " + tag + " in loop")
                    if "- name:" in line:
                        global totalSites
                        totalSites+= 1
                        #check if the previous file has been processed, this accounts for if the BTC support tag does not exist
                        if processed == False:
                    
                            nameLine = line.replace("- name:", "")
                            nameLine = nameLine.replace("\n", "")
                            nameLine = nameLine.replace("\r", "")
                            nameLine = nameLine.replace(" ", "")
                            nameLine = nameLine.replace("&amp", "&")
                            #missingList[index] = missingList[index] + " " + nameLine + ","
                            logString = logString + "" + nameLine + ", "
                            #print("logstring: " + logString)
                            global missingEntries
                            missingEntries += 1
                            tagMissingEntries += 1
                            if pathFail == False:
                                pathFail = True
                                global failedPaths
                                failedPaths += 1
                                tagFailedPaths += 1
                        processed = False

                    if tagString in line:
                        processed = True
                    index += 1

                tempString = ""
                global tagLogDic
                try:
                    tempString = tagLogDic[tag]
                except Exception as e:
                    pass
                if logString:
                    tempString = tempString + logHead + logString

                tagLogDic[tag] = tempString


            
                intPath = 0
                global tagPathDic
                try:
                    intPath = tagPathDic[tag]
                except Exception as e:
                    pass
                intPath = intPath + tagFailedPaths
                tagPathDic[tag] = intPath

                intEntries = 0
                global tagEntryDic
                try:
                    intEntries = tagEntryDic[tag]
                except Exception as e:
                    pass
                intEntries = intEntries + tagMissingEntries
                tagEntryDic[tag] = intEntries
                #global tagEntryDic
                #tagEntryDic[tag] = tagMissingEntries
                #print("inner missing entries " + str(tagEntryDic[tag]) + " total missing entries " + str(missingEntries))
                file.close()
for file in filename:
    #print("Testing path: " + path)
    countFile(dirPath, file)

#create log
timestamp = datetime.datetime.utcnow()

outputPath = os.path.join(".", "output")

try:
	os.mkdir(outputPath)
except Exception as e:
	pass

outputFile = os.path.join(outputPath, "missingEntries_log.csv")
if os.path.isfile(outputFile):
    output = codecs.open(outputFile, "a", "utf-8")
else:
    output = codecs.open(outputFile, "w+", "utf-8")
    output.write("Timestamp,Total Failed Paths,Total Missing Entries\n")

output.write(str(timestamp) + "," + str(failedPaths) + "," + str(missingEntries) + "\n")

output.close()

output = codecs.open(os.path.join(".","output","missingEntries.txt"), "w+", "utf-8")

print("\nMissing tags report")
print("Searching for these tags: " + str(tagList))
print("Ignoring these files: " + str(exceptionList))
output.write("Missing tags report \n")
output.write("Searching for these tags: " + str(tagList) + "\n")
output.write("Ignoring these files: " + str(exceptionList))

for tag, list in tagLogDic.items():
    print(list)
    output.write(list)

#print()
output.write("\n")
print("\n////////////////////////////////////////////////////////////////////\n")
for tag in tagPathDic.items():
    number = tag[1]
    tagString = tag[0]
    print(str(number) + " paths missing " + str(tagString) + "\n")
    output.write(str(number) + " paths missing " + str(tagString) + "\n")

print("////////////////////////////////////////////////////////////////////\n")

for tag in tagEntryDic.items():
    number = tag[1]
    tagString = tag[0]
    print(str(number) + " entries missing " + str(tagString) + "\n")
    output.write(str(number) + " entries missing " + str(tagString) + "\n")

print(str(failedPaths) + " files have entries missing tag entries")
output.write(str(failedPaths) + " files have entries missing the bcc tag \n")

print(str(missingEntries) + " entries are missing the tag entries")
output.write(str(missingEntries) + " entries are missing the bcc tag \n")

output.close()

