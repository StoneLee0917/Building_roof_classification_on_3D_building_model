import os
import subprocess
directory = 'Nework_output_500'  # Replace with the path to your directory

# List all files in the directory
files = os.listdir(directory)

# Sort the files to ensure they are processed in order
files.sort()

# Loop through each CityJSON file
for file_name in files:
    output_csv=file_name+".csv"
    if file_name.endswith('.json'):
        file_path = os.path.join(directory, file_name)
        command = f'cityStats.py {file_path} -o {output_csv}'
        subprocess.run(command, shell=True)
        # Print a message indicating the completion of processing
        print(f"Processed: {file_name} -> {output_csv}")