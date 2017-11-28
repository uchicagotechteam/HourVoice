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

lats = getHeaderIndex(biz_header, "LATITUDE")
lons = getHeaderIndex(biz_header, "LONGITUDE")
names = getHeaderIndex(biz_header, "DOING BUSINESS AS NAME")
for i in biz_data:
	if isFloat(i[lats]):
		i[lats] = float(i[lats])
	else:
		i[lats] = 0.0
	if isFloat(i[lons]):
		i[lons] = float(i[lons])
	else:
		i[lons] = 0.0

biz_lats_for_OSHA = map(roundMapOSHA, map(float, getCSVDataByHeader(biz_data, biz_header, "LATITUDE")[1:]))
biz_lons_for_OSHA = map(roundMapOSHA, map(float, getCSVDataByHeader(biz_data, biz_header, "LONGITUDE")[1:]))
biz_lats_for_food = map(roundMapFood, map(float, getCSVDataByHeader(biz_data, biz_header, "LATITUDE")[1:]))
biz_lons_for_food = map(roundMapFood, map(float, getCSVDataByHeader(biz_data, biz_header, "LONGITUDE")[1:]))
food_lats    = map(roundMapFood, map(float, getJSONDataByHeader(load_food, 'latitude')))
food_lons    = map(roundMapFood, map(float, getJSONDataByHeader(load_food, 'longitude')))
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
	(cross_refed, oshadata) = getCrossRefedLocations()
	names = []
	final1 = []
	final = ""
	for i in oshadata:
		if isFloat(i[9]) and isFloat(i[10]):
			i[9] = str(i[9])
			i[10] = str(i[10])
	for item in cross_refed:
		names.append(item[0])
	for i in cross_refed:
		final1.append([ i[2] + [str(names.count(i[0]))] + i[1] +[str(i[3])]])
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
		if isFloat(osha_data[i[1]][9]) and isFloat(osha_data[i[1]][10]):
			osha_data[i[1]][9]  = float(osha_data[i[1]][9])
			osha_data[i[1]][10] = float(osha_data[i[1]][10])
		oshadata.append(osha_data[i[1]])
	for j in oshalons:
		oshaloforcomp.append(float(j[0]))
	for i in biz_data:
		blats = round(float(i[lats]),2)
		blons = round(float(i[lons]),2)
		if (blats in set(oshalaforcomp)) and (blons in set(oshaloforcomp)):
			for j in oshadata:
				if j[9] == blats and j[10] == blons:
					i[lats] = str(i[lats])
					i[lons] = str(i[lons])
					j[9] = str(j[9])
					j[10] = str(j[10])
					print (i[names], j[9], blats, i, j)
					locs.append((i[names], i, j, 0))
	for i in range(len(biz_lats_for_food)):
		if (biz_lats_for_food[i] in set(food_lats)) and (biz_lons_for_food[i] in set(food_lons)):
			biz_data[i][lats] = str(biz_data[i][lats])
			biz_data[i][lons] = str(biz_data[i][lons])
			locs.append((biz_licenses[i],biz_data[i],[],i))
	return (locs, oshadata)
		
outputdata.write(countUpViolators())
