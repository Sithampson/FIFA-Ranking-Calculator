from bs4 import BeautifulSoup
import requests
import csv
import datetime
from time import strptime
import arrow
import wget
import os


# Generate the latest results
def gen_latest_results():
	if os.path.exists('latest.tsv'):
		os.remove('latest.tsv')
	else:
		pass
	wget.download('http://eloratings.net/latest.tsv')


# Use the dates from calendar.csv
def friendlywindow():
	lisdate = []
	try:
		csvfile = open('calendar.csv', 'r').read()
	except FileNotFoundError:
		return "Calendar"
	reader = csvfile.split('\n')
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
	csfile = open('Ranking_Update_Dates.csv', 'w', newline = '')
	writer = csv.writer(csfile)
	rankingdate = soup.find('div', 'fi-selected-item').text.strip()
	writer.writerow([rankingdate])
	csfile.close()

	allTeams = soup.find('tbody')
	ca = allTeams.find_all('tr')

	csvfile = open('FIFA_Ranking_Data.csv', 'w', newline = '')
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
def updateRankings(lisdate):
	try:
		rankdate = open("Ranking_Update_Dates.csv").read()
	except FileNotFoundError:
		return "Ranking"

	a = rankdate
	s = arrow.get(a, 'D MMMM YYYY')
	year = s.format('YYYY')
	month = s.format('MM')
	Date = s.format('DD')

	DateThresh = datetime.date(int(year), int(month), int(Date))
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
	csvdata = csvfile.read().split("\n")
	
	csvfile.close()
	FIFAData = []
	FIFADataDict = {}
	bigTourn = {'CA': [0, 18, 18], 'AR': [0, 44, 36], 'CCH': [0, 24, 24]}

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
					matches = bigTourn[currentResult[7]][1]
					if (bigTourn[currentResult[7]][0] < matches):
						change *= 35
						if bigTourn[currentResult[7]][0] >= bigTourn[currentResult[7]][2]:
							if change < 0 and currentResult[5] == currentResult[6]:
								rating1 -= change
							elif currentResult[5] == currentResult[6]:
								rating2 += change
					# Quarterfinals
					else:
						change *= 40
						if change < 0 and currentResult[5] == currentResult[6]:
							rating1 -= change
						elif currentResult[5] == currentResult[6]:
							rating2 += change
					bigTourn[currentResult[7]][0] += 1

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