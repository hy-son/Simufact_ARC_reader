from ARC_CSV import Arc_reader
import polyscope as ps

# Create an arc reader object
arc = Arc_reader(name="pointcloud")

# Read a csv dump
#arc.load_csv(r"data\thermomechanical\raw\Thermomecha95428laser200W\Process\_Results_\00142\Process_FV_baseplate_142.csv")
#arc.load_csv(r"data\thermomechanical\raw\Thermomecha95428laser200W\Process\_Results_\00142\Process_FV_part_142.csv")
arc.load_csv(r"examples/_Results_/00166/Process_FV_part_166.csv")

# Extract the point cloud coordinate
arc.get_coordinate()

# Add at each point all extract data
arc.get_point_cloud_data()
# If the arc.csv file is still in the Simufact folder, the printing parameters can be loaded using load_meta_parameters
# It will go in the _Results_ and Stages folder, loader Build.xml and Increments.xml to provide:
# - laser speed
# - laser power
# - layer thickness
# - time
# - time used by the arc iteration
arc.load_meta_parameters(increment_id=47)
print(f"Laser power used is {arc.metaparameters.power_W}")
print(f"Laser speed used is {arc.metaparameters.speed_m_s}")
print(f"Layer thickness used is {arc.metaparameters.layerThickness_m}")
print(f"Subprocess name is {arc.metaparameters.subProcessName}")

arc.display()
ps.show()