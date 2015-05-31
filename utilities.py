import csv
from geopy.distance import vincenty

# Find out whether two points are the same
def same_point(p1, p2):
	if vincenty([p1[0], p1[1]], [p2[0], p2[1]]) <= 0.0001:
		return True
	return False

# Given a (lat, lon), find out the grid number
def lat_lon_to_grid(point, neighbors):
	FID = -1
	(lat, lon) = point
	for FID in neighbors:
		center, left_bound, right_bound, up_bound, down_bound = neighbors[FID]
		if lon <= up_bound and lon >= down_bound and lat <= right_bound and lat >= left_bound:
			return FID
	# print "The Following Point Does not Belong to Any Grid", lat, lon
	return None

# Given a starting point, an ending point, and a proportation, calculate the each grid's share of the road.
def points_to_grids(grids, start_point, end_point, total_proportion, average_lat_diff, average_lon_diff, neighbors):
	grid1 = lat_lon_to_grid(start_point, neighbors)
	grid2 = lat_lon_to_grid(end_point, neighbors)
	## In case point out of map
	if not grid1 or not grid2:
		return None
	
	if grid1 == grid2:
		return [(grid1, total_proportion)]
	if same_point(start_point, end_point):
		return [(grid1, total_proportion)]
	else:
		# Start and End point belong to different grids. Need to find the intersection of boundaries.
		# Use binary search

		# First check if two grids share an edge. If so, find the intersection of the line and the boundary directly.
		# Else, take the midpoint, then repeat the process for both (start, mid), (mid, end).
		truth_value, lat_or_lon, value = share_an_edge(grids, lat_lon_to_grid(start_point, neighbors), lat_lon_to_grid(end_point, neighbors), average_lat_diff, average_lon_diff)
		if truth_value == True:
			# Then it becomes the intersection of two lines problem.
			slope = (start_point[0] - end_point[0]) / (start_point[1] - end_point[1] + 0.0000000001)
			y_intercept = start_point[0] - slope * start_point[1]
			
			if lat_or_lon == "lat":				
				lon_intercept = (value - y_intercept) / slope

				mid_point = [value, lon_intercept]
				start_to_mid = vincenty(start_point, mid_point)
				mid_to_end = vincenty(mid_point, end_point)
				prop1 = start_to_mid / (start_to_mid + mid_to_end)
				prop2 = mid_to_end / (start_to_mid + mid_to_end)

			elif lat_or_lon == "lon":
				lat_intercept = slope * value + y_intercept

				mid_point = [lat_intercept, value]
				start_to_mid = vincenty(start_point, mid_point)
				mid_to_end = vincenty(mid_point, end_point)

				prop1 = start_to_mid / (start_to_mid + mid_to_end)
				prop2 = mid_to_end / (start_to_mid + mid_to_end)

			else:
				raise Exception("Bad value in share_an_edge() return", lat_or_lon)
			
			return [(grid1, prop1 * total_proportion), (grid2, prop2 * total_proportion)]
		else:
			mid_point = [(start_point[0] + end_point[0])/2.0, (start_point[1] + end_point[1])/2.0]
			firstHalf = points_to_grids(grids,start_point, mid_point, total_proportion / 2.0, average_lat_diff, average_lon_diff, neighbors)
			secondHalf = points_to_grids(grids, mid_point, end_point, total_proportion / 2.0, average_lat_diff, average_lon_diff, neighbors)
			if firstHalf == None and secondHalf == None:
				return None
			elif firstHalf == None:
				return secondHalf
			elif secondHalf == None:
				return firstHalf
			else:
				return firstHalf + secondHalf


def share_an_edge(grids, grid1, grid2, average_lat_diff, average_lon_diff):
	lat_diff = abs(grids[grid1][0] - grids[grid2][0])
	lon_diff = abs(grids[grid1][1] - grids[grid2][1])

	# print lat_diff, lon_diff, average_lat_diff, average_lon_diff

	if (0.98 < lat_diff / average_lat_diff and lat_diff/ average_lat_diff < 1.02) and (lon_diff / average_lon_diff < 0.02):
		return [True, "lat", (grids[grid1][0] + grids[grid2][0])/2.0]
	if (lat_diff / average_lat_diff < 0.02) and (0.98 < lon_diff/ average_lon_diff and lon_diff/ average_lon_diff < 1.02):
		return [True, "lon", (grids[grid1][1] + grids[grid2][1])/2.0]
	return [False, "", ""]



