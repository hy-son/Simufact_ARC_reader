# Simufact_ARC_reader
Python class to read csv created from ARC files of Simufact 2021.
All results or a selections can extracted from the ARC csv files and then displayed. 
The connectivity matrix is used to generate the graph linking all nodes.
<img src="https://github.com/hy-son/Simufact_ARC_reader/blob/main/imgs/part_166_TEMPTURE.PNG?raw=true" >
To be used, the ARC files must be transformed into CSV files using **ArcTool.exe**, available in:
```installation folder /additive/2021/sfTools/sfArcTool/bin/ArcTool.exe```

## For who this code is?:
This code is intended for people using Simufact 2021 and would like to import ARC results in python.

## Installation:
### Pip
Note: The files examples are not usable when this package is installed. If you want to use the files example you will have to dowload them from the github repository.

```pip install git+https://github.com/lerouxl/Simufact_ARC_reader.git@main```

### From sources
1. Clone this project: ```git clone https://github.com/lerouxl/Simufact_ARC_reader.git```
2. Install the requirement with `pip install -r requirements.txt`
3. Import the Arc_reader class in your code with `from ARC_CSV import Arc_reader`

___

If you installed from pip, import Arc_reader with:
 ```from simufact_arc_reader import Arc_reader```

The following examples considere your have clone this repository and you are in the Simufact_arc_reader root folder.

## Example 1: Read a csv file

```python
from simufact_arc_reader.ARC_CSV import Arc_reader
import polyscope as ps
from pathlib import Path

# Create an arc reader object
arc = Arc_reader(name="pointcloud")

# Read a part of a csv dump
arc.load_csv(r"simufact_arc_reader/examples/_Results_/00166/Process_FV_part_166.csv",
                attribute_to_load= ['Coordinates', 'TEMPTURE', 'XDIS', 'YDIS', 'ZDIS']
             )
# Only the coordinates, tempture and x,y, z displacement are read from the file.

# Extract the point cloud coordinate
arc.get_coordinate()
arc.get_connectivity()

# Add at each point all extract data
arc.get_point_cloud_data()

arc.load_meta_parameters(increment_id= 48, build_path=Path(r"simufact_arc_reader\\examples\\Stages\\Build.xml"),
                         increments_path=Path(r"simufact_arc_reader\\examples\\_Results_\\Meta\\Increments.xml"))
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

## Example 2 : Read two csv files: Coarse part and supports
This project is capable of dealing with Simufact coarse voxels without any modification.
```python
from ARC_CSV import Arc_reader
import polyscope as ps
from pathlib import Path

# Extract the part
# Create an arc reader object
part = Arc_reader(name="Part")
# Read a part of a csv dump
part.load_csv(r"simufact_arc_reader/example_coarse/_Results_/00354/Thermomechanical-Simu_FV_part_354.csv" )
# Extract the point cloud coordinate
part.get_coordinate()
part.get_connectivity()
# Add at each point all extract data
part.get_point_cloud_data()
part.load_meta_parameters(increment_id=104, build_path=Path(r"simufact_arc_reader\\example_coarse\\Stages\\Build.xml"),
                         increments_path=Path(r"simufact_arc_reader\\example_coarse\\_Results_\\Meta\\Increments.xml"))
# Load the metaparameters of with the build and increments file of the 104th simulation step
# Extract the edges
part.get_edge_index()
part.display()

#Extract the Supports
# Create an arc reader object
supports = Arc_reader(name="Supports")
# Read a part of a csv dump
supports.load_csv(r"simufact_arc_reader/example_coarse/_Results_/00354/Thermomechanical-Simu_FV_supports_354.csv" )
# Extract the point cloud coordinate
supports.get_coordinate()
supports.get_connectivity()
# Add at each point all extract data
supports.get_point_cloud_data()
supports.load_meta_parameters(increment_id=104, build_path=Path(r"simufact_arc_reader\\example_coarse\\Stages\\Build.xml"),
                         increments_path=Path(r"simufact_arc_reader\\example_coarse\\_Results_\\Meta\\Increments.xml"))
# Extract the edges
supports.get_edge_index()
supports.display()

# Display everything
ps.show() 
```
Here is the output of this code, where we can see the part and the supports in the same display.
<img src="https://github.com/hy-son/Simufact_ARC_reader/blob/main/imgs/Read_thermomecha_simulation.PNG?raw=true" >
We can compare what is read to Simufact results, the only difference is that our results are using meter instead of mm.
Here is the same point results in Simufact, the total displacement (TOTDISP) is 0.14mm on Simufact and 0.00014m with our code.
<img src="https://github.com/hy-son/Simufact_ARC_reader/blob/main/imgs/Simufact_thermomecha_simulation.PNG?raw=true" >

Note: There is no edges between the supports and parts. Only nodes at the same positions.

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
- *get_edge_index*: Generate the edges index. This is using the connectivity matrix of Simufact, where each neighbours is made of 8 nodes. The edges index can be acceded through the variable `self.edge_index`
- *display*: Generate the polyscope visualisation object

## Extract Simulation files for this script:
1. Transform the desired ARC files into CSV, for this Simufact have a tool:
   1. Go to the Simufact install folder, then *sfTools*, then *sfArcTool/bin* with a command line interface (C:\Program Files\simufact\additive\2021\sfTools\sfArcTool\bin)
   2. Use *ArcToolCmd.exe* to convert ARC file to csv: ```ArcToolCmd.exe FileIn="C:\my.arc" FileOut="C:\my.csv" Format=4```
   3. Copy those CSV in a folder ```simulation_folder/_Results_/n_layers/*.csv```
2. Extract the file *meta.xml* from ```simulation_folder/_Results_/Meta/Meta.xml.gz``` to ```simulation_folder/_Results_/Meta/Meta.xml```
3. Copy *Meta.xml* from ```simulation_folder/Meta/Meta.xml```


## Limitation
This reader is not an official one and is provided as is.

## Installation errors:
### Cannot set swap interval without a current OpenGL or OpenGL ES context

If the installation process raise the following error:
```bash 
× python setup.py develop did not run successfully.
│ exit code: -11
╰─> [2 lines of output]
    GLFW emitted error: GLX: Failed to create context: GLXBadFBConfig
    GLFW emitted error: Cannot set swap interval without a current OpenGL or OpenGL ES context
    [end of output]
```
This error is due to polyscope failing to install, this can be solve by cloning this repository, removing polyscope dependancy in `setup.py` line 22 and installing it:
```bash
git clone https://github.com/lerouxl/Simufact_ARC_reader.git
cd Simufact_ARC_reader 
nano setup.py
pip install -e .
```

The line 22 of `setup.py` must now be: `install_requires=['numpy>=1.2.0','xmltodict>=0.12.0']`

Note: This will deactivate all visualisation with polyscope but allow you to load and process ARC files.
