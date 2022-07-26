# Simufact_ARC_reader
Python class to read csv created from ARC files of Simufact 2021.

## For who this code is?:
This code is intended for people using Simufact 2021 and would like to import ARC results in python.

## Installation:
1. Copy `ARC_CSV.py` in your project
2. Install the requirement with `pip install -r requirements.txt`
3. Import the Arc_reader class in your code with `from ARC_CSV import Arc_reader`

## Example
```python
from ARC_CSV import Arc_reader
import polyscope as ps
from pathlib import Path

# Create an arc reader object
arc = Arc_reader(name="pointcloud")

# Read a part of a csv dump
arc.load_csv(r"examples/_Results_/00166/Process_FV_part_166.csv",
                attribute_to_load= ['Coordinates', 'TEMPTURE', 'XDIS', 'YDIS', 'ZDIS']
             )
# Only the coordinates, tempture and x,y, z displacement are read from the file.

# Extract the point cloud coordinate
arc.get_coordinate()
arc.get_connectivity()

# Add at each point all extract data
arc.get_point_cloud_data()

arc.load_meta_parameters(increment_id= 48, build_path=Path(r"examples\\Stages\\Build.xml"),
                         increments_path=Path(r"examples\\_Results_\\Meta\\Increments.xml"))
# Load the metaparameters of with the build and increments file of the 48th simulation step

# Extract the edges
arc.get_edge_index()

arc.display()
ps.show()
```
Here is the output of this code, where we can see the temperature of each nodes.
<img src="https://github.com/hy-son/Simufact_ARC_reader/blob/main/imgs/part_166_TEMPTURE.PNG?raw=true" >
This code allow to see the deformation vectors of all nodes:
<img src="https://github.com/hy-son/Simufact_ARC_reader/blob/main/imgs/part_166_Deformation_vectors.PNG?raw=true" >

## Use
1. Transform the ARC file into a CSV file using ARCTool.exe (file in the Simufact directory) (The file with X_FV_part is the good one)
2. Use the Arc_reader class to load it with *load_csv*
3. Extract the cloud point with *get_coordinate*
4. Put all the available data to the point cloud with *get_point_cloud_data*
5. You can load in metaparameters the printing parameters.
   1. it will load `_Results_\Meta\Increments.xml` to provide:
      1. the printing time of the arc file (s)
      2. the duration of this printing/simulation step (s)
   2. it will load `Stages\Build.xml` to load:
      1. the laser power (W)
      2. the laser speed (m/s)
      3. the layer thickness (m)
   3. Those data can be acceded with `arc.metaparameters`
6. Show the cloud point with *ps.show()*

## Functions:
- *Arc_reader(name="pointcloud")*: Create an object reading csv ARC files. The arguments "name" set the display name in polyscope. 
- *load_csv("file.csv")*: Load the csv file in the *raw_data* variable.
- *get_coordinate()*: Extract the coordinate from the *raw_data*
- *get_point_cloud_data(display=True)*: Add features to the point of cloud. The *display* variable will define if the point cloud is show by default by ps.show().
- *get_edge_index*: Generate the edges. This is using the connectivity matrix of Simufact, where each neighbours is made of 8 nodes.
- *display*: Generate the polyscope visualisation object

## Limitation
This reader is not an official one and is provided as is.
