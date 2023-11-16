from cjio import cityjson
import os
import subprocess
cm = cityjson.load("Newyork_lod2.city.json")
print(cm)
# Initialize an empty list to store buildings
buildings = []

# Iterate through the features and extract buildings
for feature_id, feature in cm.cityobjects.items():
    if feature.type == 'Building':
        buildings.append((feature_id,feature))

# Split the buildings into groups of 200
building_groups = [buildings[i:i + 500] for i in range(0, len(buildings), 500)]

# Create the output directory if it doesn't exist
output_dir = 'nework_output_500'
os.makedirs(output_dir, exist_ok=True)

# Write each group of buildings to a separate file
for i, group in enumerate(building_groups):
    output_file = os.path.join(output_dir, f'city_part_{i + 1}.json')

            # Create a new CityJSON object and add selected features
    new_cm = cityjson.CityJSON()
    for co_id, co in group:
        new_cm.cityobjects[co_id] = co

    # Set the metadata and save the new CityJSON object to a file
    # new_cm.metadata = cm.metadata
    cityjson.save(new_cm, output_file)
    # new_cm.save(output_file)