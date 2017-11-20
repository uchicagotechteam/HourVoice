import json, urllib, csv

#gets data from the DoL cases via stanford's stopwagetheft
url = "http://stopwagetheft.stanford.edu/api/v1/cases"
response = urllib.urlopen(url)
j = json.loads(response.read())
loadedData = j['data']

food_data = open("cityofchicagofood.json", 'r')
load_food = json.loads(food_data.read())

bizlicense = []
with open("Business_Licenses.csv", 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter='"')
	for row in reader:
		bizlicense.append(row)
biz_header = bizlicense[0][0].split(',')

osha_data = []
with open("severeinjury.csv", 'r') as csvfile:
	reader = csv.reader(csvfile)
	for row in reader:
		osha_data.append(row)
osha_header = osha_data[0]

# separates the key info by commas
def splitCSV(data):
	csv_list = []
	for d in data:
		if (len(d[0].split(',')) == len(biz_header)):
			csv_list.append(d[0].split(','))
	return csv_list

biz_data = splitCSV(bizlicense)

# returns the index of the desired header
def getHeaderIndex(headers, header):
	print "getting headers"
	for i in range(len(headers)):
		if headers[i] == header:
			return i

def getCSVDataByHeader(data, headers, header):
	col = []
	print "getting data from csv"
	head = getHeaderIndex(headers, header)
	for d in data:
		col.append(d[head])
	return col

def getJSONDataByHeader(data, header):
	jdat = []
	for d in data:
		if header in set(d):
			jdat.append(d[header])
	return jdat

def toLower(data):
	return data.lower()

def roundMap(data):
	return round(data, 2)

def isFloat(str):
	try:
	 	float(str)
		return True
	except ValueError:
		return False

dol_emps     = getJSONDataByHeader(loadedData, "legal_name")
osha_emps    = map(toLower,  getCSVDataByHeader(osha_data, osha_header, 'Employer'))
biz_licenses = map(toLower , getCSVDataByHeader(biz_data, biz_header, "DOING BUSINESS AS NAME"))
food_emps    = map(toLower , getJSONDataByHeader(load_food, 'dba_name'))
biz_lats     = map(roundMap, map(float, filter(isFloat, getCSVDataByHeader(biz_data, biz_header, "LATITUDE")[1:])))
biz_lons     = map(roundMap, map(float, filter(isFloat, getCSVDataByHeader(biz_data, biz_header, "LONGITUDE")[1:])))
food_lats    = map(roundMap, map(float, getJSONDataByHeader(load_food, 'latitude')))
food_lons    = map(roundMap, map(float, getJSONDataByHeader(load_food, 'longitude')))
osha_lats    = getCSVDataByHeader(osha_data, osha_header, 'Latitude')[1:]
osha_lons    = getCSVDataByHeader(osha_data, osha_header, 'Longitude')[1:]
osha_cities  = getCSVDataByHeader(osha_data, osha_header, 'City')

def getOSHAChicago():
	indices = []
	chilons = []
	chilats = []
	for i in range(len(osha_cities)):
		if (osha_cities[i] == 'CHICAGO'):
			indices.append(i)
	for j in indices:
		chilons.append(osha_lons[j])
		chilats.append(osha_lats[j])
	return (map(float, chilats), (map(float, chilons)))

# we'd run disambiguation down here
def getCrossRefedEmployers():
	emps = []
	print "getting cross refed employers"
	for f in food_emps:
		if (f in set(osha_emps)):
			emps.append(f)
	return emps

def countUpViolators():
	crossRefed = getCrossRefedLocations()
	final = set([])
	for c in crossRefed:
		final.add(c + " " + str(crossRefed.count(c)))
	print '\n'.join(list(final))

def getCrossRefedLocations():
	locs = []
	(chilats, chilons) = getOSHAChicago()
	for i in range(len(chilats)):
		if (chilats[i] in set(biz_lats)) and (chilons[i] in set(biz_lons)):
			locs.append(osha_emps[i])
	for i in range(len(food_lats)):
		if (food_lats[i] in set(biz_lats)) and (food_lons[i] in set(biz_lons)):
			locs.append(food_emps[i])
	return locs

countUpViolators()