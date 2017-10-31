import json, urllib
import pprint

url = "http://stopwagetheft.stanford.edu/api/v1/cases"
response = urllib.urlopen(url)
j = json.loads(response.read())
loadedData = j['data']

def getDataJ(hName):
	for i in range(len(loadedData)):
		return loadedData[i][hName]

# gets data from the OSHA severeinjury.csv file
injury_data = open("severeinjury.csv", 'r') 
load_data = injury_data.read()
split_lines_data = load_data.split('\n')
header = split_lines_data[0].split(',')
csv_list = []

# separates the key info by commas
for i in range(len(split_lines_data)):
	csv_list.append(split_lines_data[i].split(','))

# i tried to fix some issues with OSHA's poorly formatted csv, 
# but doesn't work yet
for i in range(len(split_lines_data)):
	for j in range(len(csv_list[i])-1):
		if csv_list[i][j].find('/n') != -1:
			''.join(csv_list[i][j:j+2])

# returns the index of the desired header
def getHeaderNum(hName):
	for i in range(0, len(header)):
		if header[i] == hName:
			return i

# returns a list of the value filed under a given header for every case
# 17000 is a filler number that represents around where the bad formatting starts
def getColumn(hName):
	col = []
	for i in range(17000):
		col.append(csv_list[i][getHeaderNum(hName)])
	return col

print getColumn('"Employer"')