def grid_road(filename, grids, average_lat_diff, average_lon_diff, neighbors, verbose = False):
	with open('processed/roads_' + filename + '.csv', 'r') as f:
		reader = csv.reader(f)
		counter = 0

		iterreader = iter(reader)
		next(iterreader)

		for row in iterreader:
			counter += 1
			if counter % 100 == 0:
				print counter

			way_coordinates = []
			id, name, lanes, road_capacity_from_conversion, highway, oneway, distance, road_capacity = row[:8]

			coordinates = row[8:-1]

			road_capacity_from_conversion = float(road_capacity_from_conversion)
			for i in range(len(coordinates) / 2):
				lat, lon = float(coordinates[i*2]), float(coordinates[i*2+1])
				way_coordinates.append((lat, lon))
			current_point = way_coordinates[0]
			for (lat, lon) in way_coordinates:
				last_point = current_point
				current_point = (lat, lon)

				
				distance = vincenty(last_point, current_point).km
				road_capacity = distance * road_capacity_from_conversion
				if oneway != "yes":
					road_capacity *= 1

				# This method gives the proportion that the line segment lies in each grid it crosses
				distribution = points_to_grids(grids, last_point, current_point, 1.0, average_lat_diff, average_lon_diff, neighbors)
				if distribution:
					for (grid, proportion) in distribution:
						grids[grid][3] += road_capacity * proportion
						grids[grid][2] += distance * proportion
						# For knowing what roads are counted
						if name in grids[grid][4]:
							grids[grid][4][name][0] += distance
							grids[grid][4][name][1] += road_capacity
						else:
							grids[grid][4][name]= [distance, road_capacity]

	# print grids

	with open('processed/roads_' + filename + '_grid_capacity.csv', 'w') as f:
		writer = csv.writer(f)
		if verbose == True:
			writer.writerow(["FID", "Lat", "Lon", "Total_Distance", "Total_Capacity", "Roads in Grid"])
		else:
			writer.writerow(["FID", "Lat", "Lon", "Total_Distance", "Total_Capacity"])
		for row in grids:
			line = [row]+grids[row]
			if verbose == False:
				line = line[:-1]
			writer.writerow(line)

####################################################

# The following methods were utility calculations on whether two roads are closeby and share the same name,
# in which case we should consider them the same roads. These were not used in this iteration.

# NUMBER_DIM = 30;



# def id_to_grid(id):
# 	return (id / NUMBER_DIM, id % NUMBER_DIM)
# def grid_to_id(x, y):
# 	return x * NUMBER_DIM + y

# def grid_to_lat_lon(x, y):
# 	return ((x-1.0)/NUMBER_DIM - 90.0, (y-1.0) / NUMBER_DIM - 180.0, x / NUMBER_DIM - 90.0, y/NUMBER_DIM - 180.0)

# def find_roads_same_name():
# 	stored = {}
# 	with open('processed/roads_' + filename +'.csv', 'r') as f:
# 		reader = csv.reader(f)
# 		for row in reader:
# 			id, name, lanes, road_capacity_from_conversion, highway, oneway, distance, road_capacity, start_lat, start_lon, end_lat, end_lon = row
# 			if name in stored:
# 				stored[name].append((id, start_lat, start_lon, end_lat, end_lon))
# 			else:
# 				stored[name] = [(name, id, start_lat, start_lon, end_lat, end_lon)]
# 	with open('processed/roads_' + filename + 'repetition_by_road_name.csv', 'w') as f:
# 		writer = csv.writer(f)
# 		for roads in stored:
# 			if len(stored[roads]) > 1:
# 				print stored[roads]
# 				writer.writerow(stored[roads])

# def find_roads_closeby():
# 	stored = {}
# 	with open ('processed/roads_' + filename + '_coordinates.csv', 'r') as f:
# 		reader = csv.reader(f)
# 		for row in reader:
# 			name, id, lat, lon = row
# 			stored[id]= (name, lat, lon)

# 	with open ('processed/roads_' + filename + '_coordinates.csv', 'r') as f:
# 		reader = csv.reader(f)
# 		for row in reader:
# 			name, id, lat, lon = row
# 			for id_other in stored:
# 				name_other, lat_other, lon_other = stored[id_other]
# 				# Within 0.1m
# 				distance = vincenty([lat, lon], [lat_other, lon_other]).meters
# 				if (distance < 1.0 and distance != 0.0):
# 					print name, name_other, id, id_other, distance