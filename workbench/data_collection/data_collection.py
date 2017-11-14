import json, urllib, csv

#gets data from the DoL cases via stanford's stopwagetheft
url = "http://stopwagetheft.stanford.edu/api/v1/cases"
response = urllib.urlopen(url)
j = json.loads(response.read())
loadedData = j['data']

# gets data from the OSHA severeinjury.csv file
injury_data = open("severeinjury.csv", 'r') 
load_data = injury_data.read()
split_lines_data = load_data.split('\n')
osha_header = split_lines_data[0].split(',')

food_data = open("cityofchicagofood.json", 'r')
load_food = json.loads(food_data.read())

bizlicense = []
with open("Business_Licenses.csv", 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter='"')
	for row in reader:
		bizlicense.append(row)
biz_header = bizlicense[0][0].split(',')

# separates the key info by commas
def splitCSV(data):
	csv_list = []
	for i in range(len(data)):
		if (len(data[i][0].split(',')) == len(biz_header)):
			csv_list.append(data[i][0].split(','))
	return csv_list

osha_data = splitCSV(split_lines_data)
biz_data = splitCSV(bizlicense)

# returns the index of the desired header
def getHeaderIndex(headers, header):
	for i in range(0, len(headers)):
		if headers[i] == header:
			return i

def getCSVDataByHeader(data, headers, header):
	col = []
	for i in range(len(data)):
		col.append(data[i][getHeaderIndex(headers, header)])
	return col

def getJSONDataByHeader(data, header):
	d = []
	for i in range(len(data)):
		if header in data[i]:
			d.append(data[i][header])
	return d

def toLower(data):
	return data.lower()

def roundMap(data):
	return round(data, 6)

def isFloat(str):
	try:
	 	float(str)
		return True
	except ValueError:
		return False

dol_emps  = getJSONDataByHeader(loadedData, "legal_name")
osha_emps = getCSVDataByHeader(osha_data, osha_header, '"Employer"')
biz_licenses = map(toLower, getCSVDataByHeader(biz_data, biz_header, "DOING BUSINESS AS NAME"))
food_emps = map(toLower, getJSONDataByHeader(load_food, 'dba_name'))
biz_lats = map(roundMap, map(float, filter(isFloat, getCSVDataByHeader(biz_data, biz_header, "LATITUDE")[1:])))
biz_lons = map(roundMap, map(float, filter(isFloat, getCSVDataByHeader(biz_data, biz_header, "LONGITUDE")[1:])))
food_lats = map(roundMap, map(float, getJSONDataByHeader(load_food, 'latitude')))
food_lons = map(roundMap, map(float, getJSONDataByHeader(load_food, 'longitude')))


def getCrossRefedEmployers():
	emps = []
	for i in range(len(biz_lats)):
		if (biz_lats[i] in food_lats) and (biz_lons[i] in food_lons):
			emps.append(biz_licenses[i])
	return emps

print getCrossRefedEmployers()
