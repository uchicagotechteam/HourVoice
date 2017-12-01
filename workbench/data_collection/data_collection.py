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

outputdata.write("Frequency," + bizlicense[0][0] + ','.join(osha_header) + ','.join([x[0] for x in load_food[0].items() if not (type(x[0]) is dict)]) + "\n")

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
	for i in range(len(headers)):
		if headers[i] == header:
			return i

def getCSVDataByHeader(data, headers, header):
	head = getHeaderIndex(headers, header)
	return [d[head] for d in data]

def getJSONDataByHeader(data, header):
	return [d[header] for d in data if (header in d)]

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
osha_emps    = map(toLower, getCSVDataByHeader(osha_data, osha_header, 'Employer'))
biz_licenses = map(toLower, getCSVDataByHeader(biz_data, biz_header, "DOING BUSINESS AS NAME"))
food_emps    = map(toLower, getJSONDataByHeader(load_food, 'dba_name'))

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
food_lats         = map(roundMapFood, map(float, getJSONDataByHeader(load_food, 'latitude')))
food_lons         = map(roundMapFood, map(float, getJSONDataByHeader(load_food, 'longitude')))
osha_lats         = getCSVDataByHeader(osha_data, osha_header, 'Latitude')[1:]
osha_lons         = getCSVDataByHeader(osha_data, osha_header, 'Longitude')[1:]

def getOSHAChicago():
	indices = []
	chilons = []
	chilats = []
	osha_cities  = getCSVDataByHeader(osha_data, osha_header, 'City')
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
		bulk = [[str(names.count(i[0]))] + i[1] + i[2] + i[3]]
		final1.append(bulk)
	for j in final1:
		final = final + (','.join(j[0])) + '\n'
	return final

def getCrossRefedLocations():
	locs = []
	(biz_at_lat, oshadata) = findAllAtLatsAndLons()
	locs = locs + [b[1] for b in biz_at_lat]
	for j in biz_data:
		blats = round(float(j[lats]),6)
		blons = round(float(j[lons]),6)
		if (blats in set(food_lats)) and (blons in set(food_lons)):
			for k in load_food:
				if 'latitude' and 'longitude' in k:
					if round(float(k['latitude']),6) == blats and round(float(k['longitude']),6) == blons:
						j[lats] = str(j[lats])
						j[lons] = str(j[lons])
						k['latitude'] = str(k['latitude'])
						k['longitude'] = str(k['longitude'])
						bulk = [x[1] for x in k.items() if not (type(x[1]) is dict)]
						locs.append((j[names],j,[],bulk))
	return (locs, oshadata)

def findAllAtLatsAndLons():
	biz_at_lat = []
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
				if j[9] == blats and j[10] == blons and (i[lats] not in [b[0] for b in biz_at_lat]):
					i[lats] = str(i[lats])
					i[lons] = str(i[lons])
					j[9] = str(j[9])
					j[10] = str(j[10])
					biz_at_lat.append((i[lats], (i[names], i, j, [])))
					#print i[names], j[9], blats, i, j
	return (biz_at_lat, oshadata)

print findAllAtLatsAndLons()
outputdata.write(countUpViolators())
