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



lat_lon_to_grid(1.3438943, 103.6940396)
lat_lon_to_grid(-90.0, 179.6940396)