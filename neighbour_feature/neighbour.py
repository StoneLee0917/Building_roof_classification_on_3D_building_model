# extract ground surface and write it as wkt format into a dictionary
import re
# Function to convert a list of coordinates to WKT format
from pathlib import Path
from copy import deepcopy
from cjio import cityjson
from shapely.wkt import load
# from shapely import Polygon
from shapely.geometry import Polygon, MultiPolygon
cm=cityjson.load('data/Berlin_mitte.json')
def convert_to_multipolygon(polygon_list):
    multipolygon = MultiPolygon([Polygon(polygon) for polygon in polygon_list])
    return multipolygon.wkt
# print(cm)
count=0
file_path = "ground.txt"  # 文件路径
g_sur={}
with open(file_path, "w") as file:
  for co_id, co in cm.cityobjects.items():
      for geom in co.geometry:
          # Only LoD >= 2 models have semantic surfaces
          if float(geom.lod) >= 2.0 :
            # print("yes")
            # Extract the surfaces
            groundsurfaces = geom.get_surfaces(type='groundsurface')
            # path=co_id+".json"
            # print(path)
            # print(roofsurfaces)
            ground_boundaries = []

            if hasattr(groundsurfaces, 'values') and callable(getattr(groundsurfaces, 'values')):
                for r in groundsurfaces.values():

                    ground_boundaries.append(geom.get_surface_boundaries(r))
            # if co_id=="NL.IMBAG.Pand.1714100000730492-0":
            # print(co_id)
            # print(roofsurfaces)
            for i in ground_boundaries:
                reformatted_data = [[list(coord) for coord in polygon_coords] for polygon_list in i for polygon_coords in polygon_list]
                wkt_polygon = convert_to_multipolygon(reformatted_data)  # Assuming there's only one polygon in each line
                # Write the result to the output file
                # print(f"{co_id}: {wkt_polygon}\n")
                g_sur[co_id]=wkt_polygon
                count+=1
print(count)
import geopandas as gpd
from shapely.wkt import loads

# Remove Z-values from the WKT strings and create valid geometry objects
g_sur_2d = {co_id: loads(wkt.replace(' Z (', ' (')) for co_id, wkt in g_sur.items()}

# Create a GeoDataFrame from the corrected dictionary, including co_id as a column
gdf = gpd.GeoDataFrame(list(g_sur_2d.items()), columns=['co_id', 'geometry'])
print(gdf.head())
gdf['N_direct'] = 0
gdf['N_direct_area'] = 0
gdf['I_count'] = 0
num_rows, num_columns = gdf.shape

print(f"Number of rows: {num_rows}")
print(f"Number of columns: {num_columns}")
gdf['buffered_geometry']=gdf.geometry.buffer(0.1)
# To check: the number of polygons that are intersected with others
gdf = gdf[gdf['geometry'].is_valid]  # Filter out invalid geometries
gdf['geometry'] = gdf['geometry'].buffer(0)
gdf['buffered_geometry'] = gdf['buffered_geometry'].buffer(0)
# Make clusters:
# if two geometry intersect, put them into one cluster. in the end, give "I_count" the number of elements in their corresponding cluster

# Create an empty list to store clusters
clusters = []
# Create a list to store clusters to be removed
clusters_to_remove = []
# Iterate through each geometry in the GeoDataFrame
for index, row in gdf.iterrows():
    # Check if the current geometry intersects with any existing clusters
    intersecting_clusters = []
    for cluster in clusters:
        for cluster_index in cluster:
            if row['buffered_geometry'].intersects(gdf.at[cluster_index, 'geometry']):
                intersecting_clusters.append(cluster)
    # Merge intersecting clusters, if any
    if intersecting_clusters:
        new_cluster = set()
        for cluster in intersecting_clusters:
            new_cluster.update(cluster)
            clusters_to_remove.append(cluster)
        new_cluster.add(index)
        clusters.append(new_cluster)
    else:
        # Create a new cluster if no intersections found
        clusters.append({index})
    print(index)
# Remove clusters that were merged
for cluster in clusters_to_remove:
  if cluster in clusters:
    clusters.remove(cluster)
# Update the "I_count" attribute with the size of each cluster
for i, cluster in enumerate(clusters):
    for index in cluster:
        gdf.at[index, 'I_count'] = len(cluster)
# -1 because they always intersect with themselves
# gdf['I_count']=gdf['I_count']-1


num_rows,num_columns=gdf.shape
# Loop through each row to check for intersections
for index, row in gdf.iterrows():
    for other_index, other_row in gdf.iterrows():
        # Skip comparing a row with itself
        # if index == other_index:
        #     print(index)
        #     continue
        if row['co_id'] == other_row['co_id']:
            continue
        # Check if the geometry of the current row intersects with the other row

        if row['buffered_geometry'].intersects(other_row['geometry']):
            # If they intersect, increment the 'I_count' attribute by 1
            intersection = row['buffered_geometry'].intersection(other_row['geometry'])
            intersection_area = intersection.area
            gdf.at[index, 'N_direct'] += 1
            gdf.at[index, 'N_direct_area'] += intersection_area
    print(index)

# Now, 'I_count' contains the count of intersections for each geometry
count = 0
for index, row in gdf.iterrows():

    if row['N_direct'] == 0:
        count += 1
gdf.to_csv('Berlin_N2.csv')

print("there are ", count, "not intersected buildings")

# import pandas as pd
# df1=pd.read_csv("data/montreal_metrics.csv")
# df2=pd.read_csv("data/Montreal_N.csv")
#
# df1['id'] = df1['id'].astype(str)
# df2['id'] = df2['co_id'].astype(str)
# # 现在左侧和右侧的'id'列应该具有相同的数值数据类型
# print(df1.head())
# print(df2.head())
# merged_df = df1.merge(df2, left_on='id', right_on='id', how='left')
# merged_df.to_csv("Munich_1015.csv")