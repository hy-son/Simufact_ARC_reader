from ARC_CSV import Arc_reader
import polyscope as ps

# Create an arc reader object
arc = Arc_reader(name="pointcloud")

# Read a csv dump
arc.load_csv("examples/95428XstlXremeshedX_FV_part_13.csv")

# Extract the point cloud coordinate
arc.get_coordinate()

# Add at each point all extract data
arc.get_point_cloud_data(display=True)

ps.show()