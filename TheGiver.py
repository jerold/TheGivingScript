#!/usr/bin/python

import os
import sys
import random
import json
import shutil
import time
import datetime
from pprint import pprint


userFile = os.path.join(os.path.dirname(__file__), 'data/users.json')
saveFile = os.path.join(os.path.dirname(__file__), 'data/save.json')
browsersFile = os.path.join(os.path.dirname(__file__), 'data/browsers.json')


gridLen = 30

users = []
usersSavedData = []
browsers = []

usersObj = {}
usersSavedDataObj = {}
browsersObj = {}

writeSave = False


# Load data
with open(saveFile) as json_save_data:
	try:
		save_json = json.load(json_save_data)
	except:
		save_json = {"users":[]}
	usersSavedData = save_json["users"]
	for userSaveData in usersSavedData:
		usersSavedDataObj[userSaveData["name"]] = userSaveData
with open(userFile) as json_user_data:
	try:
		users = json.load(json_user_data)["users"]
	except:
		raise Exception("User json required!")
	for user in users:
		usersObj[user["name"]] = user
with open(browsersFile) as json_browser_data:
	try:
		browsers = json.load(json_browser_data)["browsers"]
	except:
		raise Exception("Browser json required!")
	for browser in browsers:
		browsersObj[browser["name"]] = browser


# Access methods
def usersSavedBrowserCount(userName, browserName):
	if userName in usersSavedDataObj.keys():
		for browserCount in usersSavedDataObj[userName]["previous_browser_counts"]:
			if browserCount["name"] == browserName:
				return browserCount

def usersBrowserCount(userName, browserName):
	if userName in usersObj.keys():
		for browserCount in usersObj[userName]["previous_browser_counts"]:
			if browserCount["name"] == browserName:
				return browserCount

def usersPreviousScore(userName):
	return sum(b["score"] for b in usersObj[userName]["previous_browsers"])

def previousRoundLoser():
	currentLoser = users[0]
	currentScore = usersPreviousScore(currentLoser["name"])
	for user in users:
		userScore = usersPreviousScore(user["name"])
		if userScore > currentScore:
			currentLoser = user
			currentScore = userScore
	return currentLoser

# Clean up object
for user in users:
	user["score"] = 0.0
	user["last_score"] = 0.0
	user["loses"] = 0
	user["bails"] = 0
	user["previous_browsers"] = []
	user["previous_browser_counts"] = []

	# Load saved user data into users
	if user["name"] in usersSavedDataObj.keys():
		user["score"] = usersSavedDataObj[user["name"]]["score"]
		user["loses"] = usersSavedDataObj[user["name"]]["loses"]
		user["previous_browsers"] = usersSavedDataObj[user["name"]]["previous_browsers"]
		user["previous_browser_counts"] = usersSavedDataObj[user["name"]]["previous_browser_counts"]
		user["bails"] = usersSavedDataObj[user["name"]]["bails"]

	for browser in browsers:
		browserCount = usersSavedBrowserCount(user["name"], browser["name"])
		if browserCount is None:
			browserCount = {"name":browser["name"], "count": 0}
			user["previous_browser_counts"].append(browserCount)

# Order user by score, highest score more likely to luck out and not get a second browser
orderedUsers = sorted(users, key=lambda k: k["score"])


