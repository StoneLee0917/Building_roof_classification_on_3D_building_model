import pandas as pd
from sklearn.cluster import AgglomerativeClustering,MiniBatchKMeans,DBSCAN
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Load your CSV file into a DataFrame
# df = pd.read_csv('Zurich.csv')
df = pd.read_csv('Munich.csv')
df['obb_area_per'] = (df['obb_width'] * df['obb_length']) / df['ground_area']

# print(df)
# df=df.dropna()
# df.fillna(df.mean())
# Check for NaN values in the DataFrame and get a boolean mask

nan_mask = df.isna().any()

# Extract the column names with NaN values
columns_with_nan = df.columns[nan_mask].tolist()
# Check for NaN values in the DataFrame row-wise and get a boolean mask
nan_mask = df.isna().any(axis=1)
print(columns_with_nan)
# Extract the row numbers (indices) with NaN values
rows_with_nan = df.index[nan_mask].tolist()
print(rows_with_nan)
# Print the column names with NaN values
df = df.dropna()

# columns=['proximity_index_3d','hemisphericality_3d','roughness_index_2d','dispersion_index_3d','girth_index_3d','height_range','cubeness_3d','convexity_3d','ground_area']
# columns=['N_count','proximity_index_3d','obb_area_per','roughness_index_2d','dispersion_index_3d','girth_index_3d','height_range','cubeness_3d','convexity_3d','ground_area']
columns=['N_count','height_range','ground_area','convexity_3d','obb_area_per','circularity_2d','proximity_index_3d','rectangularity_2d']
X=df[columns]
print(X)
# correlation_matrix = X.corr()
# # Create a heatmap
# plt.figure(figsize=(10, 7))  # Adjust the figure size as needed
# ax=sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f",square='True')
# xticks_labels = ax.get_xticklabels()
# ax.set_xticklabels(xticks_labels, rotation=25, horizontalalignment='center')
# # Add labels and title
# plt.xlabel('Attributes')
# plt.ylabel('Attributes')
# plt.title('Correlation Matrix Heatmap')
#
# plt.savefig('heatmap2.png')
# # Show the plot
# plt.show()


input("enter to continue")
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X = scaler.fit_transform(X)
# fea_weight=[1,1,1,1,1,5,1,1,8]
fea_weight=[5,2,2,1,2,1,1,1]
X=X*fea_weight
# Perform Agglomerative Clustering with 15 clusters
n_clusters = 15

# agg_clustering = AgglomerativeClustering(n_clusters=n_clusters).fit(X)
#
# # Add the cluster labels to your DataFrame
# df['cluster_labels'] = agg_clustering.labels_
mbkmeans = MiniBatchKMeans(n_clusters=n_clusters)
mbkmeans.fit(X)
# Add the cluster labels to your DataFrame
df['cluster_labels'] =mbkmeans.labels_
# df['cluster_labels'] = agg_clustering.labels_
# Assuming df contains the 'id' and 'cluster_labels' columns
# df[['id', 'cluster_labels']].to_csv('output.csv', index=False)

# You can now analyze and explore the results in your DataFrame
# For example, you can count how many data points are in each cluster:
cluster_counts = df['cluster_labels'].value_counts()
#
# Print the cluster counts
print(cluster_counts)
from cjio import cityjson

# Load the CityJSON file
cm = cityjson.load("MunichSample.city.json")
# cm = cityjson.load("Zurich.city.json")
# Create a dictionary mapping building IDs to cluster labels
id_to_cluster_mapping = dict(zip(df['id'], df['cluster_labels']))

# Iterate through the City Objects and update the 'cluster_labels' attribute
for co_id, co in cm.cityobjects.items():
    if co.type=='Building':
        building_id = co_id
        if building_id in id_to_cluster_mapping:
            co.attributes['cluster_labels'] = id_to_cluster_mapping[building_id]


# Save the modified CityJSON file
# cm.save("modified_cityjson_file.json")
# cityjson.save(cm,"Zurich_with_type.json")

# cityjson.save(cm,"Munich_type_15.json")
print("111")

import random
import geopandas as gpd
import matplotlib.pyplot as plt

# Load the CityJSON file
cm = cityjson.load("MunichSample.city.json")

# Create a dictionary mapping building IDs to cluster labels
id_to_cluster_mapping = dict(zip(df['id'], df['cluster_labels']))

# Create a directory to store cluster-specific files
import os

output_dir = "cluster_exported_buildings"
os.makedirs(output_dir, exist_ok=True)

# Create a dictionary to store a random building for each cluster
random_buildings = {cluster_label: None for cluster_label in range(0, 14)}

# Create a GeoDataFrame to store all buildings
gdf = gpd.GeoDataFrame()

# Iterate through the City Objects and update the 'cluster_labels' attribute
for co_id, co in cm.cityobjects.items():
    if co.type == 'Building':
        building_id = co_id
        if building_id in id_to_cluster_mapping:
            cluster_label = id_to_cluster_mapping[building_id]
            co.attributes['cluster_labels'] = cluster_label

            # Append the building to the GeoDataFrame
            gdf = gdf.append({"geometry": co.geometry, "cluster_labels": cluster_label}, ignore_index=True)

            # Store a random building from this cluster if not already stored
            if random_buildings[cluster_label] is None:
                random_buildings[cluster_label] = co_id

# Save the GeoDataFrame as a shapefile (optional)
gdf.to_file("cluster_buildings.shp")

# Save the modified CityJSON file
# cityjson.save(cm, "Munich_type_15.json")

# Plot a random building from each cluster
for cluster_label, building_id in random_buildings.items():
    co = cm.cityobjects[building_id]
    gdf_cluster = gdf[gdf['cluster_labels'] == cluster_label]

    # Plot the buildings in this cluster using GeoPandas
    ax = gdf_cluster.plot(figsize=(10, 10))
    ax.set_title(f"Cluster {cluster_label} Buildings")
    plt.show()

print("111")
