from imposm.parser.xml.parser import XMLParser
import csv


# change here to change the file you want to edit, make sure it is under data/
filename = "cambridgema"


# This is the road conversion, feel free to modify or add
road_capacity_conversion = {}
road_capacity_conversion['motorway'] = 4
road_capacity_conversion['motorway_link'] = 4
road_capacity_conversion['trunk'] = 4
road_capacity_conversion['trunk_link'] = 4
road_capacity_conversion['primary'] = 3
road_capacity_conversion['primary_link'] = 3
road_capacity_conversion['secondary'] = 3
road_capacity_conversion['secondary_link'] = 3
road_capacity_conversion['tertiary'] = 2
road_capacity_conversion['tertiary_link'] = 2
road_capacity_conversion['unclassified'] = 1
road_capacity_conversion['residential'] = 1
road_capacity_conversion['pedestrian'] = 1
road_capacity_conversion['road'] = 1
road_capacity_conversion['living_street'] = 1
road_capacity_conversion['service'] = 1

# The ones missing are cycleway and footway (for boston datasets)


## This method is not called since we parse nodes instead of roads, but can be implemented in the future to count # of stores.
def parseNodes(nodes):
  print 'hello!\n'
  array = []
  for id, description, (x, y) in nodes:
  	print description
  	if 'addr:housenumber' not in description:
  		array.append(description)


# This is the main method to parse roads.
def parseWays(ways):
	reference = {}
	mapping = {}
	
	# Each entry in ways is in this format: id, {some description dictionary}, [coordinates]
	for id, description, coordinates in ways:
		# They also include some places, for now if an entry has 'highway' and 'name' we know for sure it is a road.
		if ('highway' in description and 'name' in description):
			# uncomment this line to see what a description looks like
			# print description
			reference[id] = description

			
			name = "" or description['name']
			lanes = int(description['lanes']) if 'lanes' in description else ""
			oneway = description['oneway'] if 'oneway' in description else ""

			road_capacity_from_conversion = 1
			highway = ""

			if 'highway' in description:
				highway = description['highway']
				if description['highway'] in road_capacity_conversion:
					# Road capacity conversion, if applicable
					road_capacity_from_conversion = road_capacity_conversion[description['highway']]
				else:
					continue
					# Uncomment this line to see which highway type is not included
					# print description['highway']
			
			mapping[id] = [name, lanes, road_capacity_from_conversion, highway, oneway]
		else:
			continue
			# uncomment this line to see which elements (not roads) are not included in this parsing
			# print description


	# Write to output file when done
	with open('processed/roads_' + globals()["filename"] +'.csv', 'a') as f:
		writer = csv.writer(f)
		for element in mapping:
			# Encode for utf-8 chars
			writer.writerow([unicode(s).encode("utf-8") for s in mapping[element]])


# Write headers, then parse
with open ('processed/roads_' + filename+ '.csv', 'wb') as f:
	writer = csv.writer(f)
	header = ["name", "lanes", "road_capacity_from_conversion", "highway", "oneway"]
	w = writer.writerow(header)
# Here ways_callback tells us which method we are calling for the ways we found. Change to nodes_callback = yourmethod if want to process stores
p = XMLParser(ways_callback=parseWays)

p.parse('data/' + filename)
