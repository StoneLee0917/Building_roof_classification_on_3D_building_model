from pathlib import Path
from copy import deepcopy
from cjio import cityjson
from shapely.wkt import load
cm = cityjson.load("MunichSample.city.json")
print(cm)
# extract ground surface and write it as wkt format into a dictionary
import re
# Function to convert a list of coordinates to WKT format
from shapely.geometry import Polygon, MultiPolygon

def convert_to_multipolygon(polygon_list):
    multipolygon = MultiPolygon([Polygon(polygon) for polygon in polygon_list])
    return multipolygon.wkt
# print(cm)
count=0
#file_path = "ground.txt"  # 文件路径
g_sur={}

for co_id, co in cm.cityobjects.items():
    for geom in co.geometry:
        # Only LoD >= 2 models have semantic surfaces
        if float(geom.lod) >= 2.0:
          # print("yes")
          # Extract the surfaces
          groundsurfaces = geom.get_surfaces(type='groundsurface')
          # path=co_id+".json"
          # print(path)
          # print(roofsurfaces)
          ground_boundaries = []
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
            # cityjson.save(roofsurfaces, path)
            # file.write(co_id+": "+roofsurfaces)
# for i in g_sur:
#   print(i, g_sur[i])
import geopandas as gpd
from shapely.wkt import loads

# Remove Z-values from the WKT strings and create valid geometry objects
g_sur_2d = {co_id: loads(wkt.replace(' Z (', ' (')) for co_id, wkt in g_sur.items()}

# Create a GeoDataFrame from the corrected dictionary, including co_id as a column
gdf = gpd.GeoDataFrame(list(g_sur_2d.items()), columns=['co_id', 'geometry'])

#gdf.geometry = gdf.buffer(0.1, resolution=0.1)
gdf.geometry = gdf.buffer(0.1)
# gdf.head()
# Set the coordinate reference system (CRS) if needed
# gdf.crs = "EPSG:4326"  # for WGS 84 coordinate system

# Make clusters:
# if two geometry intersect, put them into one cluster. in the end, give "I_count" the number of elements in their corresponding cluster
gdf['I_count'] = 0

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
            if row['geometry'].intersects(gdf.at[cluster_index, 'geometry']):
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

# Remove clusters that were merged
for cluster in clusters_to_remove:
  if cluster in clusters:
    clusters.remove(cluster)

# Update the "I_count" attribute with the size of each cluster
for i, cluster in enumerate(clusters):
    for index in cluster:
        gdf.at[index, 'I_count'] = len(cluster)

# -1 because they always intersect with themselves
gdf['I_count']=gdf['I_count']-1

# count
counti=0
count=0
for index, row in gdf.iterrows():
  count+=1
  if row['I_count']==0:
    counti+=1
print("there are ",count,"builidngs in total and ","there are ",counti,"not intersected buildings")
gdf.to_csv("Munich_neighbor.csv")
import pandas as pd

# Load the CSV files into DataFrames
df1 = pd.read_csv("Munich_metrics.csv")
df2 = pd.read_csv("Munich_neighbor.csv")

# Merge the DataFrames based on the 'id' and 'co_id' columns
merged_df = df1.merge(df2, left_on='id', right_on='co_id', how='left')

# Rename the 'I_count' column to 'N_count' in the merged DataFrame
merged_df.rename(columns={'I_count': 'N_count'}, inplace=True)

# Drop the 'co_id' column (if needed)
merged_df.drop(columns='co_id', inplace=True)

# Save the merged DataFrame to a new CSV file
merged_df.to_csv("Munich.csv", index=False)

print("Merged data saved to 'merged.csv'")
