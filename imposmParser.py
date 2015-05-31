from imposm.parser.xml.parser import XMLParser
from geopy.distance import vincenty
import csv
import parseExcel
import utilities
import sys


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

reference = {}
plotting_points = []
array = []

road_capacity = {}

regions = {}


# This method is not called since we parse nodes instead of roads, but can
# be implemented in the future to count # of stores.

def coords_callback(coords):
  for osm_id, lon, lat in coords:
    reference[osm_id] = ("", [lat, lon])
    # print osm_id, lon, lat

def parseNodes(nodes):
	# print 'hello!\n'
	for id, description, (y, x) in nodes:
  		# print description
  		reference[id] = (description, [x, y])
  		if 'addr:housenumber' not in description:
  			array.append(description)


# This is the main method to parse roads.
def parseWays(ways):
	mapping = {}
	
	
	# Each entry in ways is in this format: id, {some description dictionary}, [coordinates]
	for id, description, coordinates in ways:
		distance = 0.0
		points_of_way = []
		# print coordinates
		# They also include some places, for now if an entry has 'highway' and 'name' we know for sure it is a road.
		if ('highway' in description):
			# uncomment this line to see what a description looks like
			# print description, coordinates
			reference[id] = description

			
			name = description['name'] if 'name' in description else ""

			try:
				lanes = int(description['lanes']) if 'lanes' in description else ""
			except ValueError:
				lanes = description['lanes']

			oneway = description['oneway'] if 'oneway' in description else ""

			road_capacity_from_conversion = 0
			highway = ""

			if 'highway' in description:
				highway = description['highway']
				if description['highway'] in road_capacity_conversion:
					# Road capacity conversion, if applicable
					road_capacity_from_conversion = road_capacity_conversion[description['highway']]
				else:
					pass
					# Uncomment this line to see which highway type is not included
					# print description['highway']
			
			mapping[id] = [id, name, lanes, road_capacity_from_conversion, highway, oneway]

			if coordinates[0] in reference:
				if type(reference[coordinates[0]]) != dict:
					current_point = reference[coordinates[0]][1]
					starting_point = current_point
					if not starting_point:
						continue
			else:
				print "MISSING"
				continue


			for identity in coordinates:
				if (identity in reference):
					# print reference[identity]
					if isinstance(reference[identity], tuple):
						if current_point == None:
							continue
						last_point = current_point
						points_of_way.append(last_point)
						current_point = reference[identity][1]


						# print vincenty(last_point, current_point).km

						distance += vincenty(last_point, current_point).km

						plotting_points.append((name, identity,reference[identity][1][0], reference[identity][1][1]))
						# print reference[identity]
				else:
					# print len(reference)
					# pass
					print "MISSING", identity

			points_of_way.append(current_point)
			# print distance, road_capacity_from_conversion
			capacity = distance * road_capacity_from_conversion
			if oneway != "yes":
				capacity *= 1
			
			road_capacity[id] = capacity
			mapping[id].append(distance)
			mapping[id].append(road_capacity[id])
			# Also get the coordinates that make up the way
			for point in points_of_way:
				mapping[id].append(point[0])
				mapping[id].append(point[1])
		# else:
			# print description


	# Write to output file when done
	with open('processed/roads_' + globals()["filename"] +'.csv', 'a') as f:
		writer = csv.writer(f)
		for element in mapping:
			# Encode for utf-8 chars
			writer.writerow([unicode(s).encode("utf-8") for s in mapping[element]])
	return 

if __name__ == "__main__":

	## 1st item osmfile, 2nd item filename of grids, 3rd item sheet name, if necessary
	args = sys.argv
	# Default sheet name and indices
	sheetName = 'Sheet1'
	x_index = 0
	y_index = 1
	FID_index = 2
	verbose = False

	if len(args) < 2:
		raise Exception("Too few arguments. Must specify at least the osm file and grid center file.")
	if len(args) >= 2:
		filename = args[1]
	if len(args) >= 3:
		gridDataFilename = args[2]
	if len(args) >= 4:
		verbose = args[3]
		if verbose == "True":
			verbose = True
		else:
			verbose = False
	if len(args) >= 5:
		sheetName = args[4]
	if len(args) >= 6:
		x_index = int(args[5])
	if len(args) >= 7:
		y_index = int(args[6])
	if len(args) >= 8:
		FID_index = int(args[7])
	# Here ways_callback tells us which method we are calling for the ways we found. Change to nodes_callback = yourmethod if want to process stores
	p = XMLParser(ways_callback=parseWays, nodes_callback = parseNodes, coords_callback = coords_callback)


	p.parse('data/' + filename)
	# print len(reference)


	print "Starting Second Round"

	# Write headers, then parse again
	with open ('processed/roads_' + filename+ '.csv', 'wb') as f:
		writer = csv.writer(f)
		header = ["id", "name", "lanes", "road_capacity_from_conversion", "highway", "oneway", "distance", "road_capacity", "point_lat", "point_lon"]
		w = writer.writerow(header)



	p.parse('data/' + filename)
	total_road_capacity = 0
	for item in road_capacity:
		# print road_capacity[item]
		total_road_capacity += road_capacity[item]
	print "Total road capacity: ", total_road_capacity, "km2"


	with open ('processed/roads_' + filename + '_coordinates.csv', 'wb') as f:
		writer = csv.writer(f)
		for coordinate in plotting_points:
			writer.writerow([unicode(s).encode("utf-8") for s in coordinate])

	grids, neighbors, average_lat_diff, average_lon_diff = parseExcel.parse_grid(gridDataFilename, sheetName, x_index, y_index, FID_index)
	utilities.grid_road(filename, grids, average_lat_diff, average_lon_diff, neighbors, verbose)
