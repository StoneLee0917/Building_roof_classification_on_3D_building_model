from pathlib import Path
from copy import deepcopy
from cjio import cityjson
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
plt.close('all')
import numpy as np
from tqdm import tqdm
import json
import geopandas as gpd
from shapely.wkt import loads
file_path1 = "rotterdam_1.3.city.json"
file_path2 = "rotterdam_c_22.json"
cm1 = cityjson.load(file_path1)
cm2=cityjson.load(file_path2)
# for lod 2.2 model and preserve 3d information
gdf2_3d = gpd.GeoDataFrame(columns=['id','co_id','roof_id', 'geometry_3d'])
index=0
for co_id, co in cm2.cityobjects.items():
    roof_id=0
    for geom in co.geometry:
        # Only LoD >= 2 models have semantic surfaces
        if float(geom.lod) >= 1.3:
          # print("yes")
          # Extract the surfaces
          roofsurfaces = geom.get_surfaces(type='roofsurface')
          # path=co_id+".json"
          # print(path)
          # print(roofsurfaces)
          roof_boundaries = []
          for r in roofsurfaces.values():
              roof_boundaries.append(geom.get_surface_boundaries(r))
          for i in roof_boundaries:
              for j in i:
                s=[]
                for t in j:
                  s.append(t)
                a=Polygon(s[0])
                gdf2_3d.loc[index]=[index,co_id,0,a]
                index+=1
                roof_id+=1
print("gdf2_3d: ",gdf2_3d.head())

# lod 2.2, but project to x-y plane for intersection
gdf2 = gpd.GeoDataFrame(columns=[ 'id','co_id','roof_id', 'geometry'])
index=0
for co_id, co in cm2.cityobjects.items():
    roof_id=0
    for geom in co.geometry:
        # Only LoD >= 2 models have semantic surfaces
        if float(geom.lod) >= 1.3:
          # print("yes")
          # Extract the surfaces
          roofsurfaces = geom.get_surfaces(type='roofsurface')
          # path=co_id+".json"
          # print(path)
          # print(roofsurfaces)
          roof_boundaries = []
          for r in roofsurfaces.values():
              roof_boundaries.append(geom.get_surface_boundaries(r))
          for i in roof_boundaries:
              for j in i:
                # file.write(co_id,j)
                s=[]
                for t in j:
                  s.append(t)
                a=Polygon(s[0])
                b = Polygon([(x, y) for x, y, _ in a.exterior.coords])
                gdf2.loc[index]=[index,co_id,0,b]
                index+=1
                roof_id+=1
print("gfd2: ",gdf2.head())
# for lod 1.3

gdf1 = gpd.GeoDataFrame(columns=[ 'co_id','roof_id', 'geometry'])
index=0
for co_id, co in cm1.cityobjects.items():
    roof_id=0
    for geom in co.geometry:
        # Only LoD >= 2 models have semantic surfaces
        if float(geom.lod) >= 1.3:
          # print("yes")
          # Extract the surfaces
          roofsurfaces = geom.get_surfaces(type='roofsurface')
          # path=co_id+".json"
          # print(path)
          # print(roofsurfaces)
          roof_boundaries = []
          for r in roofsurfaces.values():
              roof_boundaries.append(geom.get_surface_boundaries(r))
          for i in roof_boundaries:
              for j in i:
                # file.write(co_id,j)
                s=[]
                for t in j:
                  s.append(t)
                a=Polygon(s[0])
                b = Polygon([(x, y) for x, y, _ in a.exterior.coords])
                gdf1.loc[index]=[co_id,roof_id,b]
                index+=1
                roof_id+=1
print('gdf1: ',gdf1.head())
for index2, row2 in gdf2.iterrows():
  for index1, row1 in gdf1.iterrows():
    if row2['co_id']==row1['co_id']:
        intersection = row2['geometry'].intersection(row1['geometry'])
        i_area = intersection.area

        if i_area > 0.9 * row2['geometry'].area:
                # print(index2,index1,row2['co_id'],row1['roof_id'])
                gdf2.at[index2, 'roof_id'] = row1['roof_id']

                break
        else:
          continue
    else:
      continue
gdf2['pri_key'] = gdf2.apply(lambda row: str(row['co_id']) + '_' + str(row['roof_id']), axis=1)
merged_gdf = gdf2.merge(gdf2_3d, left_on='id', right_on='id', how='left')
to_drop=['co_id_y','roof_id_y','geometry']
gdf=merged_gdf.drop(to_drop,axis=1)
gdf.rename(columns={'co_id_x': 'co_id'}, inplace=True)
gdf.rename(columns={'roof_id_x': 'roof_id'}, inplace=True)
gdf.rename(columns={'geometry_3d': 'geometry'}, inplace=True)
print('joint: \n',gdf.head())
from shapely.geometry import MultiPolygon
grouped = gdf.groupby('pri_key')
gdf_group = gpd.GeoDataFrame(columns=['co_id', 'roof_id', 'pri_key', 'geometry'])
# multipolygons = []
for pri_key, group in grouped:
    co_id = group['co_id'].iloc[0]
    roof_id = group['roof_id'].iloc[0]
     # Merge the geometries from gdf2_3d into a MultiPolygon
    multipolygon = MultiPolygon(list(group['geometry'].values))
    # multipolygons.append(multipolygon)
    # Add the values to gdf_group
    gdf_group = gdf_group.append({'co_id': co_id, 'roof_id': roof_id, 'pri_key': pri_key, 'geometry': multipolygon}, ignore_index=True)

# Reset the index of gdf_group
gdf_group = gdf_group.reset_index(drop=True)
print('output:\n',gdf_group.head())
gdf_group.to_csv("grouped_roof_testresult.csv")