# reset when needed
if len(sys.argv) > 1:
	if sys.argv[1].upper() == "RESET":
		for user in users:
			user["score"] = 0.0
			user["last_score"] = 0.0
			user["loses"] = 0
			user["bails"] = 0
			user["previous_browsers"] = []
			user["previous_browser_counts"] = []
			for browser in browsers:
				browserCount = {"name":browser["name"], "count": 0}
				user["previous_browser_counts"].append(browserCount)

	# Check Lose Fairness
	elif sys.argv[1].upper() == "LOSERS":
		print("LOSERS:")
		orderedLosers = sorted(users, key=lambda k: k["loses"], reverse=True)
		sum = 0
		for user in orderedLosers:
			sum = sum + user["loses"]
		for user in orderedLosers:
			perc = 0.0
			if sum > perc:
				perc = float(user["loses"])/float(sum)
			lineLen = int(gridLen*perc)
			lineString = ''
			for j in range(gridLen):
				if j < lineLen:
					lineString = lineString + '|'
				else:
					lineString = lineString + '.'
			print(lineString + ' ' + user["name"] + ' (' + str(user["loses"]) + ') : ' + str(int(perc*100)) + '%')

	# Swap browser testing for previous results
	elif sys.argv[1].upper() == "SWAP":
		print("SWAP:")
		print('\n'.join('[' + str(i) + '] ' + users[i]["name"] + ' (' + str(users[i]["score"]) + ')' for i in range(len(users))))
		indexA = int(raw_input('Lucky SOB\'s index:  '))
		indexB = int(raw_input('Unlucky SOB\' index: '))
		if indexA < len(users) and indexB < len(users):
			loserUser = previousRoundLoser()
			userA = users[indexA]
			userB = users[indexB]
			browsersA = userA["previous_browsers"]
			browsersB = userB["previous_browsers"]
			print('')
			print(userA["name"] + ' can swap the following browsers:')
			print('\n'.join('[' + str(i) + '] ' + browsersA[i]["name"] + ' (' + str(browsersA[i]["score"]) + ')' for i in range(len(browsersA))))
			indexC = int(raw_input('Browser index: '))
			if (indexC < len(browsersA)):
				browserC = browsersA[indexC]
				confirm = raw_input('Take ' + browserC["name"] +
					' from ' + userA["name"] +
					' and give it to ' + userB["name"] + ' (y/n)? ')
				print('')
				if confirm is 'y':
					browsersA.pop(indexC)
					browsersB.append(browserC)

					# update saved scores
					userA["score"] = userA["score"] - browserC["score"]
					userB["score"] = userB["score"] + browserC["score"]

					# update tested browser counts
					browserCountA = usersBrowserCount(userA["name"], browserC["name"])
					browserCountA["count"] = browserCountA["count"] - 1
					browserCountB = usersBrowserCount(userB["name"], browserC["name"])
					browserCountB["count"] = browserCountB["count"] + 1

					# update last round's user if needed
					if usersPreviousScore(userB["name"]) > usersPreviousScore(loserUser["name"]):
						print('Previous Loser: ' + str(usersPreviousScore(loserUser["name"])) + ' ' + loserUser["name"])
						print('New  Loser:     ' + str(usersPreviousScore(userB["name"])) + ' ' + userB["name"])
						print('')
						loserUser["loses"] = loserUser["loses"] - 1
						userB["loses"] = userB["loses"] + 1

					print(userA["name"] + '\'s browsers:')
					if (len(browsersA) > 0):
						print('\n'.join('[' + str(i) + '] ' + browsersA[i]["name"] for i in range(len(browsersA))))
					print('')
					print(userB["name"] + '\'s browsers:')
					if (len(browsersB) > 0):
						print('\n'.join('[' + str(i) + '] ' + browsersB[i]["name"] for i in range(len(browsersB))))

					# Setup for SAVE
					writeSave = True

			else:
				print('Invalid Browser Index!')
		else:
			print('Invalid User Index!')


	# Check randomness
	elif len(sys.argv[1]) > 0:
		for user in orderedUsers:
			if sys.argv[1].upper() == user["name"].upper():
				print(sys.argv[1].upper() + ' CHECK:')
				browserCounts = []
				sum = 0
				for browserCount in user["previous_browser_counts"]:
					browserCounts.append(browserCount)
					sum = sum + browserCount["count"]
				browserCounts = sorted(browserCounts, key=lambda k: k["count"], reverse=True)
				for browserCount in browserCounts:
					perc = 0.0
					if sum > perc:
						perc = float(browserCount["count"])/float(sum)
					lineLen = int(gridLen*perc)
					lineString = ''
					for j in range(gridLen):
						if j < lineLen:
							lineString = lineString + '|'
						else:
							lineString = lineString + '.'
					print(lineString + ' ' + browserCount["name"] + ': ' + str(int(perc*100)) + '%')

