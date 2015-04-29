import csv
from geopy.distance import vincenty

# change here to change the file you want to edit, make sure it is under data/
filename = "cambridgema"

NUMBER_DIM = 30;

def same_point(p1, p2):
	if vincenty([p1[0], p1[1]], [p2[0], p2[1]]) <= 0.0001:
		return True
	return False

def id_to_grid(id):
	return (id / NUMBER_DIM, id % NUMBER_DIM)
def grid_to_id(x, y):
	return x * NUMBER_DIM + y
def lat_lon_to_grid(lat, lon):
	return (int((lat + 90) * NUMBER_DIM) + 1, int((lon + 180) * NUMBER_DIM) + 1)
def grid_to_lat_lon(x, y):
	return ((x-1.0)/NUMBER_DIM - 90.0, (y-1.0) / NUMBER_DIM - 180.0, x / NUMBER_DIM - 90.0, y/NUMBER_DIM - 180.0)


def find_roads_same_name():
	stored = {}
	with open('processed/roads_' + filename +'.csv', 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			id, name, lanes, road_capacity_from_conversion, highway, oneway, distance, road_capacity, start_lat, start_lon, end_lat, end_lon = row
			if name in stored:
				stored[name].append((id, start_lat, start_lon, end_lat, end_lon))
			else:
				stored[name] = [(name, id, start_lat, start_lon, end_lat, end_lon)]
	with open('processed/roads_' + filename + 'repetition_by_road_name.csv', 'w') as f:
		writer = csv.writer(f)
		for roads in stored:
			if len(stored[roads]) > 1:
				print stored[roads]
				writer.writerow(stored[roads])
			# for i in range(len(stored[roads])):
			# 	id, start_lat, start_lon, end_lat, end_lon = stored[roads][i]
			# 	for j in range(i+1, len(stored[roads])):
			# 		other_id, other_start_lat, other_start_lon, other_end_lat, other_end_lon = stored[roads][j]
			# 		if (vincenty([start_lat, start_lon], [other_start_lat, other_start_lon].meters) < 1.0):



find_roads_same_name()

def find_roads_closeby():
	stored = {}
	with open ('processed/roads_' + filename + '_coordinates.csv', 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			name, id, lat, lon = row
			stored[id]= (name, lat, lon)

	with open ('processed/roads_' + filename + '_coordinates.csv', 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			name, id, lat, lon = row
			for id_other in stored:
				name_other, lat_other, lon_other = stored[id_other]
				# Within 0.1m
				distance = vincenty([lat, lon], [lat_other, lon_other]).meters
				if (distance < 1.0 and distance != 0.0):
					print name, name_other, id, id_other, distance