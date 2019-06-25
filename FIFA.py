from bs4 import BeautifulSoup
import requests
import csv
import datetime
from time import strptime
import wget
import os


# Generate the latest results
def gen_latest_results():
	if os.path.exists('latest.tsv'):
		os.remove('latest.tsv')
	else:
		pass
	wget.download('http://eloratings.net/latest.tsv')


# Generate the friendly windows for current calendar year
def gen_friendly_window():
	source = requests.get('https://www.fifa.com/calendar/').text
	soup = BeautifulSoup(source, 'lxml')

	calendar = soup.find('body')
	ft = calendar.find('div', 'activeTabContent')
	friendly = []

	friendly = ft.find_all('li', 'calendar-event event')
	csvfile = open('calendar.csv', 'w')
	writer = csv.writer(csvfile)
	for match in friendly:
		line = match.text.strip()
		new = line.find('Official or friendly matches', 0, len(line))
		if new != -1:
			start = line[0:2]
			end = line[5:7]
			month = line[8:11]

			mscode = month
			y = strptime(mscode,'%b').tm_mon
					
			writer.writerow([2019, y,int(start), 2019, y, int(end)])
	csvfile.close()

gen_friendly_window()
# Use the dates generated from gen_friendly_window()
def friendlywindow():
	lisdate = []
	try:
		csvfile = open('calendar.csv', 'r').read()
	except FileNotFoundError:
		return "Calendar"
	reader = csvfile.split('\n\n')
	for line in reader:
		try:
			line = line.split(',')
			lisdate.append([line[0], line[1], line[2], line[3], line[4], line[5]])
		except IndexError:
			pass
	return lisdate


# Get current rankings from the FIFA website
def getCurrentRankings():
	source = requests.get('https://www.fifa.com/fifa-world-ranking/ranking-table/men/').text
	soup = BeautifulSoup(source, 'lxml')

	allTeams = soup.find('tbody')
	ca = allTeams.find_all('tr')

	csvfile = open('FIFA_Ranking_Data.csv', 'w')
	writer = csv.writer(csvfile)
	writer.writerow(['TeamRank', 'TeamCode', 'TeamName', 'TeamPoints'])

	for team in ca:
		teamName = team.find('span', 'fi-t__nText').text.strip()
		teamCode = team.find('span', 'fi-t__nTri').text.strip()
		teamPoints = team.find('td', 'fi-table__td fi-table__points').text.strip()
		teamRank = team.find('td', 'fi-table__td fi-table__rank').text.strip()
		writer.writerow([teamRank, teamCode, teamName, teamPoints])

	csvfile.close()


# Update rankings based on the current matches being played
def updateRankings(year, month, Date, lisdate):
	DateThresh = datetime.date(year, month, Date)
	try:
		latestResults = open("latest.tsv", "r").read()
	except FileNotFoundError:
		return "Latest"
	latestResults = latestResults.split("\n")

	tourncsv = open("FIFA_Tournaments.csv", 'r')
	tourndata = (tourncsv.read()).split("\n")
	tourndict = {}
	for tourn in tourndata:
		tourn = tourn.split(",")
		tourndict[tourn[0]] = tourn[1]

	try:
		csvfile = open('FIFA_Ranking_Data.csv', 'r')
	except FileNotFoundError:
		return "Ranking"
	next(csvfile)
	next(csvfile)
	csvdata = csvfile.read().split("\n\n")
	
	csvfile.close()
	FIFAData = []
	FIFADataDict = {}
	for data in csvdata:
		data = data.split(",")
		if(len(data) == 4):
			FIFAData.append(data)
			FIFADataDict[data[1]] = float(data[3])

	csvfile = open('FIFA_Codes.csv' , 'r')
	tecode = csvfile.read().split("\n,\n")
	csvfile.close()
	teamCodes = {}
	for code in tecode:
		code = code.split(",")
		teamCodes[code[0]] = code[1]

	for result in reversed(latestResults):
		currentResult = result.split("\t")
		matchDate = datetime.date(int(currentResult[0]), int(currentResult[1]), int(currentResult[2]))
		try:
			if matchDate >= DateThresh:
				team1 = teamCodes[currentResult[3]]
				team2 = teamCodes[currentResult[4]]

				rating1 = FIFADataDict[team1]
				rating2 = FIFADataDict[team2]
				change = ratingsChange(rating1, rating2, currentResult[5], currentResult[6])
				matchtype = tourndict[currentResult[7]]

				if matchtype == 'F':
					if matchinwindow(matchDate, lisdate) == False:
						change *= 5
					else:
						change *= 10
				elif matchtype == 'NL':
					change *= 15
				elif matchtype == 'CQ':
					change *= 25
				elif matchtype == 'CC':
					change *= 35

				rating1 += change
				rating2 -= change
				FIFADataDict[team1] = rating1
				FIFADataDict[team2] = rating2
		except KeyError:
			pass

	for team in FIFAData:
		team[3] = FIFADataDict[team[1]]


	FIFAData.sort(key = lambda FIFAData :FIFAData[3], reverse = True)

	return FIFAData


# Use the FIFA formula to update current rankings
def ratingsChange(rating1, rating2, score1, score2):
	diffrating = - (rating1 - rating2)
	diffrating /= 600
	diffrating = (10 ** diffrating) + 1
	diffrating = 1 / diffrating

	if score1 > score2:
		result = 1
	elif score1 == score2:
		result = 0.5
	else:
		result = 0

	result -= diffrating
	return result


# Check if the particular match is inside FIFA window or not
def matchinwindow(matchDate, lisdate):
	for window in lisdate:
		datestart = datetime.date(int(window[0]), int(window[1]), int(window[2]))
		dateend = datetime.date(int(window[3]), int(window[4]), int(window[5]))
		if(matchDate >= datestart and matchDate <= dateend):
			return True
	return False