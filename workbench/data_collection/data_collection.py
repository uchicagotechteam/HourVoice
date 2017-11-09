import json, urllib
import pprint

#gets data from the DoL cases via stanford's stopwagetheft
url = "http://stopwagetheft.stanford.edu/api/v1/cases"
response = urllib.urlopen(url)
j = json.loads(response.read())
loadedData = j['data']

# gets data from the OSHA severeinjury.csv file
injury_data = open("severeinjury.csv", 'r') 
load_data = injury_data.read()
split_lines_data = load_data.split('\n')
header = split_lines_data[0].split(',')
csv_list = []

food_data = open("cityofchicagofood.json", 'r')
load_food = json.loads(food_data.read())

bizlicense = open("bizlicense.json", 'r')
loadbiz = json.loads(bizlicense.read())

# separates the key info by commas
for i in range(len(split_lines_data)):
	csv_list.append(split_lines_data[i].split(','))

# i tried to fix some issues with OSHA's poorly formatted csv, 
# but doesn't work yet
for i in range(len(split_lines_data)):
	for j in range(len(csv_list[i])-1):
		if csv_list[i][j].find('/n') != -1:
			''.join(csv_list[i][j:j+2])

#retrieves DoL data by name
def getDOLDataByHeader(hName):
	data = []
	for i in range(len(loadedData)):
		data.append(loadedData[i][hName])
	return data

# returns the index of the desired header
def getOSHAHeaderIndex(hName):
	for i in range(0, len(header)):
		if header[i] == hName:
			return i

# returns a list of the value filed under a given header for every case
# 17000 is a filler number that represents around where the bad formatting starts
def getOSHADataByHeader(hName):
	col = []
	for i in range(17000):
		col.append(csv_list[i][getOSHAHeaderIndex(hName)])
	return col

def getJSONDataByHeader(fName, hName):
	data = []
	for i in range(len(fName)):
		data.append(fName[i][hName])
	return data

dol_emps  = getDOLDataByHeader("legal_name")
osha_emps = getOSHADataByHeader('"Employer"')
food_emps = getJSONDataByHeader(load_food, "dba_name")
biz_names = getJSONDataByHeader(loadbiz, "doing_business_as_name")

def getAllEmployers():
	all_employers = []
	all_employers.append(dol_emps)
	all_employers.append(osha_emps)
	all_employers.append(food_emps)
	all_employers.append(biz_names)
	return all_employers

def getCrossRefedEmployers():
	emps = []
	for i in range(len(food_emps)):
		if food_emps[i] in dol_emps:
			emps.append(food_emps + str(i))
	print emps

getCrossRefedEmployers()