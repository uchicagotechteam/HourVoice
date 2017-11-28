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

outputdata = open("output.txt", 'w')

# separates the key info by commas
def splitCSV(data):
	csv_list = []
	for d in data:
		if (len(d[0].split(',')) == len(biz_header)):
			csv_list.append(d[0].split(','))
	return csv_list

biz_data = splitCSV(bizlicense[:500])

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

def roundMapOSHA(data):
	return round(data, 2)

def roundMapFood(data):
	return round(data, 6)

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
biz_lats_for_OSHA = map(roundMapOSHA, map(float, filter(isFloat, getCSVDataByHeader(biz_data, biz_header, "LATITUDE")[1:])))
biz_lons_for_OSHA = map(roundMapOSHA, map(float, filter(isFloat, getCSVDataByHeader(biz_data, biz_header, "LONGITUDE")[1:])))
biz_lats_for_food = map(roundMapFood, map(float, filter(isFloat, getCSVDataByHeader(biz_data, biz_header, "LATITUDE")[1:])))
biz_lons_for_food = map(roundMapFood, map(float, filter(isFloat, getCSVDataByHeader(biz_data, biz_header, "LONGITUDE")[1:])))
food_lats    = map(roundMapFood, map(float, getJSONDataByHeader(load_food, 'latitude')))
food_lons    = map(roundMapFood, map(float, getJSONDataByHeader(load_food, 'longitude')))
osha_lats    = getCSVDataByHeader(osha_data, osha_header, 'Latitude')[1:]
osha_lons    = getCSVDataByHeader(osha_data, osha_header, 'Longitude')[1:]
osha_cities  = getCSVDataByHeader(osha_data, osha_header, 'City')
violation_info = getJSONDataByHeader(load_food, 'violations')
risk_info = getJSONDataByHeader(load_food,'risk')
food_inspection_result = getJSONDataByHeader(load_food, 'results')

def getOSHAChicago():
	indices = []
	chilons = []
	chilats = []
	for i in range(len(osha_cities)):
		if (osha_cities[i] == 'CHICAGO'):
			indices.append(i)
	for j in indices:
		chilons.append((osha_lons[j],j))
		chilats.append((osha_lats[j],j))
	return (chilats, chilons)

# we'd run disambiguation down here
def getCrossRefedEmployers():
	emps = []
	for f in food_emps:
		if (f in set(osha_emps)):
			emps.append(f)
	return emps

def countUpViolators():
	cross_refed = getCrossRefedLocations()
	names = []
	final1 = []
	final = ""
	(oshalats, oshalons) = getOSHAChicago()
	oshadata = []
	for i in oshalats:
		if isFloat(osha_data[i[1]][9]):
			osha_data[i[1]][9] = str(osha_data[i[1]][9])
			oshadata.append(osha_data[i[1]])
	for item in cross_refed:
		names.append(item[0])
	for i in cross_refed:
		final1.append([biz_data[i[1]] + [str(names.count(i[0]))] + oshadata[i[2]] + [str(i[3])]])
	for j in final1:
		final = final + (','.join(j[0])) + '\n'
	return final

def getCrossRefedLocations():
	locs = []
	(oshalats, oshalons) = getOSHAChicago()
	oshalaforcomp = []
	oshaloforcomp = []
	oshadata = []
	for i in oshalats:
		oshalaforcomp.append(float(i[0]))
		if isFloat(osha_data[i[1]][9]):
			osha_data[i[1]][9] = float(osha_data[i[1]][9])
			oshadata.append(osha_data[i[1]])
	for j in oshalons:
		oshaloforcomp.append(float(j[0]))
	for i in range(len(biz_lats_for_OSHA)):
		if (biz_lats_for_OSHA[i] in oshalaforcomp) and (biz_lons_for_OSHA[i] in set(oshaloforcomp)):
			for j in range(len(oshadata)):
				print (oshadata[j][9],biz_lats_for_OSHA[i], oshadata[j][9] == biz_lats_for_OSHA[i])
				if oshadata[j][9] == biz_lats_for_OSHA[i]:
					oshaindex = j
			locs.append((biz_licenses[i], i, oshaindex, 0))
	for i in range(len(biz_lats_for_food)):
		if (biz_lats_for_food[i] in set(food_lats)) and (biz_lons_for_food[i] in set(food_lons)):
			locs.append((biz_licenses[i], i, 0 ,i))
	return locs

		
outputdata.write(countUpViolators())