# Do work
else:
	# init previous browser lists
	for user in users:
		user["previous_browsers"] = []
	# assign random browsers to users
	userIndex = 0
	usersBrowsers = {}
	remainingBrowsers = list(browsers)
	random.shuffle(remainingBrowsers)
	while len(remainingBrowsers) > 0:
		user = orderedUsers[userIndex%len(orderedUsers)]
		browser = remainingBrowsers.pop(random.randrange(100)%len(remainingBrowsers))
		user["previous_browsers"].append(browser)
		userIndex = userIndex + 1

	# Identify just_awful double Jeopardy
	zeroJeopardyUsers = []
	doubleJeopardyUsers = []
	for user in orderedUsers:
		ieCount = 0
		for browser in user["previous_browsers"]:
			if browser["just_awful"]:
				ieCount = ieCount + 1
		if ieCount == 0:
			zeroJeopardyUsers.append(user)
		elif ieCount == 2:
			doubleJeopardyUsers.append(user)

	# Resolve just_awful double Jeopardy
	for i in range(min(len(zeroJeopardyUsers), len(doubleJeopardyUsers))):
		tempBrowser = zeroJeopardyUsers[i]["previous_browsers"][0]
		zeroJeopardyUsers[i]["previous_browsers"][0] = doubleJeopardyUsers[i]["previous_browsers"][0]
		doubleJeopardyUsers[i]["previous_browsers"][0] = tempBrowser

	# print results and clean up user objects
	thisLoser = ''
	thisLosingScore = 0
	biggestLoser = ''
	biggestLosingScore = 0
	scoreLinesForPrint = {}
	for user in orderedUsers:
		scoreThisRound = 0
		usersBrowsersString = ''
		for browser in user["previous_browsers"]:
			scoreThisRound = scoreThisRound + browser["score"]
			usersBrowsersString = usersBrowsersString + '[' + browser["name"] + '] '

			# update the number of times user has tested this browser
			browserCount = usersBrowserCount(user["name"], browser["name"])
			browserCount["count"] = browserCount["count"] + 1
		user["last_score"] = scoreThisRound
		user["score"] = user["score"] + scoreThisRound

		# Laugh at big losers
		if scoreThisRound > 12:
			usersBrowsersString = usersBrowsersString + ' <-- Sheesh!'

		# Track losers
		if scoreThisRound > thisLosingScore:
			thisLoser = user["name"]
			thisLosingScore = scoreThisRound
		if user["score"] > biggestLosingScore:
			biggestLoser = user["name"]
			biggestLosingScore = user["score"]
		scoreLinesForPrint[user["name"]] = user["name"] + ' (' + str(int(scoreThisRound)) + ':' + str(int(user["score"])) + ') ' + usersBrowsersString

	# Update loses
	for user in orderedUsers:
		if user["name"] == thisLoser:
			user["loses"] = user["loses"] + 1

	# Setup for SAVE
	writeSave = True

	# Print Stuff ordered by suckiness
	orderedUsers = sorted(users, key=lambda k: k["last_score"], reverse=True)
	for user in orderedUsers:
		print(scoreLinesForPrint[user["name"]])
	print('')
	print('All time biggest loser: ' + biggestLoser + ' (' + str(int(biggestLosingScore)) + ')')
print('')

if writeSave:
	# save backup of previous data
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
	shutil.copyfile(saveFile, '/Users/jeroldalbertson/Documents/whoTestsWhat/data/backup/save.' + str(st) + '.json')

	# add user save data for users not in this round but listed in save file
	legacyUsers = []
	for userSavedData in usersSavedData:
		if userSavedData["name"] not in usersObj.keys():
			userSavedData["bails"] = userSavedData["bails"] + 1
			legacyUsers.append(userSavedData)
			userSavedData["previous_browsers"] = []
			orderedUsers.append(userSavedData)
	if len(legacyUsers) > 0:
		print('Users not included in this round of testing:')
		for legacyUser in legacyUsers:
			print(legacyUser["name"])

	# dump scores back to file
	newSaveData = {"users": orderedUsers}
	with open(saveFile, 'w') as outfile:
		# json.dump(data, outfile)
		outfile.write(json.dumps(newSaveData, indent=4))
