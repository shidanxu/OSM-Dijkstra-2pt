# OSM-Dijkstra-2pt
Takes in a shape file with roads and calculates the distance between two positions. Example shape file is taken from California roads.

Geopy can be installed by pip install geopy

## Imposm parser

Takes in a shape file (can modify in the top of imposmParser.py), a file for the center of all grids, and output a csv file of all roads and relevant data in data/filename

Note that the Imposm parser has many installation dependnecies, let me know if you experience any trouble. I can try to help.

Usage:

    python imposmParser.py [name of the osm file] [name of the grid center file] [verbose] [sheet name] [x_coordinate_index] [y_coordinate_index] [FID_index]
    
    Example:
        python imposmParser.py madridcentral MAD_Test_modified.xls True 'Clustering Output' 2 1 0
    
        This will look for the madridcentral osm file and MAD_Test_modified.xls under data/.

    Example 2:
        python imposmParser.py Quito UIO_Establishments_RoadNetwork_268km2_forShidan.xlsx

Notes:

    verbose == True: road distribution will be printed in the final output

    name of the osm file and gird center files are required, rest are optional.

    verbose is by default False

    sheet name is the name of the Excel sheet that we print, by default it is 'Sheet1'

    x_coordinate_index is the Excel column that has the x_coordinates, counting columns from index 0

    Similarly for y_coordinate_index and FID_index

    By Default x_coordinate_index = 0, y_coordinate_index = 1, FID_index = 2.

    Please have the data files under data/ instead of root.


The road capacity conversions are under imposmParser.py, you may modify it directly.