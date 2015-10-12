import csv
import xlrd
from geopy.distance import vincenty
from sets import Set


# gridDataFilename = "UIO_Establishments_RoadNetwork_268km2_forShidan.xlsx"


# Find closest 4 points
# If distance smaller than necessary, that means edge point. Ignore other points
# Each of the 4 points define a boundary.
# If any boundary missing, use the opposite side as info. In case both boundaries are missing, take average.


def parse_grid(gridDataFilename, worksheet, x_coord_index = 0, y_coord_index = 1, FID_index = 2):
	grid = {}
	neighbors = {}
	my_neighbors = {}
	coordinates = []
	average_left_bound = 0.0
	num_left_bound = 0
	average_right_bound = 0.0
	num_right_bound = 0
	average_up_bound = 0.0
	num_up_bound = 0
	average_down_bound = 0.0
	num_down_bound = 0

	# Open the workbook
	workbook = xlrd.open_workbook('data/' + gridDataFilename)
	worksheet = workbook.sheet_by_name(worksheet)
	num_rows = worksheet.nrows - 1

	## Initialize neighbors to My point, left boundary, right, up, down
	for i in range(num_rows+1):
		row = worksheet.row(i)
		FID_2 = row[FID_index].value
		try:
			float(FID_2)
			neighbors[FID_2] = [(0.0, 0.0), "", "", "", ""]
			my_neighbors[FID_2] = []
		except ValueError:
			pass

	curr_row = -1
	while curr_row < num_rows:
		curr_row += 1
		row = worksheet.row(curr_row)

		# Extract x, y coordinates and ID, based on the indices given
		x_coord = row[x_coord_index].value
		y_coord = row[y_coord_index].value
		FID_2 = row[FID_index].value

		# Avoid header
		try:
			float(x_coord)	
			grid[FID_2] = [float(y_coord), float(x_coord), 0.0, 0.0, {}, "The coordinates: \n"]
			# print grid[FID_2]
			coordinates.append((float(y_coord), float(x_coord)))
		except ValueError:
			pass

	# Find out neighboring grids
	for id in grid:
		neighbors[int(id)][0] = (grid[id][0], grid[id][1])
		for other_id in grid:
			if int(id) != int(other_id):
				my_point = grid[id][0], grid[id][1]
				other_point = grid[other_id][0], grid[other_id][1]
				distance = vincenty(my_point, other_point)

				# Neighbors
				if distance < 1.1:
					my_neighbors[int(id)].append(other_point)

	# Calculate the bounding box of each grid
	for my_id in neighbors:
		my_point = neighbors[my_id][0]
		for other_point in my_neighbors[my_id]:
			# print my_point, other_point
			if abs(my_point[0] - other_point[0]) > 0.003:
				if my_point[0] - other_point[0] > 0.0:
					# left_boundary
					neighbors[my_id][1] = (my_point[0] + other_point[0]) / 2.0
					num_left_bound += 1
					average_left_bound += float((abs(my_point[0] - other_point[0])/2.0 - average_left_bound) / num_left_bound)
					# print average_left_bound
				else:
					# right boundary
					neighbors[my_id][2] = (my_point[0] + other_point[0]) / 2.0
					num_right_bound += 1
					average_right_bound += float((abs(my_point[0] - other_point[0])/2.0 - average_right_bound) / num_right_bound)
					# print average_right_bound

			elif abs(my_point[1] - other_point[1]) > 0.003:
				if my_point[1] - other_point[1] > 0.0:
					# down boundary
					neighbors[my_id][4] = (my_point[1] + other_point[1]) / 2.0
					num_down_bound += 1
					average_down_bound += float((abs(my_point[1] - other_point[1])/2.0 - average_down_bound) / num_down_bound)
					# print average_down_bound
				else:
					# up boundary
					neighbors[my_id][3] = (my_point[1] + other_point[1]) / 2.0
					num_up_bound += 1
					average_up_bound += float((abs(my_point[1] - other_point[1])/2.0 - average_up_bound) / num_up_bound)
					# print average_up_bound

	# print average_left_bound, average_right_bound, average_up_bound, average_down_bound 
	# for usage of grids on the boundaries who have no neighbors in some directions.
	for id in neighbors:
		for i in range(1, 5):
			if neighbors[id][i] == "":
				if i == 1:
					neighbors[id][i] = neighbors[id][0][0] - average_left_bound
				elif i == 2:
					neighbors[id][i] = neighbors[id][0][0] + average_right_bound
				elif i == 3:
					neighbors[id][i] = neighbors[id][0][1] + average_up_bound
				elif i == 4:
					neighbors[id][i] = neighbors[id][0][1] - average_down_bound

	# print neighbors
	
	return grid, neighbors, average_left_bound*2, average_up_bound*2
